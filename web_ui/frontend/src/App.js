import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, Box } from '@mui/material';
import NotebookList from './components/NotebookList';
import Notebook from './components/Notebook';
import Header from './components/Header';
import { NotebookProvider } from './contexts/NotebookContext';

function App() {
  return (
    <div className="App">
      <NotebookProvider>
        <Header />
        <Container maxWidth="xl">
          <Box sx={{ mt: 4 }}>
            <Routes>
              <Route path="/" element={<NotebookList />} />
              <Route path="/notebooks/:notebookId" element={<Notebook />} />
            </Routes>
          </Box>
        </Container>
      </NotebookProvider>
    </div>
  );
}

export default App;
