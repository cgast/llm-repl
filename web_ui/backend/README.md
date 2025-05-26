# LLM-REPL Web UI Backend

This is the backend API for the LLM-REPL Web UI. It provides a RESTful API and WebSocket interface for the frontend to interact with the LLM-REPL engine.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Flask application:

```bash
python app.py
```

The API will be available at http://localhost:5000 by default.

You can customize the host and port using command-line arguments:

```bash
python app.py --host 0.0.0.0 --port 5000 --debug
```

## Configuration

The backend server can be configured using command-line arguments:

- `--host`: The host to run the server on (default: 0.0.0.0)
- `--port`: The port to run the server on (default: 5000)
- `--debug`: Run in debug mode (default: False)

## Deployment

To deploy the backend to production:

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Flask application with the appropriate host and port:

```bash
python app.py --host 0.0.0.0 --port 5000
```

For production deployments, you might want to use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -b 0.0.0.0:5000 app:app
```

Or use a process manager like Supervisor to ensure the server stays running:

```
[program:llm-repl-backend]
command=python app.py --host 0.0.0.0 --port 5000
directory=/path/to/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/llm-repl-backend.err.log
stdout_logfile=/var/log/llm-repl-backend.out.log
```

## API Endpoints

### Notebooks

- `GET /api/notebooks` - Get a list of all notebooks
- `POST /api/notebooks` - Create a new notebook
- `GET /api/notebooks/<notebook_id>` - Get a notebook by ID
- `PUT /api/notebooks/<notebook_id>` - Update a notebook
- `DELETE /api/notebooks/<notebook_id>` - Delete a notebook
- `POST /api/notebooks/<notebook_id>/save` - Save a notebook to a file
- `POST /api/notebooks/load` - Load a notebook from a file

### Cells

- `GET /api/notebooks/<notebook_id>/cells` - Get all cells in a notebook
- `POST /api/notebooks/<notebook_id>/cells` - Create a new cell in a notebook
- `GET /api/notebooks/<notebook_id>/cells/<cell_id>` - Get a cell by ID
- `PUT /api/notebooks/<notebook_id>/cells/<cell_id>` - Update a cell
- `DELETE /api/notebooks/<notebook_id>/cells/<cell_id>` - Delete a cell
- `POST /api/notebooks/<notebook_id>/cells/<cell_id>/execute` - Execute a cell
- `POST /api/notebooks/<notebook_id>/execute_all` - Execute all cells in a notebook

### State

- `GET /api/notebooks/<notebook_id>/state` - Get the state of a notebook

### LLM Providers

- `GET /api/llm/providers` - Get available LLM providers
- `PUT /api/llm/provider` - Set the LLM provider

## WebSocket Events

### Server to Client

- `cell_execution_started` - Emitted when a cell execution starts
- `cell_execution_completed` - Emitted when a cell execution completes
- `cell_execution_failed` - Emitted when a cell execution fails
- `notebook_execution_started` - Emitted when a notebook execution starts
- `notebook_execution_completed` - Emitted when a notebook execution completes
- `notebook_execution_failed` - Emitted when a notebook execution fails

### Client to Server

- `connect` - Emitted when a client connects
- `disconnect` - Emitted when a client disconnects
