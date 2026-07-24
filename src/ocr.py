from paddleocr import PaddleOCR
from pathlib import Path

model = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="japan",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
image_path = PROJECT_ROOT / "images" / "Darwins_Game_v12" / "12_058.jpg"

result = model.predict(str(image_path))

for res in result:
    res.print()