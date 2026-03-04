"""Interactive dashboard generation for STRATICA.

Based on paper Section 5.4:
- TCI Basin Browser: Interactive world map of TCI scores
- Back-Cast Simulator: Interactive parameter exploration
- Deep-Time Analog Finder: Search engine for past climate states
"""

import numpy as np
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import warnings

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. Dashboard generation will be limited.")

try:
    import dash
    from dash import dcc, html, Input, Output, callback
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    warnings.warn("Dash not available. Interactive dashboard requires Dash.")


class DashboardGenerator:
    """Generate interactive dashboards for STRATICA."""
    
    def __init__(self, title: str = "STRATICA Intelligence Center"):
        """
        Initialize dashboard generator.
        
        Args:
            title: Dashboard title
        """
        self.title = title
        self.data = {}
        self.figures = {}
    
    def add_basin_data(
        self,
        basins: List[Dict[str, Any]],
        tci_scores: Dict[str, float]
    ):
        """
        Add basin data for TCI Basin Browser.
        
        Args:
            basins: List of basin dictionaries with 'name', 'lat', 'lon'
            tci_scores: Dictionary mapping basin names to TCI scores
        """
        self.data['basins'] = basins
        self.data['tci_scores'] = tci_scores
    
    def add_parameter_data(
        self,
        parameter_ranges: Dict[str, Tuple[float, float]],
        tci_sensitivity: Dict[str, np.ndarray]
    ):
        """
        Add parameter data for Back-Cast Simulator.
        
        Args:
            parameter_ranges: Parameter name to (min, max)
            tci_sensitivity: Parameter name to TCI sensitivity array
        """
        self.data['parameter_ranges'] = parameter_ranges
        self.data['tci_sensitivity'] = tci_sensitivity
    
    def add_analog_data(
        self,
        climate_events: List[Dict[str, Any]]
    ):
        """
        Add climate event data for Deep-Time Analog Finder.
        
        Args:
            climate_events: List of event dictionaries with 
                           'name', 'age', 'co2', 'temp', 'ice'
        """
        self.data['climate_events'] = climate_events
    
    def create_tci_basin_map(self) -> Optional[go.Figure]:
        """Create interactive map of TCI scores by basin."""
        if not PLOTLY_AVAILABLE:
            warnings.warn("Plotly not available. Cannot create map.")
            return None
        
        if 'basins' not in self.data or 'tci_scores' not in self.data:
            return None
        
        basins = self.data['basins']
        tci_scores = self.data['tci_scores']
        
        # Prepare data
        lats = [b.get('lat', 0) for b in basins]
        lons = [b.get('lon', 0) for b in basins]
        names = [b.get('name', 'Unknown') for b in basins]
        scores = [tci_scores.get(name, 0) for name in names]
        
        # Create color scale
        colorscale = [
            [0, 'red'],
            [0.38, 'orange'],
            [0.55, 'yellow'],
            [0.72, 'lightgreen'],
            [0.88, 'darkgreen'],
            [1.0, 'darkgreen']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            text=[f"{name}<br>TCI: {score:.3f}" for name, score in zip(names, scores)],
            mode='markers',
            marker=dict(
                size=12,
                color=scores,
                colorscale=colorscale,
                cmin=0,
                cmax=1,
                colorbar=dict(title="TCI Score"),
                line=dict(width=1, color='black')
            )
        ))
        
        fig.update_layout(
            title="TCI Basin Browser",
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)',
                coastlinecolor='rgb(204, 204, 204)'
            )
        )
        
        self.figures['basin_map'] = fig
        return fig
    
    def create_parameter_simulator(self) -> Optional[go.Figure]:
        """Create interactive parameter sensitivity simulator."""
        if not PLOTLY_AVAILABLE:
            return None
        
        if 'parameter_ranges' not in self.data:
            return None
        
        ranges = self.data['parameter_ranges']
        
        fig = make_subplots(
            rows=len(ranges),
            cols=1,
            subplot_titles=list(ranges.keys())
        )
        
        for i, (param, (min_val, max_val)) in enumerate(ranges.items()):
            x = np.linspace(min_val, max_val, 100)
            y = 0.5 + 0.5 * np.sin((x - min_val) / (max_val - min_val) * np.pi)  # Dummy sensitivity
            
            fig.add_trace(
                go.Scatter(x=x, y=y, mode='lines', name=param),
                row=i+1, col=1
            )
            
            fig.update_xaxes(title_text=param, row=i+1, col=1)
            fig.update_yaxes(title_text="TCI Sensitivity", row=i+1, col=1)
        
        fig.update_layout(
            title="Back-Cast Simulator",
            height=300 * len(ranges),
            showlegend=False
        )
        
        self.figures['parameter_simulator'] = fig
        return fig
    
    def create_analog_finder(self) -> Optional[go.Figure]:
        """Create interactive analog finder plot."""
        if not PLOTLY_AVAILABLE:
            return None
        
        if 'climate_events' not in self.data:
            return None
        
        events = self.data['climate_events']
        
        # Extract data
        names = [e.get('name', 'Unknown') for e in events]
        ages = [e.get('age', 0) for e in events]
        co2 = [e.get('co2', 280) for e in events]
        temp = [e.get('temp', 0) for e in events]
        ice = [e.get('ice', 0) for e in events]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CO₂ Level', 'Temperature Anomaly', 'Ice Volume', 'Age Distribution')
        )
        
        fig.add_trace(
            go.Bar(x=names, y=co2, marker_color='orange'),
            row=1, col=1
        )
        fig.update_xaxes(title_text="Event", tickangle=45, row=1, col=1)
        fig.update_yaxes(title_text="CO₂ (ppm)", row=1, col=1)
        
        fig.add_trace(
            go.Bar(x=names, y=temp, marker_color='red'),
            row=1, col=2
        )
        fig.update_xaxes(title_text="Event", tickangle=45, row=1, col=2)
        fig.update_yaxes(title_text="ΔT (°C)", row=1, col=2)
        
        fig.add_trace(
            go.Bar(x=names, y=ice, marker_color='blue'),
            row=2, col=1
        )
        fig.update_xaxes(title_text="Event", tickangle=45, row=2, col=1)
        fig.update_yaxes(title_text="Ice Volume (m SLE)", row=2, col=1)
        
        fig.add_trace(
            go.Scatter(x=ages, y=[1]*len(ages), mode='markers',
                      marker=dict(size=10, color=ages, colorscale='Viridis'),
                      text=names, hovertemplate='<b>%{text}</b><br>Age: %{x} Ma'),
            row=2, col=2
        )
        fig.update_xaxes(title_text="Age (Ma)", row=2, col=2)
        fig.update_yaxes(showticklabels=False, row=2, col=2)
        
        fig.update_layout(
            title="Deep-Time Analog Finder",
            height=800,
            showlegend=False
        )
        
        self.figures['analog_finder'] = fig
        return fig
    
    def generate_html(self, output_path: str = "dashboard.html") -> str:
        """
        Generate standalone HTML dashboard.
        
        Args:
            output_path: Path to save HTML file
        
        Returns:
            HTML string
        """
        if not PLOTLY_AVAILABLE:
            return "<html><body>Plotly not available</body></html>"
        
        # Create figures if not already created
        if 'basin_map' not in self.figures:
            self.create_tci_basin_map()
        if 'parameter_simulator' not in self.figures:
            self.create_parameter_simulator()
        if 'analog_finder' not in self.figures:
            self.create_analog_finder()
        
        # Build HTML
        html_parts = []
        html_parts.append(f"<html><head><title>{self.title}</title>")
        html_parts.append("<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>")
        html_parts.append("<style>")
        html_parts.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append(".header { text-align: center; margin-bottom: 30px; }")
        html_parts.append(".plot-container { margin-bottom: 40px; }")
        html_parts.append("</style>")
        html_parts.append("</head><body>")
        
        html_parts.append(f"<div class='header'><h1>{self.title}</h1></div>")
        
        # Add plots
        for name, fig in self.figures.items():
            if fig is not None:
                html_parts.append(f"<div class='plot-container' id='{name}'>")
                html_parts.append(fig.to_html(full_html=False, include_plotlyjs=False))
                html_parts.append("</div>")
        
        html_parts.append("</body></html>")
        
        html = "\n".join(html_parts)
        
        # Save to file
        with open(output_path, 'w') as f:
            f.write(html)
        
        return html
    
    def create_dash_app(self, debug: bool = False):
        """
        Create Dash application for interactive dashboard.
        
        Returns:
            Dash app object
        """
        if not DASH_AVAILABLE:
            warnings.warn("Dash not available. Cannot create app.")
            return None
        
        app = dash.Dash(__name__)
        
        # Create figures
        self.create_tci_basin_map()
        self.create_parameter_simulator()
        self.create_analog_finder()
        
        # Define layout
        app.layout = html.Div([
            html.H1(self.title, style={'textAlign': 'center'}),
            
            html.Div([
                html.H2("TCI Basin Browser"),
                dcc.Graph(figure=self.figures.get('basin_map', go.Figure()))
            ]),
            
            html.Div([
                html.H2("Back-Cast Simulator"),
                dcc.Graph(figure=self.figures.get('parameter_simulator', go.Figure()))
            ]),
            
            html.Div([
                html.H2("Deep-Time Analog Finder"),
                dcc.Graph(figure=self.figures.get('analog_finder', go.Figure()))
            ])
        ])
        
        return app
    
    def export_data(self, output_path: str = "dashboard_data.json"):
        """
        Export dashboard data to JSON.
        
        Args:
            output_path: Path to save JSON file
        """
        export_data = {
            'title': self.title,
            'basins': self.data.get('basins', []),
            'tci_scores': self.data.get('tci_scores', {}),
            'parameter_ranges': self.data.get('parameter_ranges', {}),
            'climate_events': self.data.get('climate_events', [])
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


def generate_dashboard(
    basin_data: Optional[List[Dict]] = None,
    parameter_data: Optional[Dict] = None,
    event_data: Optional[List[Dict]] = None,
    output_path: str = "dashboard.html",
    **kwargs
) -> str:
    """
    Convenience function to generate dashboard.
    
    Args:
        basin_data: List of basin dictionaries
        parameter_data: Parameter ranges and sensitivity
        event_data: List of climate events
        output_path: Path to save HTML file
    
    Returns:
        HTML string
    """
    generator = DashboardGenerator(**kwargs)
    
    if basin_data:
        # Extract TCI scores
        tci_scores = {b.get('name'): b.get('tci', 0) for b in basin_data}
        generator.add_basin_data(basin_data, tci_scores)
    
    if parameter_data:
        generator.add_parameter_data(
            parameter_data.get('ranges', {}),
            parameter_data.get('sensitivity', {})
        )
    
    if event_data:
        generator.add_analog_data(event_data)
    
    return generator.generate_html(output_path)
