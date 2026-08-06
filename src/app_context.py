from paddleocr import PaddleOCR
# from paddlex.inference.common.batch_sampler import text_batch_sampler
# from paddlex.inference.common.result.converter import build_word_blocks

from database.db_config import database_connection
from parser.deinflect import load_deinflection_rules

print("Loading AppContext from:", __file__)

class AppContext:
    def __init__(self) -> None:
         self.model = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang="japan",
            )

         self.deinflection_rules = load_deinflection_rules()

         self.connection = database_connection()
