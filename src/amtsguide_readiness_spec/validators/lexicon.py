"""
LexiconValidator

Validates text content against stop rules:
- Forbidden terms
- Forbidden regex patterns
- Sentence length limits
- Fact token limits
"""

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of validation check."""
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class LexiconValidator:
    """
    Validates text against lexicon rules.
    
    Rules:
    - Forbidden terms trigger errors
    - Forbidden patterns (regex) trigger errors
    - Sentences > max_words trigger warnings
    - Fact sentences > max_tokens trigger warnings
    """
    
    def __init__(self, config: dict | None = None):
        """
        Initialize validator with config.
        
        Args:
            config: Configuration dict with lexicon_rules, thresholds
        """
        self.config = config or {}
        
        # Thresholds
        thresholds = self.config.get("thresholds", {})
        self.max_sentence_words = thresholds.get("max_sentence_words", 22)
        self.max_fact_tokens = thresholds.get("max_fact_tokens", 18)
        
        # Lexicon rules
        lexicon = self.config.get("lexicon_rules", {})
        self.forbidden_verbs = lexicon.get("forbidden_verbs", [])
        self.forbidden_patterns = lexicon.get("forbidden_patterns", [])
        self.forbidden_terms = lexicon.get("forbidden_terms", [])
    
    def validate(self, text: str) -> ValidationResult:
        """
        Validate text content.
        
        Args:
            text: The text to validate
            
        Returns:
            ValidationResult with passed, errors, warnings
        """
        errors = []
        warnings = []
        
        # Check forbidden terms
        term_errors = self._check_forbidden_terms(text)
        errors.extend(term_errors)
        
        # Check forbidden patterns
        pattern_errors = self._check_forbidden_patterns(text)
        errors.extend(pattern_errors)
        
        # Check sentence length
        length_warnings = self._check_sentence_length(text)
        warnings.extend(length_warnings)
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _check_forbidden_terms(self, text: str) -> list[str]:
        """Check for forbidden terms in text."""
        errors = []
        text_lower = text.lower()
        
        all_forbidden = self.forbidden_verbs + self.forbidden_terms
        
        for term in all_forbidden:
            # Word boundary match
            pattern = rf"\b{re.escape(term.lower())}\b"
            if re.search(pattern, text_lower):
                errors.append(f"Forbidden term found: '{term}'")
        
        return errors
    
    def _check_forbidden_patterns(self, text: str) -> list[str]:
        """Check for forbidden regex patterns in text."""
        errors = []
        
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(f"Forbidden pattern found: '{pattern}'")
        
        return errors
    
    def _check_sentence_length(self, text: str) -> list[str]:
        """Check for sentences exceeding word limit."""
        warnings = []
        
        # Split into sentences
        sentences = re.split(r"[.!?]+", text)
        
        long_count = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            words = sentence.split()
            if len(words) > self.max_sentence_words:
                long_count += 1
                if long_count <= 3:  # Only report first 3
                    warnings.append(
                        f"Sentence too long ({len(words)} words, max {self.max_sentence_words}): "
                        f"{sentence[:60]}..."
                    )
        
        if long_count > 3:
            warnings.append(f"Total: {long_count} sentences exceed {self.max_sentence_words} words")
        
        return warnings

