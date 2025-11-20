"""
Base class for LLM-based outline generators.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

from ..parser.models import GenerationRequest, PresentationOutline
from ..parser.validator import OutlineValidator
from .prompts import get_user_prompt, get_refinement_prompt

logger = logging.getLogger(__name__)


class BaseOutlineGenerator(ABC):
    """Abstract base class for outline generators."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize generator with configuration.

        Args:
            config: LLM configuration dictionary
        """
        self.config = config
        self.validator = OutlineValidator()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_retries = 3

    @abstractmethod
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Call the LLM API.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature parameter

        Returns:
            LLM response text
        """
        pass

    async def generate_outline(
        self,
        request: GenerationRequest,
        max_retries: Optional[int] = None
    ) -> PresentationOutline:
        """
        Generate presentation outline from request.

        Args:
            request: Generation request parameters
            max_retries: Maximum retry attempts (uses default if None)

        Returns:
            Validated PresentationOutline

        Raises:
            Exception: If generation fails after all retries
        """
        if max_retries is None:
            max_retries = self.max_retries

        # Import prompts
        from .prompts import SYSTEM_PROMPT

        # Generate initial prompt
        user_prompt = get_user_prompt(
            topic=request.topic,
            audience=request.audience,
            purpose=request.purpose,
            language=request.language,
            num_slides=request.num_slides,
            bullets_per_slide=request.bullets_per_slide,
            additional_requirements=request.additional_requirements or ""
        )

        last_error = None
        temperature = self.config.get('temperature', 0.7)

        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"Generating outline (attempt {attempt + 1}/{max_retries})..."
                )

                # Call LLM
                response = await self._call_llm(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    temperature=temperature
                )

                self.logger.debug(f"LLM response: {response[:200]}...")

                # Validate response
                outline, error = self.validator.validate_from_text(response)

                if outline:
                    self.logger.info(
                        f"Successfully generated outline with {len(outline.slides)} slides"
                    )
                    return outline

                # Validation failed, prepare refinement prompt
                last_error = error
                self.logger.warning(f"Validation failed: {error}")

                # Try to refine on next iteration
                if attempt < max_retries - 1:
                    user_prompt = get_refinement_prompt(error)
                    # Slightly increase temperature for retry
                    temperature = min(temperature + 0.1, 1.0)

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Generation attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    # Retry with same prompt
                    continue
                else:
                    break

        # All attempts failed
        error_msg = f"Failed to generate valid outline after {max_retries} attempts. Last error: {last_error}"
        self.logger.error(error_msg)
        raise Exception(error_msg)

    def generate_outline_sync(self, request: GenerationRequest) -> PresentationOutline:
        """
        Synchronous wrapper for generate_outline.

        Args:
            request: Generation request parameters

        Returns:
            Validated PresentationOutline
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.generate_outline(request))
