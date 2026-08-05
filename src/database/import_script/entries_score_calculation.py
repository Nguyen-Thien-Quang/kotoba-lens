import sqlite3
import json
from dataclasses import dataclass
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
from db_config import kanji_dict_connection, dictionary_connection


# calculate kanji difficulties in an expression
def kanji_score(expression: str, kanji_cursor) -> float:
    kanji_scores = []

    for char in expression:
        if '\u4e00' <= char <= '\u9fff':
            kanji_cursor.execute(
                    "SELECT score FROM kanji WHERE literal = ?",
                    (char,)
            )
            row = kanji_cursor.fetchone()

            if row is not None:
                kanji_scores.append(row[0])

    if kanji_scores:
        score = 0.7 * max(kanji_scores) + 0.3 * (sum(kanji_scores) / len(kanji_scores))
        return score
    else:
        return 0

# JMdict dictionary database connect configuration
dict_conn = dictionary_connection()
dict_cur = dict_conn.cursor()

# kanji dictionary database connect configuration
kanji_conn = kanji_dict_connection()
kanji_cur = kanji_conn.cursor()

dict_cur.execute("""
    SELECT id, expression, pos, jlpt, common
    FROM entries
    """)

for entry_id, expression, pos, jlpt_level, common in dict_cur.fetchall():
    kanji_sc = kanji_score(expression, kanji_cur)
    jlpt_score = {
        5: 0,
        4: 25,
        3: 50,
        2: 75,
        1: 100,
        None: 60,
    }[jlpt_level]
    
    common_sc = 100 if common else 0
    pos_sc = 0 if pos else 100

    final_score = (
            0.20 * common_sc + 
            0.20 * kanji_sc +
            0.40 * pos_sc +
            0.10 * jlpt_score
            )
    dict_cur.execute(
            "UPDATE entries SET score = ? WHERE id = ?",
            (final_score, entry_id),
            )
dict_conn.commit()
dict_conn.close()
kanji_conn.close()

