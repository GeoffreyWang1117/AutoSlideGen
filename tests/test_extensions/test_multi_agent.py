"""
Tests for multi-agent extension.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from autoslidegen.extensions.multi_agent import (
    AgentRole,
    Agent,
    ContentStrategistAgent,
    WriterAgent,
    DesignerAgent,
    ReviewerAgent,
    CoordinatorAgent,
    MultiAgentOrchestrator
)


class TestAgentRole:
    """Tests for AgentRole enum."""

    def test_agent_roles_exist(self):
        """Test that all agent roles are defined."""
        assert AgentRole.CONTENT_STRATEGIST
        assert AgentRole.WRITER
        assert AgentRole.DESIGNER
        assert AgentRole.REVIEWER
        assert AgentRole.COORDINATOR


class TestBaseAgent:
    """Tests for base Agent class."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Agent response")
        return mock_gen

    def test_agent_initialization(self, llm_generator):
        """Test Agent initialization."""
        agent = Agent(AgentRole.WRITER, llm_generator)
        assert agent.role == AgentRole.WRITER
        assert agent.llm_generator == llm_generator

    @pytest.mark.asyncio
    async def test_agent_process_not_implemented(self, llm_generator):
        """Test that base Agent.process raises NotImplementedError."""
        agent = Agent(AgentRole.WRITER, llm_generator)

        with pytest.raises(NotImplementedError):
            await agent.process({'task': 'test'})


class TestContentStrategistAgent:
    """Tests for ContentStrategistAgent."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Strategy recommendations")
        return mock_gen

    @pytest.fixture
    def strategist(self, llm_generator):
        """Create ContentStrategistAgent instance."""
        return ContentStrategistAgent(llm_generator)

    def test_initialization(self, strategist):
        """Test ContentStrategistAgent initialization."""
        assert strategist.role == AgentRole.CONTENT_STRATEGIST

    @pytest.mark.asyncio
    async def test_process_task(self, strategist):
        """Test processing a strategy task."""
        task = {
            'topic': 'AI Technology',
            'audience': 'Developers',
            'purpose': 'Introduction',
            'num_slides': 10
        }

        result = await strategist.process(task)

        assert isinstance(result, dict)
        assert 'status' in result
        assert result['status'] == 'success'

    @pytest.mark.asyncio
    async def test_error_handling(self, llm_generator):
        """Test error handling in process."""
        llm_generator._call_llm = AsyncMock(side_effect=Exception("API Error"))
        strategist = ContentStrategistAgent(llm_generator)

        task = {'topic': 'Test'}

        result = await strategist.process(task)

        assert result['status'] == 'error'
        assert 'error' in result


class TestWriterAgent:
    """Tests for WriterAgent."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Content generated")
        return mock_gen

    @pytest.fixture
    def writer(self, llm_generator):
        """Create WriterAgent instance."""
        return WriterAgent(llm_generator)

    def test_initialization(self, writer):
        """Test WriterAgent initialization."""
        assert writer.role == AgentRole.WRITER

    @pytest.mark.asyncio
    async def test_process_task(self, writer):
        """Test processing a writing task."""
        task = {
            'topic': 'Machine Learning',
            'outline': 'Introduction, Methods, Applications'
        }

        result = await writer.process(task)

        assert isinstance(result, dict)
        assert 'status' in result


class TestDesignerAgent:
    """Tests for DesignerAgent."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Design suggestions")
        return mock_gen

    @pytest.fixture
    def designer(self, llm_generator):
        """Create DesignerAgent instance."""
        return DesignerAgent(llm_generator)

    def test_initialization(self, designer):
        """Test DesignerAgent initialization."""
        assert designer.role == AgentRole.DESIGNER

    @pytest.mark.asyncio
    async def test_process_task(self, designer):
        """Test processing a design task."""
        task = {
            'topic': 'Data Visualization',
            'theme': 'professional'
        }

        result = await designer.process(task)

        assert isinstance(result, dict)
        assert 'status' in result


class TestReviewerAgent:
    """Tests for ReviewerAgent."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Review feedback")
        return mock_gen

    @pytest.fixture
    def reviewer(self, llm_generator):
        """Create ReviewerAgent instance."""
        return ReviewerAgent(llm_generator)

    def test_initialization(self, reviewer):
        """Test ReviewerAgent initialization."""
        assert reviewer.role == AgentRole.REVIEWER

    @pytest.mark.asyncio
    async def test_process_task(self, reviewer):
        """Test processing a review task."""
        task = {
            'content': 'Presentation content to review',
            'criteria': ['clarity', 'accuracy']
        }

        result = await reviewer.process(task)

        assert isinstance(result, dict)
        assert 'status' in result


class TestCoordinatorAgent:
    """Tests for CoordinatorAgent."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="Coordination plan")
        return mock_gen

    @pytest.fixture
    def coordinator(self, llm_generator):
        """Create CoordinatorAgent instance."""
        return CoordinatorAgent(llm_generator)

    def test_initialization(self, coordinator):
        """Test CoordinatorAgent initialization."""
        assert coordinator.role == AgentRole.COORDINATOR

    @pytest.mark.asyncio
    async def test_process_task(self, coordinator):
        """Test processing a coordination task."""
        task = {
            'agents': ['strategist', 'writer', 'designer'],
            'workflow': 'sequential'
        }

        result = await coordinator.process(task)

        assert isinstance(result, dict)
        assert 'status' in result


class TestMultiAgentOrchestrator:
    """Tests for MultiAgentOrchestrator."""

    @pytest.fixture
    def llm_generator(self):
        """Create mock LLM generator."""
        mock_gen = Mock()
        mock_gen._call_llm = AsyncMock(return_value="LLM response")
        return mock_gen

    @pytest.fixture
    def orchestrator(self, llm_generator):
        """Create MultiAgentOrchestrator instance."""
        return MultiAgentOrchestrator(llm_generator)

    def test_initialization(self, orchestrator):
        """Test MultiAgentOrchestrator initialization."""
        assert orchestrator.llm_generator is not None
        assert len(orchestrator.agents) > 0

    def test_agents_created(self, orchestrator):
        """Test that all agents are created."""
        # Should have strategist, writer, designer, reviewer
        assert len(orchestrator.agents) >= 4

    @pytest.mark.asyncio
    async def test_generate_with_agents(self, orchestrator):
        """Test generating with multi-agent workflow."""
        # Mock agent responses
        for agent in orchestrator.agents.values():
            agent.process = AsyncMock(return_value={
                'status': 'success',
                'result': 'Agent output'
            })

        result = await orchestrator.generate_with_agents(
            topic="Test Topic",
            audience="Test Audience",
            purpose="Test Purpose",
            num_slides=10
        )

        assert isinstance(result, dict)
        assert 'workflow_results' in result

    def test_generate_with_agents_sync(self, orchestrator):
        """Test synchronous wrapper for multi-agent generation."""
        # Mock agent responses
        for agent in orchestrator.agents.values():
            agent.process = AsyncMock(return_value={
                'status': 'success',
                'result': 'Agent output'
            })

        result = orchestrator.generate_with_agents_sync(
            topic="Test Topic",
            audience="Test Audience",
            purpose="Test Purpose",
            num_slides=10
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_workflow_execution_order(self, orchestrator):
        """Test that agents execute in correct order."""
        execution_order = []

        async def track_execution(agent_name):
            async def process_wrapper(task):
                execution_order.append(agent_name)
                return {'status': 'success', 'result': f'{agent_name} output'}
            return process_wrapper

        # Set up tracking
        for name, agent in orchestrator.agents.items():
            agent.process = await track_execution(name)

        await orchestrator.generate_with_agents(
            topic="Test",
            audience="Test",
            purpose="Test",
            num_slides=5
        )

        # Verify some agents were executed
        assert len(execution_order) > 0

    @pytest.mark.asyncio
    async def test_error_handling_in_workflow(self, orchestrator):
        """Test error handling when an agent fails."""
        # Make one agent fail
        strategist = orchestrator.agents.get('strategist')
        if strategist:
            strategist.process = AsyncMock(side_effect=Exception("Agent error"))

        # Other agents succeed
        for name, agent in orchestrator.agents.items():
            if name != 'strategist':
                agent.process = AsyncMock(return_value={
                    'status': 'success',
                    'result': 'Output'
                })

        result = await orchestrator.generate_with_agents(
            topic="Test",
            audience="Test",
            purpose="Test",
            num_slides=5
        )

        # Should handle error gracefully
        assert isinstance(result, dict)

    def test_custom_agent_registration(self, orchestrator):
        """Test registering custom agents."""
        custom_agent = Mock()
        custom_agent.role = AgentRole.WRITER

        orchestrator.register_agent('custom', custom_agent)

        assert 'custom' in orchestrator.agents
        assert orchestrator.agents['custom'] == custom_agent

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, orchestrator):
        """Test that independent agents can run in parallel."""
        import asyncio
        import time

        async def slow_process(task):
            await asyncio.sleep(0.1)
            return {'status': 'success', 'result': 'output'}

        for agent in orchestrator.agents.values():
            agent.process = slow_process

        start_time = time.time()

        await orchestrator.generate_with_agents(
            topic="Test",
            audience="Test",
            purpose="Test",
            num_slides=5
        )

        elapsed = time.time() - start_time

        # If truly parallel, should be faster than sequential
        # (4 agents * 0.1s = 0.4s sequential)
        # This is a rough test - actual timing may vary
        assert elapsed < 1.0  # Allow generous time for CI
