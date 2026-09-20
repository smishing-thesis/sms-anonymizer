from sms_anonymizer.anonymize.regex_detectors import find_emails, find_phones, find_urls


def test_finds_email():
    text = "Escribime a falso.persona@ejemplo-invent.com por favor"
    spans = find_emails(text)
    assert len(spans) == 1
    assert text[spans[0].start : spans[0].end] == "falso.persona@ejemplo-invent.com"
    assert spans[0].placeholder == "<EMAIL_ADDRESS>"


def test_finds_url_with_scheme_and_www():
    text = "Mira http://ejemplo-invent-no-real.com y www.otro-invent.pe/oferta"
    spans = find_urls(text)
    assert len(spans) == 2
    assert all(s.placeholder == "<URL>" for s in spans)


def test_finds_bare_domain_without_scheme_or_www():
    text = "Actualiza tu paquete en falso-envios.sbs/osc ahora mismo"
    spans = find_urls(text)
    assert len(spans) == 1
    assert text[spans[0].start : spans[0].end] == "falso-envios.sbs/osc"


def test_finds_peruvian_phone_with_and_without_separators():
    text = "Llamame al 987654321 o al +51 999 111 222"
    spans = find_phones(text)
    assert len(spans) == 2
    assert all(s.placeholder == "<PHONE_NUMBER>" for s in spans)


def test_does_not_match_a_plain_date():
    text = "Nos vemos el 19-09-2026"
    spans = find_phones(text)
    assert spans == []
