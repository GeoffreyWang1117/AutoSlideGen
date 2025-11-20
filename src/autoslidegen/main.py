"""
Main orchestration module for AutoSlideGen.
Coordinates outline generation and PPT building.
"""

import logging
from pathlib import Path
from typing import Optional

from .parser.models import GenerationRequest, PresentationOutline
from .outline_generator.factory import GeneratorFactory
from .ppt_builder.builder import PPTBuilder
from .utils.config import get_config

logger = logging.getLogger(__name__)


class AutoSlideGen:
    """Main class for automated slide generation."""

    def __init__(
        self,
        provider: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize AutoSlideGen.

        Args:
            provider: LLM provider (openai, anthropic). Uses config default if None.
            config_path: Path to config file. Uses default if None.
        """
        self.config = get_config(config_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Determine provider
        if provider is None:
            provider = self.config.get('llm.provider', 'openai')

        self.provider = provider

        # Initialize generator
        llm_config = self.config.get_llm_config(provider)
        self.generator = GeneratorFactory.create_generator(provider, llm_config)

        # Initialize PPT builder
        ppt_config = self.config.get_ppt_config()
        self.builder = PPTBuilder(ppt_config)

        self.logger.info(f"Initialized AutoSlideGen with provider: {provider}")

    def generate(
        self,
        topic: str,
        audience: str,
        purpose: str,
        language: str = "zh",
        num_slides: int = 10,
        bullets_per_slide: int = 4,
        additional_requirements: Optional[str] = None,
        output_path: Optional[str] = None,
        save_json: bool = True
    ) -> dict:
        """
        Generate presentation from topic and build PPTX.

        Args:
            topic: Presentation topic
            audience: Target audience
            purpose: Presentation purpose
            language: Language code (zh, en, ja, es)
            num_slides: Desired number of slides
            bullets_per_slide: Average bullets per slide
            additional_requirements: Additional requirements
            output_path: Custom output path for PPTX
            save_json: Whether to save JSON outline

        Returns:
            Dictionary with paths to generated files
        """
        self.logger.info(f"Starting generation for topic: {topic}")

        # Create generation request
        request = GenerationRequest(
            topic=topic,
            audience=audience,
            purpose=purpose,
            language=language,
            num_slides=num_slides,
            bullets_per_slide=bullets_per_slide,
            additional_requirements=additional_requirements
        )

        # Generate outline
        self.logger.info("Generating outline from LLM...")
        outline = self.generator.generate_outline_sync(request)
        self.logger.info(
            f"Outline generated successfully with {len(outline.slides)} slides"
        )

        # Save JSON if requested
        json_path = None
        if save_json:
            json_path = self._save_json(outline)

        # Build PPTX
        self.logger.info("Building PPTX file...")
        pptx_path = self.builder.build(outline, output_path)
        self.logger.info(f"PPTX file created: {pptx_path}")

        return {
            'pptx_path': pptx_path,
            'json_path': json_path,
            'outline': outline
        }

    def generate_from_json(
        self,
        json_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate PPTX from existing JSON outline.

        Args:
            json_path: Path to JSON outline file
            output_path: Custom output path for PPTX

        Returns:
            Path to created PPTX file
        """
        self.logger.info(f"Loading outline from: {json_path}")
        pptx_path = self.builder.build_from_json(json_path, output_path)
        self.logger.info(f"PPTX file created: {pptx_path}")
        return pptx_path

    def _save_json(self, outline: PresentationOutline) -> str:
        """
        Save outline to JSON file.

        Args:
            outline: Presentation outline

        Returns:
            Path to saved JSON file
        """
        from datetime import datetime

        output_dir = self.config.get_output_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{outline.metadata.topic}_{timestamp}.json"
        # Sanitize filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")

        json_path = output_dir / filename
        json_path.write_text(outline.to_json(), encoding='utf-8')

        self.logger.info(f"Outline saved to JSON: {json_path}")
        return str(json_path)
