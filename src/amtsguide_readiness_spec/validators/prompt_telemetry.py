"""
Prompt Telemetry Validator

Validates prompt telemetry records against the schema.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self) -> bool:
        return self.valid


def validate_prompt_hash(hash_value: str) -> bool:
    """Validate prompt hash format (12 hex chars)."""
    if not hash_value:
        return False
    return bool(re.match(r'^[a-f0-9]{12}$', hash_value))


def validate_prompt_version(version: str) -> bool:
    """
    Validate prompt version format.
    
    Expected format: {type}-{city}-v{major}.{minor}
    Examples: cluster-berlin-v1.0, bezirk-munich-v2.1
    """
    if not version:
        return False
    return bool(re.match(r'^[a-z]+-[a-z]+-v[0-9]+\.[0-9]+$', version))


def validate_score(score: float, field_name: str) -> Optional[str]:
    """Validate a 0-100 score value."""
    if score is None:
        return None
    if not isinstance(score, (int, float)):
        return f"{field_name} must be a number"
    if score < 0 or score > 100:
        return f"{field_name} must be between 0 and 100 (got {score})"
    return None


def validate_telemetry_record(record: dict) -> ValidationResult:
    """
    Validate a prompt telemetry record.
    
    Args:
        record: Dictionary containing telemetry record
        
    Returns:
        ValidationResult with valid flag and any errors/warnings
    """
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['document_id', 'prompt_type', 'prompt_version', 'prompt_hash']
    for field in required_fields:
        if field not in record or not record[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate prompt_hash format
    prompt_hash = record.get('prompt_hash', '')
    if prompt_hash and not validate_prompt_hash(prompt_hash):
        errors.append(f"Invalid prompt_hash format: {prompt_hash} (expected 12 hex chars)")
    
    # Validate prompt_version format
    prompt_version = record.get('prompt_version', '')
    if prompt_version and not validate_prompt_version(prompt_version):
        warnings.append(f"Non-standard prompt_version format: {prompt_version}")
    
    # Validate prompt_type enum
    valid_types = ['cluster', 'bezirk', 'overview', 'supplier', 'blog']
    prompt_type = record.get('prompt_type', '')
    if prompt_type and prompt_type not in valid_types:
        errors.append(f"Invalid prompt_type: {prompt_type} (expected one of {valid_types})")
    
    # Validate scores
    score_fields = ['validator_score', 'pipeline_efficiency', 'post_gen_edit_score', 'composite_score']
    for field in score_fields:
        if field in record and record[field] is not None:
            error = validate_score(record[field], field)
            if error:
                errors.append(error)
    
    # Validate attempts_to_acceptance
    attempts = record.get('attempts_to_acceptance')
    if attempts is not None:
        if not isinstance(attempts, int) or attempts < 1:
            errors.append(f"attempts_to_acceptance must be a positive integer (got {attempts})")
    
    # Validate post_gen_edit_count
    edit_count = record.get('post_gen_edit_count')
    if edit_count is not None:
        if not isinstance(edit_count, int) or edit_count < 0:
            errors.append(f"post_gen_edit_count must be a non-negative integer (got {edit_count})")
    
    # Warnings for missing optional fields
    if 'validator_score' not in record:
        warnings.append("Missing validator_score - quality metrics will be incomplete")
    
    if 'attempts_to_acceptance' not in record:
        warnings.append("Missing attempts_to_acceptance - pipeline efficiency unknown")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_generation_attempt(attempt: dict) -> ValidationResult:
    """
    Validate a generation attempt record.
    
    Args:
        attempt: Dictionary containing attempt record
        
    Returns:
        ValidationResult with valid flag and any errors/warnings
    """
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['session_id', 'prompt_type', 'prompt_version', 'prompt_hash', 
                       'attempt_number', 'outcome', 'generated_at']
    for field in required_fields:
        if field not in attempt or attempt[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate outcome enum
    outcome = attempt.get('outcome', '')
    if outcome and outcome not in ['accepted', 'rejected']:
        errors.append(f"Invalid outcome: {outcome} (expected 'accepted' or 'rejected')")
    
    # Validate attempt_number
    attempt_number = attempt.get('attempt_number')
    if attempt_number is not None:
        if not isinstance(attempt_number, int) or attempt_number < 1:
            errors.append(f"attempt_number must be a positive integer (got {attempt_number})")
    
    # Validate prompt_hash format
    prompt_hash = attempt.get('prompt_hash', '')
    if prompt_hash and not validate_prompt_hash(prompt_hash):
        errors.append(f"Invalid prompt_hash format: {prompt_hash}")
    
    # Warning for rejected without reason
    if outcome == 'rejected' and not attempt.get('rejection_reason'):
        warnings.append("Rejected attempt without rejection_reason")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )

