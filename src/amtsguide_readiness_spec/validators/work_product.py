"""
WorkProductValidator

Validates that AI work products have required provenance:
- _metadata block with extraction info
- *_verified_at for all fact fields
- *_source for fact fields (per policy)
"""

from dataclasses import dataclass, field
from typing import Any
import re


@dataclass
class ValidationResult:
    """Result of validation check."""
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class WorkProductValidator:
    """
    Validates AI work products have required provenance.
    
    Rules:
    1. _metadata block must exist with required fields
    2. Every factual field must have *_verified_at (ISO date)
    3. Every factual field must have *_source key (value per policy)
    """
    
    def __init__(self, config: dict | None = None):
        """
        Initialize validator with config.
        
        Args:
            config: Configuration dict with field_policy, etc.
        """
        self.config = config or {}
        self.field_policy = self.config.get("field_policy", {})
        self.identity_fields = set(self.field_policy.get("identity_fields", []))
        self.non_fact_fields = set(self.field_policy.get("non_fact_fields", ["notes"]))
        self.require_source = self.field_policy.get("require_source", "numbers_only")
        self.source_exceptions = set(self.field_policy.get("source_exceptions", []))
        self.missing_source_severity = self.field_policy.get("missing_source_severity", "warning")
        self.missing_verified_at_severity = self.field_policy.get("missing_verified_at_severity", "error")
    
    def validate(self, work_product: dict) -> ValidationResult:
        """
        Validate a work product dict.
        
        Args:
            work_product: The work product to validate
            
        Returns:
            ValidationResult with passed, errors, warnings
        """
        errors = []
        warnings = []
        
        # Check _metadata
        meta_errors = self._check_metadata(work_product)
        errors.extend(meta_errors)
        
        # Get all fact fields
        fact_fields = self._get_fact_fields(work_product)
        
        # Check each fact field for provenance
        for field_name in fact_fields:
            field_errors, field_warnings = self._check_field_provenance(
                work_product, field_name
            )
            errors.extend(field_errors)
            warnings.extend(field_warnings)
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _check_metadata(self, work_product: dict) -> list[str]:
        """Check _metadata block exists with required fields."""
        errors = []
        
        if "_metadata" not in work_product:
            errors.append("Missing _metadata block")
            return errors
        
        metadata = work_product["_metadata"]
        required_fields = ["extraction_date", "model", "extractor_version"]
        
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
            elif not metadata[field]:
                errors.append(f"Empty metadata field: {field}")
        
        return errors
    
    def _get_fact_fields(self, work_product: dict) -> list[str]:
        """
        Get list of fact fields from work product.
        
        A field is a fact field if:
        - Does NOT start with _
        - Does NOT end with _source or _verified_at
        - Is NOT in identity_fields
        - Is NOT in non_fact_fields
        """
        fact_fields = []
        
        for key in work_product.keys():
            # Skip metadata
            if key.startswith("_"):
                continue
            
            # Skip provenance fields
            if key.endswith("_source") or key.endswith("_verified_at"):
                continue
            
            # Skip identity fields
            if key in self.identity_fields:
                continue
            
            # Skip non-fact fields
            if key in self.non_fact_fields:
                continue
            
            fact_fields.append(key)
        
        return fact_fields
    
    def _check_field_provenance(
        self, work_product: dict, field_name: str
    ) -> tuple[list[str], list[str]]:
        """Check a single field has required provenance."""
        errors = []
        warnings = []
        
        value = work_product.get(field_name)
        verified_at_key = f"{field_name}_verified_at"
        source_key = f"{field_name}_source"
        
        # Check verified_at exists
        if verified_at_key not in work_product:
            msg = f"Field '{field_name}' missing verification date ({verified_at_key})"
            if self.missing_verified_at_severity == "error":
                errors.append(msg)
            else:
                warnings.append(msg)
        else:
            # Validate date format (YYYY-MM-DD)
            verified_at = work_product[verified_at_key]
            if verified_at and not self._is_valid_date(verified_at):
                errors.append(
                    f"Field '{field_name}' has invalid date format: {verified_at} "
                    "(expected YYYY-MM-DD)"
                )
        
        # Check source exists (key must exist, value per policy)
        if source_key not in work_product:
            msg = f"Field '{field_name}' missing source key ({source_key})"
            if self.missing_source_severity == "error":
                errors.append(msg)
            else:
                warnings.append(msg)
        else:
            # Check if source value is required
            source_value = work_product[source_key]
            if self._requires_source_value(field_name, value):
                if not source_value:
                    msg = f"Field '{field_name}' requires non-empty source"
                    if self.missing_source_severity == "error":
                        errors.append(msg)
                    else:
                        warnings.append(msg)
        
        return errors, warnings
    
    def _requires_source_value(self, field_name: str, value: Any) -> bool:
        """Check if field requires a non-empty source value."""
        # Check exceptions
        if field_name in self.source_exceptions:
            return False
        
        # Check policy
        if self.require_source == "none":
            return False
        elif self.require_source == "all":
            return True
        elif self.require_source == "numbers_only":
            # Require source for numeric values
            return isinstance(value, (int, float)) and value is not None
        
        return False
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if string is valid ISO date (YYYY-MM-DD)."""
        if not isinstance(date_str, str):
            return False
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))

