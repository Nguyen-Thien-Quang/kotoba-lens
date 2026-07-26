from paddleocr import PaddleOCR
from pathlib import Path

model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="japan",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
image_path = PROJECT_ROOT / "images" / "image1.jpg"

result = model.predict(str(image_path))

res = result[0]  # acces first element 'res'
for text in res["rec_texts"]:  # res is a dictionary, acces element by key
    print(text)
