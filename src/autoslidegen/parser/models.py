"""
Data models for AutoSlideGen using Pydantic.
Defines the structure for presentation outlines and slides.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class BulletPoint(BaseModel):
    """A single bullet point in a slide."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The text content of the bullet point"
    )
    level: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Indentation level (1=top level, 2=sub-bullet, 3=sub-sub-bullet)"
    )

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Ensure text is not just whitespace."""
        if not v.strip():
            raise ValueError("Bullet point text cannot be empty or whitespace")
        return v.strip()


class ChartSpec(BaseModel):
    """Specification for a chart to be embedded in a slide."""

    chart_type: Literal["bar", "horizontal_bar", "stacked_bar", "pie", "donut", "line", "area", "radar", "scatter"] = Field(
        default="bar",
        description="Type of chart to generate"
    )
    title: str = Field(
        default="",
        max_length=100,
        description="Chart title"
    )
    data: dict = Field(
        default_factory=dict,
        description="Chart data in appropriate format for the chart type"
    )
    xlabel: Optional[str] = Field(
        default=None,
        max_length=50,
        description="X-axis label"
    )
    ylabel: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Y-axis label"
    )


class Slide(BaseModel):
    """A single slide in the presentation."""

    slide_number: int = Field(
        ...,
        ge=1,
        description="The sequential number of this slide"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The title of the slide"
    )
    slide_type: Literal["title", "content", "section"] = Field(
        default="content",
        description="Type of slide: title (cover), content (normal), or section (divider)"
    )
    bullet_points: List[BulletPoint] = Field(
        default_factory=list,
        description="List of bullet points for this slide"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Speaker notes for this slide (optional)"
    )
    chart: Optional[ChartSpec] = Field(
        default=None,
        description="Optional chart specification to embed in this slide"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Slide title cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode='after')
    def validate_bullet_points(self):
        """Validate bullet points based on slide type."""
        # Title and section slides typically don't have bullet points
        if self.slide_type in ["title", "section"]:
            if len(self.bullet_points) > 3:
                raise ValueError(
                    f"{self.slide_type} slides should have at most 3 bullet points"
                )
        else:  # content slides
            if len(self.bullet_points) < 2:
                raise ValueError(
                    f"Content slides must have at least 2 bullet points, got {len(self.bullet_points)}"
                )
            if len(self.bullet_points) > 8:
                raise ValueError(
                    f"Content slides should have at most 8 bullet points, got {len(self.bullet_points)}"
                )

        return self


class PresentationMetadata(BaseModel):
    """Metadata about the presentation."""

    topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The main topic/title of the presentation"
    )
    audience: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target audience for the presentation"
    )
    purpose: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Purpose and goals of the presentation"
    )
    language: str = Field(
        default="zh",
        pattern="^(zh|en|ja|es)$",
        description="Language code: zh (Chinese), en (English), ja (Japanese), es (Spanish)"
    )
    estimated_duration: Optional[int] = Field(
        default=None,
        ge=5,
        le=180,
        description="Estimated presentation duration in minutes"
    )


class PresentationOutline(BaseModel):
    """Complete presentation outline with metadata and slides."""

    metadata: PresentationMetadata = Field(
        ...,
        description="Metadata about the presentation"
    )
    slides: List[Slide] = Field(
        ...,
        min_length=5,
        max_length=50,
        description="List of slides in the presentation"
    )

    @model_validator(mode='after')
    def validate_slides(self):
        """Validate slide structure and numbering."""
        if not self.slides:
            raise ValueError("Presentation must have at least one slide")

        # Check first slide is title slide
        if self.slides[0].slide_type != "title":
            raise ValueError("First slide must be a title slide")

        # Validate slide numbering
        for i, slide in enumerate(self.slides, start=1):
            if slide.slide_number != i:
                raise ValueError(
                    f"Slide numbering error: expected {i}, got {slide.slide_number}"
                )

        return self

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return self.model_dump(mode='python')

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "PresentationOutline":
        """Create instance from dictionary."""
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> "PresentationOutline":
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)


class GenerationRequest(BaseModel):
    """Request parameters for outline generation."""

    topic: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Presentation topic"
    )
    audience: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Target audience"
    )
    purpose: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Presentation purpose"
    )
    language: str = Field(
        default="zh",
        pattern="^(zh|en|ja|es)$",
        description="Language code"
    )
    num_slides: int = Field(
        default=10,
        ge=5,
        le=30,
        description="Desired number of slides"
    )
    bullets_per_slide: int = Field(
        default=4,
        ge=2,
        le=6,
        description="Average bullet points per slide"
    )
    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional requirements or constraints"
    )
