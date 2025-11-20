"""
Command-line interface for AutoSlideGen.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from .main import AutoSlideGen
from .outline_generator.factory import GeneratorFactory

console = Console()


@click.group()
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to config.yaml file'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug logging'
)
@click.pass_context
def cli(ctx, config, debug):
    """AutoSlideGen - Automated PowerPoint Outline Generator"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config

    # Setup logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@cli.command()
@click.option('--topic', '-t', required=True, help='Presentation topic')
@click.option('--audience', '-a', required=True, help='Target audience')
@click.option('--purpose', '-p', required=True, help='Presentation purpose')
@click.option(
    '--language',
    '-l',
    default='zh',
    type=click.Choice(['zh', 'en', 'ja', 'es']),
    help='Language code'
)
@click.option(
    '--slides',
    '-s',
    default=10,
    type=click.IntRange(5, 30),
    help='Number of slides'
)
@click.option(
    '--bullets',
    '-b',
    default=4,
    type=click.IntRange(2, 6),
    help='Average bullets per slide'
)
@click.option(
    '--provider',
    type=click.Choice(['openai', 'anthropic']),
    help='LLM provider (overrides config)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file path'
)
@click.option(
    '--requirements',
    '-r',
    help='Additional requirements'
)
@click.option(
    '--no-json',
    is_flag=True,
    help='Do not save JSON outline'
)
@click.option(
    '--speaker-notes',
    is_flag=True,
    help='Generate speaker notes for each slide'
)
@click.option(
    '--add-images',
    is_flag=True,
    help='Search and add images to slides'
)
@click.option(
    '--image-provider',
    type=click.Choice(['unsplash', 'pexels']),
    default='unsplash',
    help='Image search provider'
)
@click.option(
    '--add-charts',
    is_flag=True,
    help='Auto-generate charts for applicable slides'
)
@click.pass_context
def generate(
    ctx,
    topic,
    audience,
    purpose,
    language,
    slides,
    bullets,
    provider,
    output,
    requirements,
    no_json,
    speaker_notes,
    add_images,
    image_provider,
    add_charts
):
    """Generate a presentation from topic and requirements."""

    try:
        # Display input parameters
        console.print("\n[bold cyan]AutoSlideGen - Presentation Generator[/bold cyan]\n")

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Parameter", style="bold")
        info_table.add_column("Value")
        info_table.add_row("Topic", topic)
        info_table.add_row("Audience", audience)
        info_table.add_row("Purpose", purpose)
        info_table.add_row("Language", language)
        info_table.add_row("Slides", str(slides))
        info_table.add_row("Bullets/Slide", str(bullets))
        if provider:
            info_table.add_row("Provider", provider)

        console.print(info_table)
        console.print()

        # Initialize AutoSlideGen
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            task = progress.add_task("Initializing...", total=None)

            generator = AutoSlideGen(
                provider=provider,
                config_path=ctx.obj.get('config')
            )

            progress.update(task, description="Generating outline from LLM...")

            # Generate presentation
            result = generator.generate(
                topic=topic,
                audience=audience,
                purpose=purpose,
                language=language,
                num_slides=slides,
                bullets_per_slide=bullets,
                additional_requirements=requirements,
                output_path=output,
                save_json=not no_json,
                generate_speaker_notes=speaker_notes,
                add_images=add_images,
                image_provider=image_provider,
                add_charts=add_charts
            )

            progress.update(task, description="Complete!", completed=True)

        # Display results
        console.print()
        console.print(Panel.fit(
            f"[green]✓[/green] Presentation generated successfully!\n\n"
            f"[bold]PPTX File:[/bold] {result['pptx_path']}\n" +
            (f"[bold]JSON Outline:[/bold] {result['json_path']}\n" if result['json_path'] else "") +
            f"[bold]Total Slides:[/bold] {len(result['outline'].slides)}",
            title="Success",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n", style="red")
        if ctx.obj.get('debug'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file path'
)
@click.pass_context
def build(ctx, json_file, output):
    """Build PPTX from existing JSON outline."""

    try:
        console.print("\n[bold cyan]Building PPTX from JSON outline...[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            task = progress.add_task("Initializing...", total=None)

            generator = AutoSlideGen(config_path=ctx.obj.get('config'))

            progress.update(task, description="Building PPTX...")

            pptx_path = generator.generate_from_json(json_file, output)

            progress.update(task, description="Complete!", completed=True)

        console.print()
        console.print(Panel.fit(
            f"[green]✓[/green] PPTX file created successfully!\n\n"
            f"[bold]Output:[/bold] {pptx_path}",
            title="Success",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n", style="red")
        if ctx.obj.get('debug'):
            console.print_exception()
        sys.exit(1)


@cli.command()
def providers():
    """List available LLM providers."""
    console.print("\n[bold cyan]Available LLM Providers:[/bold cyan]\n")

    providers_list = GeneratorFactory.list_providers()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Status")

    for provider in providers_list:
        table.add_row(provider, "[green]Available[/green]")

    console.print(table)
    console.print()


@cli.command()
@click.option(
    '--topic',
    default='人工智能的未来发展',
    help='Example topic'
)
@click.pass_context
def example(ctx, topic):
    """Run example generation."""
    console.print("\n[bold cyan]Running example generation...[/bold cyan]\n")

    ctx.invoke(
        generate,
        topic=topic,
        audience='技术专业人士和行业决策者',
        purpose='介绍人工智能的最新发展趋势和应用前景',
        language='zh',
        slides=12,
        bullets=4,
        provider=None,
        output=None,
        requirements='重点关注实际应用案例和未来趋势',
        no_json=False
    )


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == '__main__':
    main()
