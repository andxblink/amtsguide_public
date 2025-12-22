# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-22

### Added
- Initial project scaffold
- JSON schemas for work products, change logs, and readiness cards
- `WorkProductValidator` for provenance enforcement
- `LexiconValidator` for stop rules (forbidden terms, sentence length)
- `NumbersAgainstSourceValidator` for anti-hallucination checks
- Sample configuration with thresholds
- Synthetic examples (valid and invalid fixtures)
- Pytest test suite
- GitHub Actions CI workflow
- Privacy/leak scanner for CI
- Documentation: what-stand-means, stop-rules, error-policy, privacy

### Security
- Leak guard prevents accidental commit of real authority URLs or contact data

