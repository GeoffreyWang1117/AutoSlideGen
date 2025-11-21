"""
Tests for speaker notes generation extension.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from autoslidegen.extensions.speaker_notes import SpeakerNotesGenerator
from autoslidegen.parser.models import (
    Slide,
    BulletPoint,
    PresentationMetadata,
    PresentationOutline
)


class TestSpeakerNotesGenerator:
    """Tests for SpeakerNotesGenerator."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="这是一段演讲稿内容。")
        return mock_gen

    @pytest.fixture
    def speaker_notes_gen(self, llm_generator):
        """Create SpeakerNotesGenerator instance."""
        return SpeakerNotesGenerator(llm_generator)

    @pytest.fixture
    def sample_slide(self):
        """Create sample slide."""
        return Slide(
            slide_number=2,
            title="人工智能的应用",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="医疗诊断", level=1),
                BulletPoint(text="金融分析", level=1),
                BulletPoint(text="自动驾驶", level=1)
            ]
        )

    @pytest.fixture
    def sample_outline(self):
        """Create sample outline."""
        metadata = PresentationMetadata(
            topic="人工智能技术",
            audience="技术人员",
            purpose="介绍AI应用",
            language="zh"
        )

        slides = [
            Slide(
                slide_number=1,
                title="标题",
                slide_type="title",
                bullet_points=[BulletPoint(text="副标题", level=1)]
            ),
            Slide(
                slide_number=2,
                title="内容",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="要点1", level=1),
                    BulletPoint(text="要点2", level=1)
                ]
            )
        ]

        return PresentationOutline(metadata=metadata, slides=slides)

    def test_initialization(self, llm_generator):
        """Test SpeakerNotesGenerator initialization."""
        gen = SpeakerNotesGenerator(llm_generator)
        assert gen.llm_generator == llm_generator

    @pytest.mark.asyncio
    async def test_generate_notes_for_slide(self, speaker_notes_gen, sample_slide):
        """Test generating notes for a single slide."""
        notes = await speaker_notes_gen.generate_notes_for_slide(
            slide=sample_slide,
            presentation_context="人工智能技术演讲",
            language="zh"
        )

        assert isinstance(notes, str)
        assert len(notes) > 0
        speaker_notes_gen.llm_generator._call_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_notes_for_slide_english(self, speaker_notes_gen):
        """Test generating notes in English."""
        slide = Slide(
            slide_number=2,
            title="AI Applications",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="Healthcare", level=1),
                BulletPoint(text="Finance", level=1)
            ]
        )

        speaker_notes_gen.llm_generator._call_llm = AsyncMock(
            return_value="This is speaker notes content."
        )

        notes = await speaker_notes_gen.generate_notes_for_slide(
            slide=slide,
            presentation_context="AI Technology Presentation",
            language="en"
        )

        assert isinstance(notes, str)
        assert len(notes) > 0

    @pytest.mark.asyncio
    async def test_generate_notes_for_outline(self, speaker_notes_gen, sample_outline):
        """Test generating notes for entire outline."""
        result_outline = await speaker_notes_gen.generate_notes_for_outline(sample_outline)

        assert isinstance(result_outline, PresentationOutline)
        assert len(result_outline.slides) == len(sample_outline.slides)

        # Content slides should have notes
        for slide in result_outline.slides:
            if slide.slide_type == "content":
                assert slide.notes is not None
                assert len(slide.notes) > 0

    @pytest.mark.asyncio
    async def test_generate_notes_skips_title_slides(self, speaker_notes_gen, sample_outline):
        """Test that notes generation skips title slides."""
        result_outline = await speaker_notes_gen.generate_notes_for_outline(sample_outline)

        title_slide = result_outline.slides[0]
        assert title_slide.slide_type == "title"
        # Title slides should not get notes or get empty notes
        assert title_slide.notes is None or title_slide.notes == ""

    def test_generate_notes_sync(self, speaker_notes_gen, sample_outline):
        """Test synchronous wrapper for notes generation."""
        result_outline = speaker_notes_gen.generate_notes_for_outline_sync(sample_outline)

        assert isinstance(result_outline, PresentationOutline)
        assert len(result_outline.slides) == len(sample_outline.slides)

    @pytest.mark.asyncio
    async def test_notes_generation_error_handling(self, llm_generator, sample_slide):
        """Test error handling in notes generation."""
        llm_generator._call_llm = AsyncMock(side_effect=Exception("API Error"))
        gen = SpeakerNotesGenerator(llm_generator)

        with pytest.raises(Exception):
            await gen.generate_notes_for_slide(sample_slide, "context", "zh")

    @pytest.mark.asyncio
    async def test_empty_slide_notes_generation(self, speaker_notes_gen):
        """Test generating notes for slide with no bullet points."""
        slide = Slide(
            slide_number=3,
            title="Section Header",
            slide_type="section",
            bullet_points=[]
        )

        notes = await speaker_notes_gen.generate_notes_for_slide(slide, "context", "zh")

        # Should still generate notes even with no bullets
        assert isinstance(notes, str)

    @pytest.mark.asyncio
    async def test_notes_different_languages(self, speaker_notes_gen, sample_slide):
        """Test notes generation in different languages."""
        languages = ['zh', 'en', 'ja', 'es']

        for lang in languages:
            notes = await speaker_notes_gen.generate_notes_for_slide(
                slide=sample_slide,
                presentation_context="Test presentation",
                language=lang
            )

            assert isinstance(notes, str)
            assert len(notes) > 0

    @pytest.mark.asyncio
    async def test_notes_preserves_outline_metadata(self, speaker_notes_gen, sample_outline):
        """Test that notes generation preserves outline metadata."""
        result_outline = await speaker_notes_gen.generate_notes_for_outline(sample_outline)

        assert result_outline.metadata.topic == sample_outline.metadata.topic
        assert result_outline.metadata.audience == sample_outline.metadata.audience
        assert result_outline.metadata.purpose == sample_outline.metadata.purpose
        assert result_outline.metadata.language == sample_outline.metadata.language
