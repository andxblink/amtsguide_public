"""
NumbersAgainstSourceValidator

Anti-hallucination check: validates that all numbers in generated
content can be traced back to the source work product.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of validation check."""
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class NumbersAgainstSourceValidator:
    """
    Validates numbers in content against source work product.
    
    Flags any number in content that cannot be traced to:
    - A numeric value in the work product
    - A number within a string value in the work product
    - The allowed_numbers ignore list
    """
    
    def __init__(self, config: dict | None = None):
        """
        Initialize validator with config.
        
        Args:
            config: Configuration dict
        """
        self.config = config or {}
        
        # Numbers to always allow (years, common values, etc.)
        self.allowed_numbers = set(self.config.get("allowed_numbers", []))
        
        # Whether to ignore years (4-digit numbers 1900-2100)
        self.ignore_years = self.config.get("ignore_years", True)
        
        # Whether to ignore section numbering (1, 2, 3, etc. at start of line)
        self.ignore_section_numbers = self.config.get("ignore_section_numbers", True)
    
    def validate(
        self, content: str, work_product: dict
    ) -> ValidationResult:
        """
        Validate content numbers against work product.
        
        Args:
            content: The generated text content
            work_product: The source work product dict
            
        Returns:
            ValidationResult with passed, errors, warnings
        """
        errors = []
        warnings = []
        
        # Extract numbers from content
        content_numbers = self._extract_numbers(content)
        
        # Extract allowed numbers from work product
        source_numbers = self._extract_source_numbers(work_product)
        
        # Add configured allowed numbers
        all_allowed = source_numbers | self.allowed_numbers
        
        # Find unexpected numbers
        unexpected = content_numbers - all_allowed
        
        # Filter out years if configured
        if self.ignore_years:
            unexpected = {n for n in unexpected if not self._is_year(n)}
        
        if unexpected:
            errors.append(
                f"Unexpected numbers found (possible hallucination): "
                f"{', '.join(sorted(unexpected))}"
            )
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _extract_numbers(self, text: str) -> set[str]:
        """Extract all numbers from text."""
        # Find all number sequences
        numbers = set(re.findall(r"\d+", text))
        
        # Optionally filter section numbers (numbers at start of line followed by . or ))
        if self.ignore_section_numbers:
            # This is a simple heuristic - could be improved
            lines = text.split("\n")
            section_nums = set()
            for line in lines:
                match = re.match(r"^\s*(\d+)[.)\s]", line)
                if match:
                    section_nums.add(match.group(1))
            numbers -= section_nums
        
        return numbers
    
    def _extract_source_numbers(self, work_product: dict) -> set[str]:
        """Extract all numbers from work product values."""
        numbers = set()
        
        for key, value in work_product.items():
            if key.startswith("_"):
                continue
            
            if value is None:
                continue
            
            # Extract numbers from value
            value_str = str(value)
            found = re.findall(r"\d+", value_str)
            numbers.update(found)
        
        return numbers
    
    def _is_year(self, num_str: str) -> bool:
        """Check if number looks like a year."""
        try:
            num = int(num_str)
            return 1900 <= num <= 2100
        except ValueError:
            return False

