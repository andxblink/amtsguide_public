# Human Intervention Model

This document explains the dual-signal quality model used to measure prompt effectiveness.

## The Problem

Traditional prompt quality measurement relies on automated validators, but these miss crucial signals:

- A prompt might pass all automated checks but produce content that requires extensive human editing
- A prompt might need multiple iterations before producing acceptable output

**Real quality = how much human intervention is required**

## Two Types of Human Intervention

### 1. Pipeline Phase (Attempts to Acceptance)

```
Prompt v1.0 → Generate → Review → REJECT → Adjust prompt
Prompt v1.1 → Generate → Review → REJECT → Adjust prompt
Prompt v1.2 → Generate → Review → ACCEPT → Push to CMS

Signal: attempts_to_acceptance = 3
Meaning: Prompt took 3 tries to produce acceptable output
```

**What this measures:**
- How well the prompt captures requirements
- Whether output meets human expectations on first try
- Efficiency of the generation process

### 2. Review Phase (Post-Generation Edits)

```
CMS Draft → Human reads → Makes 5 corrections
CMS Draft → Human adds 2 USER_EDIT: changes (experimenting)
CMS → Publish

Signal: post_gen_edit_count = 7, ai_correction_count = 5, user_edit_count = 2
Meaning: AI output needed 5 fixes, plus user made 2 experimental changes
```

**What this measures:**
- Quality gap between "acceptable" and "publishable"
- How much polish AI output requires
- Whether prompt produces truly production-ready content

## The USER_EDIT: Marker Convention

Not all edits are AI mistakes. Users may:
- Experiment with new approaches
- Learn and iterate on prompts
- Add constraints they thought of later

To distinguish user experimentation from AI corrections:

```
Example revision notes:

USER_EDIT: Added max 16 words constraint (experimenting)
---
Fixed Berlin typo
Corrected fee amount from €50 to €45
```

**Parsing result:**
- `user_edit_count = 1` (doesn't penalize score)
- `ai_correction_count = 2` (penalizes score)

**Score calculation:**
```python
# Only AI corrections penalize the prompt quality
post_gen_edit_score = max(0, 100 - ai_correction_count * 10)
# = max(0, 100 - 2 * 10) = 80
```

This ensures users can freely experiment without penalizing prompt quality metrics.

## Quality Interpretation Matrix

| Iterations | AI Corrections | Diagnosis |
|------------|----------------|-----------|
| 1 | 0-2 | Excellent prompt - works first time, minimal fixes |
| 5 | 0-2 | Prompt hard to tune, but produces good final output |
| 1 | 10+ | Prompt produces "acceptable" but not publishable content |
| 5 | 10+ | Prompt is fundamentally broken |

*Note: User edits (USER_EDIT:) don't count in this matrix - only AI corrections.*

## Schema

See [`schemas/human_intervention.schema.json`](../schemas/human_intervention.schema.json) for the full schema.

### Key Fields

```json
{
  "pipeline_phase": {
    "attempts_to_acceptance": 3,
    "rejection_reasons": ["too_long", "wrong_tone"],
    "pipeline_efficiency": 33.33
  },
  "review_phase": {
    "post_gen_edit_count": 7,
    "user_edit_count": 2,
    "ai_correction_count": 5,
    "post_gen_edit_score": 50,
    "reviewer_count": 1
  },
  "composite_score": 52.67
}
```

## Why Both Signals Matter

| Scenario | Pipeline Efficiency | AI Correction Score | Problem |
|----------|---------------------|---------------------|---------|
| First try accepted, then heavily corrected | 100 | 20 | Prompt doesn't produce publication-ready content |
| Many tries, but final output is perfect | 20 | 100 | Prompt is imprecise but eventually works |
| Both high | 100 | 100 | Ideal prompt |
| Both low | 20 | 20 | Needs complete redesign |

*Note: User edits (USER_EDIT:) are tracked separately and don't affect these scores.*

## Implementation

### Tracking Pipeline Attempts

```python
from amtsguide_common.observability.prompt_telemetry import GenerationAttempt

# Log each attempt
attempt = GenerationAttempt(
    session_id="abc123",
    prompt_type="cluster",
    prompt_version="v1.0",
    prompt_hash="ae7cca7353ff",
    attempt_number=1,
    outcome="rejected",
    rejection_reason="too_long",
)
store.log_attempt(attempt)
```

### Tracking Post-Gen Edits

```python
# Run periodically to sync CMS revision history
from scripts.sync_sanity_revisions import SanityRevisionTracker

tracker = SanityRevisionTracker()
results = tracker.sync_recent(days=7)
```

### Using the USER_EDIT: Parser

```python
from amtsguide_common.observability.edit_parser import parse_edit_content

content = """
USER_EDIT: Added max 16 words constraint (experimenting)
---
Fixed Berlin typo
Corrected fee amount
"""

result = parse_edit_content(content)
print(result.user_edit_count)      # 1 (doesn't penalize)
print(result.ai_correction_count)  # 2 (penalizes)
print(result.post_gen_edit_score)  # 80
```

## Marketing Angle

> "Our prompts are measured not just by automated validators, but by real human intervention signals. A prompt that produces content requiring 5 tries and 10 AI corrections is objectively worse than one that works first time with zero fixes. We track both - and we distinguish between AI mistakes and user experimentation, so users can freely iterate without penalizing metrics."

