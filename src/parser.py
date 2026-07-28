import sqlite3

from dataclasses import dataclass

from paddlex.inference.common import result

# dataclass for vocabulary in output
@dataclass
class Word:
    lemma: str
    pos: str
    reading: str
    meaning: str
    score: float
# confiugration connection with dictionary's database   
conn = sqlite3.connect("database/jmdict.db")
c = conn.cursor()


def parse(text: str) -> list[Word]:
     for i in range(len(text)):
        
     

def look_up(word: str) -> list[Word]:
    c.execute("SELECT * FROM entries WHERE expression = "?"", (word))

    
    result = c.fetchall()

    return result

