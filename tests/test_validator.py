"""
Tests for outline validator.
"""

import json
import pytest

from autoslidegen.parser.validator import OutlineValidator
from autoslidegen.parser.models import PresentationOutline


class TestOutlineValidator:
    """Tests for OutlineValidator."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return OutlineValidator()

    @pytest.fixture
    def valid_outline_dict(self):
        """Create valid outline dictionary."""
        return {
            "metadata": {
                "topic": "Test Topic",
                "audience": "Test Audience",
                "purpose": "Test Purpose",
                "language": "zh"
            },
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Title Slide",
                    "slide_type": "title",
                    "bullet_points": [
                        {"text": "Subtitle", "level": 1}
                    ]
                },
                {
                    "slide_number": 2,
                    "title": "Content Slide",
                    "slide_type": "content",
                    "bullet_points": [
                        {"text": "Point 1", "level": 1},
                        {"text": "Point 2", "level": 1},
                        {"text": "Point 3", "level": 1}
                    ]
                }
            ]
        }

    def test_extract_json_from_markdown(self, validator):
        """Test extracting JSON from markdown code block."""
        text = """Here is the outline:

```json
{"key": "value"}
```
"""
        json_str = validator.extract_json_from_text(text)
        assert json_str == '{"key": "value"}'

    def test_extract_json_from_plain_text(self, validator):
        """Test extracting JSON from plain text."""
        text = 'Some text {"key": "value"} more text'
        json_str = validator.extract_json_from_text(text)
        assert json_str == '{"key": "value"}'

    def test_parse_valid_json(self, validator, valid_outline_dict):
        """Test parsing valid JSON."""
        json_str = json.dumps(valid_outline_dict)
        data, error = validator.parse_json(json_str)
        assert error is None
        assert data == valid_outline_dict

    def test_parse_invalid_json(self, validator):
        """Test parsing invalid JSON."""
        invalid_json = '{"key": invalid}'
        data, error = validator.parse_json(invalid_json)
        assert data is None
        assert error is not None

    def test_validate_valid_outline(self, validator, valid_outline_dict):
        """Test validating a valid outline."""
        outline, error = validator.validate_outline(valid_outline_dict)
        assert error is None
        assert isinstance(outline, PresentationOutline)
        assert len(outline.slides) == 2

    def test_validate_invalid_outline(self, validator):
        """Test validating an invalid outline."""
        invalid_outline = {
            "metadata": {
                "topic": "Test",
                "audience": "Test",
                "purpose": "Test"
            },
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Wrong Type",
                    "slide_type": "content",  # Should be "title"
                    "bullet_points": [
                        {"text": "Point", "level": 1}
                    ]
                }
            ]
        }

        outline, error = validator.validate_outline(invalid_outline)
        assert outline is None
        assert error is not None

    def test_validate_from_text(self, validator, valid_outline_dict):
        """Test validating from text with JSON."""
        json_str = json.dumps(valid_outline_dict)
        text = f"```json\n{json_str}\n```"

        outline, error = validator.validate_from_text(text)
        assert error is None
        assert isinstance(outline, PresentationOutline)
