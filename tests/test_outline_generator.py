"""
Tests for outline generator module.
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch

from autoslidegen.outline_generator.factory import GeneratorFactory
from autoslidegen.outline_generator.base import BaseOutlineGenerator
from autoslidegen.parser.models import GenerationRequest, PresentationOutline


class MockOutlineGenerator(BaseOutlineGenerator):
    """Mock generator for testing."""

    def __init__(self, config, response_text=None):
        super().__init__(config)
        self.response_text = response_text
        self.call_count = 0

    async def _call_llm(self, system_prompt, user_prompt, temperature=0.7):
        """Mock LLM call."""
        self.call_count += 1
        if self.response_text:
            return self.response_text
        return self._get_valid_response()

    def _get_valid_response(self):
        """Return a valid JSON response."""
        return json.dumps({
            "metadata": {
                "topic": "Test Topic",
                "audience": "Test Audience",
                "purpose": "Test Purpose",
                "language": "zh"
            },
            "slides": [
                {
                    "slide_number": 1,
                    "title": "标题页",
                    "slide_type": "title",
                    "bullet_points": [
                        {"text": "副标题", "level": 1}
                    ]
                },
                {
                    "slide_number": 2,
                    "title": "内容页",
                    "slide_type": "content",
                    "bullet_points": [
                        {"text": "要点1", "level": 1},
                        {"text": "要点2", "level": 1},
                        {"text": "要点3", "level": 1}
                    ]
                }
            ]
        })


class TestGeneratorFactory:
    """Tests for GeneratorFactory."""

    def test_list_providers(self):
        """Test listing available providers."""
        providers = GeneratorFactory.list_providers()
        assert 'openai' in providers
        assert 'anthropic' in providers
        assert isinstance(providers, list)

    def test_create_openai_generator(self):
        """Test creating OpenAI generator."""
        config = {'api_key': 'test-key', 'model': 'gpt-4'}
        generator = GeneratorFactory.create_generator('openai', config)
        assert generator is not None
        assert generator.config == config

    def test_create_anthropic_generator(self):
        """Test creating Anthropic generator."""
        config = {'api_key': 'test-key', 'model': 'claude-3-5-sonnet-20241022'}
        generator = GeneratorFactory.create_generator('anthropic', config)
        assert generator is not None
        assert generator.config == config

    def test_unsupported_provider_raises_error(self):
        """Test that unsupported provider raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            GeneratorFactory.create_generator('unsupported', {})
        assert 'Unsupported provider' in str(exc_info.value)

    def test_register_custom_generator(self):
        """Test registering a custom generator."""
        GeneratorFactory.register_generator('mock', MockOutlineGenerator)
        assert 'mock' in GeneratorFactory.list_providers()

        # Test creating the custom generator
        generator = GeneratorFactory.create_generator('mock', {'test': 'config'})
        assert isinstance(generator, MockOutlineGenerator)

    def test_register_invalid_generator_raises_error(self):
        """Test that registering non-BaseOutlineGenerator raises TypeError."""
        class InvalidGenerator:
            pass

        with pytest.raises(TypeError):
            GeneratorFactory.register_generator('invalid', InvalidGenerator)


class TestBaseOutlineGenerator:
    """Tests for BaseOutlineGenerator functionality."""

    @pytest.fixture
    def generator(self):
        """Create a mock generator instance."""
        config = {'temperature': 0.7}
        return MockOutlineGenerator(config)

    @pytest.fixture
    def generation_request(self):
        """Create a generation request."""
        return GenerationRequest(
            topic="人工智能技术",
            audience="技术人员",
            purpose="介绍AI基础",
            language="zh",
            num_slides=10,
            bullets_per_slide=4
        )

    @pytest.mark.asyncio
    async def test_generate_outline_success(self, generator, generation_request):
        """Test successful outline generation."""
        outline = await generator.generate_outline(generation_request)

        assert isinstance(outline, PresentationOutline)
        assert len(outline.slides) == 2
        assert outline.slides[0].slide_type == "title"
        assert outline.metadata.topic == "Test Topic"
        assert generator.call_count == 1

    @pytest.mark.asyncio
    async def test_generate_outline_retry_on_invalid_response(self, generation_request):
        """Test retry logic when LLM returns invalid response."""
        config = {'temperature': 0.7}

        # Create generator that fails first then succeeds
        call_count = 0

        async def mock_call_llm(self, system_prompt, user_prompt, temperature=0.7):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "Invalid JSON response"
            else:
                return MockOutlineGenerator(config)._get_valid_response()

        generator = MockOutlineGenerator(config)
        generator._call_llm = lambda sp, up, t=0.7: mock_call_llm(generator, sp, up, t)

        outline = await generator.generate_outline(generation_request)

        assert isinstance(outline, PresentationOutline)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_generate_outline_fails_after_max_retries(self, generation_request):
        """Test that generation fails after max retries."""
        config = {'temperature': 0.7}
        generator = MockOutlineGenerator(config, response_text="Always invalid")

        with pytest.raises(Exception) as exc_info:
            await generator.generate_outline(generation_request, max_retries=3)

        assert "Failed to generate valid outline" in str(exc_info.value)
        assert generator.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_outline_custom_max_retries(self, generator, generation_request):
        """Test using custom max_retries parameter."""
        outline = await generator.generate_outline(generation_request, max_retries=1)

        assert isinstance(outline, PresentationOutline)
        assert generator.call_count == 1

    @pytest.mark.asyncio
    async def test_temperature_increases_on_retry(self, generation_request):
        """Test that temperature increases on retry attempts."""
        config = {'temperature': 0.5}
        temperatures = []

        async def mock_call_llm(self, system_prompt, user_prompt, temperature=0.7):
            temperatures.append(temperature)
            if len(temperatures) == 1:
                return "Invalid response"
            else:
                return MockOutlineGenerator(config)._get_valid_response()

        generator = MockOutlineGenerator(config)
        generator._call_llm = lambda sp, up, t=0.7: mock_call_llm(generator, sp, up, t)

        await generator.generate_outline(generation_request)

        assert len(temperatures) == 2
        assert temperatures[1] > temperatures[0]
        assert temperatures[1] <= 1.0

    def test_generate_outline_sync(self, generator, generation_request):
        """Test synchronous wrapper for generate_outline."""
        outline = generator.generate_outline_sync(generation_request)

        assert isinstance(outline, PresentationOutline)
        assert len(outline.slides) == 2

    @pytest.mark.asyncio
    async def test_generate_outline_with_additional_requirements(self, generator):
        """Test generation with additional requirements."""
        request = GenerationRequest(
            topic="云计算",
            audience="IT经理",
            purpose="技术选型",
            language="zh",
            num_slides=8,
            additional_requirements="重点关注成本效益分析"
        )

        outline = await generator.generate_outline(request)

        assert isinstance(outline, PresentationOutline)

    @pytest.mark.asyncio
    async def test_generate_outline_different_languages(self, generator):
        """Test generation with different languages."""
        languages = ['zh', 'en', 'ja', 'es']

        for lang in languages:
            request = GenerationRequest(
                topic="Test Topic",
                audience="Test Audience",
                purpose="Test Purpose",
                language=lang,
                num_slides=6
            )

            outline = await generator.generate_outline(request)
            assert isinstance(outline, PresentationOutline)


class TestOpenAIGenerator:
    """Tests for OpenAI-specific generator."""

    @pytest.mark.asyncio
    @patch('autoslidegen.outline_generator.openai_generator.AsyncOpenAI')
    async def test_openai_call_llm(self, mock_openai_class):
        """Test OpenAI LLM call."""
        from autoslidegen.outline_generator.openai_generator import OpenAIOutlineGenerator

        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        mock_openai_class.return_value = mock_client

        config = {'api_key': 'test-key', 'model': 'gpt-4'}
        generator = OpenAIOutlineGenerator(config)

        response = await generator._call_llm("system", "user", 0.7)

        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()


class TestAnthropicGenerator:
    """Tests for Anthropic-specific generator."""

    @pytest.mark.asyncio
    @patch('autoslidegen.outline_generator.anthropic_generator.AsyncAnthropic')
    async def test_anthropic_call_llm(self, mock_anthropic_class):
        """Test Anthropic LLM call."""
        from autoslidegen.outline_generator.anthropic_generator import AnthropicOutlineGenerator

        # Mock the Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"

        mock_client = Mock()
        mock_client.messages = Mock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        mock_anthropic_class.return_value = mock_client

        config = {'api_key': 'test-key', 'model': 'claude-3-5-sonnet-20241022'}
        generator = AnthropicOutlineGenerator(config)

        response = await generator._call_llm("system", "user", 0.7)

        assert response == "Test response"
        mock_client.messages.create.assert_called_once()


class TestErrorHandling:
    """Tests for error handling in generators."""

    @pytest.mark.asyncio
    async def test_llm_api_error_triggers_retry(self):
        """Test that LLM API errors trigger retry."""
        config = {'temperature': 0.7}
        call_count = 0

        async def mock_call_llm_with_error(self, system_prompt, user_prompt, temperature=0.7):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("API Error")
            else:
                return MockOutlineGenerator(config)._get_valid_response()

        generator = MockOutlineGenerator(config)
        generator._call_llm = lambda sp, up, t=0.7: mock_call_llm_with_error(generator, sp, up, t)

        request = GenerationRequest(
            topic="Test",
            audience="Test",
            purpose="Test",
            num_slides=6
        )

        outline = await generator.generate_outline(request)

        assert isinstance(outline, PresentationOutline)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_persistent_errors_raise_exception(self):
        """Test that persistent errors raise exception after retries."""
        config = {'temperature': 0.7}

        async def mock_call_llm_always_fails(self, system_prompt, user_prompt, temperature=0.7):
            raise Exception("Persistent API Error")

        generator = MockOutlineGenerator(config)
        generator._call_llm = lambda sp, up, t=0.7: mock_call_llm_always_fails(generator, sp, up, t)

        request = GenerationRequest(
            topic="Test",
            audience="Test",
            purpose="Test",
            num_slides=6
        )

        with pytest.raises(Exception) as exc_info:
            await generator.generate_outline(request, max_retries=2)

        assert "Failed to generate valid outline" in str(exc_info.value)
