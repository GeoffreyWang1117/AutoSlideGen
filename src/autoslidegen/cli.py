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
from .batch import BatchGenerator, BatchGenerationRequest
from .interactive import run_interactive_wizard

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
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    help='Output directory for batch generation'
)
@click.option(
    '--provider',
    type=click.Choice(['openai', 'anthropic']),
    help='LLM provider (overrides config)'
)
@click.option(
    '--parallel/--sequential',
    default=True,
    help='Use parallel or sequential processing'
)
@click.option(
    '--max-workers',
    default=3,
    type=int,
    help='Maximum parallel workers (default: 3)'
)
@click.option(
    '--no-json',
    is_flag=True,
    help='Do not save JSON outlines'
)
@click.pass_context
def batch(ctx, input_file, output_dir, provider, parallel, max_workers, no_json):
    """Batch generate presentations from CSV or JSON file.

    INPUT_FILE can be either:
    - CSV file with columns: topic, audience, purpose, language, num_slides, bullets_per_slide
    - JSON file with format: {"requests": [{"topic": "...", ...}, ...]}

    Example CSV:
    topic,audience,purpose,language,num_slides
    AI Technology,Developers,Introduction,en,10
    Cloud Computing,IT Managers,Overview,zh,12

    Example usage:
    autoslidegen batch requests.csv --output-dir ./presentations --parallel
    """
    try:
        console.print("\n[bold cyan]AutoSlideGen - Batch Generation[/bold cyan]\n")

        # Determine file type and load batch request
        input_path = Path(input_file)

        if input_path.suffix.lower() == '.csv':
            console.print(f"Loading batch requests from CSV: {input_file}")
            batch_request = BatchGenerationRequest.from_csv(input_file)
        elif input_path.suffix.lower() == '.json':
            console.print(f"Loading batch requests from JSON: {input_file}")
            batch_request = BatchGenerationRequest.from_json(input_file)
        else:
            console.print("[red]Error: Input file must be CSV or JSON[/red]")
            sys.exit(1)

        console.print(f"[green]✓[/green] Loaded {batch_request.total} requests\n")

        # Create batch generator
        generator = BatchGenerator(
            provider=provider,
            config_path=ctx.obj.get('config'),
            max_workers=max_workers
        )

        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Generating {batch_request.total} presentations...",
                total=batch_request.total
            )

            def on_progress(completed, total, topic):
                progress.update(
                    task,
                    completed=completed,
                    description=f"[{completed}/{total}] {topic[:40]}..."
                )

            # Generate batch
            results = generator.generate_batch(
                batch_request,
                output_dir=output_dir,
                parallel=parallel,
                save_json=not no_json,
                on_progress=on_progress
            )

            progress.update(task, completed=batch_request.total)

        # Display results
        console.print()

        success_rate = (results['completed'] / results['total'] * 100) if results['total'] > 0 else 0

        result_table = Table(show_header=True, header_style="bold magenta")
        result_table.add_column("Metric", style="cyan")
        result_table.add_column("Value")

        result_table.add_row("Total Requests", str(results['total']))
        result_table.add_row(
            "Completed",
            f"[green]{results['completed']}[/green]"
        )
        result_table.add_row(
            "Failed",
            f"[red]{results['failed']}[/red]" if results['failed'] > 0 else "0"
        )
        result_table.add_row(
            "Success Rate",
            f"{success_rate:.1f}%"
        )
        result_table.add_row(
            "Duration",
            f"{results['duration_seconds']:.2f}s"
        )
        result_table.add_row(
            "Avg Time/Presentation",
            f"{results['avg_time_per_presentation']:.2f}s"
        )

        console.print(result_table)
        console.print()

        console.print(Panel.fit(
            f"[green]✓[/green] Batch generation completed!\n\n"
            f"[bold]Output Directory:[/bold] {results['output_dir']}\n"
            f"[bold]Report:[/bold] {results['output_dir']}/batch_report.json\n"
            f"[bold]Summary:[/bold] {results['output_dir']}/batch_summary.txt",
            title="Success",
            border_style="green"
        ))

        # Show failures if any
        if results['failures']:
            console.print("\n[bold red]Failed Presentations:[/bold red]")
            for failure in results['failures']:
                console.print(
                    f"  {failure['index']:3d}. {failure['topic']}: "
                    f"[red]{failure['error']}[/red]"
                )

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n", style="red")
        if ctx.obj.get('debug'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Interactive mode - guided presentation generation.

    This command launches an interactive wizard that guides you through
    the presentation generation process with user-friendly prompts.

    Example usage:
    autoslidegen interactive
    """
    try:
        # Run the interactive wizard
        params = run_interactive_wizard()

        if params is None:
            # User cancelled
            return

        # Extract parameters
        provider = params.pop('provider', None)
        generate_speaker_notes = params.pop('generate_speaker_notes', False)
        add_images = params.pop('add_images', False)
        image_provider = params.pop('image_provider', 'unsplash')
        add_charts = params.pop('add_charts', False)

        # Initialize AutoSlideGen
        console.print()
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

            progress.update(task, description="Generating presentation...")

            # Generate presentation
            result = generator.generate(
                **params,
                save_json=True,
                generate_speaker_notes=generate_speaker_notes,
                add_images=add_images,
                image_provider=image_provider,
                add_charts=add_charts
            )

            progress.update(task, description="Complete!", completed=True)

        # Display results
        console.print()
        console.print(Panel.fit(
            f"[green]✓[/green] Presentation generated successfully!\n\n"
            f"[bold]PPTX File:[/bold] {result['pptx_path']}\n"
            f"[bold]JSON Outline:[/bold] {result['json_path']}\n"
            f"[bold]Total Slides:[/bold] {len(result['outline'].slides)}",
            title="Success",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Generation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n", style="red")
        if ctx.obj.get('debug'):
            console.print_exception()
        sys.exit(1)


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
