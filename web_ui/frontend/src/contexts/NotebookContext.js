import React, { createContext, useState, useEffect, useContext } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import { API_BASE_URL, SOCKET_URL } from '../config';

// Create the context
const NotebookContext = createContext();

// Socket.io instance
let socket;

export const NotebookProvider = ({ children }) => {
  const [notebooks, setNotebooks] = useState([]);
  const [currentNotebook, setCurrentNotebook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [socketConnected, setSocketConnected] = useState(false);

  // Initialize socket connection
  useEffect(() => {
    // Connect to the Socket.io server with explicit configuration
    socket = io(SOCKET_URL, {
      transports: ['websocket'],
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    });

    // Set up event listeners
    socket.on('connect', () => {
      console.log('Socket connected');
      setSocketConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected');
      setSocketConnected(false);
    });

    // Helper function to get cell ID (handles both id and cell_id)
    const getCellId = (cell) => {
      return cell.id || cell.cell_id;
    };

    socket.on('cell_execution_started', (data) => {
      console.log('Cell execution started:', data);
      if (currentNotebook && currentNotebook.id === data.notebook_id) {
        // Update the cell status
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => {
            if (getCellId(cell) === data.cell_id) {
              return { ...cell, status: 'running' };
            }
            return cell;
          });

          return { ...prevNotebook, cells: updatedCells };
        });
      }
    });

    socket.on('cell_execution_completed', (data) => {
      console.log('Cell execution completed:', data);
      if (currentNotebook && currentNotebook.id === data.notebook_id) {
        // Update the cell status and outputs
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => {
            if (getCellId(cell) === data.cell_id) {
              return { ...cell, status: 'success', outputs: data.outputs };
            }
            return cell;
          });

          return { ...prevNotebook, cells: updatedCells };
        });
      }
    });

    socket.on('cell_execution_failed', (data) => {
      console.log('Cell execution failed:', data);
      if (currentNotebook && currentNotebook.id === data.notebook_id) {
        // Update the cell status and add error output
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => {
            if (getCellId(cell) === data.cell_id) {
              return {
                ...cell,
                status: 'error',
                outputs: [
                  ...(cell.outputs || []),
                  { type: 'error', content: data.error },
                ],
              };
            }
            return cell;
          });

          return { ...prevNotebook, cells: updatedCells };
        });
      }
    });

    // Clean up on unmount
    return () => {
      socket.disconnect();
    };
  }, []); // Remove currentNotebook from dependency array to prevent infinite loop

  // Fetch all notebooks
  const fetchNotebooks = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/notebooks`);
      setNotebooks(response.data.notebooks);
      setError(null);
    } catch (err) {
      console.error('Error fetching notebooks:', err);
      setError('Failed to fetch notebooks');
    } finally {
      setLoading(false);
    }
  };

  // Fetch a notebook by ID
  const fetchNotebook = async (notebookId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/notebooks/${notebookId}`);
      
      // Transform the cells to include a status field
      const transformedCells = response.data.cells.map((cell) => ({
        ...cell,
        status: 'idle',
      }));
      
      setCurrentNotebook({
        ...response.data,
        cells: transformedCells,
      });
      
      setError(null);
    } catch (err) {
      console.error('Error fetching notebook:', err);
      setError('Failed to fetch notebook');
    } finally {
      setLoading(false);
    }
  };

  // Create a new notebook
  const createNotebook = async (name) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notebooks`, { name });
      const newNotebook = response.data;
      setNotebooks([...notebooks, newNotebook]);
      setError(null);
      return newNotebook;
    } catch (err) {
      console.error('Error creating notebook:', err);
      setError('Failed to create notebook');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Update a notebook
  const updateNotebook = async (notebookId, data) => {
    setLoading(true);
    try {
      const response = await axios.put(`${API_BASE_URL}/api/notebooks/${notebookId}`, data);
      const updatedNotebook = response.data;
      
      // Update the notebooks list
      setNotebooks(
        notebooks.map((notebook) =>
          notebook.id === notebookId ? updatedNotebook : notebook
        )
      );
      
      // Update the current notebook if it's the one being updated
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook({ ...currentNotebook, ...updatedNotebook });
      }
      
      setError(null);
      return updatedNotebook;
    } catch (err) {
      console.error('Error updating notebook:', err);
      setError('Failed to update notebook');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Delete a notebook
  const deleteNotebook = async (notebookId) => {
    setLoading(true);
    try {
      await axios.delete(`${API_BASE_URL}/api/notebooks/${notebookId}`);
      setNotebooks(notebooks.filter((notebook) => notebook.id !== notebookId));
      
      // Clear the current notebook if it's the one being deleted
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook(null);
      }
      
      setError(null);
      return true;
    } catch (err) {
      console.error('Error deleting notebook:', err);
      setError('Failed to delete notebook');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Create a new cell
  const createCell = async (notebookId, cellType, content = '', options = {}) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notebooks/${notebookId}/cells`, {
        type: cellType,
        content,
        ...options,
      });
      
      const newCell = { ...response.data, status: 'idle' };
      
      // Update the current notebook if it's the one being modified
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook({
          ...currentNotebook,
          cells: [...currentNotebook.cells, newCell],
        });
      }
      
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return newCell;
    } catch (err) {
      console.error('Error creating cell:', err);
      setError('Failed to create cell');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get cell ID (handles both id and cell_id)
  const getCellId = (cell) => {
    return cell.id || cell.cell_id;
  };

  // Update a cell
  const updateCell = async (notebookId, cellId, data) => {
    setLoading(true);
    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/notebooks/${notebookId}/cells/${cellId}`,
        data
      );
      
      const updatedCell = { ...response.data, status: 'idle' };
      
      // Update the current notebook if it's the one being modified
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook({
          ...currentNotebook,
          cells: currentNotebook.cells.map((cell) =>
            getCellId(cell) === cellId ? updatedCell : cell
          ),
        });
      }
      
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return updatedCell;
    } catch (err) {
      console.error('Error updating cell:', err);
      setError('Failed to update cell');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Delete a cell
  const deleteCell = async (notebookId, cellId) => {
    setLoading(true);
    try {
      await axios.delete(`${API_BASE_URL}/api/notebooks/${notebookId}/cells/${cellId}`);
      
      // Update the current notebook if it's the one being modified
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook({
          ...currentNotebook,
          cells: currentNotebook.cells.filter((cell) => getCellId(cell) !== cellId),
        });
      }
      
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return true;
    } catch (err) {
      console.error('Error deleting cell:', err);
      setError('Failed to delete cell');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Execute a cell
  const executeCell = async (notebookId, cellId) => {
    try {
      // Update the cell status to running
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => {
            if (getCellId(cell) === cellId) {
              return { ...cell, status: 'running' };
            }
            return cell;
          });

          return { ...prevNotebook, cells: updatedCells };
        });
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/notebooks/${notebookId}/cells/${cellId}/execute`
      );
      
      // The cell status will be updated by the socket event
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return response.data;
    } catch (err) {
      console.error('Error executing cell:', err);
      setError('Failed to execute cell');
      
      // Update the cell status to error
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => {
            if (getCellId(cell) === cellId) {
              return {
                ...cell,
                status: 'error',
                outputs: [
                  ...(cell.outputs || []),
                  { type: 'error', content: err.message },
                ],
              };
            }
            return cell;
          });

          return { ...prevNotebook, cells: updatedCells };
        });
      }
      
      return null;
    }
  };

  // Execute all cells in a notebook
  const executeAllCells = async (notebookId) => {
    try {
      // Update all cells status to running
      if (currentNotebook && currentNotebook.id === notebookId) {
        setCurrentNotebook((prevNotebook) => {
          if (!prevNotebook) return null;

          const updatedCells = prevNotebook.cells.map((cell) => ({
            ...cell,
            status: 'running',
          }));

          return { ...prevNotebook, cells: updatedCells };
        });
      }

      await axios.post(`${API_BASE_URL}/api/notebooks/${notebookId}/execute_all`);
      
      // The cell statuses will be updated by the socket events
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return true;
    } catch (err) {
      console.error('Error executing all cells:', err);
      setError('Failed to execute all cells');
      return false;
    }
  };

  // Save a notebook to a file
  const saveNotebook = async (notebookId, filepath) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notebooks/${notebookId}/save`, {
        filepath,
      });
      
      // Fetch the notebook again to ensure we have the latest data
      await fetchNotebook(notebookId);
      
      setError(null);
      return response.data;
    } catch (err) {
      console.error('Error saving notebook:', err);
      setError('Failed to save notebook');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Load a notebook from a file
  const loadNotebook = async (filepath) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notebooks/load`, { filepath });
      const loadedNotebook = response.data;
      setNotebooks([...notebooks, loadedNotebook]);
      setError(null);
      return loadedNotebook;
    } catch (err) {
      console.error('Error loading notebook:', err);
      setError('Failed to load notebook');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Get the notebook state
  const getNotebookState = async (notebookId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/notebooks/${notebookId}/state`);
      setError(null);
      return response.data.state;
    } catch (err) {
      console.error('Error getting notebook state:', err);
      setError('Failed to get notebook state');
      return null;
    }
  };

  // Set the LLM provider
  const setLLMProvider = async (providerType, apiKey) => {
    setLoading(true);
    try {
      await axios.put(`${API_BASE_URL}/api/llm/provider`, {
        type: providerType,
        api_key: apiKey,
      });
      setError(null);
      return true;
    } catch (err) {
      console.error('Error setting LLM provider:', err);
      setError('Failed to set LLM provider');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Get available LLM providers
  const getLLMProviders = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/llm/providers`);
      setError(null);
      return response.data.providers;
    } catch (err) {
      console.error('Error getting LLM providers:', err);
      setError('Failed to get LLM providers');
      return [];
    }
  };

  // Context value
  const value = {
    notebooks,
    currentNotebook,
    loading,
    error,
    socketConnected,
    fetchNotebooks,
    fetchNotebook,
    createNotebook,
    updateNotebook,
    deleteNotebook,
    createCell,
    updateCell,
    deleteCell,
    executeCell,
    executeAllCells,
    saveNotebook,
    loadNotebook,
    getNotebookState,
    setLLMProvider,
    getLLMProviders,
  };

  return (
    <NotebookContext.Provider value={value}>
      {children}
    </NotebookContext.Provider>
  );
};

// Custom hook to use the notebook context
export const useNotebook = () => {
  const context = useContext(NotebookContext);
  if (context === undefined) {
    throw new Error('useNotebook must be used within a NotebookProvider');
  }
  return context;
};

export default NotebookContext;
