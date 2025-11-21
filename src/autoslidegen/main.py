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
from .utils.cache import get_cache_manager

logger = logging.getLogger(__name__)


class AutoSlideGen:
    """Main class for automated slide generation."""

    def __init__(
        self,
        provider: Optional[str] = None,
        config_path: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize AutoSlideGen.

        Args:
            provider: LLM provider (openai, anthropic). Uses config default if None.
            config_path: Path to config file. Uses default if None.
            use_cache: Whether to enable caching for outline generation.
            cache_ttl: Cache TTL in seconds (default: 3600 = 1 hour).
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

        # Initialize cache
        self.use_cache = use_cache
        if self.use_cache:
            self.cache = get_cache_manager(ttl_seconds=cache_ttl)
            self.logger.info("Cache enabled")
        else:
            self.cache = None
            self.logger.info("Cache disabled")

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
        save_json: bool = True,
        generate_speaker_notes: bool = False,
        add_images: bool = False,
        image_provider: str = "unsplash",
        add_charts: bool = False
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
            generate_speaker_notes: Whether to generate speaker notes
            add_images: Whether to search and add images
            image_provider: Image provider (unsplash, pexels)
            add_charts: Whether to auto-generate charts

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

        # Try to get cached outline
        outline = None
        request_params = request.model_dump()

        if self.use_cache and self.cache:
            cached_data = self.cache.get_outline(request_params)
            if cached_data:
                self.logger.info("Using cached outline")
                outline = PresentationOutline.model_validate(cached_data)

        # Generate outline if not cached
        if outline is None:
            self.logger.info("Generating outline from LLM...")
            outline = self.generator.generate_outline_sync(request)
            self.logger.info(
                f"Outline generated successfully with {len(outline.slides)} slides"
            )

            # Cache the generated outline
            if self.use_cache and self.cache:
                self.cache.set_outline(request_params, outline.model_dump())
                self.logger.info("Outline cached for future use")

        # Generate speaker notes if requested
        if generate_speaker_notes:
            self.logger.info("Generating speaker notes...")
            outline = self.generate_speaker_notes_for_outline(outline)

        # Search and prepare images if requested
        image_map = {}
        if add_images:
            self.logger.info("Searching for images...")
            image_map = self.search_images_for_outline(outline, image_provider)

        # Generate charts if requested
        chart_map = {}
        if add_charts:
            self.logger.info("Generating charts...")
            chart_map = self.generate_charts_for_outline(outline)

        # Merge image and chart maps
        all_images = {**image_map, **chart_map}

        # Save JSON if requested
        json_path = None
        if save_json:
            json_path = self._save_json(outline)

        # Build PPTX
        self.logger.info("Building PPTX file...")
        pptx_path = self.builder.build(outline, output_path, image_map=all_images)
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

    def generate_speaker_notes_for_outline(
        self,
        outline: PresentationOutline
    ) -> PresentationOutline:
        """
        Generate speaker notes for an existing outline.

        Args:
            outline: Presentation outline

        Returns:
            Updated outline with speaker notes
        """
        from .extensions.speaker_notes import SpeakerNotesGenerator

        notes_generator = SpeakerNotesGenerator(self.generator)
        return notes_generator.generate_notes_for_outline_sync(outline)

    def search_images_for_outline(
        self,
        outline: PresentationOutline,
        provider: str = "unsplash"
    ) -> dict:
        """
        Search and download images for outline slides.

        Args:
            outline: Presentation outline
            provider: Image provider

        Returns:
            Dictionary mapping slide numbers to image paths
        """
        from .extensions.image_search import ImageSearcher, ImageInserter
        import os

        # Get API key from environment
        api_key_env = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env)

        if not api_key:
            self.logger.warning(
                f"No API key found for {provider}. Set {api_key_env} environment variable."
            )
            return {}

        try:
            searcher = ImageSearcher(api_key=api_key, provider=provider)
            inserter = ImageInserter(searcher=searcher)

            image_map = inserter.add_images_to_outline(outline)
            self.logger.info(f"Found {len(image_map)} images for slides")

            return image_map

        except ImportError as e:
            self.logger.error(f"Image search requires additional packages: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to search images: {e}")
            return {}

    def generate_charts_for_outline(
        self,
        outline: PresentationOutline
    ) -> dict:
        """
        Generate charts for outline slides.

        Args:
            outline: Presentation outline

        Returns:
            Dictionary mapping slide numbers to chart image paths
        """
        from .extensions.chart_generator import SmartChartGenerator

        try:
            chart_gen = SmartChartGenerator(chart_library="matplotlib")
            chart_map = chart_gen.generate_charts_for_outline(outline)

            self.logger.info(f"Generated {len(chart_map)} charts for slides")
            return chart_map

        except ImportError as e:
            self.logger.error(f"Chart generation requires additional packages: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to generate charts: {e}")
            return {}
