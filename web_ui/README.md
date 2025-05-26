# LLM-REPL Web UI

A Jupyter notebook-style web interface for the LLM-REPL engine. This project provides a modern, user-friendly interface for creating and running LLM-REPL notebooks.

## Project Structure

The project is organized into two main components:

- `backend/`: Flask API server that interfaces with the LLM-REPL engine
- `frontend/`: React application that provides the user interface

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm 6+

### Quick Start

The easiest way to start both the backend and frontend servers is to use the provided start script:

```bash
cd web_ui
python start.py
```

This will start both the backend and frontend servers and open the application in your default browser.

You can customize the host and port for both servers using command-line arguments:

```bash
python start.py --backend-host 0.0.0.0 --backend-port 5000 --frontend-host localhost --frontend-port 8081
```

Or using environment variables:

```bash
BACKEND_HOST=0.0.0.0 BACKEND_PORT=5000 FRONTEND_HOST=localhost FRONTEND_PORT=3001 python start.py
```

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Flask server:

```bash
python app.py
```

The backend API will be available at http://localhost:5000.

You can customize the host and port using command-line arguments:

```bash
python app.py --host 0.0.0.0 --port 5000
```

#### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install the required Node.js dependencies:

```bash
npm install
```

3. Start the React development server:

```bash
npm start
```

The frontend will be available at http://localhost:3000.

You can customize the API base URL using environment variables:

```bash
REACT_APP_API_BASE_URL=http://localhost:5000 REACT_APP_SOCKET_URL=http://localhost:5000 npm start
```

### Deployment

To deploy the application on a hyperscaler instance (e.g., AWS, GCP, Azure), you'll need to:

1. Build the frontend for production:

```bash
cd frontend
npm run build
```

2. Serve the frontend using a static file server (e.g., Nginx, Apache) or a Node.js server.

3. Start the backend server with the appropriate host and port:

```bash
cd backend
python app.py --host 0.0.0.0 --port 5000
```

4. Configure the frontend to use the correct API base URL by setting the `REACT_APP_API_BASE_URL` and `REACT_APP_SOCKET_URL` environment variables during the build process:

```bash
REACT_APP_API_BASE_URL=https://api.example.com REACT_APP_SOCKET_URL=https://api.example.com npm run build
```

Alternatively, you can modify the `config.js` file in the frontend source code to use the correct API base URL.

## Features

- **Notebook Management**: Create, edit, delete, save, and load notebooks
- **Cell Types**: Support for all LLM-REPL cell types (Markdown, Code, Prompt, Memory)
- **Cell Execution**: Execute individual cells or run all cells in a notebook
- **Real-time Updates**: WebSocket integration for real-time updates during cell execution
- **State Management**: View and manage the notebook state
- **LLM Provider Configuration**: Configure the LLM provider (OpenAI, Mock)

## Architecture

The web UI follows a separation of concerns approach:

1. **Frontend (React)**:
   - User interface components
   - State management with React Context
   - API communication with Axios
   - Real-time updates with Socket.io client

2. **Backend (Flask)**:
   - RESTful API for notebook operations
   - WebSocket server for real-time updates
   - Integration with the LLM-REPL engine

3. **LLM-REPL Engine**:
   - Core functionality for notebook execution
   - Cell types and execution logic
   - LLM provider integration

## Development

For detailed information about development, refer to the README files in the respective directories:

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## API Documentation

The backend provides a RESTful API for interacting with the LLM-REPL engine. The API endpoints are documented in the [Backend README](backend/README.md).

## WebSocket Events

The backend provides WebSocket events for real-time updates during cell execution. The WebSocket events are documented in the [Backend README](backend/README.md).
