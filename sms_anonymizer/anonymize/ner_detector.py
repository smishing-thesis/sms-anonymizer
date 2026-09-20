import spacy

from .rules import TEXT_RULES
from .spans import Span

MODEL_NAME = "es_core_news_lg"
_PERSON_RULE = next(rule for rule in TEXT_RULES if rule.name == "person_name")

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(MODEL_NAME)
    return _nlp


def find_names(text: str) -> list[Span]:
    doc = _get_nlp()(text)
    return [
        Span(ent.start_char, ent.end_char, _PERSON_RULE.placeholder, _PERSON_RULE.priority)
        for ent in doc.ents
        if ent.label_ == "PER"
    ]
