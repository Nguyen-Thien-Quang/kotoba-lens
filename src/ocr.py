from paddleocr import PaddleOCR
from pathlib import Path

from dataclasses import dataclass
import numpy as np

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

with open("output/filtered_result.txt", "w+") as f:
    for ocrResult in format_result:
        if ocrResult.score > 0.8:
            f.write(ocrResult.text + "\n")
        else:
            print(ocrResult.text + "|")
            print(ocrResult.score)
            print("\n")
