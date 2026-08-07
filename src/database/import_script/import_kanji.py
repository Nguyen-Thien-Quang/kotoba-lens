import json
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
from db_config import kanji_dict_connection
# ==========================
# Config
# ==========================

DICT_PATH = Path("KANJIS.json")

# ==========================
# Database
# ==========================

conn = kanji_dict_connection()
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
