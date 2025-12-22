# amtsguide-readiness-spec

A public specification for **reviewable AI work products** in government service contexts.

This repo contains schemas, validators, and documentation that define how AI-generated content can be:
- **Traceable** — every fact has provenance (`*_source`, `*_verified_at`)
- **Constrained** — stop rules block forbidden patterns and ungrounded claims
- **Testable** — validators enforce the spec with failing tests as proof

## What This Is

This is a **methods + bridges** repo. It publishes the *mechanisms* that make AI content reviewable, without exposing proprietary data or operational details.

**Included:**
- JSON schemas for work products, change logs, and readiness cards
- Python validators for provenance, lexicon, and anti-hallucination checks
- Sample config with thresholds and stop rules
- Synthetic examples (no real data)
- Tests that prove enforcement works

**Not included:**
- Real city/authority data
- Source URLs or partner information
- Content templates or prompts
- Operational schedules or credentials

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Validate a work product
validate-work-product examples/work_product.valid.json

# Validate text content
validate-text examples/text.valid.md --config config/sample.yaml

# Run tests
pytest -q
```

## Project Structure

```
├── schemas/                 # JSON schemas
│   ├── work_product.schema.json
│   ├── change_log.schema.json
│   └── readiness_card.schema.json
├── validators/              # Python validators
│   ├── work_product.py
│   ├── lexicon.py
│   └── numbers.py
├── config/                  # Sample configuration
│   └── sample.yaml
├── examples/                # Synthetic test fixtures
│   ├── work_product.valid.json
│   ├── work_product.missing_verified_at.json
│   └── text.forbidden_term.md
├── docs/                    # Documentation
│   ├── what-stand-means.md
│   ├── stop-rules.md
│   ├── error-policy.md
│   └── privacy.md
└── tests/                   # Pytest suite
    ├── test_work_product.py
    ├── test_lexicon.py
    └── test_numbers.py
```

## Key Concepts

### Work Product Format

Every AI-generated work product follows this pattern:

```json
{
  "_metadata": {
    "extraction_date": "2025-01-15T10:30:00Z",
    "model": "claude-sonnet-4",
    "extractor_version": "1.0"
  },
  "fee_amount": 25,
  "fee_amount_source": "https://example.gov/fees",
  "fee_amount_verified_at": "2025-01-15"
}
```

For each factual field `X`:
- `X` — the value
- `X_source` — URL or document reference (nullable for some field types)
- `X_verified_at` — ISO date of last human verification

### Stop Rules

The lexicon validator blocks:
- **Forbidden verbs** — terms that overstate certainty
- **Forbidden patterns** — bureaucratic language that obscures meaning
- **Long sentences** — exceeding 22 words (Einfache Sprache)

### Anti-Hallucination

The numbers validator:
- Extracts all numbers from generated content
- Compares against allowed numbers from the work product
- Flags any number not traceable to source data

## Documentation

- [What "Stand" Means](docs/what-stand-means.md) — The `*_verified_at` promise
- [Stop Rules](docs/stop-rules.md) — Lexicon and threshold configuration
- [Error Policy](docs/error-policy.md) — Errors vs warnings, correction flow
- [Privacy](docs/privacy.md) — What stays private and why

## License

MIT — see [LICENSE](LICENSE)

## Contributing

This repo uses synthetic examples only. Do not submit real authority data, source URLs, or contact information. See [docs/privacy.md](docs/privacy.md) for contribution guidelines.

