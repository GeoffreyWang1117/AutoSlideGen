"""
Factory for creating outline generators based on provider.
"""

from typing import Dict, Any
import logging

from .base import BaseOutlineGenerator
from .openai_generator import OpenAIOutlineGenerator
from .anthropic_generator import AnthropicOutlineGenerator

logger = logging.getLogger(__name__)


class GeneratorFactory:
    """Factory for creating outline generators."""

    _generators = {
        'openai': OpenAIOutlineGenerator,
        'anthropic': AnthropicOutlineGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        provider: str,
        config: Dict[str, Any]
    ) -> BaseOutlineGenerator:
        """
        Create an outline generator for the specified provider.

        Args:
            provider: Provider name (openai, anthropic, local)
            config: Configuration dictionary for the provider

        Returns:
            Initialized outline generator

        Raises:
            ValueError: If provider not supported
        """
        provider = provider.lower()

        if provider not in cls._generators:
            available = ', '.join(cls._generators.keys())
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Available providers: {available}"
            )

        generator_class = cls._generators[provider]
        logger.info(f"Creating {provider} outline generator")

        return generator_class(config)

    @classmethod
    def register_generator(
        cls,
        provider: str,
        generator_class: type
    ):
        """
        Register a custom generator class.

        Args:
            provider: Provider name
            generator_class: Generator class (must extend BaseOutlineGenerator)
        """
        if not issubclass(generator_class, BaseOutlineGenerator):
            raise TypeError(
                "Generator class must extend BaseOutlineGenerator"
            )

        cls._generators[provider.lower()] = generator_class
        logger.info(f"Registered generator for provider: {provider}")

    @classmethod
    def list_providers(cls) -> list:
        """
        List available providers.

        Returns:
            List of provider names
        """
        return list(cls._generators.keys())
