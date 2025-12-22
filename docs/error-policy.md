# Error Policy

This document defines the difference between errors and warnings, and the process for handling each.

## Severity Levels

### Errors (Must Block)

Errors are violations that **must prevent publishing**. They indicate the content cannot be trusted.

| Violation | Why It's an Error |
|-----------|-------------------|
| Missing `_metadata` | Cannot verify provenance of entire work product |
| Missing `*_verified_at` | Cannot prove field was human-verified |
| Invalid date format | Verification date is corrupted/unusable |
| Forbidden term in content | Content may mislead users |
| Hallucinated number | Claim is not grounded in source data |

**Action:** Fix the issue before proceeding. Do not override without documented justification.

### Warnings (Report Only)

Warnings are issues that **should be reviewed** but do not block publishing.

| Violation | Why It's a Warning |
|-----------|-------------------|
| Missing `*_source` (nullable) | Source may legitimately be unknown |
| Sentence > 22 words | Readability issue, not factual error |
| Fact sentence > 18 tokens | GEO optimization, not correctness |

**Action:** Log for later review. Consider fixing in next revision.

## Correction Flow

When an error is found in published content:

```
┌─────────────────────────────────────────────────────────────┐
│  1. DETECT                                                   │
│     - Validator flags error                                  │
│     - User reports issue                                     │
│     - Periodic audit finds problem                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. ASSESS                                                   │
│     - Verify the error exists                                │
│     - Determine scope (single field vs systemic)             │
│     - Check if source has changed                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. CORRECT                                                  │
│     - Update field value                                     │
│     - Update *_source if needed                              │
│     - Update *_verified_at to today                          │
│     - Add entry to change log                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VALIDATE                                                 │
│     - Run validators on corrected content                    │
│     - Ensure no new errors introduced                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  5. DEPLOY                                                   │
│     - Publish corrected content                              │
│     - Clear caches as needed                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  6. REVIEW                                                   │
│     - Document root cause                                    │
│     - Consider adding new stop rule                          │
│     - Update training data if AI-generated                   │
└─────────────────────────────────────────────────────────────┘
```

## Change Log Entry

Every correction should be logged:

```json
{
  "field": "fee_amount",
  "old_value": 25,
  "new_value": 30,
  "changed_at": "2025-02-01T10:30:00Z",
  "reason": "Fee increased per official notice dated 2025-01-15",
  "source_ref": "https://example.gov/notices/2025-001"
}
```

## Override Policy

In rare cases, an error may need to be overridden:

1. **Document the justification** — Why is this override necessary?
2. **Get approval** — Who authorized the override?
3. **Set expiration** — When should this be re-reviewed?
4. **Log the override** — Record in change log

Example override log:

```json
{
  "type": "override",
  "rule": "missing_verified_at",
  "field": "legacy_field",
  "reason": "Field imported from legacy system; verification in progress",
  "approved_by": "reviewer@example.com",
  "expires_at": "2025-03-01",
  "logged_at": "2025-02-01T10:30:00Z"
}
```

## Monitoring

Track error rates over time:

- **Error rate by type** — Which rules trigger most often?
- **Time to fix** — How long between detection and correction?
- **Override frequency** — Are overrides increasing? (Bad sign)
- **Recurrence rate** — Are the same errors happening again?

High error rates may indicate:
- Training data needs improvement
- Stop rules are too strict (or not strict enough)
- Process gaps in the review workflow

