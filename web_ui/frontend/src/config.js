/**
 * Application configuration
 */

// API base URL
// In production, this should be set to the actual domain or IP address of the server
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

// Socket.io URL (usually the same as API_BASE_URL)
export const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || API_BASE_URL;

export default {
  API_BASE_URL,
  SOCKET_URL
};
