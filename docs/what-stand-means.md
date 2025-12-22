# What "Stand" Means

## The `*_verified_at` Promise

Every factual field in a work product has a corresponding `*_verified_at` field containing an ISO date (`YYYY-MM-DD`).

**Definition:**

> `*_verified_at` is the date a human last checked this specific field against a source or internal research note.

## What It Is

- **Field-level verification date** — Each fact is verified independently
- **Human check** — A person reviewed this field, not just an automated process
- **Against a source** — Checked against an official document, website, or research note
- **Point-in-time snapshot** — Accurate as of the verification date

## What It Is NOT

- **Real-time accuracy promise** — Sources change; the field may be outdated
- **Automatic update trigger** — The system does not monitor for source changes
- **Legal guarantee** — This is operational metadata, not a legal warranty
- **Freshness indicator** — A recent date doesn't mean "more correct"

## Example

```json
{
  "fee_amount": 25,
  "fee_amount_source": "https://example.gov/fees",
  "fee_amount_verified_at": "2025-01-15"
}
```

This means:
- The fee amount is 25
- It was sourced from the given URL
- A human verified this on January 15, 2025

It does NOT mean:
- The fee is still 25 today
- The URL still shows this value
- The fee will be 25 tomorrow

## Staleness Policy

Organizations should define their own staleness thresholds:

| Field Type | Suggested Review Cadence |
|------------|--------------------------|
| Fees/costs | Every 90 days |
| Contact info | Every 180 days |
| Legal references | Every 365 days |
| Process steps | Every 180 days |

When a `*_verified_at` date exceeds the threshold, the field should be flagged for re-verification.

## Format

- **Required format:** `YYYY-MM-DD` (ISO 8601 date)
- **Timezone:** Implicit local time (no timezone suffix)
- **Validation:** Must match regex `^\d{4}-\d{2}-\d{2}$`

## Correction Flow

When a field is found to be incorrect:

1. Update the field value
2. Update `*_source` if the source changed
3. Update `*_verified_at` to today's date
4. Log the change in the change log with reason

See [error-policy.md](error-policy.md) for the full correction process.

