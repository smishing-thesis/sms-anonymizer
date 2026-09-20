import pytest

spacy = pytest.importorskip("spacy")

from sms_anonymizer.anonymize.ner_detector import MODEL_NAME, find_names  # noqa: E402

try:
    spacy.load(MODEL_NAME)
    _MODEL_AVAILABLE = True
except OSError:
    _MODEL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODEL_AVAILABLE, reason=f"{MODEL_NAME} not installed in this environment"
)


def test_finds_person_name():
    spans = find_names("Hola Rosa Ficticia, como estas")
    assert any(s.placeholder == "<NAMED_ENTITY>" for s in spans)


def test_no_names_in_plain_text():
    spans = find_names("todo bien por aca")
    assert spans == []
