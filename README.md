# sms-anonymizer

Offline research tool for a Software Engineering thesis on smishing
detection. It is **not** part of any deployable system: it has no UI, makes
no network calls, and is never distributed — it runs locally, once in a
while, over a folder of raw message exports you supply, to build the
Spanish-language legitimate/ham corpus for the
[charcnn-smishing-model](../charcnn-smishing-model) training set.

Raw messages, anonymized-but-unlabeled data, review samples and any other
intermediate output all live under `data/`, which is entirely gitignored —
nothing real ever gets committed. Anonymization rules live as data in
[sms_anonymizer/anonymize/rules.py](sms_anonymizer/anonymize/rules.py); this
is also the contract a future Android/Kotlin implementation must match.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate  # or .venv/bin/activate on Linux/macOS
pip install -r requirements-dev.txt
python -m spacy download es_core_news_lg==3.8.0
```

## Pipeline stages

The CLI (`python -m sms_anonymizer.cli <command>`) exposes one command per
stage, plus a `pipeline` command that chains everything that doesn't need a
human in the loop.

### 1. `spec-export` — document the anonymization rules

```bash
python -m sms_anonymizer.cli spec-export --output data/anonymization_spec.json
```

Writes the rule table (patterns, placeholders, `rules_version`) as JSON —
for the thesis appendix and as the contract the Kotlin implementation must
mirror.

### 2. `process` — ingest, clean, anonymize, dedupe

```bash
python -m sms_anonymizer.cli process \
  --source android_xml:data/raw/android_backup.xml \
  --source ios_sms_db:data/raw/iphone.db \
  --source csv:data/raw/manual_contributions.csv \
  --output data/to_label/messages.xlsx \
  --metadata data/to_label/metadata.json \
  --stats data/to_label/stats.json \
  --salt-path data/.sender_salt \
  --min-length 5 \
  --review-sample data/review/sample.csv \
  --review-sample-size 30
```

- `--source` is repeatable, one per input file, as `FORMAT:PATH`. Known
  formats: `android_xml`, `ios_sms_db`, `csv` (a plain CSV with a required
  `text` column and optional `sender`/`timestamp`/`service` columns).
- Applies, in order: mojibake repair, whitespace normalization,
  anonymization (name/phone/email/URL placeholders), minimum-length
  filtering, and dedupe by normalized text.
- `--output` is the Excel file for manual scam/ham labeling (`id`, `text`,
  empty `label` with a dropdown).
- `--metadata` is a JSON sidecar keyed by `id`, carrying what must stay out
  of the final model-facing CSV: source, service, sender category
  (`short_code`/`alphanumeric`/`full_number`/`unknown`), a salted
  pseudonymous sender id, and the processing timestamp. The sender's literal
  value never leaves this process.
- `--salt-path` is a local secret file (auto-created, gitignored via
  `data/`) used to pseudonymize senders. Keep it stable across runs if you
  want the sender-concentration report to be comparable over time; treat it
  like a password — never commit it, never share it.
- `--stats` records counts per source and discards per reason, consumed
  later by `finalize` to build the run's manifest.
- `--review-sample` writes a random N before/after sample for manual QA.
  Contains personal data — it's written under `data/`, never committed.

### 3. `verify` — check the anonymization actually worked

```bash
python -m sms_anonymizer.cli verify \
  --input data/to_label/messages.xlsx \
  --report data/verify_report.json
```

Re-runs every detector against the already-anonymized text and reports any
row where something PII-shaped is still present.

### 4. Manual labeling

Open `data/to_label/messages.xlsx` and set `label` to `scam` or `ham` for
every row (dropdown restricted to those two values; commercial spam counts
as `ham`). Save the file under `data/labeled/`.

### 5. `finalize` — produce the model-facing CSV and the run manifest

```bash
python -m sms_anonymizer.cli finalize \
  --input data/labeled/messages.xlsx \
  --output data/labeled/final.csv \
  --manifest data/labeled/manifest.json \
  --version-state data/.corpus_version.json \
  --stats data/to_label/stats.json
```

- `--output` is exactly `text,label` (`label` 1=scam, 0=ham) — the schema
  the model repo expects. Copy it by hand into
  `charcnn-smishing-model/data/raw/legit_es.csv`; that step is intentionally
  not automated.
- `--manifest` records the corpus version, the rules version, per-source
  counts, discards by reason, replacement counts per placeholder, and the
  output file's SHA-256 — so a trained model can point back at the exact
  corpus version that produced it.
- The corpus version is SemVer, auto-computed from `--version-state`: it
  starts at `1.0.0` and only bumps the patch number when the output content
  actually changes between runs.

### `pipeline` — everything before manual labeling, in one call

Runs `spec-export` + `process` + `verify` back to back. Takes the same flags
as `process`, plus `--spec-output` and `--verify-report`.

## Known limitation

`es_core_news_lg`'s NER occasionally folds a leading greeting into the name
span (e.g. "Hola Rosa" tagged as one PERSON entity), so the greeting word
gets swallowed by `<NAMED_ENTITY>` along with the name. This doesn't leak
anything, but it does erase a word that isn't PII. The manual labeling pass
is the safety net for this; flag it if it turns out to be frequent enough to
warrant a rule-based trim.

## Tests

```bash
python -m pytest
```

Tests that need `es_core_news_lg` skip automatically if the model isn't
installed. All fixtures use invented data — never anything real.
