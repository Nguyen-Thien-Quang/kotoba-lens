from pathlib import Path
from statistics import median
from dataclasses import dataclass
import numpy as np

from paddleocr import OCROptions, PaddleOCR
from paddlex.inference.common.batch_sampler import text_batch_sampler
from paddlex.inference.common.result.converter import build_word_blocks


# class object for each text boxes
@dataclass
class OCRResult:
    text: str
    poly: np.ndarray
    score: float
    box: np.ndarray

    def get_x_min(self) -> int:
        return self.box[0]

    def get_x_max(self) -> int:
        return self.box[2]

    def get_y_min(self) -> int:
        return self.box[1]

    def get_y_max(self) -> int:
        return self.box[3]

    def get_text_width(self) -> int:
        return self.get_x_max() - self.get_x_min()


# call model inference and return list of OCRResult object
def extract_text(image_path: str, model: PaddleOCR) -> list[OCRResult]:
    result = model.predict(str(image_path))
    data = result[0]  # get the raw_data in 'res' key
    # format raw_result into text boxes object
    format_result = [
        OCRResult(text, poly, score, box)
        for text, poly, score, box in zip(
            data["rec_texts"], data["rec_polys"], data["rec_scores"], data["rec_boxes"]
        )
    ]
    return format_result


# clean raw ouput from ocr model into list of meaningful, complete text lines
def clean_text(data: list[OCRResult]) -> list[str]:
    # data is list of OCRResult object
    # sort the list of text in order of right to left
    data.sort(key=lambda r: r.get_x_max(), reverse=True)

    # remove furigana
    data = remove_furigana(data)

    # calculate average text height
    avg_text_h = 0
    for result in data:
        avg_text_h += result.get_text_width()
    avg_text_h = avg_text_h / len(data)

    # groups close OCRResults into same bubble_speech
    bubble_id = [-1] * len(data)  # list to store bubble_id of each text box
    bubble_speech = list()  # list of bubble text
    thres = avg_text_h * 0.2  # threshold of distance decide grouping text box
    for i in range(len(data)):
        # first text auto have it own bubble_speech
        if i == 0:
            bubble_speech.append(data[i].text)  # append as new bubble
            bubble_id[i] = len(bubble_speech) - 1  # store bubble_id
            continue

        found_flag = False
        for j in range(i - 1, -1, -1):  # compare with all text box before
            horizontal_dis = max(0, data[j].get_x_min() - data[i].get_x_max())

            # stop if meet text box that is already too far from current text box
            if horizontal_dis > avg_text_h:
                break
            else:
                # check if vertical position suitable
                if (
                    data[i].get_y_max() > data[j].get_y_min()
                    and data[j].get_y_max() > data[i].get_y_min()
                ):
                    # if match: put text[i] into bubble of text[j]
                    bubble_speech[bubble_id[j]] += data[i].text
                    bubble_id[i] = bubble_id[j]
                    found_flag = True
                    break
        if found_flag == True:
            continue
        else:
            bubble_speech.append(data[i].text)
            bubble_id[i] = len(bubble_speech) - 1
    return bubble_speech


def remove_furigana(data: list[OCRResult]) -> list[OCRResult]:

    heights = [result.get_text_width() for result in data]
    median_height = median(heights)

    # remove furigana by remove all text with confidence score smaller than 0.8
    data = [r for r in data if r.get_text_width() >= 0.6 * median_height]
    return data
