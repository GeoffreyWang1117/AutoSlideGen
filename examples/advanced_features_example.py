"""
Advanced features examples for AutoSlideGen.
Demonstrates speaker notes, images, charts, RAG, templates, and multi-agent.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoslidegen import AutoSlideGen


def example_with_speaker_notes():
    """Example: Generate presentation with speaker notes."""
    print("\n=== Example 1: Speaker Notes Generation ===\n")

    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="Effective Team Communication",
        audience="Team Leaders and Managers",
        purpose="Improve team collaboration and communication",
        language="en",
        num_slides=10,
        generate_speaker_notes=True  # Enable speaker notes
    )

    print(f"✓ Generated with speaker notes")
    print(f"  PPTX: {result['pptx_path']}")


def example_with_images():
    """Example: Generate presentation with images."""
    print("\n=== Example 2: Image Search and Insertion ===\n")

    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="Beautiful Destinations Around the World",
        audience="Travel Enthusiasts",
        purpose="Inspire travel and exploration",
        language="en",
        num_slides=12,
        add_images=True,              # Enable image search
        image_provider='unsplash'      # Use Unsplash
    )

    print(f"✓ Generated with images")
    print(f"  PPTX: {result['pptx_path']}")


def example_with_charts():
    """Example: Generate presentation with charts."""
    print("\n=== Example 3: Chart Generation ===\n")

    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="Sales Performance Analysis",
        audience="Sales Team and Management",
        purpose="Review quarterly performance",
        language="en",
        num_slides=10,
        add_charts=True,  # Enable chart generation
        additional_requirements="Focus on data visualization and trends"
    )

    print(f"✓ Generated with charts")
    print(f"  PPTX: {result['pptx_path']}")


def example_with_all_features():
    """Example: Combine all features."""
    print("\n=== Example 4: All Features Combined ===\n")

    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="AI技术在企业中的应用",
        audience="企业决策者和技术负责人",
        purpose="展示AI技术的商业价值和实施路径",
        language="zh",
        num_slides=15,
        generate_speaker_notes=True,   # Speaker notes
        add_images=True,                # Images
        add_charts=True,                # Charts
        additional_requirements="重点关注实际应用案例和ROI分析"
    )

    print(f"✓ Generated with all features")
    print(f"  PPTX: {result['pptx_path']}")
    print(f"  JSON: {result['json_path']}")
    print(f"  Slides: {len(result['outline'].slides)}")


def example_template_management():
    """Example: Template management."""
    print("\n=== Example 5: Template Management ===\n")

    from autoslidegen.extensions import TemplateManager

    tm = TemplateManager()

    # List available templates
    templates = tm.list_templates()
    print(f"Available templates: {templates}")

    # Add a new template (if you have one)
    # tm.add_template('./my_template.pptx', 'my_template')

    # Get template info
    if templates:
        info = tm.get_template_info(templates[0])
        if info:
            print(f"\nTemplate info:")
            print(f"  Name: {info['name']}")
            print(f"  Layouts: {info['num_layouts']}")


def example_rag_enhanced():
    """Example: RAG-enhanced generation."""
    print("\n=== Example 6: RAG Enhanced Generation ===\n")

    from autoslidegen.extensions import SimpleRAGGenerator

    # Create knowledge base directory and add some documents
    kb_path = "./knowledge_base"
    Path(kb_path).mkdir(exist_ok=True)

    # Add sample document
    sample_doc = Path(kb_path) / "ai_basics.txt"
    if not sample_doc.exists():
        sample_doc.write_text("""
        Artificial Intelligence (AI) is the simulation of human intelligence processes by machines.
        Key areas include machine learning, natural language processing, and computer vision.
        AI has applications in healthcare, finance, transportation, and more.
        """)

    # Use RAG
    rag_gen = SimpleRAGGenerator(knowledge_base_path=kb_path)

    enhanced_requirements = rag_gen.get_enhanced_requirements(
        topic="Artificial Intelligence",
        original_requirements="Focus on practical applications"
    )

    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="Artificial Intelligence Overview",
        audience="Business Professionals",
        purpose="Introduce AI concepts",
        language="en",
        num_slides=10,
        additional_requirements=enhanced_requirements  # Use RAG-enhanced requirements
    )

    print(f"✓ Generated with RAG enhancement")
    print(f"  PPTX: {result['pptx_path']}")


def example_multi_agent():
    """Example: Multi-agent generation."""
    print("\n=== Example 7: Multi-Agent Generation ===\n")

    from autoslidegen.extensions import MultiAgentOrchestrator
    from autoslidegen.outline_generator.factory import GeneratorFactory
    from autoslidegen.utils.config import get_config

    config = get_config()
    llm_config = config.get_llm_config('openai')
    llm_gen = GeneratorFactory.create_generator('openai', llm_config)

    orchestrator = MultiAgentOrchestrator(llm_gen)

    results = orchestrator.generate_with_agents_sync(
        topic="Product Launch Strategy",
        audience="Stakeholders and Investors",
        purpose="Present new product launch plan",
        num_slides=12
    )

    print(f"✓ Multi-agent workflow completed")
    print(f"  Strategy: {results['workflow_results']['strategy']['status']}")
    print(f"  Content: {results['workflow_results']['content']['status']}")
    print(f"  Design: {results['workflow_results']['design']['status']}")


def example_chart_generation():
    """Example: Direct chart generation."""
    print("\n=== Example 8: Direct Chart Generation ===\n")

    from autoslidegen.extensions import ChartGenerator

    chart_gen = ChartGenerator(library='matplotlib')

    # Create bar chart
    bar_chart = chart_gen.create_bar_chart(
        data={'Q1': 100, 'Q2': 150, 'Q3': 120, 'Q4': 180},
        title='Quarterly Revenue (in thousands)',
        xlabel='Quarter',
        ylabel='Revenue ($K)'
    )
    print(f"✓ Created bar chart: {bar_chart}")

    # Create pie chart
    pie_chart = chart_gen.create_pie_chart(
        data={'Product A': 35, 'Product B': 25, 'Product C': 40},
        title='Market Share by Product'
    )
    print(f"✓ Created pie chart: {pie_chart}")

    # Create line chart
    line_chart = chart_gen.create_line_chart(
        data={
            'Revenue': [100, 120, 115, 135, 150, 165],
            'Costs': [60, 65, 63, 70, 75, 78]
        },
        title='Revenue vs Costs Trend',
        xlabel='Month',
        ylabel='Amount ($K)'
    )
    print(f"✓ Created line chart: {line_chart}")


if __name__ == "__main__":
    import os

    # Check if API keys are configured
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: No LLM API keys configured.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        print("   Some examples will not work without API keys.\n")

    try:
        # Run examples (comment out ones you don't want to run)

        # Basic examples (require LLM API)
        # example_with_speaker_notes()
        # example_with_charts()

        # Image example (requires image API key)
        # example_with_images()

        # Combined example (requires LLM API)
        # example_with_all_features()

        # Template example (no API needed)
        example_template_management()

        # Chart generation (no API needed)
        example_chart_generation()

        # RAG example (requires LLM API)
        # example_rag_enhanced()

        # Multi-agent example (requires LLM API)
        # example_multi_agent()

        print("\n✓ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
