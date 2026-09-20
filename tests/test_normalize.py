from sms_anonymizer.clean.normalize import normalize_whitespace


def test_collapses_repeated_spaces_and_tabs():
    assert normalize_whitespace("Hola   \t  mundo") == "Hola mundo"


def test_collapses_multiple_blank_lines():
    assert normalize_whitespace("Linea 1\n\n\n\nLinea 2") == "Linea 1\nLinea 2"


def test_normalizes_windows_and_mac_line_endings():
    assert normalize_whitespace("Linea 1\r\nLinea 2\rLinea 3") == "Linea 1\nLinea 2\nLinea 3"


def test_strips_leading_and_trailing_whitespace():
    assert normalize_whitespace("  Hola  ") == "Hola"
