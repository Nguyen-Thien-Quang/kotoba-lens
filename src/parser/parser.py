import sqlite3
import indeflect
from collections import deque
from dataclasses import dataclass


# dataclass for vocabulary in output
@dataclass
class Word:
    id: int
    lemma: str
    reading: str
    pos: str
    meaning: str
    score: float = -1


def parse(text: str) -> list[Word]:
    # configuration database connection
    conn = sqlite3.connect("database/dictionary.db")
    c = conn.cursor()
    MAX_EXPRESSION_LENGTH = 10

    output = []
    pos = 0
    while pos < len(text):
        flag = False
        MAX_LENGTH = min(MAX_EXPRESSION_LENGTH, len(text) - pos)
        for length in range(MAX_LENGTH, 0, -1):
            candidate = text[pos : pos + length]
            # initialize queue for text
            queue = deque([candidate])
            # initialize visited set
            visited = {candidate}
            while queue:
                word = queue.pop()
                result = look_up(word, c)
                if result:
                    output.extend(result)
                    pos += length
                    flag = True
                    break
                else:
                    for new_word in deinflect(word):
                        if new_word not in visited:
                            visited.add(new_word)
                            queue.append(new_word)
            if flag:
                break
        if not flag:
            pos += 1
    conn.close()
    return output


def look_up(word: str, c) -> list[Word]:
    c.execute("SELECT * FROM entries WHERE expression = ?", (word,))
    result = [Word(*row) for row in c.fetchall()]
    return result
