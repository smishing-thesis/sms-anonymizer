from sms_anonymizer.anonymize import anonymizer
from sms_anonymizer.anonymize.spans import Span


def test_anonymize_replaces_regex_matches_without_needing_the_ner_model(monkeypatch):
    monkeypatch.setattr(anonymizer, "find_names", lambda text: [])

    text = "Escribime a falso.persona@ejemplo-invent.com o al 987654321"
    result = anonymizer.anonymize(text)

    assert result == "Escribime a <EMAIL_ADDRESS> o al <PHONE_NUMBER>"


def test_anonymize_merges_ner_and_regex_spans(monkeypatch):
    text = "Hola Rosa Ficticia, mi correo es falso.persona@ejemplo-invent.com"
    name_span = Span(text.index("Rosa"), text.index("Rosa") + len("Rosa Ficticia"), "<NAMED_ENTITY>", 1)
    monkeypatch.setattr(anonymizer, "find_names", lambda t: [name_span])

    result = anonymizer.anonymize(text)

    assert result == "Hola <NAMED_ENTITY>, mi correo es <EMAIL_ADDRESS>"


def test_anonymize_returns_text_unchanged_when_nothing_found(monkeypatch):
    monkeypatch.setattr(anonymizer, "find_names", lambda text: [])
    assert anonymizer.anonymize("todo bien por aca") == "todo bien por aca"


def test_anonymize_with_stats_counts_replacements_per_placeholder(monkeypatch):
    monkeypatch.setattr(anonymizer, "find_names", lambda text: [])

    text = "Escribime a falso.persona@ejemplo-invent.com o al 987654321, tambien al 999888777"
    _, stats = anonymizer.anonymize_with_stats(text)

    assert stats["<EMAIL_ADDRESS>"] == 1
    assert stats["<PHONE_NUMBER>"] == 2
