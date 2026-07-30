from dataclasses import dataclass


@dataclass
class Candidate:
    text: str
    conditon: set[str]


@dataclass
class Rule:
    inflected: str
    deinflected: str
    conditions_in: set[str]
    conditons_out: set[str]


def deinflect(word: str) -> list[str]:
    queue = [Candidate(word, None)]
    visited = set()
    result = []

    while queue:
        candidate = queue.pop()

        for rule in rules:
            new_candidate = apply_rule(candidate, rule)

            if new_candidate:
                queue.append(new_candidate)
                result.append(new_candidate)


def apply_rule(candidate: Candidate, rule: Rule) -> Candidate | None:

    return Candidate(new_text, rule.conditons_out)
