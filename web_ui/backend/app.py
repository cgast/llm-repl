#!/usr/bin/env python3
"""
Flask API for LLM-REPL Web UI.

This module provides a RESTful API and WebSocket interface for the LLM-REPL
web UI to interact with the LLM-REPL engine.
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Add the parent directory to the path so we can import the LLM-REPL package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm_repl.notebook import Notebook
from src.llm_repl.cells import MarkdownCell, ComputationCell, PromptCell, MemoryCell
from src.llm_repl.llm import get_llm_provider, set_provider

# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    engineio_logger=True
)

# Dictionary to store active notebooks
notebooks = {}


@app.route('/api/notebooks', methods=['GET'])
def get_notebooks():
    """Get a list of all notebooks."""
    return jsonify({
        'notebooks': [
            {
                'id': notebook_id,
                'name': notebook.name,
                'created_at': notebook.created_at,
                'updated_at': notebook.updated_at,
                'cell_count': len(notebook.cells)
            }
            for notebook_id, notebook in notebooks.items()
        ]
    })


@app.route('/api/notebooks', methods=['POST'])
def create_notebook():
    """Create a new notebook."""
    data = request.json or {}
    name = data.get('name', 'Untitled Notebook')
    
    notebook = Notebook(name=name)
    notebooks[notebook.notebook_id] = notebook
    
    return jsonify({
        'id': notebook.notebook_id,
        'name': notebook.name,
        'created_at': notebook.created_at,
        'updated_at': notebook.updated_at
    })


@app.route('/api/notebooks/<notebook_id>', methods=['GET'])
def get_notebook(notebook_id):
    """Get a notebook by ID."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    return jsonify(notebook.to_dict())


@app.route('/api/notebooks/<notebook_id>', methods=['PUT'])
def update_notebook(notebook_id):
    """Update a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    data = request.json or {}
    notebook = notebooks[notebook_id]
    
    if 'name' in data:
        notebook.name = data['name']
    
    return jsonify({
        'id': notebook.notebook_id,
        'name': notebook.name,
        'created_at': notebook.created_at,
        'updated_at': notebook.updated_at
    })


@app.route('/api/notebooks/<notebook_id>', methods=['DELETE'])
def delete_notebook(notebook_id):
    """Delete a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    del notebooks[notebook_id]
    return jsonify({'success': True})


@app.route('/api/notebooks/<notebook_id>/cells', methods=['GET'])
def get_cells(notebook_id):
    """Get all cells in a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    return jsonify({
        'cells': [
            {
                'id': cell.cell_id,
                'type': cell.__class__.__name__,
                'content': cell.content,
                'outputs': cell.outputs,
                # Include any cell-specific attributes
                **({"model": cell.model, "temperature": cell.temperature} 
                   if isinstance(cell, PromptCell) else {})
            }
            for cell in notebook.cells
        ]
    })


@app.route('/api/notebooks/<notebook_id>/cells', methods=['POST'])
def create_cell(notebook_id):
    """Create a new cell in a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    data = request.json or {}
    cell_type = data.get('type')
    content = data.get('content', '')
    
    notebook = notebooks[notebook_id]
    cell = None
    
    if cell_type == 'markdown':
        cell = notebook.create_markdown_cell(content)
    elif cell_type == 'code':
        cell = notebook.create_computation_cell(content)
    elif cell_type == 'prompt':
        model = data.get('model', 'gpt-4')
        temperature = data.get('temperature', 0.7)
        cell = notebook.create_prompt_cell(content, model=model, temperature=temperature)
    elif cell_type == 'memory':
        cell = notebook.create_memory_cell(content)
    else:
        return jsonify({'error': 'Invalid cell type'}), 400
    
    return jsonify({
        'id': cell.cell_id,
        'type': cell.__class__.__name__,
        'content': cell.content,
        'outputs': cell.outputs
    })


@app.route('/api/notebooks/<notebook_id>/cells/<cell_id>', methods=['GET'])
def get_cell(notebook_id, cell_id):
    """Get a cell by ID."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    for cell in notebook.cells:
        if cell.cell_id == cell_id:
            return jsonify({
                'id': cell.cell_id,
                'type': cell.__class__.__name__,
                'content': cell.content,
                'outputs': cell.outputs,
                # Include any cell-specific attributes
                **({"model": cell.model, "temperature": cell.temperature} 
                   if isinstance(cell, PromptCell) else {})
            })
    
    return jsonify({'error': 'Cell not found'}), 404


@app.route('/api/notebooks/<notebook_id>/cells/<cell_id>', methods=['PUT'])
def update_cell(notebook_id, cell_id):
    """Update a cell."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    for i, cell in enumerate(notebook.cells):
        if cell.cell_id == cell_id:
            data = request.json or {}
            
            if 'content' in data:
                cell.content = data['content']
            
            if isinstance(cell, PromptCell):
                if 'model' in data:
                    cell.model = data['model']
                if 'temperature' in data:
                    cell.temperature = data['temperature']
            
            # Clear outputs since the content has changed
            cell.outputs = []
            
            return jsonify({
                'id': cell.cell_id,
                'type': cell.__class__.__name__,
                'content': cell.content,
                'outputs': cell.outputs
            })
    
    return jsonify({'error': 'Cell not found'}), 404


@app.route('/api/notebooks/<notebook_id>/cells/<cell_id>', methods=['DELETE'])
def delete_cell(notebook_id, cell_id):
    """Delete a cell."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    for i, cell in enumerate(notebook.cells):
        if cell.cell_id == cell_id:
            del notebook.cells[i]
            return jsonify({'success': True})
    
    return jsonify({'error': 'Cell not found'}), 404


@app.route('/api/notebooks/<notebook_id>/cells/<cell_id>/execute', methods=['POST'])
def execute_cell(notebook_id, cell_id):
    """Execute a cell."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    for i, cell in enumerate(notebook.cells):
        if cell.cell_id == cell_id:
            # Execute the cell
            try:
                # Emit a message to indicate execution has started
                socketio.emit('cell_execution_started', {
                    'notebook_id': notebook_id,
                    'cell_id': cell_id
                })
                
                # Execute the cell
                updated_state = cell.execute(notebook.state)
                
                # Update the notebook state
                notebook.state = updated_state
                
                # Emit a message to indicate execution has completed
                socketio.emit('cell_execution_completed', {
                    'notebook_id': notebook_id,
                    'cell_id': cell_id,
                    'outputs': cell.outputs
                })
                
                return jsonify({
                    'id': cell.cell_id,
                    'outputs': cell.outputs
                })
            except Exception as e:
                # Emit a message to indicate execution has failed
                socketio.emit('cell_execution_failed', {
                    'notebook_id': notebook_id,
                    'cell_id': cell_id,
                    'error': str(e)
                })
                
                return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Cell not found'}), 404


@app.route('/api/notebooks/<notebook_id>/execute_all', methods=['POST'])
def execute_all_cells(notebook_id):
    """Execute all cells in a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    try:
        # Emit a message to indicate execution has started
        socketio.emit('notebook_execution_started', {
            'notebook_id': notebook_id
        })
        
        # Execute all cells
        notebook.execute_all_cells()
        
        # Emit a message to indicate execution has completed
        socketio.emit('notebook_execution_completed', {
            'notebook_id': notebook_id
        })
        
        return jsonify({'success': True})
    except Exception as e:
        # Emit a message to indicate execution has failed
        socketio.emit('notebook_execution_failed', {
            'notebook_id': notebook_id,
            'error': str(e)
        })
        
        return jsonify({'error': str(e)}), 500


@app.route('/api/notebooks/<notebook_id>/state', methods=['GET'])
def get_state(notebook_id):
    """Get the state of a notebook."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    notebook = notebooks[notebook_id]
    
    # Convert the state to a serializable format
    serializable_state = {}
    for key, value in notebook.state.items():
        try:
            # Try to convert to JSON
            json.dumps({key: value})
            serializable_state[key] = value
        except (TypeError, OverflowError):
            # If not serializable, convert to string
            serializable_state[key] = str(value)
    
    return jsonify({
        'state': serializable_state
    })


@app.route('/api/notebooks/<notebook_id>/save', methods=['POST'])
def save_notebook(notebook_id):
    """Save a notebook to a file."""
    if notebook_id not in notebooks:
        return jsonify({'error': 'Notebook not found'}), 404
    
    data = request.json or {}
    filepath = data.get('filepath')
    
    if not filepath:
        # Default filename based on notebook name
        notebook = notebooks[notebook_id]
        safe_name = "".join(c if c.isalnum() else "_" for c in notebook.name)
        filepath = f"{safe_name}.llmn"
    
    try:
        notebook = notebooks[notebook_id]
        notebook.save(filepath)
        return jsonify({'success': True, 'filepath': filepath})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notebooks/load', methods=['POST'])
def load_notebook():
    """Load a notebook from a file."""
    data = request.json or {}
    filepath = data.get('filepath')
    
    if not filepath:
        return jsonify({'error': 'Filepath is required'}), 400
    
    try:
        notebook = Notebook.load(filepath)
        notebooks[notebook.notebook_id] = notebook
        return jsonify({
            'id': notebook.notebook_id,
            'name': notebook.name,
            'created_at': notebook.created_at,
            'updated_at': notebook.updated_at
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/llm/providers', methods=['GET'])
def get_llm_providers():
    """Get available LLM providers."""
    # For now, we only support OpenAI and Mock
    return jsonify({
        'providers': ['openai', 'mock']
    })


@app.route('/api/llm/provider', methods=['PUT'])
def set_llm_provider():
    """Set the LLM provider."""
    data = request.json or {}
    provider_type = data.get('type')
    
    if not provider_type:
        return jsonify({'error': 'Provider type is required'}), 400
    
    try:
        provider_args = {}
        if 'api_key' in data:
            provider_args['api_key'] = data['api_key']
        
        set_provider(provider_type, **provider_args)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print('Client disconnected')


if __name__ == '__main__':
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start the LLM-REPL backend server')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to run the server on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    args = parser.parse_args()
    
    socketio.run(app, debug=args.debug, host=args.host, port=args.port, allow_unsafe_werkzeug=True)