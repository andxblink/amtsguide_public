# Privacy and Contribution Guidelines

This document explains what data stays private, why examples are synthetic, and rules for contributing to this repository.

## What Stays Private

This public repository does **not** contain:

| Category | Examples | Why Private |
|----------|----------|-------------|
| Real data | Addresses, phone numbers, fees, names | PII and competitive data |
| Source URLs | Authority websites, partner portals | Operational intelligence |
| Partner info | Supplier lists, contact databases | Business relationships |
| SEO data | Keywords, rankings, competitor analysis | Competitive advantage |
| Prompts | AI generation templates, system prompts | Operational know-how |
| Schedules | Cron jobs, review cadence, update timing | Operational security |
| Credentials | API keys, passwords, tokens | Security |

## Why Examples Are Synthetic

All examples in this repository use **synthetic data**:

- Fake district names ("Example District")
- Placeholder URLs (`https://example.gov/...`)
- Made-up fees and values
- Test email domains (`@example.com`)

This allows the repository to:
1. Demonstrate the schema without exposing real data
2. Enable testing without privacy concerns
3. Allow public contribution without data leakage

## Contribution Rules

### DO

- Use synthetic/fake data in examples
- Use `@example.com`, `@example.org`, or `@example.invalid` for emails
- Use `example.gov`, `example.com` for URLs
- Use placeholder phone numbers (`+1-555-555-5555`)
- Test your changes locally before submitting

### DO NOT

- Submit real authority URLs (`.gov`, `.berlin.de`, `.bund.de`, etc.)
- Include real email addresses
- Include real phone numbers
- Include real names or addresses
- Reference internal systems by name

## Leak Guard

This repository includes a CI check that scans for accidental real data:

```python
# Patterns that trigger the leak guard:
BLOCKED_PATTERNS = [
    r"\.berlin\.de",        # Real Berlin domains
    r"\.bund\.de",          # German federal domains
    r"\.gov\b",             # Government domains
    r"@(?!example\.(com|org|invalid))",  # Non-example emails
    r"\+49\s?\d",           # German phone numbers
]
```

If your PR triggers the leak guard:
1. Review the flagged content
2. Replace real data with synthetic equivalents
3. Re-submit

## Example: Converting Real to Synthetic

**Real (DO NOT SUBMIT):**
```json
{
  "authority": "Straßenverkehrsbehörde Berlin-Mitte",
  "phone": "+49 30 9018 22823",
  "email": "verkehr@ba-mitte.berlin.de",
  "fee": 21
}
```

**Synthetic (OK TO SUBMIT):**
```json
{
  "authority": "Example Traffic Authority",
  "phone": "+1-555-555-5555",
  "email": "traffic@example.gov",
  "fee": 25
}
```

## Questions

If you're unsure whether something is safe to include, ask before submitting. When in doubt, use synthetic data.

