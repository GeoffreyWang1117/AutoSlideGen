"""
Outline generation module for AutoSlideGen.
"""

from .base import BaseOutlineGenerator
from .factory import GeneratorFactory
from .openai_generator import OpenAIOutlineGenerator
from .anthropic_generator import AnthropicOutlineGenerator

__all__ = [
    'BaseOutlineGenerator',
    'GeneratorFactory',
    'OpenAIOutlineGenerator',
    'AnthropicOutlineGenerator',
]
