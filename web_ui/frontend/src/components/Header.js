import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Box,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SettingsIcon from '@mui/icons-material/Settings';
import { useNotebook } from '../contexts/NotebookContext';

const Header = () => {
  const { createNotebook, setLLMProvider, getLLMProviders } = useNotebook();
  
  const [anchorEl, setAnchorEl] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [newNotebookOpen, setNewNotebookOpen] = useState(false);
  const [notebookName, setNotebookName] = useState('');
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [apiKey, setApiKey] = useState('');
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleSettingsOpen = async () => {
    handleMenuClose();
    // Fetch available providers
    const availableProviders = await getLLMProviders();
    setProviders(availableProviders);
    setSettingsOpen(true);
  };
  
  const handleSettingsClose = () => {
    setSettingsOpen(false);
  };
  
  const handleSettingsSave = async () => {
    await setLLMProvider(selectedProvider, apiKey);
    setSettingsOpen(false);
  };
  
  const handleNewNotebookOpen = () => {
    handleMenuClose();
    setNewNotebookOpen(true);
  };
  
  const handleNewNotebookClose = () => {
    setNewNotebookOpen(false);
    setNotebookName('');
  };
  
  const handleNewNotebookCreate = async () => {
    if (notebookName.trim()) {
      const newNotebook = await createNotebook(notebookName);
      if (newNotebook) {
        // Redirect to the new notebook
        window.location.href = `/notebooks/${newNotebook.id}`;
      }
    }
    handleNewNotebookClose();
  };
  
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
          onClick={handleMenuOpen}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          <RouterLink to="/" style={{ color: 'inherit', textDecoration: 'none' }}>
            LLM-REPL
          </RouterLink>
        </Typography>
        
        <IconButton
          color="inherit"
          aria-label="settings"
          onClick={handleSettingsOpen}
        >
          <SettingsIcon />
        </IconButton>
      </Toolbar>
      
      {/* Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleNewNotebookOpen}>New Notebook</MenuItem>
        <MenuItem component={RouterLink} to="/" onClick={handleMenuClose}>
          Notebooks
        </MenuItem>
        <MenuItem onClick={handleSettingsOpen}>Settings</MenuItem>
      </Menu>
      
      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={handleSettingsClose}>
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ minWidth: 400, mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>LLM Provider</InputLabel>
              <Select
                value={selectedProvider}
                label="LLM Provider"
                onChange={(e) => setSelectedProvider(e.target.value)}
              >
                {providers.map((provider) => (
                  <MenuItem key={provider} value={provider}>
                    {provider}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            {selectedProvider === 'openai' && (
              <TextField
                fullWidth
                label="API Key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSettingsClose}>Cancel</Button>
          <Button onClick={handleSettingsSave}>Save</Button>
        </DialogActions>
      </Dialog>
      
      {/* New Notebook Dialog */}
      <Dialog open={newNotebookOpen} onClose={handleNewNotebookClose}>
        <DialogTitle>Create New Notebook</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Notebook Name"
            type="text"
            fullWidth
            value={notebookName}
            onChange={(e) => setNotebookName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleNewNotebookClose}>Cancel</Button>
          <Button onClick={handleNewNotebookCreate}>Create</Button>
        </DialogActions>
      </Dialog>
    </AppBar>
  );
};

export default Header;
