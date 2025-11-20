"""
Multi-agent architecture for specialized presentation generation tasks.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum

from ..parser.models import PresentationOutline, Slide, BulletPoint

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the system."""

    CONTENT_STRATEGIST = "content_strategist"  # Plans content structure
    WRITER = "writer"  # Generates slide content
    DESIGNER = "designer"  # Suggests visual elements
    REVIEWER = "reviewer"  # Reviews and refines content
    COORDINATOR = "coordinator"  # Coordinates agent activities


class Agent:
    """Base class for specialized agents."""

    def __init__(self, role: AgentRole, llm_generator=None):
        """
        Initialize agent.

        Args:
            role: Agent's role
            llm_generator: LLM generator instance
        """
        self.role = role
        self.llm_generator = llm_generator
        self.logger = logging.getLogger(f"{self.__class__.__name__}:{role.value}")

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task.

        Args:
            task: Task dictionary

        Returns:
            Result dictionary
        """
        raise NotImplementedError("Subclasses must implement process method")


class ContentStrategistAgent(Agent):
    """Agent responsible for planning content structure."""

    def __init__(self, llm_generator=None):
        super().__init__(AgentRole.CONTENT_STRATEGIST, llm_generator)

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan presentation structure.

        Args:
            task: Contains topic, audience, purpose, num_slides

        Returns:
            Structural plan with sections and flow
        """
        topic = task.get('topic')
        audience = task.get('audience')
        purpose = task.get('purpose')
        num_slides = task.get('num_slides', 10)

        self.logger.info(f"Planning structure for: {topic}")

        # Create high-level structure
        structure = {
            'sections': [],
            'flow': 'linear',
            'total_slides': num_slides
        }

        # Simple structure planning
        structure['sections'] = [
            {'name': 'Introduction', 'slides': 1},
            {'name': 'Main Content', 'slides': num_slides - 2},
            {'name': 'Conclusion', 'slides': 1}
        ]

        return {
            'status': 'success',
            'structure': structure
        }


class WriterAgent(Agent):
    """Agent responsible for generating slide content."""

    def __init__(self, llm_generator=None):
        super().__init__(AgentRole.WRITER, llm_generator)

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate slide content.

        Args:
            task: Contains slide_info, context

        Returns:
            Generated slide content
        """
        slide_info = task.get('slide_info', {})
        title = slide_info.get('title', 'Slide Title')

        self.logger.info(f"Writing content for slide: {title}")

        # Generate bullet points (simplified)
        bullets = [
            BulletPoint(text=f"Key point about {title}", level=1),
            BulletPoint(text="Supporting detail", level=2),
            BulletPoint(text="Another important aspect", level=1),
        ]

        return {
            'status': 'success',
            'bullets': bullets
        }


class DesignerAgent(Agent):
    """Agent responsible for visual design suggestions."""

    def __init__(self, llm_generator=None):
        super().__init__(AgentRole.DESIGNER, llm_generator)

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest visual elements for slides.

        Args:
            task: Contains slide content

        Returns:
            Design suggestions
        """
        slide_title = task.get('slide_title', '')

        self.logger.info(f"Designing visuals for: {slide_title}")

        suggestions = {
            'image_keywords': [],
            'chart_type': None,
            'color_scheme': 'professional'
        }

        # Simple keyword analysis for images
        title_lower = slide_title.lower()

        if any(word in title_lower for word in ['process', 'flow', 'steps']):
            suggestions['chart_type'] = 'flowchart'
            suggestions['image_keywords'] = ['process', 'workflow']

        elif any(word in title_lower for word in ['growth', 'trend', 'over time']):
            suggestions['chart_type'] = 'line'
            suggestions['image_keywords'] = ['growth', 'chart']

        elif any(word in title_lower for word in ['comparison', 'vs', 'versus']):
            suggestions['chart_type'] = 'bar'
            suggestions['image_keywords'] = ['comparison', 'analysis']

        return {
            'status': 'success',
            'suggestions': suggestions
        }


class ReviewerAgent(Agent):
    """Agent responsible for reviewing and refining content."""

    def __init__(self, llm_generator=None):
        super().__init__(AgentRole.REVIEWER, llm_generator)

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and suggest improvements.

        Args:
            task: Contains outline to review

        Returns:
            Review results and suggestions
        """
        outline = task.get('outline')

        self.logger.info("Reviewing presentation outline")

        feedback = {
            'issues': [],
            'suggestions': [],
            'quality_score': 0.0
        }

        if not outline:
            feedback['issues'].append("No outline provided")
            return {'status': 'error', 'feedback': feedback}

        # Check slide count
        num_slides = len(outline.slides) if hasattr(outline, 'slides') else 0

        if num_slides < 5:
            feedback['issues'].append("Presentation is too short")
        elif num_slides > 25:
            feedback['issues'].append("Presentation is too long")

        # Quality scoring (simplified)
        feedback['quality_score'] = min(100, num_slides * 8)

        if not feedback['issues']:
            feedback['suggestions'].append("Content looks good overall")

        return {
            'status': 'success',
            'feedback': feedback
        }


class CoordinatorAgent(Agent):
    """Coordinator agent that manages other agents."""

    def __init__(self, llm_generator=None):
        super().__init__(AgentRole.COORDINATOR, llm_generator)

        # Initialize sub-agents
        self.agents = {
            AgentRole.CONTENT_STRATEGIST: ContentStrategistAgent(llm_generator),
            AgentRole.WRITER: WriterAgent(llm_generator),
            AgentRole.DESIGNER: DesignerAgent(llm_generator),
            AgentRole.REVIEWER: ReviewerAgent(llm_generator)
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate multi-agent workflow.

        Args:
            task: Master task specification

        Returns:
            Coordinated results
        """
        self.logger.info("Coordinating multi-agent workflow")

        workflow_results = {}

        # Step 1: Content Strategy
        strategy_task = {
            'topic': task.get('topic'),
            'audience': task.get('audience'),
            'purpose': task.get('purpose'),
            'num_slides': task.get('num_slides', 10)
        }

        strategy_result = await self.agents[AgentRole.CONTENT_STRATEGIST].process(
            strategy_task
        )
        workflow_results['strategy'] = strategy_result

        # Step 2: Content Writing (would iterate per slide in real implementation)
        writer_task = {
            'slide_info': {'title': task.get('topic')},
            'context': strategy_result.get('structure')
        }

        writer_result = await self.agents[AgentRole.WRITER].process(writer_task)
        workflow_results['content'] = writer_result

        # Step 3: Design Suggestions
        designer_task = {
            'slide_title': task.get('topic')
        }

        designer_result = await self.agents[AgentRole.DESIGNER].process(designer_task)
        workflow_results['design'] = designer_result

        return {
            'status': 'success',
            'workflow_results': workflow_results
        }


class MultiAgentOrchestrator:
    """Orchestrates multi-agent presentation generation."""

    def __init__(self, llm_generator=None):
        """
        Initialize orchestrator.

        Args:
            llm_generator: LLM generator instance
        """
        self.coordinator = CoordinatorAgent(llm_generator)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_with_agents(
        self,
        topic: str,
        audience: str,
        purpose: str,
        num_slides: int = 10
    ) -> Dict[str, Any]:
        """
        Generate presentation using multi-agent approach.

        Args:
            topic: Presentation topic
            audience: Target audience
            purpose: Presentation purpose
            num_slides: Number of slides

        Returns:
            Generation results from all agents
        """
        self.logger.info("Starting multi-agent generation")

        task = {
            'topic': topic,
            'audience': audience,
            'purpose': purpose,
            'num_slides': num_slides
        }

        results = await self.coordinator.process(task)

        self.logger.info("Multi-agent generation completed")

        return results

    def generate_with_agents_sync(
        self,
        topic: str,
        audience: str,
        purpose: str,
        num_slides: int = 10
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for generate_with_agents.

        Args:
            topic: Presentation topic
            audience: Target audience
            purpose: Presentation purpose
            num_slides: Number of slides

        Returns:
            Generation results
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.generate_with_agents(topic, audience, purpose, num_slides)
        )
