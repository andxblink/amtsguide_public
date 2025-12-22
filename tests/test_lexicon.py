"""Tests for LexiconValidator."""

import pytest

from amtsguide_readiness_spec.validators.lexicon import LexiconValidator


class TestLexiconValidator:
    """Test suite for LexiconValidator."""

    def test_valid_text_passes(self, valid_text, sample_config):
        """Valid text without forbidden terms should pass."""
        validator = LexiconValidator(sample_config)
        result = validator.validate(valid_text)
        
        assert result.passed is True
        assert len(result.errors) == 0

    def test_forbidden_term_fails(self, text_with_forbidden_term, sample_config):
        """Text with forbidden terms should fail."""
        validator = LexiconValidator(sample_config)
        result = validator.validate(text_with_forbidden_term)
        
        assert result.passed is False
        assert len(result.errors) > 0
        # Should detect at least one forbidden term
        assert any("forbidden" in error.lower() for error in result.errors)

    def test_forbidden_verb_detected(self):
        """Forbidden verbs should be detected."""
        config = {
            "lexicon_rules": {
                "forbidden_verbs": ["guarantee", "promise"]
            }
        }
        
        text = "We guarantee fast processing of your application."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        assert result.passed is False
        assert any("guarantee" in error.lower() for error in result.errors)

    def test_forbidden_pattern_detected(self):
        """Forbidden patterns (regex) should be detected."""
        config = {
            "lexicon_rules": {
                "forbidden_patterns": ["with regard to"]
            }
        }
        
        text = "With regard to your application, please wait."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        assert result.passed is False
        assert any("with regard to" in error.lower() for error in result.errors)

    def test_long_sentence_triggers_warning(self):
        """Sentences exceeding max words should trigger warning."""
        config = {
            "thresholds": {
                "max_sentence_words": 10
            }
        }
        
        # 15-word sentence
        text = "This is a very long sentence that contains way more than ten words in total."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        # Long sentences are warnings, not errors
        assert len(result.warnings) > 0
        assert any("too long" in warning.lower() for warning in result.warnings)

    def test_short_sentences_no_warning(self):
        """Short sentences should not trigger warnings."""
        config = {
            "thresholds": {
                "max_sentence_words": 22
            }
        }
        
        text = "This is short. So is this. And this one too."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        assert result.passed is True
        assert len(result.warnings) == 0

    def test_case_insensitive_matching(self):
        """Forbidden terms should match case-insensitively."""
        config = {
            "lexicon_rules": {
                "forbidden_terms": ["always"]
            }
        }
        
        text = "ALWAYS check your documents. Always verify."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        assert result.passed is False

    def test_empty_config_defaults(self):
        """Validator should work with empty config (defaults)."""
        validator = LexiconValidator({})
        result = validator.validate("This is a normal sentence.")
        
        assert result.passed is True

    def test_multiple_forbidden_terms_all_reported(self):
        """Multiple forbidden terms should all be reported."""
        config = {
            "lexicon_rules": {
                "forbidden_terms": ["always", "never", "definitely"]
            }
        }
        
        text = "We always deliver. You will never wait. Results are definitely guaranteed."
        
        validator = LexiconValidator(config)
        result = validator.validate(text)
        
        assert result.passed is False
        assert len(result.errors) >= 3

