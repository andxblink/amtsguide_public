"""Pytest configuration and fixtures."""

import json
from pathlib import Path

import pytest
import yaml


EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
CONFIG_DIR = Path(__file__).parent.parent / "config"
SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


@pytest.fixture
def sample_config():
    """Load sample configuration."""
    config_path = CONFIG_DIR / "sample.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def valid_work_product():
    """Load valid work product example."""
    path = EXAMPLES_DIR / "work_product.valid.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def work_product_missing_verified_at():
    """Load work product missing verified_at."""
    path = EXAMPLES_DIR / "work_product.missing_verified_at.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def work_product_missing_metadata():
    """Load work product missing metadata."""
    path = EXAMPLES_DIR / "work_product.missing_metadata.json"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def valid_text():
    """Load valid text example."""
    path = EXAMPLES_DIR / "text.valid.md"
    return path.read_text()


@pytest.fixture
def text_with_forbidden_term():
    """Load text with forbidden terms."""
    path = EXAMPLES_DIR / "text.forbidden_term.md"
    return path.read_text()


@pytest.fixture
def text_with_hallucinated_number():
    """Load text with hallucinated numbers."""
    path = EXAMPLES_DIR / "text.hallucinated_number.md"
    return path.read_text()

