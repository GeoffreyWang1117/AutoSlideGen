"""
Chart generation module.
Creates charts and visualizations for slides.

Supported chart types:
- bar: Bar chart (vertical)
- horizontal_bar: Horizontal bar chart
- stacked_bar: Stacked bar chart
- pie: Pie chart
- donut: Donut chart
- line: Line chart
- area: Area chart
- radar: Radar/Spider chart
- scatter: Scatter plot
- heatmap: Heatmap
"""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import io
import math

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    np = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..parser.models import PresentationOutline

logger = logging.getLogger(__name__)

# Chart type keywords for intelligent detection
CHART_TYPE_KEYWORDS = {
    'bar': ['对比', '比较', 'comparison', 'compare', 'vs', '差异', 'difference'],
    'horizontal_bar': ['排名', 'ranking', 'rank', '排行', 'top'],
    'stacked_bar': ['组成', 'composition', '构成', '堆叠', 'stacked', '分解'],
    'pie': ['占比', 'share', '比例', 'proportion', '分布', 'distribution', '百分比'],
    'donut': ['环形', 'donut', '中心', 'center'],
    'line': ['趋势', 'trend', '变化', 'change', '增长', 'growth', '时间', 'time', '演变'],
    'area': ['累计', 'cumulative', '区域', 'area', '范围', 'range'],
    'radar': ['多维', 'multi', '综合', 'comprehensive', '能力', 'ability', '评估', 'evaluation', '雷达'],
    'scatter': ['关系', 'relationship', '相关', 'correlation', '分散', 'scatter'],
    'heatmap': ['热力', 'heat', '密度', 'density', '矩阵', 'matrix'],
}


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

    def create_horizontal_bar_chart(
        self,
        data: Dict[str, float],
        title: str = "Horizontal Bar Chart",
        xlabel: str = "Value",
        ylabel: str = "Category",
        output_path: Optional[str] = None
    ) -> str:
        """Create a horizontal bar chart."""
        if self.library == "matplotlib":
            return self._create_horizontal_bar_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_horizontal_bar_plotly(data, title, xlabel, ylabel, output_path)

    def _create_horizontal_bar_matplotlib(
        self, data: Dict[str, float], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create horizontal bar chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = list(data.keys())
        values = list(data.values())

        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(categories)))
        ax.barh(categories, values, color=colors, alpha=0.9)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, v in enumerate(values):
            ax.text(v + max(values) * 0.01, i, f'{v:.1f}', va='center', fontsize=10)

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/hbar_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_horizontal_bar_plotly(
        self, data: Dict[str, float], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create horizontal bar chart using plotly."""
        fig = go.Figure(data=[
            go.Bar(y=list(data.keys()), x=list(data.values()), orientation='h', marker_color='steelblue')
        ])
        fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel, template='plotly_white')
        if output_path is None:
            output_path = f"./output/charts/hbar_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)
        return output_path

    def create_stacked_bar_chart(
        self,
        data: Dict[str, Dict[str, float]],
        title: str = "Stacked Bar Chart",
        xlabel: str = "Category",
        ylabel: str = "Value",
        output_path: Optional[str] = None
    ) -> str:
        """Create a stacked bar chart. Data format: {series_name: {category: value}}"""
        if self.library == "matplotlib":
            return self._create_stacked_bar_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_stacked_bar_plotly(data, title, xlabel, ylabel, output_path)

    def _create_stacked_bar_matplotlib(
        self, data: Dict[str, Dict[str, float]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create stacked bar chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))

        series_names = list(data.keys())
        if not series_names:
            raise ValueError("No data provided for stacked bar chart")

        categories = list(data[series_names[0]].keys())
        bottom = np.zeros(len(categories))
        colors = plt.cm.Set2(np.linspace(0, 1, len(series_names)))

        for i, series in enumerate(series_names):
            values = [data[series].get(cat, 0) for cat in categories]
            ax.bar(categories, values, bottom=bottom, label=series, color=colors[i], alpha=0.9)
            bottom += np.array(values)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)

        if len(max(categories, key=len)) > 8:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/stacked_bar_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_stacked_bar_plotly(
        self, data: Dict[str, Dict[str, float]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create stacked bar chart using plotly."""
        fig = go.Figure()
        series_names = list(data.keys())
        categories = list(data[series_names[0]].keys()) if series_names else []

        for series in series_names:
            values = [data[series].get(cat, 0) for cat in categories]
            fig.add_trace(go.Bar(name=series, x=categories, y=values))

        fig.update_layout(barmode='stack', title=title, xaxis_title=xlabel, yaxis_title=ylabel, template='plotly_white')
        if output_path is None:
            output_path = f"./output/charts/stacked_bar_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)
        return output_path

    def create_donut_chart(
        self,
        data: Dict[str, float],
        title: str = "Donut Chart",
        output_path: Optional[str] = None
    ) -> str:
        """Create a donut chart."""
        if self.library == "matplotlib":
            return self._create_donut_matplotlib(data, title, output_path)
        elif self.library == "plotly":
            return self._create_donut_plotly(data, title, output_path)

    def _create_donut_matplotlib(self, data: Dict[str, float], title: str, output_path: Optional[str]) -> str:
        """Create donut chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 8))
        categories = list(data.keys())
        values = list(data.values())
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))

        wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%',
                                          startangle=90, colors=colors, pctdistance=0.75)
        # Create donut by adding white circle in center
        centre_circle = plt.Circle((0, 0), 0.5, fc='white')
        ax.add_patch(centre_circle)
        ax.set_title(title, fontsize=16, fontweight='bold')

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/donut_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_donut_plotly(self, data: Dict[str, float], title: str, output_path: Optional[str]) -> str:
        """Create donut chart using plotly."""
        fig = go.Figure(data=[go.Pie(labels=list(data.keys()), values=list(data.values()), hole=0.4)])
        fig.update_layout(title=title)
        if output_path is None:
            output_path = f"./output/charts/donut_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=800)
        return output_path

    def create_area_chart(
        self,
        data: Dict[str, List[float]],
        title: str = "Area Chart",
        xlabel: str = "X",
        ylabel: str = "Y",
        output_path: Optional[str] = None
    ) -> str:
        """Create an area chart."""
        if self.library == "matplotlib":
            return self._create_area_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_area_plotly(data, title, xlabel, ylabel, output_path)

    def _create_area_matplotlib(
        self, data: Dict[str, List[float]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create area chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Blues(np.linspace(0.3, 0.8, len(data)))

        for i, (label, values) in enumerate(data.items()):
            ax.fill_between(range(len(values)), values, alpha=0.6, label=label, color=colors[i])
            ax.plot(range(len(values)), values, color=colors[i], linewidth=2)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/area_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_area_plotly(
        self, data: Dict[str, List[float]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create area chart using plotly."""
        fig = go.Figure()
        for label, values in data.items():
            fig.add_trace(go.Scatter(x=list(range(len(values))), y=values, fill='tozeroy', name=label, mode='lines'))
        fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel, template='plotly_white')
        if output_path is None:
            output_path = f"./output/charts/area_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)
        return output_path

    def create_radar_chart(
        self,
        data: Dict[str, Dict[str, float]],
        title: str = "Radar Chart",
        output_path: Optional[str] = None
    ) -> str:
        """Create a radar/spider chart. Data format: {series_name: {dimension: value}}"""
        if self.library == "matplotlib":
            return self._create_radar_matplotlib(data, title, output_path)
        elif self.library == "plotly":
            return self._create_radar_plotly(data, title, output_path)

    def _create_radar_matplotlib(self, data: Dict[str, Dict[str, float]], title: str, output_path: Optional[str]) -> str:
        """Create radar chart using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        series_names = list(data.keys())
        if not series_names:
            raise ValueError("No data provided for radar chart")

        categories = list(data[series_names[0]].keys())
        num_vars = len(categories)
        angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
        angles += angles[:1]  # Complete the loop

        colors = plt.cm.Set1(np.linspace(0, 1, len(series_names)))

        for i, series in enumerate(series_names):
            values = [data[series].get(cat, 0) for cat in categories]
            values += values[:1]  # Complete the loop
            ax.plot(angles, values, 'o-', linewidth=2, label=series, color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_title(title, fontsize=16, fontweight='bold', y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/radar_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_radar_plotly(self, data: Dict[str, Dict[str, float]], title: str, output_path: Optional[str]) -> str:
        """Create radar chart using plotly."""
        fig = go.Figure()
        series_names = list(data.keys())
        categories = list(data[series_names[0]].keys()) if series_names else []

        for series in series_names:
            values = [data[series].get(cat, 0) for cat in categories]
            fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=series))

        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, title=title)
        if output_path is None:
            output_path = f"./output/charts/radar_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=800)
        return output_path

    def create_scatter_chart(
        self,
        data: Dict[str, List[Tuple[float, float]]],
        title: str = "Scatter Plot",
        xlabel: str = "X",
        ylabel: str = "Y",
        output_path: Optional[str] = None
    ) -> str:
        """Create a scatter plot. Data format: {series_name: [(x1, y1), (x2, y2), ...]}"""
        if self.library == "matplotlib":
            return self._create_scatter_matplotlib(data, title, xlabel, ylabel, output_path)
        elif self.library == "plotly":
            return self._create_scatter_plotly(data, title, xlabel, ylabel, output_path)

    def _create_scatter_matplotlib(
        self, data: Dict[str, List[Tuple[float, float]]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create scatter plot using matplotlib."""
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Set1(np.linspace(0, 1, len(data)))

        for i, (label, points) in enumerate(data.items()):
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            ax.scatter(x_vals, y_vals, label=label, color=colors[i], alpha=0.7, s=80)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        if output_path is None:
            output_path = f"./output/charts/scatter_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    def _create_scatter_plotly(
        self, data: Dict[str, List[Tuple[float, float]]], title: str, xlabel: str, ylabel: str, output_path: Optional[str]
    ) -> str:
        """Create scatter plot using plotly."""
        fig = go.Figure()
        for label, points in data.items():
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', name=label))
        fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel, template='plotly_white')
        if output_path is None:
            output_path = f"./output/charts/scatter_chart_{hash(title) % 10000}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_image(output_path, width=1000, height=600)
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
        elif chart_type == 'horizontal_bar':
            return self.create_horizontal_bar_chart(data, title, xlabel, ylabel, output_path)
        elif chart_type == 'stacked_bar':
            return self.create_stacked_bar_chart(data, title, xlabel, ylabel, output_path)
        elif chart_type == 'pie':
            return self.create_pie_chart(data, title, output_path)
        elif chart_type == 'donut':
            return self.create_donut_chart(data, title, output_path)
        elif chart_type == 'line':
            return self.create_line_chart(data, title, xlabel, ylabel, output_path)
        elif chart_type == 'area':
            return self.create_area_chart(data, title, xlabel, ylabel, output_path)
        elif chart_type == 'radar':
            return self.create_radar_chart(data, title, output_path)
        elif chart_type == 'scatter':
            return self.create_scatter_chart(data, title, xlabel, ylabel, output_path)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}. Supported: bar, horizontal_bar, stacked_bar, pie, donut, line, area, radar, scatter")


class SmartChartGenerator:
    """Intelligently generates charts for presentation slides using LLM."""

    # Prompt for LLM to generate chart data
    CHART_DATA_PROMPT = """You are a data visualization expert. Based on the slide content below, generate appropriate chart data.

Slide Title: {title}
Slide Content:
{content}

Analyze this slide and determine:
1. Whether a chart would enhance this slide
2. The most suitable chart type
3. Realistic sample data that matches the topic

Respond with a JSON object ONLY (no markdown, no explanation):
{{
    "needs_chart": true/false,
    "chart_type": "bar|horizontal_bar|stacked_bar|pie|donut|line|area|radar|scatter",
    "title": "Chart title in same language as slide",
    "xlabel": "X-axis label (if applicable)",
    "ylabel": "Y-axis label (if applicable)",
    "data": <data in appropriate format for chart type>,
    "reason": "Brief explanation why this chart type was chosen"
}}

Data formats by chart type:
- bar/horizontal_bar/pie/donut: {{"Category1": value1, "Category2": value2, ...}}
- line/area: {{"Series1": [v1, v2, v3, ...], "Series2": [v1, v2, v3, ...]}}
- stacked_bar/radar: {{"Series1": {{"Cat1": v1, "Cat2": v2}}, "Series2": {{"Cat1": v1, "Cat2": v2}}}}
- scatter: {{"Series1": [[x1, y1], [x2, y2], ...]}}

If no chart is needed, set needs_chart to false and leave other fields empty.
Generate realistic data values that would make sense for the topic (e.g., percentages should sum to ~100 for pie charts)."""

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

    def _detect_chart_type(self, title: str, content: str) -> Optional[str]:
        """Detect chart type based on keywords."""
        text = (title + " " + content).lower()

        for chart_type, keywords in CHART_TYPE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return chart_type
        return None

    def _generate_sample_data(self, chart_type: str, title: str, content: str) -> Dict[str, Any]:
        """Generate sample data based on chart type and content context."""
        # Extract potential category names from content
        words = [w.strip(',.;:()[]') for w in content.split() if len(w) > 2][:6]
        categories = words[:4] if words else ['A', 'B', 'C', 'D']

        if chart_type in ['bar', 'horizontal_bar']:
            return {cat: round(50 + 50 * (i + 1) / len(categories), 1) for i, cat in enumerate(categories)}
        elif chart_type in ['pie', 'donut']:
            total = 100
            values = []
            for i in range(len(categories) - 1):
                v = round(total * (0.15 + 0.2 * (i + 1) / len(categories)), 1)
                values.append(v)
                total -= v
            values.append(round(total, 1))
            return {cat: val for cat, val in zip(categories, values)}
        elif chart_type in ['line', 'area']:
            return {'趋势': [round(20 + i * 10 + (i % 2) * 5, 1) for i in range(6)]}
        elif chart_type == 'stacked_bar':
            return {
                '类型A': {cat: round(20 + 10 * i, 1) for i, cat in enumerate(categories[:3])},
                '类型B': {cat: round(15 + 8 * i, 1) for i, cat in enumerate(categories[:3])}
            }
        elif chart_type == 'radar':
            dims = categories[:5] if len(categories) >= 5 else ['维度1', '维度2', '维度3', '维度4', '维度5']
            return {
                '当前': {d: round(60 + 10 * (i % 3), 1) for i, d in enumerate(dims)},
                '目标': {d: round(80 + 5 * (i % 2), 1) for i, d in enumerate(dims)}
            }
        elif chart_type == 'scatter':
            return {'数据点': [[round(10 + i * 8, 1), round(20 + i * 6 + (i % 2) * 10, 1)] for i in range(8)]}
        else:
            return {cat: round(50 + 20 * i, 1) for i, cat in enumerate(categories)}

    async def generate_chart_data_with_llm(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """Use LLM to generate intelligent chart data."""
        if not self.llm_generator:
            return None

        prompt = self.CHART_DATA_PROMPT.format(title=title, content=content)

        try:
            # Call LLM to generate chart specification
            response = await self.llm_generator._call_llm(prompt)

            # Parse JSON response
            response_text = response.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            response_text = response_text.strip()

            spec = json.loads(response_text)

            if spec.get('needs_chart', False):
                # Convert scatter data format if needed
                if spec.get('chart_type') == 'scatter' and 'data' in spec:
                    for series, points in spec['data'].items():
                        spec['data'][series] = [tuple(p) for p in points]
                return spec

        except Exception as e:
            self.logger.warning(f"LLM chart generation failed: {e}")

        return None

    def suggest_chart_for_slide(self, slide_title: str, slide_content: str) -> Optional[Dict[str, Any]]:
        """
        Suggest chart specification for a slide using rule-based detection.

        Args:
            slide_title: Slide title
            slide_content: Slide content

        Returns:
            Chart specification or None
        """
        # Detect chart type based on keywords
        chart_type = self._detect_chart_type(slide_title, slide_content)

        if not chart_type:
            return None

        # Generate appropriate sample data
        data = self._generate_sample_data(chart_type, slide_title, slide_content)

        spec = {
            'type': chart_type,
            'title': slide_title,
            'data': data,
        }

        # Add axis labels for appropriate chart types
        if chart_type in ['bar', 'horizontal_bar', 'stacked_bar', 'line', 'area', 'scatter']:
            spec['xlabel'] = '类别' if any(c > '\u4e00' for c in slide_title) else 'Category'
            spec['ylabel'] = '数值' if any(c > '\u4e00' for c in slide_title) else 'Value'

        return spec

    async def generate_charts_for_outline_async(
        self,
        outline: PresentationOutline,
        use_llm: bool = True,
        auto_detect: bool = True
    ) -> Dict[int, str]:
        """
        Generate charts for presentation outline (async version).

        Args:
            outline: Presentation outline
            use_llm: Use LLM to generate intelligent chart data
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
            spec = None

            # Try LLM-based generation first
            if use_llm and self.llm_generator:
                spec = await self.generate_chart_data_with_llm(slide.title, content)

            # Fall back to rule-based detection
            if not spec and auto_detect:
                spec = self.suggest_chart_for_slide(slide.title, content)

            if spec:
                try:
                    chart_path = self.chart_generator.create_chart_from_spec(spec)
                    chart_map[slide.slide_number] = chart_path
                    self.logger.info(f"Generated {spec.get('type', 'unknown')} chart for slide {slide.slide_number}")
                except Exception as e:
                    self.logger.error(f"Failed to generate chart for slide {slide.slide_number}: {e}")

        return chart_map

    def generate_charts_for_outline(
        self,
        outline: PresentationOutline,
        use_llm: bool = False,
        auto_detect: bool = True
    ) -> Dict[int, str]:
        """
        Generate charts for presentation outline (sync version).

        Args:
            outline: Presentation outline
            use_llm: Use LLM to generate intelligent chart data (requires async)
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

            # Use rule-based detection for sync version
            if auto_detect:
                spec = self.suggest_chart_for_slide(slide.title, content)

                if spec:
                    try:
                        chart_path = self.chart_generator.create_chart_from_spec(spec)
                        chart_map[slide.slide_number] = chart_path
                        self.logger.info(f"Generated {spec.get('type', 'unknown')} chart for slide {slide.slide_number}")
                    except Exception as e:
                        self.logger.error(f"Failed to generate chart for slide {slide.slide_number}: {e}")

        return chart_map
