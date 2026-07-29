import json
import sqlite3
from pathlib import Path

# ==========================
# Config
# ==========================

DICT_PATH = Path("jmdictExtended.json")
DB_PATH = Path("dictionary.db")

# ==========================
# POS mapping
# ==========================

POS_MAP = {
    "n": "noun",
    "v1": "verb",
    "v2": "verb",
    "v4": "verb",
    "v5": "verb",
    "vk": "verb",
    "vs": "verb",
    "vz": "verb",
    "vn": "verb",
    "adj-i": "adjective",
    "adj-na": "adjective",
    "adj-no": "adjective",
    "adj-pn": "adjective",
    "adj-f": "adjective",
    "adj-t": "adjective",
    "adv": "adverb",
    "adv-to": "adverb",
}


def extract_pos(senses) -> str:
    pos = []

    for sense in senses:
        for tag in sense.get("partOfSpeech", []):
            for prefix, mapped in POS_MAP.items():
                if tag == prefix or tag.startswith(prefix):
                    if mapped not in pos:
                        pos.append(mapped)

    return "|".join(pos)


def extract_glossary(senses) -> str:
    glossary = []

    for sense in senses:
        for gloss in sense.get("gloss", []):
            text = gloss.get("text", "").strip()
            if text and text not in glossary:
                glossary.append(text)

    return "; ".join(glossary)


def extract_jlpt(entry):
    # Search kanji first
    for kanji in entry.get("kanji", []):
        jlpt = kanji.get("jlptLevel")
        if jlpt is not None:
            return jlpt

    # Then search kana
    for kana in entry.get("kana", []):
        jlpt = kana.get("jlptLevel")
        if jlpt is not None:
            return jlpt

    return None


# ==========================
# Database
# ==========================

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS entries(
    id INTEGER,
    expression TEXT NOT NULL,
    reading TEXT NOT NULL,
    pos TEXT,
    glossary TEXT,
    jlpt INTEGER,
    PRIMARY KEY(id, expression)
)
""")

cur.execute("DELETE FROM entries")

# ==========================
# Import
# ==========================

with open(DICT_PATH, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

for entry in data.get("words", []):
    entry_id = int(entry["id"])

    senses = entry.get("sense", [])
    pos = extract_pos(senses)
    glossary = extract_glossary(senses)
    jlpt = extract_jlpt(entry)

    kanji_list = entry.get("kanji", [])
    kana_list = entry.get("kana", [])

    if kanji_list:
        reading = kana_list[0]["text"] if kana_list else ""

        for kanji in kanji_list:
            cur.execute(
                """
                INSERT INTO entries(id, expression, reading, pos, glossary, jlpt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    kanji["text"],
                    reading,
                    pos,
                    glossary,
                    jlpt,
                ),
            )

    else:
        for kana in kana_list:
            cur.execute(
                """
                INSERT INTO entries(id, expression, reading, pos, glossary, jlpt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    kana["text"],
                    kana["text"],
                    pos,
                    glossary,
                    jlpt,
                ),
            )

conn.commit()

cur.execute("CREATE INDEX IF NOT EXISTS idx_expression ON entries(expression)")

cur.execute("CREATE INDEX IF NOT EXISTS idx_reading ON entries(reading)")

conn.commit()
conn.close()

print("Done.")
