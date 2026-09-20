from sms_anonymizer.manifest.versioning import next_corpus_version


def test_first_run_starts_at_1_0_0(tmp_path):
    state_path = str(tmp_path / "state.json")
    assert next_corpus_version(state_path, "hash-a") == "1.0.0"


def test_same_hash_keeps_same_version(tmp_path):
    state_path = str(tmp_path / "state.json")
    next_corpus_version(state_path, "hash-a")
    assert next_corpus_version(state_path, "hash-a") == "1.0.0"


def test_different_hash_bumps_patch(tmp_path):
    state_path = str(tmp_path / "state.json")
    next_corpus_version(state_path, "hash-a")
    next_corpus_version(state_path, "hash-b")
    assert next_corpus_version(state_path, "hash-c") == "1.0.2"
