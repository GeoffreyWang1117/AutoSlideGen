"""
Tests for data models.
"""

import pytest
from pydantic import ValidationError

from autoslidegen.parser.models import (
    BulletPoint,
    Slide,
    PresentationMetadata,
    PresentationOutline,
    GenerationRequest
)


class TestBulletPoint:
    """Tests for BulletPoint model."""

    def test_valid_bullet_point(self):
        """Test creating a valid bullet point."""
        bp = BulletPoint(text="Test bullet point", level=1)
        assert bp.text == "Test bullet point"
        assert bp.level == 1

    def test_bullet_point_strips_whitespace(self):
        """Test that whitespace is stripped from text."""
        bp = BulletPoint(text="  Test  ", level=1)
        assert bp.text == "Test"

    def test_empty_text_raises_error(self):
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError):
            BulletPoint(text="", level=1)

    def test_invalid_level_raises_error(self):
        """Test that invalid level raises validation error."""
        with pytest.raises(ValidationError):
            BulletPoint(text="Test", level=0)

        with pytest.raises(ValidationError):
            BulletPoint(text="Test", level=4)


class TestSlide:
    """Tests for Slide model."""

    def test_valid_content_slide(self):
        """Test creating a valid content slide."""
        slide = Slide(
            slide_number=1,
            title="Test Slide",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="Point 1", level=1),
                BulletPoint(text="Point 2", level=1),
            ]
        )
        assert slide.slide_number == 1
        assert slide.title == "Test Slide"
        assert len(slide.bullet_points) == 2

    def test_title_slide_validation(self):
        """Test title slide validation."""
        slide = Slide(
            slide_number=1,
            title="Title",
            slide_type="title",
            bullet_points=[
                BulletPoint(text="Subtitle", level=1)
            ]
        )
        assert slide.slide_type == "title"

    def test_content_slide_requires_min_bullets(self):
        """Test that content slides require minimum bullet points."""
        with pytest.raises(ValidationError):
            Slide(
                slide_number=1,
                title="Test",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="Only one", level=1)
                ]
            )

    def test_too_many_bullets_raises_error(self):
        """Test that too many bullets raises validation error."""
        bullets = [
            BulletPoint(text=f"Point {i}", level=1)
            for i in range(10)
        ]

        with pytest.raises(ValidationError):
            Slide(
                slide_number=1,
                title="Test",
                slide_type="content",
                bullet_points=bullets
            )


class TestPresentationMetadata:
    """Tests for PresentationMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid metadata."""
        metadata = PresentationMetadata(
            topic="Test Topic",
            audience="Test Audience",
            purpose="Test Purpose",
            language="zh"
        )
        assert metadata.topic == "Test Topic"
        assert metadata.language == "zh"

    def test_invalid_language_raises_error(self):
        """Test that invalid language raises error."""
        with pytest.raises(ValidationError):
            PresentationMetadata(
                topic="Test",
                audience="Test",
                purpose="Test",
                language="invalid"
            )


class TestPresentationOutline:
    """Tests for PresentationOutline model."""

    def test_valid_outline(self):
        """Test creating a valid outline."""
        metadata = PresentationMetadata(
            topic="Test",
            audience="Test",
            purpose="Test",
            language="zh"
        )

        slides = [
            Slide(
                slide_number=1,
                title="Title",
                slide_type="title",
                bullet_points=[BulletPoint(text="Subtitle", level=1)]
            ),
            Slide(
                slide_number=2,
                title="Content",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="Point 1", level=1),
                    BulletPoint(text="Point 2", level=1),
                ]
            )
        ]

        outline = PresentationOutline(metadata=metadata, slides=slides)
        assert len(outline.slides) == 2

    def test_first_slide_must_be_title(self):
        """Test that first slide must be title type."""
        metadata = PresentationMetadata(
            topic="Test",
            audience="Test",
            purpose="Test"
        )

        slides = [
            Slide(
                slide_number=1,
                title="Not Title",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="Point 1", level=1),
                    BulletPoint(text="Point 2", level=1),
                ]
            )
        ]

        with pytest.raises(ValidationError):
            PresentationOutline(metadata=metadata, slides=slides)

    def test_slide_numbering_validation(self):
        """Test that slide numbering is validated."""
        metadata = PresentationMetadata(
            topic="Test",
            audience="Test",
            purpose="Test"
        )

        slides = [
            Slide(
                slide_number=1,
                title="Title",
                slide_type="title",
                bullet_points=[BulletPoint(text="Sub", level=1)]
            ),
            Slide(
                slide_number=3,  # Wrong number
                title="Content",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="Point 1", level=1),
                    BulletPoint(text="Point 2", level=1),
                ]
            )
        ]

        with pytest.raises(ValidationError):
            PresentationOutline(metadata=metadata, slides=slides)

    def test_json_serialization(self):
        """Test JSON serialization."""
        metadata = PresentationMetadata(
            topic="Test",
            audience="Test",
            purpose="Test"
        )

        slides = [
            Slide(
                slide_number=1,
                title="Title",
                slide_type="title",
                bullet_points=[BulletPoint(text="Sub", level=1)]
            )
        ]

        outline = PresentationOutline(metadata=metadata, slides=slides)
        json_str = outline.to_json()
        assert isinstance(json_str, str)

        # Test deserialization
        outline2 = PresentationOutline.from_json(json_str)
        assert outline2.metadata.topic == outline.metadata.topic


class TestGenerationRequest:
    """Tests for GenerationRequest model."""

    def test_valid_request(self):
        """Test creating a valid generation request."""
        request = GenerationRequest(
            topic="Test Topic",
            audience="Test Audience",
            purpose="Test Purpose",
            language="zh",
            num_slides=10,
            bullets_per_slide=4
        )
        assert request.topic == "Test Topic"
        assert request.num_slides == 10

    def test_invalid_num_slides_raises_error(self):
        """Test that invalid num_slides raises error."""
        with pytest.raises(ValidationError):
            GenerationRequest(
                topic="Test",
                audience="Test",
                purpose="Test",
                num_slides=3  # Too few
            )

        with pytest.raises(ValidationError):
            GenerationRequest(
                topic="Test",
                audience="Test",
                purpose="Test",
                num_slides=50  # Too many
            )
