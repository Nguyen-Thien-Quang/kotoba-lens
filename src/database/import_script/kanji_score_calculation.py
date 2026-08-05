import math
from pathlib import Path
from db_config import kanji_dict_connection
from dataclasses import dataclass
from math import log

@dataclass
class Kanji:
    text: str
    grade: int | None
    frequency: int | None
    strokes_count: int
    score: float | None


conn = kanji_dict_connection()
cur = conn.cursor()

cur.execute("SELECT * FROM kanji")

result = [Kanji(*row)for row in cur.fetchall()]

LOG_MAX_FREQ = math.log(2501)
for kanji in result:
    # normalize frequency and grade_score
    grade_score = (kanji.grade-1) / 9 if kanji.grade else 1.0
    frequency_score = math.log(kanji.frequency) / LOG_MAX_FREQ if kanji.frequency else 1.0
    final_score = 80 * frequency_score + 20 * grade_score
    cur.execute(
    "UPDATE kanji SET score = ? WHERE literal = ?",
    (final_score, kanji.text),
    )

conn.commit()
conn.close()   
