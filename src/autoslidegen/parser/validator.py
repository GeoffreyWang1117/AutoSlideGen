"""
Schema validator for presentation outlines.
Validates and parses JSON output from LLM.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple

from pydantic import ValidationError

from .models import PresentationOutline, GenerationRequest

logger = logging.getLogger(__name__)


class OutlineValidator:
    """Validates and parses presentation outlines from LLM output."""

    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON content from text that may contain markdown or other formatting.

        Args:
            text: Raw text possibly containing JSON

        Returns:
            Extracted JSON string or None if not found
        """
        # Try to find JSON in markdown code blocks
        import re

        # Pattern for ```json ... ```
        json_block_pattern = r'```(?:json)?\s*\n(.*?)\n```'
        matches = re.findall(json_block_pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Try to find raw JSON by looking for outermost braces
        brace_start = text.find('{')
        brace_end = text.rfind('}')

        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            potential_json = text[brace_start:brace_end + 1]
            # Verify it's valid JSON
            try:
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass

        return None

    def parse_json(self, json_str: str) -> Tuple[Optional[Dict[Any, Any]], Optional[str]]:
        """
        Parse JSON string into dictionary.

        Args:
            json_str: JSON string to parse

        Returns:
            Tuple of (parsed dict or None, error message or None)
        """
        try:
            data = json.loads(json_str)
            return data, None
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg

    def validate_outline(
        self,
        data: Dict[Any, Any]
    ) -> Tuple[Optional[PresentationOutline], Optional[str]]:
        """
        Validate outline data against Pydantic model.

        Args:
            data: Dictionary containing outline data

        Returns:
            Tuple of (validated PresentationOutline or None, error message or None)
        """
        try:
            outline = PresentationOutline.model_validate(data)
            self.logger.info(
                f"Successfully validated outline with {len(outline.slides)} slides"
            )
            return outline, None
        except ValidationError as e:
            error_msg = f"Validation error: {e}"
            self.logger.error(error_msg)
            return None, str(e)

    def validate_from_text(
        self,
        text: str
    ) -> Tuple[Optional[PresentationOutline], Optional[str]]:
        """
        Extract, parse, and validate outline from raw text.

        Args:
            text: Raw text from LLM containing JSON outline

        Returns:
            Tuple of (validated PresentationOutline or None, error message or None)
        """
        # Step 1: Extract JSON
        json_str = self.extract_json_from_text(text)
        if json_str is None:
            error_msg = "Could not extract JSON from text"
            self.logger.error(error_msg)
            return None, error_msg

        # Step 2: Parse JSON
        data, parse_error = self.parse_json(json_str)
        if parse_error:
            return None, parse_error

        # Step 3: Validate against schema
        return self.validate_outline(data)

    def validate_generation_request(
        self,
        request_data: Dict[Any, Any]
    ) -> Tuple[Optional[GenerationRequest], Optional[str]]:
        """
        Validate generation request parameters.

        Args:
            request_data: Dictionary containing request parameters

        Returns:
            Tuple of (validated GenerationRequest or None, error message or None)
        """
        try:
            request = GenerationRequest.model_validate(request_data)
            self.logger.info(f"Validated generation request for topic: {request.topic}")
            return request, None
        except ValidationError as e:
            error_msg = f"Request validation error: {e}"
            self.logger.error(error_msg)
            return None, str(e)

    def get_validation_errors_detail(self, validation_error: ValidationError) -> list:
        """
        Extract detailed validation errors from Pydantic ValidationError.

        Args:
            validation_error: Pydantic ValidationError instance

        Returns:
            List of error dictionaries with location and message
        """
        errors = []
        for error in validation_error.errors():
            errors.append({
                "location": " -> ".join(str(loc) for loc in error['loc']),
                "message": error['msg'],
                "type": error['type']
            })
        return errors
