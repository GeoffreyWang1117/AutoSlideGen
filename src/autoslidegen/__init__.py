"""
AutoSlideGen - Automated PowerPoint Outline Generator

A tool for automatically generating presentation outlines using LLM and
converting them to standard PPTX files.
"""

__version__ = "0.1.0"
__author__ = "AutoSlideGen Team"

from .main import AutoSlideGen
from .parser.models import (
    PresentationOutline,
    Slide,
    BulletPoint,
    PresentationMetadata,
    GenerationRequest
)
from .outline_generator.factory import GeneratorFactory
from .ppt_builder.builder import PPTBuilder

__all__ = [
    'AutoSlideGen',
    'PresentationOutline',
    'Slide',
    'BulletPoint',
    'PresentationMetadata',
    'GenerationRequest',
    'GeneratorFactory',
    'PPTBuilder',
]
