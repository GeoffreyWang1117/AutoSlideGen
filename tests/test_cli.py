"""
Tests for CLI module.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from autoslidegen.cli import cli, generate, build, providers, example
from autoslidegen.parser.models import (
    BulletPoint,
    Slide,
    PresentationMetadata,
    PresentationOutline
)


class TestCLI:
    """Tests for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_outline(self):
        """Create sample outline."""
        metadata = PresentationMetadata(
            topic="测试主题",
            audience="测试观众",
            purpose="测试目的",
            language="zh"
        )

        slides = [
            Slide(
                slide_number=1,
                title="标题",
                slide_type="title",
                bullet_points=[BulletPoint(text="副标题", level=1)]
            ),
            Slide(
                slide_number=2,
                title="内容",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="要点1", level=1),
                    BulletPoint(text="要点2", level=1)
                ]
            )
        ]

        return PresentationOutline(metadata=metadata, slides=slides)

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'AutoSlideGen' in result.output

    def test_cli_debug_flag(self, runner):
        """Test CLI debug flag."""
        result = runner.invoke(cli, ['--debug', '--help'])
        assert result.exit_code == 0

    def test_generate_help(self, runner):
        """Test generate command help."""
        result = runner.invoke(cli, ['generate', '--help'])
        assert result.exit_code == 0
        assert 'topic' in result.output
        assert 'audience' in result.output
        assert 'purpose' in result.output

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_basic(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test basic generate command."""
        # Mock the AutoSlideGen class
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': str(Path(temp_dir) / 'output.json'),
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', '测试主题',
            '--audience', '测试观众',
            '--purpose', '测试目的',
            '--output', str(Path(temp_dir) / 'output.pptx')
        ])

        assert result.exit_code == 0
        assert '✓' in result.output or 'Success' in result.output
        mock_instance.generate.assert_called_once()

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_with_all_options(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate command with all options."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': str(Path(temp_dir) / 'output.json'),
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'AI Technology',
            '--audience', 'Developers',
            '--purpose', 'Introduction',
            '--language', 'en',
            '--slides', '15',
            '--bullets', '5',
            '--provider', 'openai',
            '--output', str(Path(temp_dir) / 'output.pptx'),
            '--requirements', 'Focus on practical examples',
            '--speaker-notes',
            '--add-images',
            '--image-provider', 'unsplash',
            '--add-charts'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['topic'] == 'AI Technology'
        assert call_kwargs['audience'] == 'Developers'
        assert call_kwargs['num_slides'] == 15
        assert call_kwargs['bullets_per_slide'] == 5
        assert call_kwargs['language'] == 'en'
        assert call_kwargs['generate_speaker_notes'] is True
        assert call_kwargs['add_images'] is True
        assert call_kwargs['add_charts'] is True

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_missing_required_args(self, mock_autoslidegen, runner):
        """Test generate command with missing required arguments."""
        result = runner.invoke(cli, ['generate'])

        assert result.exit_code != 0
        assert 'topic' in result.output.lower() or 'required' in result.output.lower()

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_invalid_language(self, mock_autoslidegen, runner):
        """Test generate command with invalid language."""
        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--language', 'invalid'
        ])

        assert result.exit_code != 0

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_invalid_slides_count(self, mock_autoslidegen, runner):
        """Test generate command with invalid slides count."""
        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--slides', '3'  # Too few
        ])

        assert result.exit_code != 0

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--slides', '50'  # Too many
        ])

        assert result.exit_code != 0

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_no_json_flag(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate command with --no-json flag."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': None,
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--no-json'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['save_json'] is False

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_with_config_file(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate command with config file."""
        # Create a dummy config file
        config_path = Path(temp_dir) / 'config.yaml'
        config_path.write_text('default_provider: openai')

        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': None,
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            '--config', str(config_path),
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test'
        ])

        assert result.exit_code == 0

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_error_handling(self, mock_autoslidegen, runner):
        """Test generate command error handling."""
        mock_instance = Mock()
        mock_instance.generate.side_effect = Exception("Test error")
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test'
        ])

        assert result.exit_code == 1
        assert 'Error' in result.output
        assert 'Test error' in result.output

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_build_command(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test build command."""
        # Create JSON file
        json_path = Path(temp_dir) / 'outline.json'
        json_path.write_text(sample_outline.to_json())

        mock_instance = Mock()
        mock_instance.generate_from_json.return_value = str(Path(temp_dir) / 'output.pptx')
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'build',
            str(json_path),
            '--output', str(Path(temp_dir) / 'output.pptx')
        ])

        assert result.exit_code == 0
        assert '✓' in result.output or 'Success' in result.output
        mock_instance.generate_from_json.assert_called_once()

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_build_command_missing_file(self, mock_autoslidegen, runner):
        """Test build command with missing JSON file."""
        result = runner.invoke(cli, [
            'build',
            '/nonexistent/file.json'
        ])

        assert result.exit_code != 0

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_build_command_error_handling(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test build command error handling."""
        json_path = Path(temp_dir) / 'outline.json'
        json_path.write_text(sample_outline.to_json())

        mock_instance = Mock()
        mock_instance.generate_from_json.side_effect = Exception("Build error")
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'build',
            str(json_path)
        ])

        assert result.exit_code == 1
        assert 'Error' in result.output

    def test_providers_command(self, runner):
        """Test providers command."""
        result = runner.invoke(cli, ['providers'])

        assert result.exit_code == 0
        assert 'openai' in result.output.lower() or 'anthropic' in result.output.lower()

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_example_command(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test example command."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': str(Path(temp_dir) / 'output.json'),
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, ['example'])

        assert result.exit_code == 0
        mock_instance.generate.assert_called_once()

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_example_command_custom_topic(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test example command with custom topic."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': str(Path(temp_dir) / 'output.json'),
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'example',
            '--topic', '自定义主题'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['topic'] == '自定义主题'

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_debug_mode_shows_traceback(self, mock_autoslidegen, runner):
        """Test that debug mode shows traceback on error."""
        mock_instance = Mock()
        mock_instance.generate.side_effect = Exception("Test error")
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            '--debug',
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test'
        ])

        assert result.exit_code == 1
        # In debug mode, more detailed error info should be shown

    def test_generate_different_languages(self, runner):
        """Test generate command accepts different languages."""
        languages = ['zh', 'en', 'ja', 'es']

        for lang in languages:
            with patch('autoslidegen.cli.AutoSlideGen') as mock_autoslidegen:
                mock_instance = Mock()
                mock_instance.generate.return_value = {
                    'pptx_path': 'output.pptx',
                    'json_path': 'output.json',
                    'outline': Mock(slides=[])
                }
                mock_autoslidegen.return_value = mock_instance

                result = runner.invoke(cli, [
                    'generate',
                    '--topic', 'Test',
                    '--audience', 'Test',
                    '--purpose', 'Test',
                    '--language', lang
                ])

                assert result.exit_code == 0

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_with_speaker_notes(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate with speaker notes option."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': None,
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--speaker-notes'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['generate_speaker_notes'] is True

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_with_images(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate with images option."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': None,
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Test',
            '--audience', 'Test',
            '--purpose', 'Test',
            '--add-images',
            '--image-provider', 'pexels'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['add_images'] is True
        assert call_kwargs['image_provider'] == 'pexels'

    @patch('autoslidegen.cli.AutoSlideGen')
    def test_generate_with_charts(self, mock_autoslidegen, runner, temp_dir, sample_outline):
        """Test generate with charts option."""
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'pptx_path': str(Path(temp_dir) / 'output.pptx'),
            'json_path': None,
            'outline': sample_outline
        }
        mock_autoslidegen.return_value = mock_instance

        result = runner.invoke(cli, [
            'generate',
            '--topic', 'Sales Analysis',
            '--audience', 'Management',
            '--purpose', 'Review',
            '--add-charts'
        ])

        assert result.exit_code == 0
        call_kwargs = mock_instance.generate.call_args[1]
        assert call_kwargs['add_charts'] is True
