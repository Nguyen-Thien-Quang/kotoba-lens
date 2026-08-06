from collections import deque
from dataclasses import dataclass
import json


@dataclass
class Candidate:
    text: str
    condition: set[str] | None = None


# class represent each deinflection rule
@dataclass
class Rule:
    inflected: str
    deinflected: str
    conditions_in: set[str]
    conditions_out: set[str]


def deinflect(word: str, rules: list[Rule]) -> list[str]:
    queue = deque([Candidate(text=word, condition=None)])
    visited = {word}
    result = []

    # BFS using queue
    while queue:
        # take out candidate
        candidate = queue.popleft()

        # apply every possible rule
        for rule in rules:
            new_candidate = apply_rule(candidate, rule)

            if new_candidate:
                # check whether new_candidate already existed
                if new_candidate.text in visited:
                    continue
                visited.add(new_candidate.text)
                queue.append(new_candidate)
                result.append(new_candidate.text)

    return result


# apply specific rules for word
def apply_rule(candidate: Candidate, rule: Rule) -> Candidate | None:
    text = candidate.text
    new_text = None

    # check whether the ending match with rule inflected string
    if text.endswith(rule.inflected):
        # check for condition input
        if candidate.condition == None or any(
            cond in rule.conditions_in for cond in candidate.condition
        ):
            # replace old ending with new ending after deinflection
            new_text = text.removesuffix(rule.inflected) + rule.deinflected

    # return new Candidate
    if new_text:
        return Candidate(new_text, rule.conditions_out)
    else:
        return None


def load_deinflection_rules() -> list[Rule]:
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

    return deinflect_rules



