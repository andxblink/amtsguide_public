# Prompt Telemetry

This document describes the telemetry format used to track AI prompt quality at AmtsGuide.

## Overview

Prompt telemetry captures quality signals for AI-generated content:

1. **Automated validation** - Lexicon compliance, sentence length, encoding checks
2. **Pipeline efficiency** - How many attempts before human accepted output
3. **Post-generation edits** - How many corrections humans made in CMS

## Schema

See [`schemas/prompt_telemetry.schema.json`](../schemas/prompt_telemetry.schema.json) for the full schema.

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | string | Unique ID for the generated document |
| `prompt_type` | string | Type: cluster, bezirk, overview, supplier, blog |
| `prompt_version` | string | Version string (e.g., "cluster-berlin-v1.0") |
| `prompt_hash` | string | SHA256 hash (12 chars) of prompt content |
| `validator_score` | number | 0-100 automated quality score |
| `attempts_to_acceptance` | integer | Pipeline attempts (1 = first try) |
| `post_gen_edit_count` | integer | Human edits after generation |
| `composite_score` | number | Weighted quality score |

## Composite Score Calculation

```
composite_score = (
    validator_score * 0.2 +           # Automated checks
    pipeline_efficiency * 0.4 +        # First-try success
    post_gen_edit_score * 0.4          # No human fixes
)

where:
    pipeline_efficiency = 100 / attempts_to_acceptance
    post_gen_edit_score = max(0, 100 - edits * 10)
```

## Score Interpretation

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent - works first time, minimal fixes |
| 70-89 | B | Good - minor iterations or edits |
| 50-69 | C | Needs improvement - multiple attempts or significant edits |
| <50 | F | Broken - rethink approach |

## Usage Examples

### Logging a Generation

```python
from amtsguide_common.observability.prompt_telemetry import PromptTelemetryRecord
from amtsguide_common.observability.telemetry_store import TelemetryStore

store = TelemetryStore()

record = PromptTelemetryRecord(
    document_id="bezirk-mitte-de",
    prompt_type="bezirk",
    prompt_version="bezirk-berlin-v1.0",
    prompt_hash="ae7cca7353ff",
    validator_score=87.5,
    validator_passed=True,
    attempts_to_acceptance=2,
    rejection_reasons=["too_long"],
)

store.log_generation(record)
```

### Querying Quality Metrics

```python
store = TelemetryStore()

# Get stats for a specific prompt
stats = store.get_prompt_stats("ae7cca7353ff")
print(f"Avg score: {stats['avg_composite_score']}")
print(f"Avg attempts: {stats['avg_attempts']}")

# Get history by type
history = store.get_prompt_history("cluster", limit=10)
```

## Privacy Considerations

- Telemetry records do **not** contain the actual generated content
- Only metadata and quality scores are stored
- Reviewer IDs are pseudonymized where possible

