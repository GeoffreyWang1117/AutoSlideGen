"""
Chart generation module.
Creates charts and visualizations for slides.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import io

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..parser.models import PresentationOutline

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates charts and visualizations."""

    def __init__(self, library: str = "matplotlib"):
        """
        Initialize chart generator.

        Args:
            library: Charting library to use (matplotlib, plotly)
        """
        self.library = library
        self.logger = logging.getLogger(self.__class__.__name__)

        if library == "matplotlib" and not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib required for chart generation. Install with: pip install matplotlib")
        elif library == "plotly" and not PLOTLY_AVAILABLE:
            raise ImportError("plotly required for chart generation. Install with: pip install plotly")

    def create_bar_chart(
        self,
        data: Dict[str, float],
        title: str = "Bar Chart",
        xlabel: str = "Category",
        ylabel: str = "Value",
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a bar chart.

        Args:
            data: Dictionary mapping categories to values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Path to save chart

        Returns:
            Path to saved chart
        """
        if self.library == "matplotlib":
            return self._create_bar_chart_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_bar_chart_plotly(data, title, xlabel, ylabel, output_path)
        else:
            raise ValueError(f"Unsupported library: {self.library}")

    def _create_bar_chart_matplotlib(
        self,
        data: Dict[str, float],
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: Optional[str]
    ) -> str:
        """Create bar chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = list(data.keys())
        values = list(data.values())

        ax.bar(categories, values, color='steelblue', alpha=0.8)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(axis='y', alpha=0.3)

        # Rotate x-axis labels if needed
        if len(max(categories, key=len)) > 10:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Save
        if output_path is None:
            output_path = f"./output/charts/bar_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Created bar chart: {output_path}")
        return output_path

    def _create_bar_chart_plotly(
        self,
        data: Dict[str, float],
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: Optional[str]
    ) -> str:
        """Create bar chart using plotly."""
        fig = go.Figure(data=[
            go.Bar(x=list(data.keys()), y=list(data.values()), marker_color='steelblue')
        ])

        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            template='plotly_white'
        )

        if output_path is None:
            output_path = f"./output/charts/bar_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)

        self.logger.info(f"Created bar chart: {output_path}")
        return output_path

    def create_pie_chart(
        self,
        data: Dict[str, float],
        title: str = "Pie Chart",
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a pie chart.

        Args:
            data: Dictionary mapping categories to values
            title: Chart title
            output_path: Path to save chart

        Returns:
            Path to saved chart
        """
        if self.library == "matplotlib":
            return self._create_pie_chart_matplotlib(data, title, output_path)
        elif self.library == "plotly":
            return self._create_pie_chart_plotly(data, title, output_path)

    def _create_pie_chart_matplotlib(
        self,
        data: Dict[str, float],
        title: str,
        output_path: Optional[str]
    ) -> str:
        """Create pie chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 8))

        categories = list(data.keys())
        values = list(data.values())

        ax.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=16, fontweight='bold')

        plt.tight_layout()

        if output_path is None:
            output_path = f"./output/charts/pie_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Created pie chart: {output_path}")
        return output_path

    def _create_pie_chart_plotly(
        self,
        data: Dict[str, float],
        title: str,
        output_path: Optional[str]
    ) -> str:
        """Create pie chart using plotly."""
        fig = go.Figure(data=[
            go.Pie(labels=list(data.keys()), values=list(data.values()))
        ])

        fig.update_layout(title=title)

        if output_path is None:
            output_path = f"./output/charts/pie_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=800)

        self.logger.info(f"Created pie chart: {output_path}")
        return output_path

    def create_line_chart(
        self,
        data: Dict[str, List[float]],
        title: str = "Line Chart",
        xlabel: str = "X",
        ylabel: str = "Y",
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a line chart.

        Args:
            data: Dictionary mapping series names to lists of values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Path to save chart

        Returns:
            Path to saved chart
        """
        if self.library == "matplotlib":
            return self._create_line_chart_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_line_chart_plotly(data, title, xlabel, ylabel, output_path)

    def _create_line_chart_matplotlib(
        self,
        data: Dict[str, List[float]],
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: Optional[str]
    ) -> str:
        """Create line chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))

        for label, values in data.items():
            ax.plot(range(len(values)), values, marker='o', label=label, linewidth=2)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()

        if output_path is None:
            output_path = f"./output/charts/line_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Created line chart: {output_path}")
        return output_path

    def _create_line_chart_plotly(
        self,
        data: Dict[str, List[float]],
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: Optional[str]
    ) -> str:
        """Create line chart using plotly."""
        fig = go.Figure()

        for label, values in data.items():
            fig.add_trace(go.Scatter(
                x=list(range(len(values))),
                y=values,
                mode='lines+markers',
                name=label
            ))

        fig.update_layout(
            title=title,
            xaxis_title=xlabel,
            yaxis_title=ylabel,
            template='plotly_white'
        )

        if output_path is None:
            output_path = f"./output/charts/line_chart_{hash(title) % 10000}.png"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)

        self.logger.info(f"Created line chart: {output_path}")
        return output_path

    def create_chart_from_spec(
        self,
        spec: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Create chart from specification dictionary.

        Args:
            spec: Chart specification with type, data, and options
            output_path: Path to save chart

        Returns:
            Path to saved chart
        """
        chart_type = spec.get('type', 'bar')
        data = spec.get('data', {})
        title = spec.get('title', 'Chart')
        xlabel = spec.get('xlabel', 'X')
        ylabel = spec.get('ylabel', 'Y')

        if chart_type == 'bar':
            return self.create_bar_chart(data, title, xlabel, ylabel, output_path)
        elif chart_type == 'pie':
            return self.create_pie_chart(data, title, output_path)
        elif chart_type == 'line':
            return self.create_line_chart(data, title, xlabel, ylabel, output_path)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")


class SmartChartGenerator:
    """Intelligently generates charts for presentation slides."""

    def __init__(self, llm_generator=None, chart_library: str = "matplotlib"):
        """
        Initialize smart chart generator.

        Args:
            llm_generator: LLM generator for intelligent suggestions
            chart_library: Charting library to use
        """
        self.llm_generator = llm_generator
        self.chart_generator = ChartGenerator(library=chart_library)
        self.logger = logging.getLogger(self.__class__.__name__)

    def suggest_chart_for_slide(self, slide_title: str, slide_content: str) -> Optional[Dict[str, Any]]:
        """
        Suggest chart specification for a slide.

        Args:
            slide_title: Slide title
            slide_content: Slide content

        Returns:
            Chart specification or None
        """
        # Simple rule-based suggestions
        title_lower = slide_title.lower()
        content_lower = slide_content.lower()

        # Look for keywords suggesting charts
        if any(word in title_lower for word in ['comparison', '对比', '比较', 'vs']):
            return {
                'type': 'bar',
                'title': f"{slide_title} Comparison",
                'data': {'A': 75, 'B': 85, 'C': 60},  # Sample data
                'xlabel': 'Category',
                'ylabel': 'Value'
            }
        elif any(word in title_lower for word in ['distribution', '分布', 'share', '占比']):
            return {
                'type': 'pie',
                'title': f"{slide_title} Distribution",
                'data': {'Category A': 30, 'Category B': 45, 'Category C': 25}
            }
        elif any(word in title_lower for word in ['trend', '趋势', 'growth', '增长', 'over time']):
            return {
                'type': 'line',
                'title': f"{slide_title} Trend",
                'data': {'Series 1': [10, 15, 13, 17, 20, 25]},
                'xlabel': 'Time',
                'ylabel': 'Value'
            }

        return None

    def generate_charts_for_outline(
        self,
        outline: PresentationOutline,
        auto_detect: bool = True
    ) -> Dict[int, str]:
        """
        Generate charts for presentation outline.

        Args:
            outline: Presentation outline
            auto_detect: Auto-detect slides that need charts

        Returns:
            Dictionary mapping slide numbers to chart image paths
        """
        chart_map = {}

        for slide in outline.slides:
            if slide.slide_type != "content":
                continue

            # Get slide content as string
            content = "\n".join(bp.text for bp in slide.bullet_points)

            # Suggest chart
            if auto_detect:
                spec = self.suggest_chart_for_slide(slide.title, content)

                if spec:
                    try:
                        chart_path = self.chart_generator.create_chart_from_spec(spec)
                        chart_map[slide.slide_number] = chart_path
                        self.logger.info(f"Generated chart for slide {slide.slide_number}")
                    except Exception as e:
                        self.logger.error(f"Failed to generate chart for slide {slide.slide_number}: {e}")

        return chart_map
