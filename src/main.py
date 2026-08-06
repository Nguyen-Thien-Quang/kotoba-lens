from pathlib import Path
from database import db_config
from app_context import AppContext
from services import image_process

    
if __name__ == "__main__":

    context = AppContext()
    conn = context.connection
    rules = context.deinflection_rules
    model = context.model

# specify image_path
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    image_path = PROJECT_ROOT / "images" / "image1.jpg"

# ocr image and parser all the vocabularies from text
    output = image_process(image_path, -1, -1, model, rules, conn.cursor())
    conn.commit()
    conn.close()

