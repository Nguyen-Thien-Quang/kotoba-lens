from pathlib import Path

from paddleocr import PaddleOCR
from paddlex.inference.common.batch_sampler import text_batch_sampler
from paddlex.inference.common.result.converter import build_word_blocks

import ocr

# instantiate the model
model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="japan",
)

# specify image_path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
image_path = PROJECT_ROOT / "images" / "image1.jpg"

# extract text from image,output list of object contain text, bouding boxes and score
text_boxes = ocr.extract_text(image_path, model)
# groups text box from same bubble speech into ones
lines = ocr.clean_text(text_boxes)

for text in lines:
    print(text)
