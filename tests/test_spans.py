from sms_anonymizer.anonymize.spans import Span, merge_spans


def test_no_overlap_keeps_all():
    spans = [Span(0, 3, "<A>"), Span(5, 8, "<B>")]
    assert merge_spans(spans) == [Span(0, 3, "<A>"), Span(5, 8, "<B>")]


def test_higher_priority_wins_on_overlap():
    low = Span(0, 10, "<LOW>", priority=1)
    high = Span(2, 5, "<HIGH>", priority=2)
    assert merge_spans([low, high]) == [Span(2, 5, "<HIGH>", priority=2)]


def test_result_is_sorted_by_start():
    spans = [Span(10, 12, "<B>"), Span(0, 2, "<A>")]
    result = merge_spans(spans)
    assert [s.start for s in result] == [0, 10]
