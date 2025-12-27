# Measured Prompt Iteration (PromptOps)

A pragmatic approach to prompt improvement through observability, traceability, and human-in-the-loop iteration.

## Philosophy

**PromptOps** is the practice of treating prompts as versioned artifacts with measurable quality outcomes.

Key principles:
1. **Every prompt is versioned** - Know exactly which version produced which output
2. **Quality is measured** - Track automated + human intervention signals
3. **Changes are documented** - Semantic diffs link changes to outcomes
4. **Patterns emerge from data** - Evidence-backed improvements, not intuition
5. **Humans stay in the loop** - No autonomous changes without approval

## The PromptOps Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     1. GENERATE                              │
│                                                              │
│   Prompt v1.0 (hash: ae7cca) → LLM → Content                │
│                                                              │
│   Log: prompt_version, prompt_hash, model, timestamp        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     2. VALIDATE                              │
│                                                              │
│   Automated checks → validator_score (0-100)                │
│   - Lexicon compliance                                       │
│   - Sentence length (10-16 words avg)                       │
│   - Forbidden terms                                          │
│   - Encoding issues                                          │
│                                                              │
│   Log: validator_score, validator_passed                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     3. REVIEW                                │
│                                                              │
│   Human reviews output:                                      │
│   - ACCEPT → Push to CMS                                    │
│   - REJECT → Log reason, re-generate                        │
│                                                              │
│   Log: attempts_to_acceptance, rejection_reasons            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     4. POLISH                                │
│                                                              │
│   CMS editors refine content before publication             │
│                                                              │
│   Log: post_gen_edit_count, reviewer_count                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     5. ANALYZE                               │
│                                                              │
│   Aggregate telemetry by prompt_hash:                       │
│   - avg_composite_score                                      │
│   - avg_attempts                                             │
│   - avg_edits                                                │
│                                                              │
│   Compare v1.0 vs v1.1 → Quality delta                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     6. ITERATE                               │
│                                                              │
│   Identify patterns:                                         │
│   - "Adding max word count constraint → +15 score"          │
│   - "Removing Konjunktiv examples → -10 score"              │
│                                                              │
│   Human approves changes → Prompt v1.1                      │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Observability
- Hash and version every prompt
- Log all generation events
- Store telemetry in SQLite

### Phase 2: Diffing
- Semantic diff between prompt versions
- Categorize changes (CONSTRAINT, STYLE, CONTENT, etc.)
- Link changes to quality deltas

### Phase 3: Pattern Discovery
- Aggregate telemetry to find correlations
- Build evidence-backed pattern library
- Suggest improvements to humans

### Phase 4: Human-in-the-Loop Proposals
- System proposes prompt changes
- Human reviews and approves
- Track improvement over time

### Phase 5: Autonomous Iteration (Future)
- System tests prompt variants
- A/B testing with quality gates
- Auto-rollback on quality regression

## CLI Commands

```bash
# Compare two prompt versions
python main.py diff-prompts prompts/old.txt prompts/new.txt

# Show quality metrics
python main.py quality-report --prompt-type cluster --days 30

# Export telemetry for analysis
python main.py export-telemetry --format json -o telemetry.json
```

## What the Public Specification Proves

By publishing these schemas, we demonstrate:

1. **Transparency** - Our quality measurement methodology is documented
2. **Rigor** - We track real human intervention, not just automated scores
3. **Evidence-based** - Improvements come from production data
4. **Auditable** - Every generation is traceable to a prompt version

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Avg composite score | >80 | - |
| Avg attempts to acceptance | <2 | - |
| Avg post-gen edits | <5 | - |
| First-try acceptance rate | >50% | - |

---

*"The best prompt is the one that needs the least human intervention."*

