"""
Tests for the notebook module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.llm_repl.notebook import Notebook
from src.llm_repl.cells import MarkdownCell, ComputationCell, PromptCell, MemoryCell


class TestNotebook(unittest.TestCase):
    """Test cases for the Notebook class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notebook = Notebook(name="Test Notebook")
    
    def test_init(self):
        """Test notebook initialization."""
        self.assertEqual(self.notebook.name, "Test Notebook")
        self.assertEqual(len(self.notebook.cells), 0)
        self.assertEqual(self.notebook.state, {})
        self.assertIsNotNone(self.notebook.notebook_id)
        self.assertIsNotNone(self.notebook.created_at)
        self.assertEqual(self.notebook.created_at, self.notebook.updated_at)
    
    def test_add_cell(self):
        """Test adding a cell to the notebook."""
        cell = MarkdownCell("# Test")
        self.notebook.add_cell(cell)
        self.assertEqual(len(self.notebook.cells), 1)
        self.assertEqual(self.notebook.cells[0], cell)
    
    def test_create_markdown_cell(self):
        """Test creating a markdown cell."""
        cell = self.notebook.create_markdown_cell("# Test Markdown")
        self.assertEqual(len(self.notebook.cells), 1)
        self.assertIsInstance(cell, MarkdownCell)
        self.assertEqual(cell.content, "# Test Markdown")
    
    def test_create_computation_cell(self):
        """Test creating a computation cell."""
        cell = self.notebook.create_computation_cell("x = 1 + 1")
        self.assertEqual(len(self.notebook.cells), 1)
        self.assertIsInstance(cell, ComputationCell)
        self.assertEqual(cell.content, "x = 1 + 1")
    
    def test_create_prompt_cell(self):
        """Test creating a prompt cell."""
        cell = self.notebook.create_prompt_cell("Tell me about {topic}", model="gpt-4")
        self.assertEqual(len(self.notebook.cells), 1)
        self.assertIsInstance(cell, PromptCell)
        self.assertEqual(cell.content, "Tell me about {topic}")
        self.assertEqual(cell.model, "gpt-4")
    
    def test_create_memory_cell(self):
        """Test creating a memory cell."""
        cell = self.notebook.create_memory_cell("x = 42")
        self.assertEqual(len(self.notebook.cells), 1)
        self.assertIsInstance(cell, MemoryCell)
        self.assertEqual(cell.content, "x = 42")
    
    def test_execute_cell(self):
        """Test executing a cell."""
        # Add a computation cell
        cell = self.notebook.create_computation_cell("x = 42")
        
        # Execute the cell
        outputs = self.notebook.execute_cell(0)
        
        # Check that the state was updated
        self.assertEqual(self.notebook.state.get("x"), 42)
        self.assertEqual(outputs, [])  # No stdout output
    
    def test_execute_cell_with_output(self):
        """Test executing a cell with output."""
        # Add a computation cell with print
        cell = self.notebook.create_computation_cell("print('Hello, world!')")
        
        # Execute the cell
        outputs = self.notebook.execute_cell(0)
        
        # Check the output
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["type"], "stdout")
        self.assertEqual(outputs[0]["content"], "Hello, world!\n")
    
    def test_execute_cell_with_error(self):
        """Test executing a cell that raises an error."""
        # Add a computation cell with an error
        cell = self.notebook.create_computation_cell("1/0")
        
        # Execute the cell
        outputs = self.notebook.execute_cell(0)
        
        # Check the output
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["type"], "error")
        self.assertIn("division by zero", outputs[0]["content"])
    
    @patch('src.llm_repl.llm.get_llm_provider')
    def test_execute_prompt_cell(self, mock_get_llm_provider):
        """Test executing a prompt cell."""
        # Mock the LLM provider
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "This is a mock response."
        mock_get_llm_provider.return_value = mock_provider
        
        # Add a prompt cell
        cell = self.notebook.create_prompt_cell("Tell me about {topic}")
        
        # Set up the state
        self.notebook.state = {"topic": "Python"}
        
        # Execute the cell
        outputs = self.notebook.execute_cell(0)
        
        # Check that the LLM was called with the right prompt
        mock_provider.generate.assert_called_once()
        args, kwargs = mock_provider.generate.call_args
        self.assertEqual(kwargs["prompt"], "Tell me about Python")
        
        # Check the output
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["type"], "llm_response")
        self.assertEqual(outputs[0]["content"], "This is a mock response.")

        # Check that the response was added to the state
        # Response should be named response_0 since it's the first (index 0) cell
        self.assertIn("response_0", self.notebook.state)
        self.assertEqual(self.notebook.state["response_0"], "This is a mock response.")
        # Also check for IPython-style last response
        self.assertIn("_", self.notebook.state)
        self.assertEqual(self.notebook.state["_"], "This is a mock response.")
    
    def test_execute_memory_cell(self):
        """Test executing a memory cell."""
        # Add a memory cell
        cell = self.notebook.create_memory_cell("x = 42\ny = 'hello'\nmemory.update({'z': [1, 2, 3]})")
        
        # Execute the cell
        outputs = self.notebook.execute_cell(0)
        
        # Check that the state was updated
        self.assertEqual(self.notebook.state.get("x"), 42)
        self.assertEqual(self.notebook.state.get("y"), "hello")
        self.assertEqual(self.notebook.state.get("z"), [1, 2, 3])
        
        # Check the output
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["type"], "memory_update")
        self.assertEqual(set(outputs[0]["added"]), {"x", "y", "z"})
    
    def test_execute_all_cells(self):
        """Test executing all cells."""
        # Add a few cells
        self.notebook.create_computation_cell("x = 1")
        self.notebook.create_computation_cell("y = x + 1")
        self.notebook.create_computation_cell("z = y + 1")
        
        # Execute all cells
        self.notebook.execute_all_cells()
        
        # Check that the state was updated correctly
        self.assertEqual(self.notebook.state.get("x"), 1)
        self.assertEqual(self.notebook.state.get("y"), 2)
        self.assertEqual(self.notebook.state.get("z"), 3)
    
    def test_get_cell_dependencies(self):
        """Test getting cell dependencies."""
        # Add cells with dependencies
        self.notebook.create_computation_cell("x = 1")
        self.notebook.create_computation_cell("y = x + 1")
        
        # Execute the cells to establish dependencies
        self.notebook.execute_all_cells()
        
        # Get dependencies for the second cell
        deps = self.notebook.get_cell_dependencies(1)
        
        # Check that the second cell depends on the first
        self.assertEqual(deps, {0})
    
    def test_get_dependent_cells(self):
        """Test getting dependent cells."""
        # Add cells with dependencies
        self.notebook.create_computation_cell("x = 1")
        self.notebook.create_computation_cell("y = x + 1")
        
        # Execute the cells to establish dependencies
        self.notebook.execute_all_cells()
        
        # Get cells that depend on the first cell
        deps = self.notebook.get_dependent_cells(0)
        
        # Check that the second cell depends on the first
        self.assertEqual(deps, {1})
    
    def test_save_and_load(self):
        """Test saving and loading a notebook."""
        # Add some cells
        self.notebook.create_markdown_cell("# Test Notebook")
        self.notebook.create_computation_cell("x = 42")
        self.notebook.create_prompt_cell("Tell me about {topic}", model="gpt-4")
        
        # Execute the cells
        self.notebook.execute_all_cells()
        
        # Save the notebook to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".llmn", delete=False) as f:
            filepath = f.name
        
        try:
            self.notebook.save(filepath)
            
            # Load the notebook
            loaded_notebook = Notebook.load(filepath)
            
            # Check that the loaded notebook has the same properties
            self.assertEqual(loaded_notebook.name, self.notebook.name)
            self.assertEqual(loaded_notebook.notebook_id, self.notebook.notebook_id)
            self.assertEqual(len(loaded_notebook.cells), len(self.notebook.cells))
            
            # Check that the cells have the right types
            self.assertIsInstance(loaded_notebook.cells[0], MarkdownCell)
            self.assertIsInstance(loaded_notebook.cells[1], ComputationCell)
            self.assertIsInstance(loaded_notebook.cells[2], PromptCell)
            
            # Check that the cell contents are preserved
            self.assertEqual(loaded_notebook.cells[0].content, "# Test Notebook")
            self.assertEqual(loaded_notebook.cells[1].content, "x = 42")
            self.assertEqual(loaded_notebook.cells[2].content, "Tell me about {topic}")
            
            # Check that the prompt cell model is preserved
            self.assertEqual(loaded_notebook.cells[2].__dict__.get("model"), "gpt-4")
            
        finally:
            # Clean up
            os.unlink(filepath)
    
    def test_clear_outputs(self):
        """Test clearing cell outputs."""
        # Add a cell with output
        cell = self.notebook.create_computation_cell("print('Hello, world!')")
        
        # Execute the cell
        self.notebook.execute_cell(0)
        
        # Check that the cell has output
        self.assertTrue(cell.outputs)
        
        # Clear outputs
        self.notebook.clear_outputs()
        
        # Check that the outputs were cleared
        self.assertFalse(cell.outputs)
    
    def test_clear_state(self):
        """Test clearing the notebook state."""
        # Add a cell that updates the state
        self.notebook.create_computation_cell("x = 42")
        
        # Execute the cell
        self.notebook.execute_cell(0)
        
        # Check that the state was updated
        self.assertEqual(self.notebook.state.get("x"), 42)
        
        # Clear the state
        self.notebook.clear_state()
        
        # Check that the state was cleared
        self.assertEqual(self.notebook.state, {})


if __name__ == "__main__":
    unittest.main()
