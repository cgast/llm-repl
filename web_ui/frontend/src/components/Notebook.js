import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Fab,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNotebook } from '../contexts/NotebookContext';
import Cell from './Cell';

const Notebook = () => {
  const { notebookId } = useParams();
  const navigate = useNavigate();
  const {
    currentNotebook,
    loading,
    error,
    fetchNotebook,
    createCell,
    executeAllCells,
    saveNotebook,
    getNotebookState,
  } = useNotebook();

  const [addCellAnchorEl, setAddCellAnchorEl] = useState(null);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [filePath, setFilePath] = useState('');
  const [stateDialogOpen, setStateDialogOpen] = useState(false);
  const [notebookState, setNotebookState] = useState({});
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  useEffect(() => {
    if (notebookId) {
      fetchNotebook(notebookId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [notebookId]); // Remove fetchNotebook from dependency array to prevent infinite loop

  const handleAddCellClick = (event) => {
    setAddCellAnchorEl(event.currentTarget);
  };

  const handleAddCellClose = () => {
    setAddCellAnchorEl(null);
  };

  const handleAddCell = async (cellType) => {
    handleAddCellClose();
    
    let content = '';
    let options = {};
    
    // Set default content based on cell type
    switch (cellType) {
      case 'markdown':
        content = '# New Markdown Cell\n\nEnter your markdown here.';
        break;
      case 'code':
        content = '# Enter your Python code here\n';
        break;
      case 'prompt':
        content = 'Enter your prompt template here.\nYou can use {variable} syntax to reference state variables.';
        options = { model: 'gpt-4', temperature: 0.7 };
        break;
      case 'memory':
        content = '# Enter your memory operations here\n# Examples:\n# variable = value\n# memory.update({"key": value})';
        break;
      default:
        break;
    }
    
    await createCell(notebookId, cellType, content, options);
  };

  const handleRunAll = async () => {
    await executeAllCells(notebookId);
  };

  const handleSaveClick = () => {
    setSaveDialogOpen(true);
  };

  const handleSaveDialogClose = () => {
    setSaveDialogOpen(false);
    setFilePath('');
  };

  const handleSaveNotebook = async () => {
    const result = await saveNotebook(notebookId, filePath);
    if (result) {
      setSnackbarMessage(`Notebook saved to ${result.filepath}`);
      setSnackbarOpen(true);
    }
    handleSaveDialogClose();
  };

  const handleViewState = async () => {
    const state = await getNotebookState(notebookId);
    if (state) {
      setNotebookState(state);
      setStateDialogOpen(true);
    }
  };

  const handleStateDialogClose = () => {
    setStateDialogOpen(false);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleBack = () => {
    navigate('/');
  };

  if (loading && !currentNotebook) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!currentNotebook) {
    return <Alert severity="info">Notebook not found</Alert>;
  }

  return (
    <Container maxWidth="lg">
      <Box
        className="notebook-toolbar"
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
          p: 2,
          bgcolor: 'background.paper',
          borderRadius: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={handleBack} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h5" component="h1">
            {currentNotebook.name}
          </Typography>
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<PlayArrowIcon />}
            onClick={handleRunAll}
            sx={{ mr: 1 }}
          >
            Run All
          </Button>
          <Button
            variant="outlined"
            startIcon={<SaveIcon />}
            onClick={handleSaveClick}
            sx={{ mr: 1 }}
          >
            Save
          </Button>
          <Button variant="outlined" onClick={handleViewState}>
            View State
          </Button>
        </Box>
      </Box>

      {currentNotebook.cells.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '50vh',
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            This notebook is empty
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddCellClick}
          >
            Add Cell
          </Button>
        </Box>
      ) : (
        <Box className="notebook-cells">
          {currentNotebook.cells.map((cell) => (
            <Cell key={cell.id} cell={cell} notebookId={notebookId} />
          ))}
        </Box>
      )}

      <Fab
        color="primary"
        aria-label="add"
        className="add-cell-button"
        onClick={handleAddCellClick}
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
        }}
      >
        <AddIcon />
      </Fab>

      {/* Add Cell Menu */}
      <Menu
        anchorEl={addCellAnchorEl}
        open={Boolean(addCellAnchorEl)}
        onClose={handleAddCellClose}
      >
        <MenuItem onClick={() => handleAddCell('markdown')}>
          Markdown Cell
        </MenuItem>
        <MenuItem onClick={() => handleAddCell('code')}>Code Cell</MenuItem>
        <MenuItem onClick={() => handleAddCell('prompt')}>Prompt Cell</MenuItem>
        <MenuItem onClick={() => handleAddCell('memory')}>Memory Cell</MenuItem>
      </Menu>

      {/* Save Dialog */}
      <Dialog open={saveDialogOpen} onClose={handleSaveDialogClose}>
        <DialogTitle>Save Notebook</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="File Path"
            type="text"
            fullWidth
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="e.g., /path/to/notebook.llmn"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSaveDialogClose}>Cancel</Button>
          <Button onClick={handleSaveNotebook}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* State Dialog */}
      <Dialog
        open={stateDialogOpen}
        onClose={handleStateDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Notebook State</DialogTitle>
        <DialogContent>
          <Box
            sx={{
              maxHeight: '70vh',
              overflow: 'auto',
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              p: 2,
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
            }}
          >
            {Object.entries(notebookState).map(([key, value]) => (
              <Box key={key} sx={{ mb: 2 }}>
                <Typography
                  variant="subtitle2"
                  color="primary"
                  sx={{ fontWeight: 'bold' }}
                >
                  {key}:
                </Typography>
                <Typography variant="body2">
                  {typeof value === 'object'
                    ? JSON.stringify(value, null, 2)
                    : String(value)}
                </Typography>
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleStateDialogClose}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default Notebook;
