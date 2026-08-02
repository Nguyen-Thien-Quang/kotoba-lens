import json
from parser import parser
from dataclasses import dataclass


# class represent each deinflection rule
@dataclass
class Rule:
    inflected: str
    deinflected: str
    conditions_in: set[str]
    conditions_out: set[str]

def test_parse(text):
    result = parser.parse(text, deinflect_rules)

    for word in result:
        print(str(word.id) + "." + word.lemma + ":" + word.meaning)


# loading deinflected rules from json file
with open("parser/deinflect_rules.json", encoding="utf-8") as f:
    data = json.load(f)
deinflect_rules: list[Rule] = []

for transform in data["transforms"].values():
    for rule in transform["rules"]:
        deinflect_rules.append(
            Rule(
                inflected=rule["inflected"],
                deinflected=rule["deinflected"],
                conditions_in=rule["conditionsIn"],
                conditions_out=rule["conditionsOut"],
            )
        )

test_parse("りんごを食べる")
