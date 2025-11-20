"""
PPT builder module using python-pptx.
Converts presentation outlines to PPTX files.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

from ..parser.models import PresentationOutline, Slide, BulletPoint

logger = logging.getLogger(__name__)


class PPTBuilder:
    """Builds PPTX files from presentation outlines."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PPT builder.

        Args:
            config: PPT configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract font configurations
        self.fonts = self.config.get('fonts', {})
        self.layout_config = self.config.get('layout', {})
        self.image_map = {}  # Maps slide numbers to image paths

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """
        Convert hex color to RGBColor.

        Args:
            hex_color: Hex color string (e.g., "1F4E78")

        Returns:
            RGBColor object
        """
        hex_color = hex_color.lstrip('#')
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )

    def _apply_font_style(
        self,
        text_frame,
        font_config: Dict[str, Any],
        alignment: PP_ALIGN = PP_ALIGN.LEFT
    ):
        """
        Apply font styling to a text frame.

        Args:
            text_frame: Text frame to style
            font_config: Font configuration dictionary
            alignment: Text alignment
        """
        for paragraph in text_frame.paragraphs:
            paragraph.alignment = alignment

            font = paragraph.font
            font.name = font_config.get('name', 'Arial')
            font.size = Pt(font_config.get('size', 18))
            font.bold = font_config.get('bold', False)

            color_hex = font_config.get('color', '000000')
            font.color.rgb = self._hex_to_rgb(color_hex)

    def _create_title_slide(
        self,
        prs: Presentation,
        slide_data: Slide,
        metadata
    ):
        """
        Create a title slide.

        Args:
            prs: Presentation object
            slide_data: Slide data
            metadata: Presentation metadata
        """
        # Use title slide layout (typically layout 0)
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)

        # Set title
        title = slide.shapes.title
        title.text = slide_data.title
        self._apply_font_style(
            title.text_frame,
            self.fonts.get('title', {}),
            PP_ALIGN.CENTER
        )

        # Set subtitle
        if len(slide.placeholders) > 1:
            subtitle = slide.placeholders[1]
            subtitle_text = f"{metadata.audience}\n{metadata.purpose}"
            subtitle.text = subtitle_text
            self._apply_font_style(
                subtitle.text_frame,
                self.fonts.get('subtitle', {}),
                PP_ALIGN.CENTER
            )

        self.logger.debug("Created title slide")

    def _create_content_slide(
        self,
        prs: Presentation,
        slide_data: Slide
    ):
        """
        Create a content slide with bullet points.

        Args:
            prs: Presentation object
            slide_data: Slide data
        """
        # Check if we have an image for this slide
        has_image = slide_data.slide_number in self.image_map

        # Use appropriate layout
        if has_image:
            # Layout 8 is typically "Two Content" or picture layout
            try:
                slide_layout = prs.slide_layouts[8]
            except IndexError:
                # Fallback to standard layout
                slide_layout = prs.slide_layouts[1]
                has_image = False
        else:
            slide_layout = prs.slide_layouts[1]

        slide = prs.slides.add_slide(slide_layout)

        # Set title
        title = slide.shapes.title
        title.text = slide_data.title
        self._apply_font_style(
            title.text_frame,
            self.fonts.get('title', {})
        )

        # Add bullet points
        if len(slide.placeholders) > 1:
            body = slide.placeholders[1]
            text_frame = body.text_frame
            text_frame.clear()

            bullet_font = self.fonts.get('bullet', {})

            for i, bullet in enumerate(slide_data.bullet_points):
                if i == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()

                p.text = bullet.text
                p.level = bullet.level - 1  # pptx uses 0-based levels

                # Apply bullet styling
                font = p.font
                font.name = bullet_font.get('name', 'Arial')
                font.size = Pt(bullet_font.get('size', 16))
                font.bold = bullet_font.get('bold', False)
                font.color.rgb = self._hex_to_rgb(
                    bullet_font.get('color', '333333')
                )

        # Add image if available
        if has_image:
            image_path = self.image_map[slide_data.slide_number]
            self._add_image_to_slide(slide, image_path)

        # Add speaker notes if present
        if slide_data.notes:
            notes_slide = slide.notes_slide
            notes_text_frame = notes_slide.notes_text_frame
            notes_text_frame.text = slide_data.notes

        self.logger.debug(f"Created content slide: {slide_data.title}")

    def _create_section_slide(
        self,
        prs: Presentation,
        slide_data: Slide
    ):
        """
        Create a section divider slide.

        Args:
            prs: Presentation object
            slide_data: Slide data
        """
        # Use section header layout (typically layout 2 or fallback to title)
        try:
            slide_layout = prs.slide_layouts[2]
        except IndexError:
            slide_layout = prs.slide_layouts[0]

        slide = prs.slides.add_slide(slide_layout)

        # Set title
        title = slide.shapes.title
        title.text = slide_data.title
        self._apply_font_style(
            title.text_frame,
            self.fonts.get('title', {}),
            PP_ALIGN.CENTER
        )

        self.logger.debug(f"Created section slide: {slide_data.title}")

    def _add_image_to_slide(self, slide, image_path: str):
        """
        Add image to slide.

        Args:
            slide: Slide object
            image_path: Path to image file
        """
        try:
            # Position image on right side of slide
            left = Inches(6.5)
            top = Inches(2.0)
            width = Inches(3.0)

            # Add picture
            pic = slide.shapes.add_picture(
                image_path,
                left,
                top,
                width=width
            )

            self.logger.debug(f"Added image to slide: {image_path}")

        except Exception as e:
            self.logger.error(f"Failed to add image {image_path}: {e}")

    def build(
        self,
        outline: PresentationOutline,
        output_path: Optional[str] = None,
        image_map: Optional[Dict[int, str]] = None
    ) -> str:
        """
        Build PPTX file from outline.

        Args:
            outline: Validated presentation outline
            output_path: Output file path. If None, auto-generates.
            image_map: Optional dict mapping slide numbers to image paths

        Returns:
            Path to created PPTX file
        """
        # Store image map
        if image_map:
            self.image_map = image_map
        self.logger.info(f"Building presentation: {outline.metadata.topic}")

        # Create presentation
        prs = Presentation()

        # Set slide size if configured
        template_config = self.config.get('template', {})
        if 'slide_width' in template_config:
            prs.slide_width = Inches(template_config['slide_width'])
        if 'slide_height' in template_config:
            prs.slide_height = Inches(template_config['slide_height'])

        # Create slides
        for slide_data in outline.slides:
            if slide_data.slide_type == "title":
                self._create_title_slide(prs, slide_data, outline.metadata)
            elif slide_data.slide_type == "section":
                self._create_section_slide(prs, slide_data)
            else:  # content
                self._create_content_slide(prs, slide_data)

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{outline.metadata.topic}_{timestamp}.pptx"
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
            output_path = str(Path("./output") / filename)

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save presentation
        prs.save(str(output_file))
        self.logger.info(f"Presentation saved to: {output_file}")

        return str(output_file)

    def build_from_json(
        self,
        json_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Build PPTX from JSON file.

        Args:
            json_path: Path to JSON outline file
            output_path: Output file path

        Returns:
            Path to created PPTX file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            json_content = f.read()

        outline = PresentationOutline.from_json(json_content)
        return self.build(outline, output_path)
