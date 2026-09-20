from sms_anonymizer.clean.mojibake import fix_mojibake


def test_fixes_common_mojibake():
    broken = "MaÃ±ana te aviso"
    assert fix_mojibake(broken) == "Mañana te aviso"


def test_leaves_clean_text_unchanged():
    assert fix_mojibake("Todo bien, gracias") == "Todo bien, gracias"
