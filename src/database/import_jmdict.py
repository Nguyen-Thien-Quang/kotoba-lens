import json
import sqlite3
from pathlib import Path

# ==========================
# Config
# ==========================

DICT_DIR = Path("database/JMdict_english")  # folder chứa term_bank_*.json
DB_PATH = Path("databae/jmdict.db")

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


def extract_pos(definition_tags: str) -> str:
    pos = []

    for tag in definition_tags.split():
        for prefix, mapped in POS_MAP.items():
            if tag == prefix or tag.startswith(prefix):
                if mapped not in pos:
                    pos.append(mapped)

    return "|".join(pos)


# ==========================
# Glossary parser
# ==========================


def extract_glossary(glossary_data) -> str:
    result = []

    def walk(node):
        if isinstance(node, str):
            text = node.strip()
            if text:
                result.append(text)

        elif isinstance(node, list):
            for item in node:
                walk(item)

        elif isinstance(node, dict):
            if "content" in node:
                walk(node["content"])

    walk(glossary_data)

    # remove duplicates while preserving order
    result = list(dict.fromkeys(result))

    return "; ".join(result)


# ==========================
# Database
# ==========================

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS entries(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT NOT NULL,
    reading TEXT NOT NULL,
    pos TEXT,
    glossary TEXT
)
""")

cur.execute("DELETE FROM entries")

# ==========================
# Import
# ==========================

files = sorted(DICT_DIR.glob("term_bank_*.json"))

for file in files:
    print(f"Importing {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        expression = entry[0]
        reading = entry[1]
        definition_tags = entry[2]
        glossary_data = entry[5]

        # Skip form entries
        if definition_tags == "forms":
            continue

        pos = extract_pos(definition_tags)
        glossary = extract_glossary(glossary_data)

        cur.execute(
            """
            INSERT INTO entries(expression, reading, pos, glossary)
            VALUES (?, ?, ?, ?)
            """,
            (
                expression,
                reading,
                pos,
                glossary,
            ),
        )

conn.commit()

cur.execute("CREATE INDEX IF NOT EXISTS idx_expression ON entries(expression)")

cur.execute("CREATE INDEX IF NOT EXISTS idx_reading ON entries(reading)")

conn.commit()
conn.close()

print("Done.")
