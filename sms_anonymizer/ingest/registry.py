from typing import Callable, Iterator

from . import android_xml, csv_source, curated_xml, ios_sms_db
from .models import RawMessage

# Add a new source format by writing a module with a parse(path) function
# and registering it here — nothing else needs to change.
PARSERS: dict[str, Callable[[str], Iterator[RawMessage]]] = {
    "android_xml": android_xml.parse,
    "ios_sms_db": ios_sms_db.parse,
    "csv": csv_source.parse,
    "curated_xml": curated_xml.parse,
}


def parse(format_name: str, path: str) -> Iterator[RawMessage]:
    try:
        parser = PARSERS[format_name]
    except KeyError:
        raise ValueError(
            f"Unknown ingest format: {format_name!r}. Known formats: {sorted(PARSERS)}"
        )
    return parser(path)
