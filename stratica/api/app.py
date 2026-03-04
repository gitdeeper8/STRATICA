"""REST API for STRATICA.

Provides endpoints for:
- TCI analysis
- Parameter computation
- Back-casting
- Data retrieval
"""

import os
import json
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    import warnings
    warnings.warn("Flask not available. API will not work.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def create_app(config_path: Optional[str] = None):
    """
    Create Flask application for STRATICA API.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Flask app
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for API")
    
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    app.config['STRATICA_CONFIG'] = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                app.config['STRATICA_CONFIG'] = json.load(f)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                import yaml
                app.config['STRATICA_CONFIG'] = yaml.safe_load(f)
    
    # Import STRATICA modules
    try:
        from stratica.core import StratigraphicAnalyzer, TCIIndex
        from stratica.parameters import (
            LithologicalDepositionRate, IsotopeFractionation,
            MicroFossilAssemblage, MagneticSusceptibility,
            GeochemicalAnomalyIndex, PalynologicalYieldScore,
            VarveSedimentaryIntegrity, ThermalDiffusionModel,
            CyclostratigraphicEnergyCycle
        )
        from stratica.models.backcast import TemporalBackcast
        
        STRATICA_AVAILABLE = True
    except ImportError:
        STRATICA_AVAILABLE = False
        app.logger.warning("STRATICA core modules not available")
    
    @app.route('/')
    def index():
        """API root endpoint."""
        return jsonify({
            'name': 'STRATICA API',
            'version': '1.0.0',
            'status': 'active',
            'endpoints': [
                '/health',
                '/analyze',
                '/parameters',
                '/backcast',
                '/basins',
                '/petm'
            ]
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'stratica_available': STRATICA_AVAILABLE,
            'flask_version': flask.__version__
        })
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        """
        Run TCI analysis on uploaded data.
        
        Expected JSON:
        {
            "data": {
                "depth": [float],
                "values": {"param1": [float], ...}
            },
            "options": {
                "weights": {...},
                "thresholds": {...}
            }
        }
        """
        if not STRATICA_AVAILABLE:
            return jsonify({'error': 'STRATICA core not available'}), 503
        
        try:
            req_data = request.get_json()
            
            if not req_data or 'data' not in req_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Initialize analyzer
            config = app.config['STRATICA_CONFIG']
            analyzer = StratigraphicAnalyzer(config)
            
            # Run analysis
            data = req_data['data']
            options = req_data.get('options', {})
            
            # Convert to appropriate format
            depth = np.array(data.get('depth', []))
            
            # Compute TCI
            results = analyzer.compute_tci(data)
            
            # Generate profile
            profile = analyzer.generate_profile(results)
            
            return jsonify({
                'success': True,
                'tci': results.tci_composite,
                'classification': results.classification,
                'parameters': results.parameters,
                'profile': profile
            })
            
        except Exception as e:
            app.logger.error(f"Analysis error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/parameters', methods=['GET'])
    def list_parameters():
        """List available parameters and their weights."""
        from stratica.utils.constants import PARAMETER_WEIGHTS
        
        return jsonify({
            'parameters': [
                {
                    'name': name,
                    'weight': weight,
                    'description': _get_param_description(name)
                }
                for name, weight in PARAMETER_WEIGHTS.items()
            ]
        })
    
    @app.route('/parameters/<param_name>', methods=['POST'])
    def compute_parameter(param_name):
        """
        Compute a single parameter.
        
        Expected JSON:
        {
            "data": {...},
            "options": {...}
        }
        """
        if not STRATICA_AVAILABLE:
            return jsonify({'error': 'STRATICA core not available'}), 503
        
        param_classes = {
            'LDR': LithologicalDepositionRate,
            'ISO': IsotopeFractionation,
            'MFA': MicroFossilAssemblage,
            'MAG': MagneticSusceptibility,
            'GCH': GeochemicalAnomalyIndex,
            'PYS': PalynologicalYieldScore,
            'VSI': VarveSedimentaryIntegrity,
            'TDM': ThermalDiffusionModel,
            'CEC': CyclostratigraphicEnergyCycle
        }
        
        if param_name.upper() not in param_classes:
            return jsonify({'error': f'Unknown parameter: {param_name}'}), 400
        
        try:
            req_data = request.get_json()
            
            if not req_data or 'data' not in req_data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Initialize parameter
            param_class = param_classes[param_name.upper()]
            param = param_class()
            
            # Compute
            data = req_data['data']
            value = param(data)
            
            return jsonify({
                'success': True,
                'parameter': param_name.upper(),
                'raw_value': value,
                'normalized': param.normalized_score,
                'weight': param.weight
            })
            
        except Exception as e:
            app.logger.error(f"Parameter computation error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/backcast', methods=['POST'])
    def backcast():
        """
        Run temporal back-casting to fill gaps.
        
        Expected JSON:
        {
            "timeseries": [float],
            "age": [float],
            "mask": [bool] (optional)
        }
        """
        if not STRATICA_AVAILABLE:
            return jsonify({'error': 'STRATICA core not available'}), 503
        
        try:
            req_data = request.get_json()
            
            if not req_data or 'timeseries' not in req_data:
                return jsonify({'error': 'No timeseries provided'}), 400
            
            timeseries = np.array(req_data['timeseries'])
            age = np.array(req_data.get('age', np.arange(len(timeseries))))
            mask = np.array(req_data.get('mask', None))
            
            # Initialize backcast model
            backcast = TemporalBackcast()
            
            # Fill gaps
            filled = backcast.fill_gaps(timeseries, age, mask)
            
            # Estimate uncertainty if requested
            if req_data.get('uncertainty', False):
                mean_filled, std_filled = backcast.backcast_with_uncertainty(
                    timeseries, age, mask
                )
                return jsonify({
                    'success': True,
                    'filled': filled.tolist(),
                    'mean': mean_filled.tolist(),
                    'std': std_filled.tolist()
                })
            
            return jsonify({
                'success': True,
                'filled': filled.tolist()
            })
            
        except Exception as e:
            app.logger.error(f"Backcast error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/basins', methods=['GET'])
    def list_basins():
        """List available sedimentary basins."""
        # Sample basin data
        basins = [
            {'name': 'Shatsky Rise', 'location': 'North Pacific', 'tci': 0.78},
            {'name': 'Walvis Ridge', 'location': 'South Atlantic', 'tci': 0.81},
            {'name': 'Demerara Rise', 'location': 'Equatorial Atlantic', 'tci': 0.74},
            {'name': 'Iberian Margin', 'location': 'North Atlantic', 'tci': 0.83},
            {'name': 'Ceará Rise', 'location': 'Equatorial Atlantic', 'tci': 0.79},
            {'name': 'Kerguelen Plateau', 'location': 'Southern Ocean', 'tci': 0.68},
            {'name': 'Campbell Plateau', 'location': 'Southwest Pacific', 'tci': 0.72}
        ]
        
        return jsonify({'basins': basins})
    
    @app.route('/petm', methods=['GET'])
    def get_petm_data():
        """Get PETM case study data."""
        petm_data = {
            'name': 'Paleocene-Eocene Thermal Maximum',
            'age': 55.9,  # Ma
            'duration_kyr': 200,
            'carbon_release_gtc': 3200,
            'carbon_release_error': 600,
            'warming_c': 5.2,
            'warming_error': 0.8,
            'earth_system_sensitivity': 4.8,
            'ess_error': 0.6,
            'sites': [
                {
                    'name': 'ODP Site 1209B',
                    'location': 'Shatsky Rise',
                    'tci_pre': 0.78,
                    'tci_peak': 0.31,
                    'tci_post': 0.74
                }
            ]
        }
        
        return jsonify(petm_data)
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Upload data file for processing."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Save temporarily
        temp_path = Path('/tmp') / file.filename
        file.save(temp_path)
        
        # Try to read based on extension
        try:
            if temp_path.suffix.lower() == '.csv':
                if PANDAS_AVAILABLE:
                    df = pd.read_csv(temp_path)
                    data = df.to_dict(orient='list')
                else:
                    return jsonify({'error': 'Pandas not available'}), 503
            elif temp_path.suffix.lower() in ['.xlsx', '.xls']:
                if PANDAS_AVAILABLE:
                    df = pd.read_excel(temp_path)
                    data = df.to_dict(orient='list')
                else:
                    return jsonify({'error': 'Pandas not available'}), 503
            elif temp_path.suffix.lower() == '.json':
                with open(temp_path, 'r') as f:
                    data = json.load(f)
            else:
                return jsonify({'error': f'Unsupported file type: {temp_path.suffix}'}), 400
            
            # Clean up
            temp_path.unlink()
            
            return jsonify({
                'success': True,
                'filename': file.filename,
                'columns': list(data.keys()),
                'n_rows': len(next(iter(data.values()))) if data else 0,
                'preview': {k: v[:5] for k, v in data.items()}
            })
            
        except Exception as e:
            temp_path.unlink()
            return jsonify({'error': str(e)}), 500
    
    def _get_param_description(name: str) -> str:
        """Get parameter description."""
        descriptions = {
            'LDR': 'Lithological Deposition Rate - sediment accumulation rate',
            'ISO': 'Stable Isotope Fractionation - δ¹⁸O/δ¹³C paleothermometry',
            'MFA': 'Micro-Fossil Assemblage - biostratigraphic age control',
            'MAG': 'Magnetic Susceptibility - geomagnetic polarity reversals',
            'GCH': 'Geochemical Anomaly Index - trace element event signatures',
            'PYS': 'Palynological Yield Score - terrestrial vegetation history',
            'VSI': 'Varve Sedimentary Integrity - annual lamination preservation',
            'TDM': 'Thermal Diffusion Model - burial depth & thermal maturity',
            'CEC': 'Cyclostratigraphic Energy Cycle - Milankovitch orbital frequencies'
        }
        return descriptions.get(name.upper(), '')
    
    return app


def run_api(host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
    """Run the STRATICA API server."""
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_api()
