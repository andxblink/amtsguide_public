"""
Command-line interface for amtsguide-readiness-spec validators.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

from .validators.work_product import WorkProductValidator
from .validators.lexicon import LexiconValidator


def load_config(config_path: str | None) -> dict:
    """Load configuration from YAML file."""
    if not config_path:
        return {}
    
    path = Path(config_path)
    if not path.exists():
        print(f"Warning: Config file not found: {config_path}", file=sys.stderr)
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate_work_product():
    """CLI entrypoint for work product validation."""
    parser = argparse.ArgumentParser(
        description="Validate an AI work product for required provenance"
    )
    parser.add_argument("path", help="Path to work product JSON file")
    parser.add_argument("--config", help="Path to config YAML file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only output errors")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Load work product
    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    with open(path) as f:
        work_product = json.load(f)
    
    # Validate
    validator = WorkProductValidator(config)
    result = validator.validate(work_product)
    
    # Output
    if not args.quiet:
        print(f"Validating: {args.path}")
        print()
    
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings and not args.quiet:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.passed:
        if not args.quiet:
            print("\n✓ Validation passed")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


def validate_text():
    """CLI entrypoint for text content validation."""
    parser = argparse.ArgumentParser(
        description="Validate text content against lexicon rules"
    )
    parser.add_argument("path", help="Path to text/markdown file")
    parser.add_argument("--config", help="Path to config YAML file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only output errors")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Load text
    path = Path(args.path)
    if not path.exists():
        print(f"Error: File not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    text = path.read_text()
    
    # Validate
    validator = LexiconValidator(config)
    result = validator.validate(text)
    
    # Output
    if not args.quiet:
        print(f"Validating: {args.path}")
        print()
    
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings and not args.quiet:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.passed:
        if not args.quiet:
            print("\n✓ Validation passed")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    validate_work_product()

