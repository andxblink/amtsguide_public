"""
Tests for prompt telemetry validation.
"""

import json
import pytest
from pathlib import Path

from amtsguide_readiness_spec.validators.prompt_telemetry import (
    validate_prompt_hash,
    validate_prompt_version,
    validate_telemetry_record,
    validate_generation_attempt,
)


# === Hash Validation Tests ===

def test_valid_prompt_hash():
    """Valid 12-char hex hash should pass."""
    assert validate_prompt_hash("ae7cca7353ff") is True
    assert validate_prompt_hash("000000000000") is True
    assert validate_prompt_hash("abcdef123456") is True


def test_invalid_prompt_hash():
    """Invalid hashes should fail."""
    assert validate_prompt_hash("") is False
    assert validate_prompt_hash("ae7cca") is False  # Too short
    assert validate_prompt_hash("ae7cca7353ff1234") is False  # Too long
    assert validate_prompt_hash("ae7cca7353fX") is False  # Invalid char
    assert validate_prompt_hash("AE7CCA7353FF") is False  # Uppercase


# === Version Validation Tests ===

def test_valid_prompt_version():
    """Valid version strings should pass."""
    assert validate_prompt_version("cluster-berlin-v1.0") is True
    assert validate_prompt_version("bezirk-munich-v2.1") is True
    assert validate_prompt_version("overview-hamburg-v10.25") is True


def test_invalid_prompt_version():
    """Invalid version strings should fail."""
    assert validate_prompt_version("") is False
    assert validate_prompt_version("v1.0") is False  # Missing type-city
    assert validate_prompt_version("cluster-v1.0") is False  # Missing city
    assert validate_prompt_version("cluster-berlin-1.0") is False  # Missing 'v'
    assert validate_prompt_version("CLUSTER-BERLIN-v1.0") is False  # Uppercase


# === Telemetry Record Validation Tests ===

def test_valid_telemetry_record():
    """Valid telemetry record should pass."""
    record = {
        "document_id": "bezirk-mitte-de",
        "prompt_type": "bezirk",
        "prompt_version": "bezirk-berlin-v1.0",
        "prompt_hash": "ae7cca7353ff",
        "validator_score": 87.5,
        "attempts_to_acceptance": 2,
    }
    result = validate_telemetry_record(record)
    assert result.valid is True
    assert len(result.errors) == 0


def test_missing_required_fields():
    """Missing required fields should fail."""
    record = {
        "prompt_type": "bezirk",
        # Missing document_id, prompt_version, prompt_hash
    }
    result = validate_telemetry_record(record)
    assert result.valid is False
    assert len(result.errors) >= 3


def test_invalid_prompt_type():
    """Invalid prompt_type should fail."""
    record = {
        "document_id": "test-doc",
        "prompt_type": "invalid_type",
        "prompt_version": "bezirk-berlin-v1.0",
        "prompt_hash": "ae7cca7353ff",
    }
    result = validate_telemetry_record(record)
    assert result.valid is False
    assert any("prompt_type" in e for e in result.errors)


def test_invalid_score_range():
    """Scores outside 0-100 should fail."""
    record = {
        "document_id": "test-doc",
        "prompt_type": "bezirk",
        "prompt_version": "bezirk-berlin-v1.0",
        "prompt_hash": "ae7cca7353ff",
        "validator_score": 150,  # Invalid
    }
    result = validate_telemetry_record(record)
    assert result.valid is False
    assert any("validator_score" in e for e in result.errors)


def test_invalid_attempts():
    """attempts_to_acceptance < 1 should fail."""
    record = {
        "document_id": "test-doc",
        "prompt_type": "bezirk",
        "prompt_version": "bezirk-berlin-v1.0",
        "prompt_hash": "ae7cca7353ff",
        "attempts_to_acceptance": 0,  # Invalid
    }
    result = validate_telemetry_record(record)
    assert result.valid is False
    assert any("attempts_to_acceptance" in e for e in result.errors)


# === Generation Attempt Validation Tests ===

def test_valid_generation_attempt():
    """Valid generation attempt should pass."""
    attempt = {
        "session_id": "abc123",
        "prompt_type": "bezirk",
        "prompt_version": "v1.0",
        "prompt_hash": "ae7cca7353ff",
        "attempt_number": 1,
        "outcome": "rejected",
        "rejection_reason": "too_long",
        "generated_at": "2025-12-27T14:30:00Z",
    }
    result = validate_generation_attempt(attempt)
    assert result.valid is True


def test_invalid_outcome():
    """Invalid outcome value should fail."""
    attempt = {
        "session_id": "abc123",
        "prompt_type": "bezirk",
        "prompt_version": "v1.0",
        "prompt_hash": "ae7cca7353ff",
        "attempt_number": 1,
        "outcome": "maybe",  # Invalid
        "generated_at": "2025-12-27T14:30:00Z",
    }
    result = validate_generation_attempt(attempt)
    assert result.valid is False
    assert any("outcome" in e for e in result.errors)


def test_rejected_without_reason_warning():
    """Rejected attempt without reason should warn."""
    attempt = {
        "session_id": "abc123",
        "prompt_type": "bezirk",
        "prompt_version": "v1.0",
        "prompt_hash": "ae7cca7353ff",
        "attempt_number": 1,
        "outcome": "rejected",
        # Missing rejection_reason
        "generated_at": "2025-12-27T14:30:00Z",
    }
    result = validate_generation_attempt(attempt)
    assert result.valid is True  # Still valid
    assert len(result.warnings) > 0  # But warns


# === Example File Validation Tests ===

@pytest.fixture
def examples_dir():
    """Get path to examples directory."""
    return Path(__file__).parent.parent / "examples"


def test_example_telemetry_valid(examples_dir):
    """Example telemetry file should be valid."""
    example_path = examples_dir / "prompt_telemetry.valid.json"
    if example_path.exists():
        with open(example_path) as f:
            record = json.load(f)
        result = validate_telemetry_record(record)
        assert result.valid is True, f"Errors: {result.errors}"


def test_example_attempt_valid(examples_dir):
    """Example attempt file should be valid."""
    example_path = examples_dir / "generation_attempt.valid.json"
    if example_path.exists():
        with open(example_path) as f:
            attempt = json.load(f)
        result = validate_generation_attempt(attempt)
        assert result.valid is True, f"Errors: {result.errors}"

