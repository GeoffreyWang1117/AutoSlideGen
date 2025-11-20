"""
Speaker notes generator module.
Generates detailed speaker notes for presentation slides.
"""

import logging
from typing import List, Optional

from ..parser.models import PresentationOutline, Slide
from ..outline_generator.base import BaseOutlineGenerator

logger = logging.getLogger(__name__)


class SpeakerNotesGenerator:
    """Generates speaker notes for presentation slides."""

    def __init__(self, llm_generator: BaseOutlineGenerator):
        """
        Initialize speaker notes generator.

        Args:
            llm_generator: LLM generator instance to use for generation
        """
        self.llm_generator = llm_generator
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_notes_prompt(
        self,
        slide: Slide,
        presentation_context: str,
        language: str = "zh"
    ) -> str:
        """
        Generate prompt for speaker notes.

        Args:
            slide: Slide to generate notes for
            presentation_context: Context about the presentation
            language: Language code

        Returns:
            Formatted prompt
        """
        bullet_text = "\n".join(
            f"{'  ' * (bp.level - 1)}- {bp.text}"
            for bp in slide.bullet_points
        )

        language_instructions = {
            "zh": "请用中文",
            "en": "Please use English",
            "ja": "日本語で",
            "es": "Por favor, use español"
        }

        instruction = language_instructions.get(language, "Please use Chinese")

        return f"""为以下幻灯片生成详细的演讲稿（Speaker Notes）。

**演示背景**: {presentation_context}

**幻灯片信息**:
- 标题: {slide.title}
- 类型: {slide.slide_type}
- 要点:
{bullet_text}

**要求**:
1. {instruction}生成自然流畅的演讲稿
2. 扩展每个要点，提供具体细节和例子
3. 使用口语化的表达，适合现场演讲
4. 长度约200-400字
5. 包含开场、要点阐述和过渡
6. 只输出演讲稿文本，不要其他格式

演讲稿:"""

    async def generate_notes_for_slide(
        self,
        slide: Slide,
        presentation_context: str,
        language: str = "zh"
    ) -> str:
        """
        Generate speaker notes for a single slide.

        Args:
            slide: Slide to generate notes for
            presentation_context: Context about the presentation
            language: Language code

        Returns:
            Generated speaker notes text
        """
        # Skip if slide already has notes
        if slide.notes:
            self.logger.debug(f"Slide {slide.slide_number} already has notes, skipping")
            return slide.notes

        # Skip for title slides (optional)
        if slide.slide_type == "title":
            return f"这是演示的标题页。欢迎大家参加关于「{slide.title}」的分享。"

        # Skip for section slides
        if slide.slide_type == "section":
            return f"接下来我们进入「{slide.title}」这一部分。"

        try:
            prompt = self._get_notes_prompt(slide, presentation_context, language)

            # Use a simple system prompt
            system_prompt = "You are an expert presentation coach helping to create engaging speaker notes."

            # Generate notes using LLM
            notes = await self.llm_generator._call_llm(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=0.7
            )

            self.logger.info(f"Generated notes for slide {slide.slide_number}")
            return notes.strip()

        except Exception as e:
            self.logger.error(f"Failed to generate notes for slide {slide.slide_number}: {e}")
            # Fallback: generate simple notes from bullet points
            return self._generate_fallback_notes(slide)

    def _generate_fallback_notes(self, slide: Slide) -> str:
        """
        Generate simple fallback notes when LLM fails.

        Args:
            slide: Slide to generate notes for

        Returns:
            Simple notes text
        """
        notes = [f"在这一页中，我将介绍{slide.title}。"]

        for bp in slide.bullet_points:
            if bp.level == 1:
                notes.append(f"\n首先，{bp.text}。")
            elif bp.level == 2:
                notes.append(f"具体来说，{bp.text}。")
            else:
                notes.append(f"另外，{bp.text}。")

        return "".join(notes)

    async def generate_notes_for_outline(
        self,
        outline: PresentationOutline,
        skip_existing: bool = True
    ) -> PresentationOutline:
        """
        Generate speaker notes for all slides in outline.

        Args:
            outline: Presentation outline
            skip_existing: Skip slides that already have notes

        Returns:
            Updated outline with speaker notes
        """
        self.logger.info("Generating speaker notes for presentation")

        # Create presentation context
        context = (
            f"主题: {outline.metadata.topic}\n"
            f"受众: {outline.metadata.audience}\n"
            f"目的: {outline.metadata.purpose}"
        )

        # Generate notes for each slide
        for slide in outline.slides:
            if skip_existing and slide.notes:
                continue

            notes = await self.generate_notes_for_slide(
                slide=slide,
                presentation_context=context,
                language=outline.metadata.language
            )

            slide.notes = notes

        self.logger.info("Completed speaker notes generation")
        return outline

    def generate_notes_for_outline_sync(
        self,
        outline: PresentationOutline,
        skip_existing: bool = True
    ) -> PresentationOutline:
        """
        Synchronous wrapper for generate_notes_for_outline.

        Args:
            outline: Presentation outline
            skip_existing: Skip slides that already have notes

        Returns:
            Updated outline with speaker notes
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.generate_notes_for_outline(outline, skip_existing)
        )
