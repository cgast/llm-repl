import React, { useState } from 'react';
import {
  Paper,
  Box,
  IconButton,
  Typography,
  TextField,
  CircularProgress,
  Divider,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useNotebook } from '../contexts/NotebookContext';

const Cell = ({ cell, notebookId }) => {
  const { updateCell, deleteCell, executeCell } = useNotebook();
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(cell.content);

  // Get the cell ID - backend uses cell_id but frontend expects id
  const getCellId = () => {
    return cell.id || cell.cell_id;
  };

  const handleExecute = async () => {
    await executeCell(notebookId, getCellId());
  };

  const handleEdit = () => {
    setEditing(true);
  };

  const handleSave = async () => {
    await updateCell(notebookId, getCellId(), { content });
    setEditing(false);
  };

  const handleCancel = () => {
    setContent(cell.content);
    setEditing(false);
  };

  const handleDelete = async () => {
    await deleteCell(notebookId, getCellId());
  };

  const handleContentChange = (e) => {
    setContent(e.target.value);
  };

  const renderCellContent = () => {
    if (editing) {
      return (
        <TextField
          multiline
          fullWidth
          value={content}
          onChange={handleContentChange}
          variant="outlined"
          autoFocus
          sx={{ my: 1 }}
        />
      );
    }

    switch (cell.type) {
      case 'MarkdownCell':
        return (
          <Box className="cell-content markdown-content">
            <ReactMarkdown>{cell.content}</ReactMarkdown>
          </Box>
        );
      case 'ComputationCell':
      case 'PromptCell':
      case 'MemoryCell':
        return (
          <Box className="cell-content code-content">
            <SyntaxHighlighter language="python" style={materialLight}>
              {cell.content}
            </SyntaxHighlighter>
          </Box>
        );
      default:
        return (
          <Box className="cell-content">
            <Typography variant="body1">{cell.content}</Typography>
          </Box>
        );
    }
  };

  const renderCellOutputs = () => {
    if (!cell.outputs || cell.outputs.length === 0) {
      return null;
    }

    return (
      <>
        <Divider />
        <Box className="cell-output">
          {cell.outputs.map((output, index) => {
            switch (output.type) {
              case 'markdown':
                return (
                  <Box key={`${getCellId()}-output-markdown-${index}-${output.content.substring(0, 20).replace(/\s+/g, '-')}`} className="output-item">
                    <ReactMarkdown>{output.content}</ReactMarkdown>
                  </Box>
                );
              case 'stdout':
                return (
                  <Box key={`${getCellId()}-output-stdout-${index}-${output.content.substring(0, 20).replace(/\s+/g, '-')}`} className="output-item">
                    <SyntaxHighlighter language="text" style={materialLight}>
                      {output.content}
                    </SyntaxHighlighter>
                  </Box>
                );
              case 'error':
                return (
                  <Box key={`${getCellId()}-output-error-${index}-${output.content.substring(0, 20).replace(/\s+/g, '-')}`} className="output-item error">
                    <Typography color="error" component="pre">
                      {output.content}
                    </Typography>
                  </Box>
                );
              case 'llm_response':
                return (
                  <Box key={`${getCellId()}-output-llm-${index}-${(output.prompt || '').substring(0, 20).replace(/\s+/g, '-')}`} className="output-item">
                    <Typography variant="subtitle2" color="text.secondary">
                      Prompt:
                    </Typography>
                    <SyntaxHighlighter language="text" style={materialLight}>
                      {output.prompt}
                    </SyntaxHighlighter>
                    <Typography variant="subtitle2" color="text.secondary">
                      Response:
                    </Typography>
                    <ReactMarkdown>{output.content}</ReactMarkdown>
                  </Box>
                );
              default:
                return (
                  <Box key={`${getCellId()}-output-default-${index}-${(output.content || '').substring(0, 20).replace(/\s+/g, '-')}`} className="output-item">
                    <Typography variant="body2">{output.content}</Typography>
                  </Box>
                );
            }
          })}
        </Box>
      </>
    );
  };

  const getCellClassName = () => {
    switch (cell.type) {
      case 'MarkdownCell':
        return 'markdown-cell';
      case 'ComputationCell':
        return 'code-cell';
      case 'PromptCell':
        return 'prompt-cell';
      case 'MemoryCell':
        return 'memory-cell';
      default:
        return '';
    }
  };

  const getStatusIndicator = () => {
    switch (cell.status) {
      case 'running':
        return (
          <CircularProgress
            size={16}
            thickness={5}
            sx={{ mr: 1 }}
          />
        );
      case 'success':
        return (
          <Box
            className="cell-execution-indicator success"
            sx={{ mr: 1 }}
          />
        );
      case 'error':
        return (
          <Box
            className="cell-execution-indicator error"
            sx={{ mr: 1 }}
          />
        );
      default:
        return (
          <Box
            className="cell-execution-indicator idle"
            sx={{ mr: 1 }}
          />
        );
    }
  };

  return (
    <Paper
      className={`cell ${getCellClassName()}`}
      elevation={2}
      sx={{ mb: 2 }}
    >
      <Box
        className="cell-controls"
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 1,
          bgcolor: 'rgba(0, 0, 0, 0.03)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {getStatusIndicator()}
          <Typography variant="caption" color="text.secondary">
            {cell.type.replace('Cell', '')}
          </Typography>
        </Box>
        <Box>
          {editing ? (
            <>
              <IconButton size="small" onClick={handleSave}>
                <SaveIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={handleCancel}>
                <CancelIcon fontSize="small" />
              </IconButton>
            </>
          ) : (
            <>
              {(cell.type === 'ComputationCell' ||
                cell.type === 'PromptCell' ||
                cell.type === 'MemoryCell') && (
                <IconButton
                  size="small"
                  onClick={handleExecute}
                  disabled={cell.status === 'running'}
                >
                  <PlayArrowIcon fontSize="small" />
                </IconButton>
              )}
              <IconButton size="small" onClick={handleEdit}>
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={handleDelete}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </>
          )}
        </Box>
      </Box>
      <Box sx={{ p: 2 }}>{renderCellContent()}</Box>
      {renderCellOutputs()}
    </Paper>
  );
};

export default Cell;
