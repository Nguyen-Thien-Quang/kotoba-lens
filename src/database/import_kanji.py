import json
import sqlite3
from pathlib import Path
# ==========================
# Config
# ==========================

DICT_PATH = Path("KANJIS.json")
DB_PATH = Path("kanji.db")

# ==========================
# Database
# ==========================

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS kanji (
    literal TEXT PRIMARY KEY,
    grade INTEGER,
    freq INTEGER,
    strokes INTEGER,
    score REAL
)
""")

cur.execute("DELETE FROM kanji")

# ==========================
# Import
# ==========================

with open(DICT_PATH, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

for entry in data:
    cur.execute(
        """
        INSERT INTO kanji (
            literal,
            grade,
            freq,
            strokes,
            score
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            entry["literal"],
            entry.get("grade"),
            entry.get("freq"),
            entry.get("strokeCounts", [None])[0],
            None,  # calculate later
        ),
    )

conn.commit()
conn.close()
