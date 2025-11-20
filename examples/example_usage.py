"""
Example usage of AutoSlideGen API.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from autoslidegen import AutoSlideGen


def example_basic_usage():
    """Basic usage example."""
    print("=== 基础使用示例 ===\n")

    # Initialize generator with OpenAI
    generator = AutoSlideGen(provider='openai')

    # Generate presentation
    result = generator.generate(
        topic="Python编程最佳实践",
        audience="初级到中级Python开发者",
        purpose="分享实用的Python编程技巧和模式",
        language="zh",
        num_slides=12,
        bullets_per_slide=4,
        additional_requirements="重点关注代码可读性和维护性"
    )

    print(f"✓ 生成成功!")
    print(f"  PPTX文件: {result['pptx_path']}")
    print(f"  JSON大纲: {result['json_path']}")
    print(f"  幻灯片数量: {len(result['outline'].slides)}")


def example_with_anthropic():
    """Example using Anthropic Claude."""
    print("\n=== 使用Anthropic Claude ===\n")

    # Initialize with Anthropic
    generator = AutoSlideGen(provider='anthropic')

    result = generator.generate(
        topic="Artificial Intelligence Ethics",
        audience="Technology Leaders and Policymakers",
        purpose="Discuss ethical considerations in AI development and deployment",
        language="en",
        num_slides=15,
        bullets_per_slide=3
    )

    print(f"✓ Generated successfully!")
    print(f"  PPTX file: {result['pptx_path']}")
    print(f"  Number of slides: {len(result['outline'].slides)}")


def example_from_json():
    """Example building PPTX from existing JSON."""
    print("\n=== 从JSON构建PPTX ===\n")

    # First, generate and save JSON
    generator = AutoSlideGen(provider='openai')

    result = generator.generate(
        topic="机器学习入门",
        audience="数据科学初学者",
        purpose="介绍机器学习的基本概念和应用",
        language="zh",
        num_slides=10
    )

    json_path = result['json_path']
    print(f"✓ JSON大纲已保存: {json_path}")

    # Now build PPTX from JSON
    pptx_path = generator.generate_from_json(
        json_path=json_path,
        output_path="./output/from_json_example.pptx"
    )

    print(f"✓ 从JSON构建PPTX成功: {pptx_path}")


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n=== 自定义配置示例 ===\n")

    # Use custom config file
    generator = AutoSlideGen(
        provider='openai',
        config_path='./config.yaml'
    )

    result = generator.generate(
        topic="データサイエンスの基礎",
        audience="ビジネスアナリスト",
        purpose="データ分析の重要性と基本的な手法を説明する",
        language="ja",
        num_slides=10,
        bullets_per_slide=4
    )

    print(f"✓ 日本語プレゼンテーション生成成功!")
    print(f"  ファイル: {result['pptx_path']}")


if __name__ == "__main__":
    try:
        # Run examples
        example_basic_usage()

        # Uncomment to run other examples:
        # example_with_anthropic()
        # example_from_json()
        # example_custom_configuration()

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
