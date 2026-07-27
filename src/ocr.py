from paddleocr import PaddleOCR
from pathlib import Path

from dataclasses import dataclass
import numpy as np
from paddlex.inference.common.batch_sampler import text_batch_sampler
from paddlex.inference.common.result.converter import build_word_blocks

# class object for each text boxes


@dataclass
class OCRResult:
    text: str
    poly: np.ndarray
    score: float
    box: np.ndarray


# instantiate the model

model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="japan",
)

# specify image path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
image_path = PROJECT_ROOT / "images" / "image1.jpg"

# inference, OCR the image
result = model.predict(str(image_path))

res = result[0]  # acces first element 'res'\

# zip result into list of OCRResult
format_result = [
    OCRResult(text, poly, score, box)
    for text, poly, score, box in zip(
        res["rec_texts"], res["rec_polys"], res["rec_scores"], res["rec_boxes"]
    )
]

# delete all furigana
format_result = [r for r in format_result if r.score >= 0.8]
# sorting in order of box's position from right to left
format_result.sort(key=lambda r: r.box[2], reverse=True)

# calculate average text height
avrg_text_h = 0
for result in format_result:
    avrg_text_h = avrg_text_h + result.box[2] - result.box[0]

avrg_text_h = avrg_text_h / len(format_result)

# for res in format_result:
#     print(res.box[0], res.box[1], res.box[2], res.box[3])
#     print(res.text)
# # groups nearby text into clusters
bubble_id = [-1] * len(format_result)  # list to store bubble_id of each text box
bubble_speech = list()  # list of bubble text
thres = avrg_text_h * 0.2  # threshold of distance decide grouping text box
for i in range(len(format_result)):
    # first text auto have it own bubble_speech
    if i == 0:
        bubble_speech.append(format_result[i].text)  # append as new bubble
        bubble_id[i] = len(bubble_speech) - 1  # store bubble_id
        continue

    found_flag = False
    for j in range(i - 1, -1, -1):  # compare with all text box before
        horizontal_dis = max(0, format_result[j].box[0] - format_result[i].box[2])

        # stop if meet text box that is already too far from current text box
        if horizontal_dis > avrg_text_h:
            break
        else:
            # check if vertical position suitable
            if (
                format_result[i].box[3] > format_result[j].box[1]
                and format_result[j].box[3] > format_result[i].box[1]
            ):
                # if match: put text[i] into bubble of text[j]
                bubble_speech[bubble_id[j]] += format_result[i].text
                bubble_id[i] = bubble_id[j]
                found_flag = True
                break
    if found_flag == True:
        continue
    else:
        bubble_speech.append(format_result[i].text)
        bubble_id[i] = len(bubble_speech) - 1

print(len(bubble_speech))
for text in bubble_speech:
    print(text)
