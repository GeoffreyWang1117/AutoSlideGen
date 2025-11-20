"""
Anthropic Claude-based outline generator.
"""

from typing import Dict, Any
import logging

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import BaseOutlineGenerator

logger = logging.getLogger(__name__)


class AnthropicOutlineGenerator(BaseOutlineGenerator):
    """Outline generator using Anthropic Claude API."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Anthropic generator.

        Args:
            config: Anthropic configuration

        Raises:
            ImportError: If anthropic package not installed
            ValueError: If API key not provided
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package is required for Anthropic generator. "
                "Install with: pip install anthropic"
            )

        super().__init__(config)

        api_key = config.get('api_key')
        if not api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = config.get('model_name', 'claude-3-5-sonnet-20241022')
        self.logger.info(f"Initialized Anthropic generator with model: {self.model}")

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Call Anthropic API.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature parameter

        Returns:
            LLM response text
        """
        max_tokens = self.config.get('max_tokens', 4096)

        self.logger.debug(f"Calling Anthropic API with model {self.model}")

        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.content[0].text
            self.logger.debug(f"Received response with {len(content)} characters")

            return content

        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
