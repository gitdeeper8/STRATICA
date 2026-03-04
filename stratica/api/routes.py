"""API route definitions for STRATICA."""

from flask import Blueprint, request, jsonify
import numpy as np
from typing import Dict, Any

# Create blueprint
api_router = Blueprint('api', __name__, url_prefix='/api/v1')


@api_router.route('/analyze', methods=['POST'])
def analyze():
    """Analyze stratigraphic data."""
    # This is a placeholder - actual implementation in app.py
    return jsonify({'status': 'endpoint active', 'version': 'v1'})


@api_router.route('/tci', methods=['POST'])
def compute_tci():
    """Compute TCI index."""
    data = request.get_json()
    
    if not data or 'parameters' not in data:
        return jsonify({'error': 'No parameters provided'}), 400
    
    parameters = data['parameters']
    weights = data.get('weights', {})
    
    try:
        from stratica.core import TCIIndex
        tci_index = TCIIndex(weights)
        
        tci = tci_index.compute(parameters)
        classification = tci_index.classify(tci)
        
        return jsonify({
            'success': True,
            'tci': tci,
            'classification': classification,
            'functional': tci_index.is_functional(tci)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_router.route('/parameters', methods=['GET'])
def get_parameters():
    """Get list of available parameters."""
    from stratica.utils.constants import PARAMETER_WEIGHTS
    
    return jsonify({
        'parameters': [
            {'name': k, 'weight': v} 
            for k, v in PARAMETER_WEIGHTS.items()
        ]
    })


@api_router.route('/backcast', methods=['POST'])
def backcast():
    """Perform temporal back-casting."""
    data = request.get_json()
    
    if not data or 'timeseries' not in data:
        return jsonify({'error': 'No timeseries provided'}), 400
    
    try:
        from stratica.models.backcast import TemporalBackcast
        
        timeseries = np.array(data['timeseries'])
        age = np.array(data.get('age', np.arange(len(timeseries))))
        mask = np.array(data.get('mask', None))
        
        backcast = TemporalBackcast()
        filled = backcast.fill_gaps(timeseries, age, mask)
        
        return jsonify({
            'success': True,
            'filled': filled.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_router.route('/validate', methods=['POST'])
def validate():
    """Validate data against reference."""
    data = request.get_json()
    
    if not data or 'values' not in data or 'reference' not in data:
        return jsonify({'error': 'Values and reference required'}), 400
    
    try:
        from stratica.processing.quality_control import QualityController
        
        values = np.array(data['values'])
        reference = np.array(data['reference'])
        
        qc = QualityController()
        metrics = qc.validate_against_reference(values, reference)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_router.route('/species', methods=['GET'])
def list_species():
    """List microfossil species."""
    # Placeholder - would load from database
    species = [
        'Globigerinoides_ruber',
        'Globigerinoides_sacculifer',
        'Neogloboquadrina_pachyderma',
        'Neogloboquadrina_dutertrei',
        'Globorotalia_truncatulinoides',
        'Globorotalia_menardii',
        'Globigerina_bulloides',
        'Orbulina_universa',
        'Cibicidoides_wuellerstorfi',
        'Uvigerina_peregrina'
    ]
    
    return jsonify({'species': species})


@api_router.route('/basins', methods=['GET'])
def list_basins():
    """List sedimentary basins."""
    basins = [
        {'id': 'shatsky-rise', 'name': 'Shatsky Rise', 'ocean': 'Pacific'},
        {'id': 'walvis-ridge', 'name': 'Walvis Ridge', 'ocean': 'Atlantic'},
        {'id': 'demerara-rise', 'name': 'Demerara Rise', 'ocean': 'Atlantic'},
        {'id': 'iberian-margin', 'name': 'Iberian Margin', 'ocean': 'Atlantic'},
        {'id': 'ceara-rise', 'name': 'Ceará Rise', 'ocean': 'Atlantic'},
        {'id': 'kerguelen', 'name': 'Kerguelen Plateau', 'ocean': 'Southern'},
        {'id': 'campbell', 'name': 'Campbell Plateau', 'ocean': 'Pacific'}
    ]
    
    return jsonify({'basins': basins})


@api_router.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'api_version': 'v1'
    })
