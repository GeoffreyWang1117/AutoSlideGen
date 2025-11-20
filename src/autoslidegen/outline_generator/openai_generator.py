"""
OpenAI-based outline generator.
"""

from typing import Dict, Any
import logging

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseOutlineGenerator

logger = logging.getLogger(__name__)


class OpenAIOutlineGenerator(BaseOutlineGenerator):
    """Outline generator using OpenAI API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI generator.

        Args:
            config: OpenAI configuration

        Raises:
            ImportError: If openai package not installed
            ValueError: If API key not provided
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required for OpenAI generator. "
                "Install with: pip install openai"
            )

        super().__init__(config)

        api_key = config.get('api_key')
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get('model_name', 'gpt-4-turbo-preview')
        self.logger.info(f"Initialized OpenAI generator with model: {self.model}")

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Call OpenAI API.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature parameter

        Returns:
            LLM response text
        """
        max_tokens = self.config.get('max_tokens', 4096)

        self.logger.debug(f"Calling OpenAI API with model {self.model}")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )

            content = response.choices[0].message.content
            self.logger.debug(f"Received response with {len(content)} characters")

            return content

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
