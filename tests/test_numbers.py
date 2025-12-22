"""Tests for NumbersAgainstSourceValidator."""

import pytest

from amtsguide_readiness_spec.validators.numbers import NumbersAgainstSourceValidator


class TestNumbersAgainstSourceValidator:
    """Test suite for NumbersAgainstSourceValidator."""

    def test_valid_numbers_pass(self, valid_work_product, valid_text):
        """Content with numbers from work product should pass."""
        validator = NumbersAgainstSourceValidator()
        result = validator.validate(valid_text, valid_work_product)
        
        assert result.passed is True
        assert len(result.errors) == 0

    def test_hallucinated_number_fails(self, valid_work_product, text_with_hallucinated_number):
        """Content with numbers NOT in work product should fail."""
        validator = NumbersAgainstSourceValidator()
        result = validator.validate(text_with_hallucinated_number, valid_work_product)
        
        assert result.passed is False
        assert any("hallucination" in error.lower() or "unexpected" in error.lower() 
                   for error in result.errors)

    def test_specific_hallucinated_number(self):
        """Specific hallucinated number should be flagged."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = "The fee is 25 EUR, but premium costs 150 EUR."
        
        validator = NumbersAgainstSourceValidator()
        result = validator.validate(content, work_product)
        
        assert result.passed is False
        assert any("150" in error for error in result.errors)

    def test_years_are_ignored_by_default(self):
        """Years (1900-2100) should be ignored by default."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = "As of 2025, the fee is 25 EUR. Updated from 2024 rates."
        
        validator = NumbersAgainstSourceValidator({"ignore_years": True})
        result = validator.validate(content, work_product)
        
        assert result.passed is True

    def test_years_can_be_checked_if_configured(self):
        """Years can be checked if ignore_years is False."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = "As of 2025, the fee is 25 EUR."
        
        validator = NumbersAgainstSourceValidator({"ignore_years": False})
        result = validator.validate(content, work_product)
        
        # 2025 is not in work product values, so should fail
        assert result.passed is False

    def test_section_numbers_ignored_by_default(self):
        """Section numbers (1. 2. 3.) should be ignored by default."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = """
1. First step
2. Second step
3. Third step

The fee is 25 EUR.
"""
        
        validator = NumbersAgainstSourceValidator({"ignore_section_numbers": True})
        result = validator.validate(content, work_product)
        
        assert result.passed is True

    def test_allowed_numbers_config(self):
        """Configured allowed_numbers should be accepted."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = "The fee is 25 EUR. Processing takes 14 days."
        
        # 14 is not in work product, but is in allowed_numbers
        validator = NumbersAgainstSourceValidator({"allowed_numbers": ["14"]})
        result = validator.validate(content, work_product)
        
        assert result.passed is True

    def test_numbers_extracted_from_strings(self):
        """Numbers in string values should be extracted."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "processing_time": "approximately 14 days"
        }
        
        content = "Processing takes about 14 days."
        
        validator = NumbersAgainstSourceValidator()
        result = validator.validate(content, work_product)
        
        assert result.passed is True

    def test_empty_content_passes(self):
        """Empty content should pass."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"}
        }
        
        validator = NumbersAgainstSourceValidator()
        result = validator.validate("", work_product)
        
        assert result.passed is True

    def test_content_without_numbers_passes(self):
        """Content without any numbers should pass."""
        work_product = {
            "_metadata": {"extraction_date": "2025-01-15T10:00:00Z", "model": "test", "extractor_version": "1.0"},
            "fee": 25
        }
        
        content = "Please apply for your permit at the office."
        
        validator = NumbersAgainstSourceValidator()
        result = validator.validate(content, work_product)
        
        assert result.passed is True

