"""
Interactive wizard for AutoSlideGen.
Provides user-friendly prompts for generating presentations.
"""

import logging
from typing import Dict, Any, Optional

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class GenerationWizard:
    """Interactive wizard for presentation generation."""

    LANGUAGES = {
        '1': ('zh', '中文 (Chinese)'),
        '2': ('en', 'English'),
        '3': ('ja', '日本語 (Japanese)'),
        '4': ('es', 'Español (Spanish)')
    }

    PROVIDERS = {
        '1': ('openai', 'OpenAI (GPT-4)'),
        '2': ('anthropic', 'Anthropic (Claude)')
    }

    def __init__(self):
        """Initialize wizard."""
        self.params = {}

    def run(self) -> Dict[str, Any]:
        """
        Run interactive wizard.

        Returns:
            Dictionary with generation parameters
        """
        console.print()
        console.print(Panel.fit(
            "[bold cyan]AutoSlideGen Interactive Wizard[/bold cyan]\n\n"
            "让我帮您创建一个精彩的演示文稿！\n"
            "Let me help you create an amazing presentation!",
            border_style="cyan"
        ))
        console.print()

        # Get basic information
        self._ask_topic()
        self._ask_audience()
        self._ask_purpose()
        self._ask_language()

        # Get presentation details
        self._ask_slides_count()
        self._ask_bullets_per_slide()

        # Ask about optional features
        console.print()
        console.print("[bold]Optional Features:[/bold]")

        self._ask_additional_requirements()
        self._ask_speaker_notes()
        self._ask_images()
        self._ask_charts()

        # Ask about provider
        self._ask_provider()

        # Summary
        self._show_summary()

        # Confirm
        if Confirm.ask("\n[bold]Proceed with generation?[/bold]", default=True):
            return self.params
        else:
            console.print("[yellow]Generation cancelled.[/yellow]")
            return None

    def _ask_topic(self):
        """Ask for presentation topic."""
        topic = Prompt.ask(
            "\n[bold cyan]📝 What is the topic of your presentation?[/bold cyan]",
            default="人工智能技术"
        )
        self.params['topic'] = topic

    def _ask_audience(self):
        """Ask for target audience."""
        audience = Prompt.ask(
            "[bold cyan]👥 Who is your target audience?[/bold cyan]",
            default="技术人员和行业专家"
        )
        self.params['audience'] = audience

    def _ask_purpose(self):
        """Ask for presentation purpose."""
        purpose = Prompt.ask(
            "[bold cyan]🎯 What is the purpose of this presentation?[/bold cyan]",
            default="介绍技术概念和应用场景"
        )
        self.params['purpose'] = purpose

    def _ask_language(self):
        """Ask for language."""
        console.print("\n[bold cyan]🌐 Select language:[/bold cyan]")

        for key, (code, name) in self.LANGUAGES.items():
            console.print(f"  {key}. {name}")

        choice = Prompt.ask(
            "Choose language",
            choices=list(self.LANGUAGES.keys()),
            default='1'
        )

        lang_code, lang_name = self.LANGUAGES[choice]
        self.params['language'] = lang_code
        console.print(f"[green]✓[/green] Selected: {lang_name}")

    def _ask_slides_count(self):
        """Ask for number of slides."""
        num_slides = IntPrompt.ask(
            "\n[bold cyan]📊 How many slides do you want?[/bold cyan]",
            default=10
        )

        # Validate range
        if num_slides < 5:
            console.print("[yellow]Minimum 5 slides. Setting to 5.[/yellow]")
            num_slides = 5
        elif num_slides > 30:
            console.print("[yellow]Maximum 30 slides. Setting to 30.[/yellow]")
            num_slides = 30

        self.params['num_slides'] = num_slides

    def _ask_bullets_per_slide(self):
        """Ask for bullets per slide."""
        bullets = IntPrompt.ask(
            "[bold cyan]• How many bullet points per slide (average)?[/bold cyan]",
            default=4
        )

        # Validate range
        if bullets < 2:
            console.print("[yellow]Minimum 2 bullets. Setting to 2.[/yellow]")
            bullets = 2
        elif bullets > 6:
            console.print("[yellow]Maximum 6 bullets. Setting to 6.[/yellow]")
            bullets = 6

        self.params['bullets_per_slide'] = bullets

    def _ask_additional_requirements(self):
        """Ask for additional requirements."""
        has_requirements = Confirm.ask(
            "\n[bold]Do you have any additional requirements or preferences?[/bold]",
            default=False
        )

        if has_requirements:
            requirements = Prompt.ask(
                "[cyan]Please describe your requirements[/cyan]",
                default=""
            )
            self.params['additional_requirements'] = requirements
        else:
            self.params['additional_requirements'] = None

    def _ask_speaker_notes(self):
        """Ask about speaker notes generation."""
        generate_notes = Confirm.ask(
            "\n[bold]🎤 Generate speaker notes for each slide?[/bold]",
            default=False
        )
        self.params['generate_speaker_notes'] = generate_notes

        if generate_notes:
            console.print(
                "[dim]Speaker notes will provide detailed talking points for each slide[/dim]"
            )

    def _ask_images(self):
        """Ask about image insertion."""
        add_images = Confirm.ask(
            "\n[bold]🖼️  Search and add relevant images?[/bold]",
            default=False
        )
        self.params['add_images'] = add_images

        if add_images:
            console.print("[cyan]Select image provider:[/cyan]")
            console.print("  1. Unsplash (High-quality stock photos)")
            console.print("  2. Pexels (Free stock photos)")

            provider_choice = Prompt.ask(
                "Choose image provider",
                choices=['1', '2'],
                default='1'
            )

            self.params['image_provider'] = 'unsplash' if provider_choice == '1' else 'pexels'
            console.print(f"[green]✓[/green] Will use {self.params['image_provider']}")

    def _ask_charts(self):
        """Ask about chart generation."""
        add_charts = Confirm.ask(
            "\n[bold]📈 Auto-generate charts where appropriate?[/bold]",
            default=False
        )
        self.params['add_charts'] = add_charts

        if add_charts:
            console.print(
                "[dim]Charts will be generated for slides with numeric data[/dim]"
            )

    def _ask_provider(self):
        """Ask for LLM provider."""
        console.print("\n[bold cyan]🤖 Select LLM Provider:[/bold cyan]")

        for key, (code, name) in self.PROVIDERS.items():
            console.print(f"  {key}. {name}")

        choice = Prompt.ask(
            "Choose provider",
            choices=list(self.PROVIDERS.keys()),
            default='1',
            show_default=True
        )

        provider_code, provider_name = self.PROVIDERS[choice]
        self.params['provider'] = provider_code
        console.print(f"[green]✓[/green] Selected: {provider_name}")

    def _show_summary(self):
        """Show summary of selections."""
        console.print()
        console.print(Panel.fit(
            "[bold]Generation Summary[/bold]",
            border_style="green"
        ))

        table = Table(show_header=False, box=None)
        table.add_column("Parameter", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("Topic", self.params['topic'])
        table.add_row("Audience", self.params['audience'])
        table.add_row("Purpose", self.params['purpose'])
        table.add_row("Language", self._get_language_name())
        table.add_row("Number of Slides", str(self.params['num_slides']))
        table.add_row("Bullets per Slide", str(self.params['bullets_per_slide']))

        if self.params.get('additional_requirements'):
            table.add_row("Requirements", self.params['additional_requirements'])

        # Optional features
        features = []
        if self.params.get('generate_speaker_notes'):
            features.append("Speaker Notes")
        if self.params.get('add_images'):
            features.append(f"Images ({self.params.get('image_provider', 'unsplash')})")
        if self.params.get('add_charts'):
            features.append("Charts")

        if features:
            table.add_row("Optional Features", ", ".join(features))

        table.add_row("LLM Provider", self._get_provider_name())

        console.print(table)

    def _get_language_name(self) -> str:
        """Get language display name."""
        lang_code = self.params.get('language', 'zh')
        for code, name in self.LANGUAGES.values():
            if code == lang_code:
                return name
        return lang_code

    def _get_provider_name(self) -> str:
        """Get provider display name."""
        provider_code = self.params.get('provider', 'openai')
        for code, name in self.PROVIDERS.values():
            if code == provider_code:
                return name
        return provider_code


def run_interactive_wizard() -> Optional[Dict[str, Any]]:
    """
    Run the interactive wizard and return parameters.

    Returns:
        Dictionary with generation parameters, or None if cancelled
    """
    wizard = GenerationWizard()
    return wizard.run()
