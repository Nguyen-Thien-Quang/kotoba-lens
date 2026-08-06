import ocr
from dataclasses import dataclass
from pathlib import Path
from parser import parser
from parser.deinflect import deinflect, load_deinflection_rules
from DAO import add_word, add_image

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



def image_process(image_path: Path,
                  model,
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
    if image_id is not None:
        add_words_to_DB(output, image_id, c)

def load_image(book_id: int, path: str, raw_result: str, page: int, cursor) -> int | None:
    return add_image(book_id, path, raw_result, page, cursor)


