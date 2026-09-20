import csv

from sms_anonymizer.verify.review_sample import write_review_sample


def test_samples_are_capped_at_sample_size(tmp_path):
    output = tmp_path / "sample.csv"
    pairs = [(f"before {i}", f"after {i}") for i in range(10)]

    count = write_review_sample(pairs, str(output), sample_size=3, seed=1)

    assert count == 3
    with open(output, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["before", "after"]
    assert len(rows) == 4


def test_returns_all_when_fewer_than_sample_size(tmp_path):
    output = tmp_path / "sample.csv"
    pairs = [("before 0", "after 0")]

    count = write_review_sample(pairs, str(output), sample_size=5, seed=1)

    assert count == 1
