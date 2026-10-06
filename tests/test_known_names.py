import pytest

from sms_anonymizer.anonymize import anonymizer
from sms_anonymizer.anonymize.known_names import compile_known_names, find_known_names, load_known_names


@pytest.fixture(autouse=True)
def _no_ner(monkeypatch):
    monkeypatch.setattr(anonymizer, "find_names", lambda text: [])


def _anonymize(text, names):
    return anonymizer.anonymize(text, compile_known_names(names))


def test_replaces_all_caps_full_name_as_a_single_span():
    text = "Hola ROSA MARIA FICTICIA PEREZ VDA DE LOPEZ, tu prestamo esta aprobado"
    result = _anonymize(text, ["Rosa", "Maria", "Ficticia", "Perez", "Lopez"])
    assert result == "Hola <NAMED_ENTITY> VDA DE <NAMED_ENTITY>, tu prestamo esta aprobado"


def test_is_case_and_accent_insensitive_both_ways():
    names = ["Díaz", "lopez"]
    assert _anonymize("Sr. DIAZ y Sr. López", names) == "Sr. <NAMED_ENTITY> y Sr. <NAMED_ENTITY>"
    assert _anonymize("Sr. diaz y Sr. LÓPEZ", names) == "Sr. <NAMED_ENTITY> y Sr. <NAMED_ENTITY>"


def test_matches_whole_words_only():
    text = "Hoy es el dia de Rosario y mi rosa preferida"
    assert _anonymize(text, ["Rosa"]) == "Hoy es el dia de Rosario y mi <NAMED_ENTITY> preferida"


def test_does_not_confuse_similar_words():
    assert _anonymize("Buenos días, Díaz", ["Díaz"]) == "Buenos días, <NAMED_ENTITY>"


def test_names_are_not_merged_across_newlines():
    result = _anonymize("Rosa\nFicticia", ["Rosa", "Ficticia"])
    assert result == "<NAMED_ENTITY>\n<NAMED_ENTITY>"


def test_no_names_means_no_pattern_and_no_changes():
    assert compile_known_names([]) is None
    assert find_known_names("Rosa Ficticia", None) == []
    assert anonymizer.anonymize("Rosa Ficticia") == "Rosa Ficticia"


def test_known_names_win_over_overlapping_ner_span(monkeypatch):
    from sms_anonymizer.anonymize.spans import Span

    text = "Buen dia ROSA FICTICIA: tu cita"
    ner = Span(text.index("Buen"), text.index("FICTICIA") + len("FICTICIA"), "<NAMED_ENTITY>", 1)
    monkeypatch.setattr(anonymizer, "find_names", lambda t: [ner])

    result = anonymizer.anonymize(text, compile_known_names(["Rosa", "Ficticia"]))

    # NER over-reached into "Buen dia"; the explicit list keeps the exact name span
    assert result == "Buen dia <NAMED_ENTITY>: tu cita"


def test_load_known_names_ignores_blanks_and_comments(tmp_path):
    path = tmp_path / "names.txt"
    path.write_text("# duenos de los chats\nRosa\n\nFicticia  # apellido\n", encoding="utf-8")
    assert load_known_names(str(path)) == ["Rosa", "Ficticia"]


def test_load_known_names_rejects_entries_that_are_too_short(tmp_path):
    path = tmp_path / "names.txt"
    path.write_text("Rosa\nde\n", encoding="utf-8")
    with pytest.raises(ValueError, match="shorter than"):
        load_known_names(str(path))
