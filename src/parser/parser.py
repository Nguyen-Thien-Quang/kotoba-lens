import sqlite3
from . import deinflect
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


def parse(text: str, deinflect_rules) -> list[Word]:
    # configuration database connection
    conn = sqlite3.connect("database/dictionary.db")
    c = conn.cursor()
    MAX_EXPRESSION_LENGTH = 10

    output = []
    pos = 0
    # iterate through each charater of the string
    while pos < len(text):
        flag = False  # founded flag
        MAX_LENGTH = min(MAX_EXPRESSION_LENGTH, len(text) - pos)
        # look up the sub string for each length from 10 -> 1
        for length in range(MAX_LENGTH, 0, -1):
            # extract the text
            candidate = text[pos : pos + length]
            # initialize queue for text
            queue = deque([candidate])
            # initialize visited set
            visited = {candidate}
            while queue:
                word = queue.pop()
                result = look_up(word, c)
                if result:
                    output.extend(result)  # add all the list of entries into result
                    pos += length  # move cursor to the next charater of string
                    flag = True  # mark that result founded
                    break
                else:
                    # apply deinflection and enqueue all generated output into queue
                    for new_word in deinflect.deinflect(word, deinflect_rules):
                        # add unvisited word only
                        if new_word not in visited:
                            visited.add(new_word)
                            queue.append(new_word)
            if flag:
                break
        # if no result founded for all length of substring, iterate next charater
        if not flag:
            pos += 1
    conn.close()
    return output


def look_up(word: str, c) -> list[Word]:
    c.execute("SELECT * FROM entries WHERE expression = ?", (word,))
    result = [Word(*row) for row in c.fetchall()]
    return result
