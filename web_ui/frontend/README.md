# LLM-REPL Web UI Frontend

This is the frontend for the LLM-REPL Web UI. It provides a Jupyter notebook-style interface for interacting with the LLM-REPL engine.

## Setup

1. Install the required dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm start
```

The frontend will be available at http://localhost:8081by default.

You can customize the port and API base URL using environment variables:

```bash
PORT=8081 REACT_APP_API_BASE_URL=http://localhost:5000 REACT_APP_SOCKET_URL=http://localhost:5000 npm start
```

## Configuration

The frontend uses a configuration file (`src/config.js`) to define the API base URL and Socket.io URL. By default, these are set to `http://localhost:5000`, but they can be overridden using environment variables:

```javascript
// src/config.js
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
export const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || API_BASE_URL;
```

When deploying to production, you should set these environment variables to the appropriate values for your environment.

## Deployment

To deploy the frontend to production:

1. Build the frontend for production:

```bash
npm run build
```

2. Set the environment variables for the API base URL and Socket.io URL:

```bash
REACT_APP_API_BASE_URL=https://api.example.com REACT_APP_SOCKET_URL=https://api.example.com npm run build
```

3. Serve the built files using a static file server (e.g., Nginx, Apache) or a Node.js server.

For example, to serve the built files using the `serve` package:

```bash
npm install -g serve
serve -s build
```

## Features

- **Notebook Management**: Create, edit, delete, save, and load notebooks
- **Cell Types**: Support for all LLM-REPL cell types (Markdown, Code, Prompt, Memory)
- **Cell Execution**: Execute individual cells or run all cells in a notebook
- **Real-time Updates**: WebSocket integration for real-time updates during cell execution
- **State Management**: View and manage the notebook state
- **LLM Provider Configuration**: Configure the LLM provider (OpenAI, Mock)

## Project Structure

- `src/components/`: React components for the UI
  - `Header.js`: Application header with navigation and settings
  - `NotebookList.js`: List of available notebooks
  - `Notebook.js`: Notebook editor with cells
  - `Cell.js`: Individual cell component
- `src/contexts/`: React contexts for state management
  - `NotebookContext.js`: Context for notebook operations and state
- `src/services/`: API services (if needed)
- `public/`: Static assets

## Dependencies

- React
- React Router
- Material-UI
- Axios
- Socket.io-client
- React Markdown
- React Syntax Highlighter

## Development

The frontend is built with React and uses the following technologies:

- **React Router**: For navigation between pages
- **Material-UI**: For UI components
- **Axios**: For API requests
- **Socket.io-client**: For real-time updates
- **React Markdown**: For rendering markdown content
- **React Syntax Highlighter**: For syntax highlighting in code cells

## API Integration

The frontend communicates with the backend API using the base URL defined in the configuration. The API endpoints are defined in the `NotebookContext.js` file.

All API calls now use the configured base URL, which makes it easy to deploy the application to different environments without modifying the code.

## WebSocket Integration

The frontend connects to the WebSocket server using the URL defined in the configuration for real-time updates during cell execution. The WebSocket events are handled in the `NotebookContext.js` file.

This allows the application to be deployed to different environments without modifying the code.
