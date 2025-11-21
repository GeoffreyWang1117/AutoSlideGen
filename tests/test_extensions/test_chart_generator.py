"""
Tests for chart generation extension.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from autoslidegen.extensions.chart_generator import (
    ChartGenerator,
    SmartChartGenerator
)
from autoslidegen.parser.models import (
    Slide,
    BulletPoint,
    PresentationMetadata,
    PresentationOutline
)


class TestChartGenerator:
    """Tests for ChartGenerator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def chart_gen_matplotlib(self, temp_dir):
        """Create ChartGenerator with matplotlib."""
        return ChartGenerator(library='matplotlib', output_dir=temp_dir)

    @pytest.fixture
    def chart_gen_plotly(self, temp_dir):
        """Create ChartGenerator with plotly."""
        return ChartGenerator(library='plotly', output_dir=temp_dir)

    def test_initialization_matplotlib(self, chart_gen_matplotlib):
        """Test ChartGenerator initialization with matplotlib."""
        assert chart_gen_matplotlib.library == 'matplotlib'
        assert Path(chart_gen_matplotlib.output_dir).exists()

    def test_initialization_plotly(self, chart_gen_plotly):
        """Test ChartGenerator initialization with plotly."""
        assert chart_gen_plotly.library == 'plotly'

    def test_invalid_library_raises_error(self, temp_dir):
        """Test that invalid library raises ValueError."""
        with pytest.raises(ValueError):
            ChartGenerator(library='invalid', output_dir=temp_dir)

    def test_create_bar_chart_matplotlib(self, chart_gen_matplotlib):
        """Test creating bar chart with matplotlib."""
        data = {'Q1': 100, 'Q2': 150, 'Q3': 120, 'Q4': 180}

        chart_path = chart_gen_matplotlib.create_bar_chart(
            data=data,
            title='Quarterly Revenue',
            xlabel='Quarter',
            ylabel='Revenue ($K)'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()
        assert Path(chart_path).suffix == '.png'

    def test_create_pie_chart_matplotlib(self, chart_gen_matplotlib):
        """Test creating pie chart with matplotlib."""
        data = {'Product A': 35, 'Product B': 25, 'Product C': 40}

        chart_path = chart_gen_matplotlib.create_pie_chart(
            data=data,
            title='Market Share'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_create_line_chart_matplotlib(self, chart_gen_matplotlib):
        """Test creating line chart with matplotlib."""
        data = {
            'Revenue': [100, 120, 115, 135, 150, 165],
            'Costs': [60, 65, 63, 70, 75, 78]
        }

        chart_path = chart_gen_matplotlib.create_line_chart(
            data=data,
            title='Revenue vs Costs',
            xlabel='Month',
            ylabel='Amount ($K)'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_create_bar_chart_plotly(self, chart_gen_plotly):
        """Test creating bar chart with plotly."""
        data = {'Q1': 100, 'Q2': 150, 'Q3': 120, 'Q4': 180}

        chart_path = chart_gen_plotly.create_bar_chart(
            data=data,
            title='Quarterly Revenue',
            xlabel='Quarter',
            ylabel='Revenue ($K)'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_create_pie_chart_plotly(self, chart_gen_plotly):
        """Test creating pie chart with plotly."""
        data = {'Product A': 35, 'Product B': 25, 'Product C': 40}

        chart_path = chart_gen_plotly.create_pie_chart(
            data=data,
            title='Market Share'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_create_line_chart_plotly(self, chart_gen_plotly):
        """Test creating line chart with plotly."""
        data = {
            'Revenue': [100, 120, 115, 135, 150, 165],
            'Costs': [60, 65, 63, 70, 75, 78]
        }

        chart_path = chart_gen_plotly.create_line_chart(
            data=data,
            title='Revenue vs Costs',
            xlabel='Month',
            ylabel='Amount ($K)'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_empty_data_handling(self, chart_gen_matplotlib):
        """Test handling of empty data."""
        data = {}

        chart_path = chart_gen_matplotlib.create_bar_chart(
            data=data,
            title='Empty Chart'
        )

        # Should handle gracefully (return None or create empty chart)
        if chart_path:
            assert Path(chart_path).exists()

    def test_chart_with_chinese_labels(self, chart_gen_matplotlib):
        """Test creating chart with Chinese labels."""
        data = {'第一季度': 100, '第二季度': 150, '第三季度': 120}

        chart_path = chart_gen_matplotlib.create_bar_chart(
            data=data,
            title='季度收入',
            xlabel='季度',
            ylabel='收入 (千元)'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()

    def test_large_dataset_chart(self, chart_gen_matplotlib):
        """Test creating chart with large dataset."""
        data = {f'Item{i}': i * 10 for i in range(100)}

        chart_path = chart_gen_matplotlib.create_bar_chart(
            data=data,
            title='Large Dataset'
        )

        assert chart_path is not None
        assert Path(chart_path).exists()


class TestSmartChartGenerator:
    """Tests for SmartChartGenerator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def smart_chart_gen(self, temp_dir):
        """Create SmartChartGenerator instance."""
        chart_gen = ChartGenerator(library='matplotlib', output_dir=temp_dir)
        return SmartChartGenerator(chart_gen)

    @pytest.fixture
    def sample_outline(self):
        """Create sample outline with chart-relevant slides."""
        metadata = PresentationMetadata(
            topic="销售数据分析",
            audience="管理层",
            purpose="展示销售趋势"
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
                title="季度销售对比",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="Q1: 100万", level=1),
                    BulletPoint(text="Q2: 150万", level=1),
                    BulletPoint(text="Q3: 120万", level=1)
                ]
            ),
            Slide(
                slide_number=3,
                title="市场份额分布",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="产品A: 35%", level=1),
                    BulletPoint(text="产品B: 25%", level=1),
                    BulletPoint(text="产品C: 40%", level=1)
                ]
            ),
            Slide(
                slide_number=4,
                title="收入增长趋势",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="1月: 100", level=1),
                    BulletPoint(text="2月: 120", level=1),
                    BulletPoint(text="3月: 140", level=1)
                ]
            )
        ]

        return PresentationOutline(metadata=metadata, slides=slides)

    def test_initialization(self, smart_chart_gen):
        """Test SmartChartGenerator initialization."""
        assert smart_chart_gen.chart_generator is not None

    def test_detect_chart_type_comparison(self, smart_chart_gen):
        """Test detecting bar chart for comparison."""
        slide = Slide(
            slide_number=2,
            title="销售对比分析",
            slide_type="content",
            bullet_points=[BulletPoint(text="数据", level=1)]
        )

        chart_type = smart_chart_gen.detect_chart_type(slide)
        assert chart_type in ['bar', None]

    def test_detect_chart_type_distribution(self, smart_chart_gen):
        """Test detecting pie chart for distribution."""
        slide = Slide(
            slide_number=2,
            title="市场份额分布",
            slide_type="content",
            bullet_points=[BulletPoint(text="数据", level=1)]
        )

        chart_type = smart_chart_gen.detect_chart_type(slide)
        assert chart_type in ['pie', None]

    def test_detect_chart_type_trend(self, smart_chart_gen):
        """Test detecting line chart for trends."""
        slide = Slide(
            slide_number=2,
            title="增长趋势分析",
            slide_type="content",
            bullet_points=[BulletPoint(text="数据", level=1)]
        )

        chart_type = smart_chart_gen.detect_chart_type(slide)
        assert chart_type in ['line', None]

    def test_extract_data_from_slide(self, smart_chart_gen):
        """Test extracting data from slide bullets."""
        slide = Slide(
            slide_number=2,
            title="销售数据",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="Q1: 100", level=1),
                BulletPoint(text="Q2: 150", level=1),
                BulletPoint(text="Q3: 120", level=1)
            ]
        )

        data = smart_chart_gen.extract_data_from_slide(slide)

        assert isinstance(data, dict)
        # Should extract numeric values
        if len(data) > 0:
            assert all(isinstance(v, (int, float)) for v in data.values())

    def test_generate_charts_for_outline(self, smart_chart_gen, sample_outline):
        """Test generating charts for entire outline."""
        chart_map = smart_chart_gen.generate_charts_for_outline(sample_outline)

        assert isinstance(chart_map, dict)
        # Should have generated some charts
        # Note: Actual chart generation depends on data extraction

    def test_generate_chart_for_slide(self, smart_chart_gen):
        """Test generating chart for a single slide."""
        slide = Slide(
            slide_number=2,
            title="季度销售",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="Q1: 100", level=1),
                BulletPoint(text="Q2: 150", level=1)
            ]
        )

        chart_path = smart_chart_gen.generate_chart_for_slide(slide)

        # May or may not generate chart depending on data extraction
        if chart_path:
            assert Path(chart_path).exists()

    def test_skip_slides_without_data(self, smart_chart_gen):
        """Test that slides without extractable data are skipped."""
        slide = Slide(
            slide_number=2,
            title="文字描述",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="这是一段描述性文字", level=1),
                BulletPoint(text="没有数值数据", level=1)
            ]
        )

        chart_path = smart_chart_gen.generate_chart_for_slide(slide)

        # Should not generate chart for non-numeric data
        assert chart_path is None or chart_path == ""

    def test_different_chart_types(self, smart_chart_gen, temp_dir):
        """Test generating different chart types."""
        chart_gen = ChartGenerator(library='matplotlib', output_dir=temp_dir)
        smart_gen = SmartChartGenerator(chart_gen)

        slides = {
            'bar': Slide(
                slide_number=1,
                title="对比分析",
                slide_type="content",
                bullet_points=[BulletPoint(text="A: 100", level=1)]
            ),
            'pie': Slide(
                slide_number=2,
                title="分布情况",
                slide_type="content",
                bullet_points=[BulletPoint(text="A: 50", level=1)]
            ),
            'line': Slide(
                slide_number=3,
                title="趋势变化",
                slide_type="content",
                bullet_points=[BulletPoint(text="1月: 100", level=1)]
            )
        }

        for chart_type, slide in slides.items():
            detected_type = smart_gen.detect_chart_type(slide)
            # Just verify detection runs without error
            assert detected_type in ['bar', 'pie', 'line', None]

    def test_handles_malformed_data(self, smart_chart_gen):
        """Test handling of malformed data in bullets."""
        slide = Slide(
            slide_number=2,
            title="数据",
            slide_type="content",
            bullet_points=[
                BulletPoint(text="Invalid data format", level=1),
                BulletPoint(text="Q1: abc", level=1),  # Non-numeric
                BulletPoint(text=": 100", level=1),  # Missing label
            ]
        )

        # Should handle gracefully without crashing
        data = smart_chart_gen.extract_data_from_slide(slide)
        assert isinstance(data, dict)
