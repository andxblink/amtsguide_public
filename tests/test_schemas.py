"""Tests for JSON schemas."""

import json
from pathlib import Path

import pytest

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def load_schema(name: str) -> dict:
    """Load a JSON schema by name."""
    path = SCHEMAS_DIR / name
    with open(path) as f:
        return json.load(f)


def load_example(name: str) -> dict:
    """Load a JSON example by name."""
    path = EXAMPLES_DIR / name
    with open(path) as f:
        return json.load(f)


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestSchemas:
    """Test suite for JSON schemas."""

    def test_work_product_schema_is_valid(self):
        """Work product schema should be valid JSON Schema."""
        schema = load_schema("work_product.schema.json")
        
        # Should have required properties
        assert "$schema" in schema
        assert "properties" in schema
        assert "_metadata" in schema["properties"]

    def test_change_log_schema_is_valid(self):
        """Change log schema should be valid JSON Schema."""
        schema = load_schema("change_log.schema.json")
        
        assert "$schema" in schema
        assert "properties" in schema
        assert "changes" in schema["properties"]

    def test_readiness_card_schema_is_valid(self):
        """Readiness card schema should be valid JSON Schema."""
        schema = load_schema("readiness_card.schema.json")
        
        assert "$schema" in schema
        assert "required" in schema
        assert "stop_rules" in schema["required"]
        assert "non_claims" in schema["required"]

    def test_valid_work_product_validates(self):
        """Valid work product should validate against schema."""
        schema = load_schema("work_product.schema.json")
        example = load_example("work_product.valid.json")
        
        # Should not raise
        jsonschema.validate(example, schema)

    def test_valid_change_log_validates(self):
        """Valid change log should validate against schema."""
        schema = load_schema("change_log.schema.json")
        example = load_example("change_log.valid.json")
        
        # Should not raise
        jsonschema.validate(example, schema)

    def test_valid_readiness_card_validates(self):
        """Valid readiness card should validate against schema."""
        schema = load_schema("readiness_card.schema.json")
        example = load_example("readiness_card.valid.json")
        
        # Should not raise
        jsonschema.validate(example, schema)

    def test_missing_metadata_fails_schema(self):
        """Work product without _metadata should fail schema validation."""
        schema = load_schema("work_product.schema.json")
        example = load_example("work_product.missing_metadata.json")
        
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(example, schema)

    def test_all_schemas_exist(self):
        """All expected schema files should exist."""
        expected_schemas = [
            "work_product.schema.json",
            "change_log.schema.json",
            "readiness_card.schema.json"
        ]
        
        for schema_name in expected_schemas:
            path = SCHEMAS_DIR / schema_name
            assert path.exists(), f"Schema {schema_name} not found"

    def test_all_schemas_are_valid_json(self):
        """All schema files should be valid JSON."""
        for schema_path in SCHEMAS_DIR.glob("*.json"):
            with open(schema_path) as f:
                data = json.load(f)  # Should not raise
                assert isinstance(data, dict)

