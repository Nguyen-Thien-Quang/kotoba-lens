
# insert new word into database
def add_word(image_id: int,
             lemma: str, 
             pos: str, 
             reading: str, 
             meaning: str, 
             score: float, 
             order: int, 
             cursor):
    cursor.execute(
        """
        INSERT INTO WORDS (LEMMA, POS, READING, MEANING, SCORE)
        VALUES (?, ?, ?, ?, ?)
        """,
        (lemma, pos, reading, meaning, score),
        )

    word_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO IMAGES_WORDS (IMAGE_ID, WORD_ID, WORD_ORDER)
        VALUES (?, ?, ?)
        """,
        (image_id, word_id, order),
        )

def add_image(book_id: int,
              path: str,
              ocr_result: str,
              page: int,
              cursor) -> int | None:

    cursor.execute(
            """
            SELECT IMG_ID FROM IMAGES
            WHERE PATH = ?
            """,
            (path,),
            )
    existed = cursor.fetchone()

    if existed is None:
        cursor.execute(
                """
                INSERT INTO IMAGES (BOOK_ID, PATH, OCR_RESULT, PAGE)
                VALUES (?, ?, ?, ?)
                """,
                (book_id, path, ocr_result, page),
            )

        return cursor.lastrowid
    else:
        return None


def add_book(name: str, path: str, cursor) -> int | None:
    cursor.execute(
            """
            SELECT BOOK_ID FROM BOOKS
            WHERE PATH = ?
            """,
            (path,),
            )
    existed = cursor.fetchone()

    if existed is None:
        cursor.execute(
                """
                INSERT INTO BOOKS (NAME, PATH)
                VALUES (?, ?)
                """,
                (name, path),
                )
        return cursor.lastrowid
    else:
        return None


