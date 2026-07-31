from dataclasses import dataclass
import json


@dataclass
class Candidate:
    text: str
    condition: set[str] | None = None


@dataclass
class Rule:
    inflected: str
    deinflected: str
    conditions_in: set[str]
    conditions_out: set[str]


def deinflect(word: str, rules: list[Rule]) -> list[str]:
    queue = [Candidate(text=word, condition=None)]
    visited = set()
    result = []

    while queue:
        candidate = queue.pop()

        for rule in rules:
            new_candidate = apply_rule(candidate, rule)

            if new_candidate:
                queue.append(new_candidate)
                result.append(new_candidate)

    return result


def apply_rule(candidate: Candidate, rule: Rule) -> Candidate | None:
    text = candidate.text
    new_text = None

    if text.endswith(rule.inflected):
        if candidate.condition == None or any(
            cond in rule.conditions_in for cond in candidate.condition
        ):
            new_text = text.removesuffix(rule.inflected) + rule.deinflected

    if new_text:
        return Candidate(new_text, rule.conditions_out)
    else:
        return None


with open("deinflect_rules.json", encoding="utf-8") as f:
    data = json.load(f)
rules: list[Rule] = []

for transform in data["transforms"].values():
    for rule in transform["rules"]:
        rules.append(
            Rule(
                inflected=rule["inflected"],
                deinflected=rule["deinflected"],
                conditions_in=rule["conditionsIn"],
                conditions_out=rule["conditionsOut"],
            )
        )
