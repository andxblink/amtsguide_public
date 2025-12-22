#!/usr/bin/env python3
"""
Leak Guard

Scans repository files for accidental inclusion of real data:
- Real authority domains (.berlin.de, .bund.de, .gov)
- Non-example email addresses
- Real phone number patterns

Exits with code 1 if leaks are found.
"""

import re
import sys
from pathlib import Path


# Directories to scan
SCAN_DIRS = ["examples", "docs"]
SCAN_FILES = ["README.md", "CHANGELOG.md"]

# Patterns that indicate real data (should NOT be present)
LEAK_PATTERNS = [
    # Real German authority domains
    (r"\.berlin\.de\b", "Real Berlin domain"),
    (r"\.bund\.de\b", "Real German federal domain"),
    (r"\.gov\b(?!/)", "Real government domain"),  # Avoid matching example.gov/path
    (r"ba-[a-z]+\.berlin\.de", "Real Berlin district domain"),
    
    # Real email addresses (not @example.com/org/invalid)
    (r"[a-zA-Z0-9._%+-]+@(?!example\.(com|org|invalid))[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", 
     "Real email address"),
    
    # German phone numbers
    (r"\+49\s*\d", "German phone number (+49)"),
    (r"\(0\d{2,4}\)\s*\d", "German phone number format"),
    (r"030[\s-]?\d{3,}", "Berlin phone number (030)"),
]

# Patterns to allow (false positive prevention)
ALLOW_PATTERNS = [
    r"example\.gov",
    r"example\.com",
    r"example\.org",
    r"@example\.",
    r"\+1-555-",  # US fake numbers
]

# Lines containing these phrases are documentation about what NOT to do
DOCUMENTATION_CONTEXT = [
    "DO NOT",
    "do not",
    "Real (",
    "# Blocked",
    "# Real",
    "should NOT",
    "reject",
    "Reject",
    "BLOCKED",
]


def should_skip_line(line: str) -> bool:
    """Check if line contains allowed patterns or is documentation."""
    # Skip lines with allowed example patterns
    for pattern in ALLOW_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    # Skip lines that are documenting what NOT to do
    for phrase in DOCUMENTATION_CONTEXT:
        if phrase in line:
            return True
    
    # Skip lines that are regex patterns (documenting the scanner itself)
    if line.strip().startswith("r\"") or line.strip().startswith("(r\""):
        return True
    
    return False


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """
    Scan a file for leak patterns.
    
    Returns list of (line_number, pattern_description, line_content) tuples.
    """
    issues = []
    
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read {path}: {e}", file=sys.stderr)
        return issues
    
    in_code_block = False
    in_bad_example = False  # Track if we're in a "bad example" section
    
    for line_num, line in enumerate(content.splitlines(), 1):
        # Track code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        
        # Track "bad example" sections (documentation showing what NOT to do)
        if "DO NOT" in line or "Real (" in line or "Bad:" in line:
            in_bad_example = True
        elif line.strip().startswith("**") and ("OK" in line or "Good" in line or "Synthetic" in line):
            in_bad_example = False
        
        # Skip code blocks entirely (they're examples/documentation)
        if in_code_block:
            continue
        
        # Skip if in a "bad example" section
        if in_bad_example:
            continue
        
        # Skip lines with allowed patterns
        if should_skip_line(line):
            continue
        
        for pattern, description in LEAK_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append((line_num, description, line.strip()[:100]))
    
    return issues


def main():
    """Run leak guard scan."""
    repo_root = Path(__file__).parent.parent
    all_issues: dict[str, list] = {}
    
    # Scan directories
    for dir_name in SCAN_DIRS:
        dir_path = repo_root / dir_name
        if not dir_path.exists():
            continue
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".md", ".json", ".yaml", ".yml", ".txt"]:
                issues = scan_file(file_path)
                if issues:
                    rel_path = file_path.relative_to(repo_root)
                    all_issues[str(rel_path)] = issues
    
    # Scan root files
    for file_name in SCAN_FILES:
        file_path = repo_root / file_name
        if file_path.exists():
            issues = scan_file(file_path)
            if issues:
                all_issues[file_name] = issues
    
    # Report results
    if all_issues:
        print("=" * 60)
        print("LEAK GUARD: Potential real data detected!")
        print("=" * 60)
        print()
        
        for file_path, issues in all_issues.items():
            print(f"📄 {file_path}")
            for line_num, description, content in issues:
                print(f"   Line {line_num}: {description}")
                print(f"   > {content}")
            print()
        
        print("=" * 60)
        print("Please replace real data with synthetic examples.")
        print("See docs/privacy.md for guidelines.")
        print("=" * 60)
        
        sys.exit(1)
    else:
        print("✓ Leak guard: No real data detected")
        sys.exit(0)


if __name__ == "__main__":
    main()

