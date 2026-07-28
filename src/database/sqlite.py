import sqlite3

conn = sqlite3.connect(":memory")
c = conn.cursor()

print("Set up connection successful")

c.execute("""
CREATE TABLE BOOKS (
    BOOK_ID INTEGER PRIMARY KEY,
    NAME TEXT NOT NULL,
    PATH TEXT NOT NULL,
    CREATED_AT TEXT
)
""")

print("create books table successful")

c.execute("""
CREATE TABLE IMAGES (
    IMG_ID INTEGER PRIMARY KEY,
    BOOK_ID INTEGER NOT NULL,
    PATH TEXT NOT NULL,
    OCR_RESULT TEXT,
    IMPORT_TIME TEXT,
    PAGE INTEGER,
    FOREIGN KEY (BOOK_ID) REFERENCES BOOKS(BOOK_ID)
)
""")

print("create image table successful")

c.execute("""
CREATE TABLE WORDS (
    WORD_ID INTEGER PRIMARY KEY,
    IMAGE_ID INTEGER NOT NULL,
    LEMMA TEXT NOT NULL,
    POS TEXT,
    READING TEXT,
    MEANING TEXT,
    SCORE REAL,
    FOREIGN KEY (IMAGE_ID) REFERENCES IMAGES(IMG_ID)
)
""")

print("create word table successful")

c.execute("""
CREATE TABLE IMAGES_WORDS (
    IMAGE_ID INTEGER NOT NULL,
    WORD_ID INTEGER NOT NULL,
    SURFACE TEXT NOT NULL,
    WORD_ORDER INTEGER NOT NULL,
    PRIMARY KEY (IMAGE_ID, WORD_ID, WORD_ORDER),
    FOREIGN KEY (IMAGE_ID) REFERENCES IMAGES(IMG_ID),
    FOREIGN KEY (WORD_ID) REFERENCES WORDS(WORD_ID)
)
""")

print("create all table successful")

conn.commit()

conn.close()
