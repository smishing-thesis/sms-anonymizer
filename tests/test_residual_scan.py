from unittest.mock import patch

from sms_anonymizer.verify.residual_scan import scan_residuals


def test_reports_leaked_email_and_phone():
    rows = [("id:0", "Escribime a persona@ejemplo.com o al 987654321")]

    with patch("sms_anonymizer.verify.residual_scan.find_names", return_value=[]):
        findings = scan_residuals(rows)

    assert len(findings) == 1
    assert findings[0]["id"] == "id:0"
    # the email's domain also matches the (independent) URL pattern — both
    # get reported, since this scan doesn't merge spans, it just flags leaks
    assert set(findings[0]["placeholders_missed"]) == {"<EMAIL_ADDRESS>", "<PHONE_NUMBER>", "<URL>"}


def test_clean_text_produces_no_findings():
    rows = [("id:0", "Hola <NAMED_ENTITY>, todo bien")]

    with patch("sms_anonymizer.verify.residual_scan.find_names", return_value=[]):
        findings = scan_residuals(rows)

    assert findings == []


def test_reports_known_name_that_slipped_through():
    rows = [("id:0", "Hola ROSA FICTICIA, todo bien"), ("id:1", "Hola <NAMED_ENTITY>, todo bien")]

    with patch("sms_anonymizer.verify.residual_scan.find_names", return_value=[]):
        findings = scan_residuals(rows, known_names=["Rosa", "Ficticia"])

    assert [f["id"] for f in findings] == ["id:0"]
    assert findings[0]["placeholders_missed"] == ["<NAMED_ENTITY>"]
