# Stop Rules

Stop rules define when the system must **refuse to proceed** or **escalate to human review**. They are the enforcement mechanism that makes "human-in-the-loop" architecture, not marketing.

## Categories of Stop Rules

### 1. Provenance Stops

The system stops if a work product lacks required provenance:

| Condition | Severity | Action |
|-----------|----------|--------|
| Missing `_metadata` block | Error | Block publishing |
| Missing `*_verified_at` for fact field | Error | Block publishing |
| Invalid date format in `*_verified_at` | Error | Block publishing |
| Missing `*_source` key | Warning | Report, continue |
| Empty `*_source` for numeric field | Warning | Report, continue |

### 2. Lexicon Stops

The system stops if content contains forbidden language:

| Condition | Severity | Action |
|-----------|----------|--------|
| Forbidden term found | Error | Block publishing |
| Forbidden pattern matched | Error | Block publishing |
| Sentence > 22 words | Warning | Report, continue |
| Fact sentence > 18 tokens | Warning | Report, continue |

### 3. Hallucination Stops

The system stops if content contains ungrounded claims:

| Condition | Severity | Action |
|-----------|----------|--------|
| Number not in source data | Error | Block publishing |
| Claim without citation | Error | Block publishing |

## Configuration

Stop rules are configured in `config/sample.yaml`:

```yaml
thresholds:
  max_sentence_words: 22
  max_fact_tokens: 18

lexicon_rules:
  forbidden_verbs:
    - "guarantee"
    - "promise"
  forbidden_patterns:
    - "with regard to"
  forbidden_terms:
    - "definitely"
    - "always"

field_policy:
  missing_source_severity: "warning"
  missing_verified_at_severity: "error"
```

## Customization

Organizations should customize stop rules for their domain:

### Adding Forbidden Terms

```yaml
lexicon_rules:
  forbidden_terms:
    - "your-domain-specific-term"
    - "another-forbidden-phrase"
```

### Adjusting Severity

To make missing sources an error instead of warning:

```yaml
field_policy:
  missing_source_severity: "error"
```

### Domain-Specific Patterns

```yaml
lexicon_rules:
  forbidden_patterns:
    - "(?i)guaranteed\\s+approval"
    - "(?i)100%\\s+accurate"
```

## Enforcement

Stop rules are enforced by validators:

- `WorkProductValidator` — Provenance stops
- `LexiconValidator` — Language stops
- `NumbersAgainstSourceValidator` — Hallucination stops

Each validator returns:
- `passed: bool` — Whether validation succeeded
- `errors: list` — Blocking issues (stops)
- `warnings: list` — Non-blocking issues (reports)

## CI Integration

In CI, validators should be run with strict mode:

```bash
# Fail build on any error
validate-work-product data/output.json --config config/production.yaml
if [ $? -ne 0 ]; then
  echo "Stop rule triggered — blocking deploy"
  exit 1
fi
```

## Escalation

When a stop rule triggers, the system should:

1. **Log the violation** — Record what rule was triggered
2. **Block the operation** — Do not publish/deploy
3. **Notify a human** — Alert the appropriate reviewer
4. **Provide context** — Show what failed and why

The human then decides whether to:
- Fix the issue and retry
- Override (with documentation)
- Escalate further

See [error-policy.md](error-policy.md) for the correction flow.

