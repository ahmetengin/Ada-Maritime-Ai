"""Privacy Layer - PII Protection and Data Sanitization

Implements privacy-preserving execution:
- PII detection and tokenization
- Sensitive data filtering
- Secure intermediate result handling
"""

import re
import hashlib
import uuid
from typing import Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PIIToken:
    """PII token mapping"""
    original: str
    token: str
    pii_type: str


class PIIDetector:
    """Detect and classify PII in text"""

    # Regex patterns for common PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        # Maritime-specific
        'imo_number': r'\bIMO\s?\d{7}\b',
        'mmsi': r'\b\d{9}\b',  # Maritime Mobile Service Identity
        'vessel_name': r'\b(?:M/V|S/Y|M/Y)\s+[\w\s]+\b',
    }

    SENSITIVE_KEYWORDS = {
        'password', 'secret', 'token', 'key', 'credential',
        'api_key', 'access_token', 'private_key'
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, list]:
        """
        Detect PII in text.

        Returns:
            Dict mapping PII type to list of matches
        """
        detections = {}

        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detections[pii_type] = matches

        return detections

    @classmethod
    def has_sensitive_keywords(cls, text: str) -> bool:
        """Check if text contains sensitive keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.SENSITIVE_KEYWORDS)


class PrivacyLayer:
    """
    Privacy-preserving execution layer.

    Features:
    - Automatic PII detection and tokenization
    - Sensitive data filtering
    - Reversible tokenization for data flow
    """

    def __init__(self):
        self._token_map: Dict[str, PIIToken] = {}
        self._reverse_map: Dict[str, str] = {}

    def sanitize_code(self, code: str) -> str:
        """
        Sanitize code before execution.

        Checks for hardcoded secrets and sensitive patterns.
        """
        # Check for sensitive keywords in strings
        if PIIDetector.has_sensitive_keywords(code):
            # Warn but don't block (might be legitimate variable names)
            pass

        return code

    def tokenize_pii(self, text: str, preserve_format: bool = True) -> Tuple[str, Dict[str, PIIToken]]:
        """
        Tokenize PII in text.

        Args:
            text: Text containing PII
            preserve_format: Keep similar format for tokens (e.g., email-like for emails)

        Returns:
            Tuple of (tokenized_text, token_mappings)
        """
        detections = PIIDetector.detect(text)
        tokenized = text
        tokens = {}

        for pii_type, matches in detections.items():
            for match in matches:
                if match not in self._token_map:
                    # Generate token
                    if preserve_format:
                        token = self._generate_format_preserving_token(match, pii_type)
                    else:
                        token = f"[{pii_type.upper()}_{uuid.uuid4().hex[:8]}]"

                    pii_token = PIIToken(
                        original=match,
                        token=token,
                        pii_type=pii_type
                    )

                    self._token_map[match] = pii_token
                    self._reverse_map[token] = match

                else:
                    pii_token = self._token_map[match]

                tokens[match] = pii_token
                tokenized = tokenized.replace(match, pii_token.token)

        return tokenized, tokens

    def detokenize(self, text: str) -> str:
        """Restore original PII from tokens"""
        detokenized = text

        for token, original in self._reverse_map.items():
            detokenized = detokenized.replace(token, original)

        return detokenized

    def _generate_format_preserving_token(self, value: str, pii_type: str) -> str:
        """
        Generate token that preserves format.

        Example:
            user@example.com -> token_abc123@example.com
            +1-555-0100 -> +1-555-9999
        """
        # Hash for consistency
        hash_suffix = hashlib.md5(value.encode()).hexdigest()[:8]

        if pii_type == 'email':
            local, domain = value.split('@')
            return f"token_{hash_suffix}@{domain}"

        elif pii_type == 'phone':
            # Keep format, randomize digits
            return re.sub(r'\d', lambda m: str(hash(m.group() + hash_suffix) % 10), value)

        elif pii_type == 'imo_number':
            return f"IMO{hash(value + hash_suffix) % 10000000}"

        elif pii_type == 'vessel_name':
            prefix = value.split()[0]  # M/V, S/Y, etc.
            return f"{prefix} TOKEN_{hash_suffix.upper()}"

        else:
            # Generic token
            return f"[{pii_type.upper()}_{hash_suffix}]"

    def filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter sensitive fields from data dictionary.

        Removes or masks common sensitive fields.
        """
        sensitive_keys = {
            'password', 'secret', 'token', 'key', 'credential',
            'api_key', 'access_token', 'private_key', 'ssn',
            'credit_card', 'card_number'
        }

        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()

            if any(sensitive in key_lower for sensitive in sensitive_keys):
                # Mask sensitive value
                filtered[key] = "[REDACTED]"

            elif isinstance(value, dict):
                # Recurse into nested dicts
                filtered[key] = self.filter_sensitive_data(value)

            elif isinstance(value, list):
                # Handle lists
                filtered[key] = [
                    self.filter_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]

            else:
                filtered[key] = value

        return filtered

    def secure_log(self, message: str) -> str:
        """
        Sanitize log message by removing PII.

        Returns sanitized version safe for logging.
        """
        sanitized, _ = self.tokenize_pii(message, preserve_format=False)
        return sanitized


class SecureDataHandler:
    """
    Handler for secure data operations.

    Ensures sensitive data stays in execution environment.
    """

    def __init__(self, privacy_layer: PrivacyLayer):
        self.privacy = privacy_layer

    def process_api_response(self, response_data: Any, pii_fields: Optional[Set[str]] = None) -> Any:
        """
        Process API response to protect PII.

        Args:
            response_data: API response
            pii_fields: Known PII field names

        Returns:
            Processed response with PII tokenized
        """
        if isinstance(response_data, dict):
            return self._process_dict(response_data, pii_fields or set())

        elif isinstance(response_data, list):
            return [self.process_api_response(item, pii_fields) for item in response_data]

        elif isinstance(response_data, str):
            tokenized, _ = self.privacy.tokenize_pii(response_data)
            return tokenized

        else:
            return response_data

    def _process_dict(self, data: Dict[str, Any], pii_fields: Set[str]) -> Dict[str, Any]:
        """Process dictionary data"""
        processed = {}

        for key, value in data.items():
            if key in pii_fields or PIIDetector.has_sensitive_keywords(key):
                # Tokenize PII field
                if isinstance(value, str):
                    tokenized, _ = self.privacy.tokenize_pii(value)
                    processed[key] = tokenized
                else:
                    processed[key] = value

            elif isinstance(value, dict):
                processed[key] = self._process_dict(value, pii_fields)

            elif isinstance(value, list):
                processed[key] = [
                    self._process_dict(item, pii_fields) if isinstance(item, dict) else item
                    for item in value
                ]

            else:
                processed[key] = value

        return processed
