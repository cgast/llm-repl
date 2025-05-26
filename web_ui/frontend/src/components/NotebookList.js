import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { useNotebook } from '../contexts/NotebookContext';

const NotebookList = () => {
  const {
    notebooks,
    loading,
    error,
    fetchNotebooks,
    createNotebook,
    updateNotebook,
    deleteNotebook,
    loadNotebook,
  } = useNotebook();

  const [newNotebookOpen, setNewNotebookOpen] = useState(false);
  const [editNotebookOpen, setEditNotebookOpen] = useState(false);
  const [loadNotebookOpen, setLoadNotebookOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [notebookName, setNotebookName] = useState('');
  const [notebookFilePath, setNotebookFilePath] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState(null);

  useEffect(() => {
    fetchNotebooks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Remove fetchNotebooks from dependency array to prevent infinite loop

  const handleNewNotebookOpen = () => {
    setNewNotebookOpen(true);
  };

  const handleNewNotebookClose = () => {
    setNewNotebookOpen(false);
    setNotebookName('');
  };

  const handleNewNotebookCreate = async () => {
    if (notebookName.trim()) {
      await createNotebook(notebookName);
    }
    handleNewNotebookClose();
  };

  const handleEditNotebookOpen = (notebook) => {
    setSelectedNotebook(notebook);
    setNotebookName(notebook.name);
    setEditNotebookOpen(true);
  };

  const handleEditNotebookClose = () => {
    setEditNotebookOpen(false);
    setNotebookName('');
    setSelectedNotebook(null);
  };

  const handleEditNotebookSave = async () => {
    if (selectedNotebook && notebookName.trim()) {
      await updateNotebook(selectedNotebook.id, { name: notebookName });
    }
    handleEditNotebookClose();
  };

  const handleDeleteConfirmOpen = (notebook) => {
    setSelectedNotebook(notebook);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirmClose = () => {
    setDeleteConfirmOpen(false);
    setSelectedNotebook(null);
  };

  const handleDeleteNotebook = async () => {
    if (selectedNotebook) {
      await deleteNotebook(selectedNotebook.id);
    }
    handleDeleteConfirmClose();
  };

  const handleLoadNotebookOpen = () => {
    setLoadNotebookOpen(true);
  };

  const handleLoadNotebookClose = () => {
    setLoadNotebookOpen(false);
    setNotebookFilePath('');
  };

  const handleLoadNotebook = async () => {
    if (notebookFilePath.trim()) {
      await loadNotebook(notebookFilePath);
    }
    handleLoadNotebookClose();
  };

  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Notebooks
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleNewNotebookOpen}
            sx={{ mr: 2 }}
          >
            New Notebook
          </Button>
          <Button variant="outlined" onClick={handleLoadNotebookOpen}>
            Load Notebook
          </Button>
        </Box>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && notebooks.length === 0 && (
        <Typography variant="body1" color="text.secondary" align="center">
          No notebooks found. Create a new one to get started.
        </Typography>
      )}

      <Grid container spacing={3}>
        {notebooks.map((notebook) => (
          <Grid item xs={12} sm={6} md={4} key={notebook.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  {notebook.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Created: {new Date(notebook.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Updated: {new Date(notebook.updated_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cells: {notebook.cell_count || 0}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  component={RouterLink}
                  to={`/notebooks/${notebook.id}`}
                >
                  Open
                </Button>
                <IconButton
                  size="small"
                  onClick={() => handleEditNotebookOpen(notebook)}
                >
                  <EditIcon fontSize="small" />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => handleDeleteConfirmOpen(notebook)}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

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

      {/* Edit Notebook Dialog */}
      <Dialog open={editNotebookOpen} onClose={handleEditNotebookClose}>
        <DialogTitle>Edit Notebook</DialogTitle>
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
          <Button onClick={handleEditNotebookClose}>Cancel</Button>
          <Button onClick={handleEditNotebookSave}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={handleDeleteConfirmClose}>
        <DialogTitle>Delete Notebook</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the notebook "
            {selectedNotebook?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteConfirmClose}>Cancel</Button>
          <Button onClick={handleDeleteNotebook} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Load Notebook Dialog */}
      <Dialog open={loadNotebookOpen} onClose={handleLoadNotebookClose}>
        <DialogTitle>Load Notebook</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="File Path"
            type="text"
            fullWidth
            value={notebookFilePath}
            onChange={(e) => setNotebookFilePath(e.target.value)}
            placeholder="e.g., /path/to/notebook.llmn"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleLoadNotebookClose}>Cancel</Button>
          <Button onClick={handleLoadNotebook}>Load</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default NotebookList;
