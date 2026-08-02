import sqlite3
from pathlib import Path
from dataclasses import dataclass
DB_PATH = Path("kanji.db")

@dataclass
class Kanji:
    text: str
    grade: int
    frequency: int
    strokes_count: int
    score: float


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT * FROM kanji")

result = [Kanji(*row)for row in cur.fetchall()]

for kanji in result:
    
