"""
Extensions module for AutoSlideGen.
Contains advanced features like speaker notes, images, charts, RAG, and multi-agent.
"""

from .speaker_notes import SpeakerNotesGenerator
from .image_search import ImageSearcher, ImageInserter, create_image_searcher
from .chart_generator import ChartGenerator, SmartChartGenerator
from .template_manager import TemplateManager, CustomizableTemplateBuilder
from .rag_enhancer import DocumentStore, RAGEnhancer, SimpleRAGGenerator
from .multi_agent import (
    MultiAgentOrchestrator,
    AgentRole,
    ContentStrategistAgent,
    WriterAgent,
    DesignerAgent,
    ReviewerAgent
)

__all__ = [
    # Speaker notes
    'SpeakerNotesGenerator',

    # Image search
    'ImageSearcher',
    'ImageInserter',
    'create_image_searcher',

    # Charts
    'ChartGenerator',
    'SmartChartGenerator',

    # Templates
    'TemplateManager',
    'CustomizableTemplateBuilder',

    # RAG
    'DocumentStore',
    'RAGEnhancer',
    'SimpleRAGGenerator',

    # Multi-agent
    'MultiAgentOrchestrator',
    'AgentRole',
    'ContentStrategistAgent',
    'WriterAgent',
    'DesignerAgent',
    'ReviewerAgent',
]
