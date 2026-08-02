from pathlib import Path
from dataclasses import dataclass
from pprint import pprint
import json
import logging

from paddleocr import PaddleOCR
from paddlex.inference.common.batch_sampler import text_batch_sampler
from paddlex.inference.common.result.converter import build_word_blocks

import ocr
from parser import parser
from parser.deinflect import deinflect

# logging configurations

logging.basicConfig(filename='log/system.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# class represent each deinflection rule
@dataclass
class Rule:
    inflected: str
    deinflected: str
    conditions_in: set[str]
    conditions_out: set[str]


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
text_boxes = ocr.extract_text(str(image_path), model)
logging.info('Done OCR process, result returned with: {} bounding boxes'.format(len(text_boxes)))
# groups text box from same bubble speech into ones
lines = ocr.clean_text(text_boxes)
logging.info('result return with {} bubble speeches'.format(len(lines)))
# loading deinflected rules from json file
with open("parser/deinflect_rules.json", encoding="utf-8") as f:
    data = json.load(f)
deinflect_rules: list[Rule] = []

logging.debug('start load deinflection rules..')

for transform in data["transforms"].values():
    for rule in transform["rules"]:
        deinflect_rules.append(
            Rule(
                inflected=rule["inflected"],
                deinflected=rule["deinflected"],
                conditions_in=rule["conditionsIn"],
                conditions_out=rule["conditionsOut"],
            )
        )

logging.info('start looking up word in dictionary')
for text in lines:
    # receive list of word objects
    result = parser.parse(text, deinflect_rules)

    for word in result:
        print(str(word.id) + ". " + word.lemma + ":" + word.meaning)
