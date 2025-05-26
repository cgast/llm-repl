import axios from 'axios';
import { API_BASE_URL } from '../config';

// Create an axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Notebook API
export const notebookApi = {
  // Get all notebooks
  getNotebooks: () => api.get('/notebooks'),
  
  // Get a notebook by ID
  getNotebook: (notebookId) => api.get(`/notebooks/${notebookId}`),
  
  // Create a new notebook
  createNotebook: (data) => api.post('/notebooks', data),
  
  // Update a notebook
  updateNotebook: (notebookId, data) => api.put(`/notebooks/${notebookId}`, data),
  
  // Delete a notebook
  deleteNotebook: (notebookId) => api.delete(`/notebooks/${notebookId}`),
  
  // Save a notebook to a file
  saveNotebook: (notebookId, filepath) => api.post(`/notebooks/${notebookId}/save`, { filepath }),
  
  // Load a notebook from a file
  loadNotebook: (filepath) => api.post('/notebooks/load', { filepath }),
  
  // Get the state of a notebook
  getNotebookState: (notebookId) => api.get(`/notebooks/${notebookId}/state`),
};

// Cell API
export const cellApi = {
  // Get all cells in a notebook
  getCells: (notebookId) => api.get(`/notebooks/${notebookId}/cells`),
  
  // Create a new cell
  createCell: (notebookId, data) => api.post(`/notebooks/${notebookId}/cells`, data),
  
  // Get a cell by ID
  getCell: (notebookId, cellId) => api.get(`/notebooks/${notebookId}/cells/${cellId}`),
  
  // Update a cell
  updateCell: (notebookId, cellId, data) => api.put(`/notebooks/${notebookId}/cells/${cellId}`, data),
  
  // Delete a cell
  deleteCell: (notebookId, cellId) => api.delete(`/notebooks/${notebookId}/cells/${cellId}`),
  
  // Execute a cell
  executeCell: (notebookId, cellId) => api.post(`/notebooks/${notebookId}/cells/${cellId}/execute`),
  
  // Execute all cells in a notebook
  executeAllCells: (notebookId) => api.post(`/notebooks/${notebookId}/execute_all`),
};

// LLM Provider API
export const llmApi = {
  // Get available LLM providers
  getProviders: () => api.get('/llm/providers'),
  
  // Set the LLM provider
  setProvider: (data) => api.put('/llm/provider', data),
};

export default {
  notebook: notebookApi,
  cell: cellApi,
  llm: llmApi,
};
