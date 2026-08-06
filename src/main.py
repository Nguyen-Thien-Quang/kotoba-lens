from pathlib import Path
from dataclasses import dataclass

from paddleocr import PaddleOCR
from paddlex.inference.common.batch_sampler import text_batch_sampler
from paddlex.inference.common.result.converter import build_word_blocks

from database import db_config
import ocr
from parser import parser
from parser.deinflect import deinflect, load_deinflection_rules
from DAO import add_word, add_image

def image_process(image_path: Path,
                  model: PaddleOCR,
                  deinflect_rules ,
                  c): 
    # extract text from image,output list of object contain text, bouding boxes and score
    text_boxes = ocr.extract_text(str(image_path), model)
    # groups text box from same bubble speech into ones
    lines = ocr.clean_text(text_boxes)

    # parsing vocabularies from texts and load image into database
    output = []
    raw_result = ""
    for text in lines:
        # receive list of word objects
        raw_result += text + "\n"
        result = parser.parse(text, deinflect_rules)
        output.extend(result)

    output.sort(key=lambda r: r.score, reverse=True)

    # load inmages and word into database
    image_id = load_image(-1, str(image_path), raw_result, -1, c)
    add_words_to_DB(output, image_id, c)

def add_words_to_DB(words: list[parser.Word], image_id: int, cursor):
    for i, word in enumerate(words):
        add_word(image_id,
                 word.lemma,
                 word.pos, 
                 word.reading, 
                 word.meaning, 
                 word.score, 
                 i, 
                 cursor)

def load_image(book_id: int, path: str, raw_result: str, page: int, cursor) -> int:
    return add_image(book_id, path, raw_result, page, cursor)


    
if __name__ == "__main__":
# instantiate the model
    model = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        lang="japan",
    )

    conn = db_config.database_connection()
# specify image_path
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    image_path = PROJECT_ROOT / "images" / "image1.jpg"

# load deinflect_rules
    rules = load_deinflection_rules()
# ocr image and parser all the vocabularies from text
    output = image_process(image_path, model, rules, conn.cursor())
    conn.commit()
    conn.close()

