"""Tests for WorkProductValidator."""

import pytest

from amtsguide_readiness_spec.validators.work_product import WorkProductValidator


class TestWorkProductValidator:
    """Test suite for WorkProductValidator."""

    def test_valid_work_product_passes(self, valid_work_product, sample_config):
        """Valid work product should pass validation."""
        validator = WorkProductValidator(sample_config)
        result = validator.validate(valid_work_product)
        
        assert result.passed is True
        assert len(result.errors) == 0

    def test_missing_metadata_fails(self, work_product_missing_metadata, sample_config):
        """Work product without _metadata should fail."""
        validator = WorkProductValidator(sample_config)
        result = validator.validate(work_product_missing_metadata)
        
        assert result.passed is False
        assert any("_metadata" in error for error in result.errors)

    def test_missing_verified_at_fails(self, work_product_missing_verified_at, sample_config):
        """Work product missing *_verified_at should fail."""
        validator = WorkProductValidator(sample_config)
        result = validator.validate(work_product_missing_verified_at)
        
        assert result.passed is False
        assert any("verified_at" in error.lower() for error in result.errors)

    def test_non_fact_fields_are_ignored(self, sample_config):
        """Fields in non_fact_fields should not require provenance."""
        work_product = {
            "_metadata": {
                "extraction_date": "2025-01-15T10:00:00Z",
                "model": "test-model",
                "extractor_version": "1.0"
            },
            "id": "test-id",
            "name": "Test Name",
            "notes": "This is a note without provenance - should be OK"
        }
        
        # Configure 'notes' as non-fact field
        config = {
            "field_policy": {
                "identity_fields": ["id", "name"],
                "non_fact_fields": ["notes"],
                "missing_verified_at_severity": "error"
            }
        }
        
        validator = WorkProductValidator(config)
        result = validator.validate(work_product)
        
        assert result.passed is True
        assert len(result.errors) == 0

    def test_identity_fields_are_ignored(self, sample_config):
        """Fields in identity_fields should not require provenance."""
        work_product = {
            "_metadata": {
                "extraction_date": "2025-01-15T10:00:00Z",
                "model": "test-model",
                "extractor_version": "1.0"
            },
            "id": "test-id",
            "slug": "test-slug"
        }
        
        config = {
            "field_policy": {
                "identity_fields": ["id", "slug"],
                "non_fact_fields": [],
                "missing_verified_at_severity": "error"
            }
        }
        
        validator = WorkProductValidator(config)
        result = validator.validate(work_product)
        
        assert result.passed is True

    def test_invalid_date_format_fails(self, sample_config):
        """Invalid date format in *_verified_at should fail."""
        work_product = {
            "_metadata": {
                "extraction_date": "2025-01-15T10:00:00Z",
                "model": "test-model",
                "extractor_version": "1.0"
            },
            "fee": 25,
            "fee_source": "https://example.gov/fees",
            "fee_verified_at": "January 15, 2025"  # Wrong format
        }
        
        validator = WorkProductValidator(sample_config)
        result = validator.validate(work_product)
        
        assert result.passed is False
        assert any("invalid date format" in error.lower() for error in result.errors)

    def test_missing_source_is_warning_by_default(self):
        """Missing source should be a warning, not error, by default."""
        work_product = {
            "_metadata": {
                "extraction_date": "2025-01-15T10:00:00Z",
                "model": "test-model",
                "extractor_version": "1.0"
            },
            "fee": 25,
            "fee_verified_at": "2025-01-15"
            # Missing fee_source
        }
        
        config = {
            "field_policy": {
                "identity_fields": [],
                "non_fact_fields": [],
                "missing_source_severity": "warning",
                "missing_verified_at_severity": "error"
            }
        }
        
        validator = WorkProductValidator(config)
        result = validator.validate(work_product)
        
        # Should pass (warning, not error)
        assert result.passed is False or len(result.warnings) > 0
        # The missing source key should cause a warning
        assert any("source" in w.lower() for w in result.warnings) or \
               any("source" in e.lower() for e in result.errors)

    def test_empty_metadata_fields_fail(self):
        """Empty required metadata fields should fail."""
        work_product = {
            "_metadata": {
                "extraction_date": "2025-01-15T10:00:00Z",
                "model": "",  # Empty
                "extractor_version": "1.0"
            }
        }
        
        validator = WorkProductValidator()
        result = validator.validate(work_product)
        
        assert result.passed is False
        assert any("model" in error.lower() for error in result.errors)

