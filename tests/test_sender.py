from sms_anonymizer.anonymize.sender import classify_sender, pseudonymize_sender


def test_classifies_short_code():
    assert classify_sender("80800") == "short_code"


def test_classifies_full_number():
    assert classify_sender("+51987654321") == "full_number"


def test_classifies_full_number_with_spaces():
    assert classify_sender("+51 921 103 794") == "full_number"


def test_pseudonymize_same_number_regardless_of_formatting(tmp_path):
    salt_path = str(tmp_path / "salt.bin")
    assert pseudonymize_sender("+51 921 103 794", salt_path) == pseudonymize_sender(
        "+51921103794", salt_path
    )


def test_classifies_alphanumeric_entity():
    assert classify_sender("BancoInventado") == "alphanumeric"


def test_classifies_missing_sender_as_unknown():
    assert classify_sender(None) == "unknown"
    assert classify_sender("") == "unknown"


def test_pseudonymize_is_stable_across_calls(tmp_path):
    salt_path = str(tmp_path / "salt.bin")

    first = pseudonymize_sender("+51987654321", salt_path)
    second = pseudonymize_sender("+51987654321", salt_path)

    assert first == second
    assert first.startswith("SENDER_")


def test_pseudonymize_differs_between_senders(tmp_path):
    salt_path = str(tmp_path / "salt.bin")

    a = pseudonymize_sender("+51987654321", salt_path)
    b = pseudonymize_sender("+51900000000", salt_path)

    assert a != b


def test_pseudonymize_none_for_missing_sender(tmp_path):
    salt_path = str(tmp_path / "salt.bin")
    assert pseudonymize_sender(None, salt_path) is None


def test_salt_file_is_reused_not_regenerated(tmp_path):
    salt_path = str(tmp_path / "salt.bin")

    pseudonymize_sender("+51987654321", salt_path)
    with open(salt_path, "rb") as f:
        salt_after_first_call = f.read()

    pseudonymize_sender("+51900000000", salt_path)
    with open(salt_path, "rb") as f:
        salt_after_second_call = f.read()

    assert salt_after_first_call == salt_after_second_call
