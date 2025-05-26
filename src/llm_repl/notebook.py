"""
Notebook implementation for LLM-REPL.

This module provides the core Notebook class that manages cells, state,
and execution flow for LLM-REPL notebooks.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from .cells import Cell, MarkdownCell, ComputationCell, PromptCell, MemoryCell


class Notebook:
    """Main notebook class for LLM-REPL."""
    
    def __init__(self, name: str = "Untitled Notebook"):
        """Initialize a notebook.
        
        Args:
            name: The name of the notebook
        """
        self.name = name
        self.cells: List[Cell] = []
        self.state: Dict[str, Any] = {}
        self.notebook_id = str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.metadata = {
            "kernel": "python3",
            "language_info": {
                "name": "python",
                "version": "3.8+"
            }
        }
    
    def add_cell(self, cell: Cell) -> None:
        """Add a cell to the notebook.
        
        Args:
            cell: The cell to add
        """
        self.cells.append(cell)
        self.updated_at = datetime.now().isoformat()
    
    def create_markdown_cell(self, content: str) -> MarkdownCell:
        """Create and add a markdown cell.
        
        Args:
            content: The markdown content
            
        Returns:
            The created cell
        """
        cell = MarkdownCell(content)
        self.add_cell(cell)
        return cell
    
    def create_computation_cell(self, content: str) -> ComputationCell:
        """Create and add a computation cell.
        
        Args:
            content: The Python code
            
        Returns:
            The created cell
        """
        cell = ComputationCell(content)
        self.add_cell(cell)
        return cell
    
    def create_prompt_cell(self, content: str, model: str = "gpt-4", 
                         temperature: float = 0.7) -> PromptCell:
        """Create and add a prompt cell.
        
        Args:
            content: The prompt template
            model: The LLM model to use
            temperature: The sampling temperature
            
        Returns:
            The created cell
        """
        cell = PromptCell(content, model=model, temperature=temperature)
        self.add_cell(cell)
        return cell
    
    def create_memory_cell(self, content: str) -> MemoryCell:
        """Create and add a memory cell.
        
        Args:
            content: The memory operations
            
        Returns:
            The created cell
        """
        cell = MemoryCell(content)
        self.add_cell(cell)
        return cell
    
    def execute_cell(self, cell_index: int) -> List[Dict[str, Any]]:
        """Execute a cell and update the notebook state.
        
        Args:
            cell_index: The index of the cell to execute
            
        Returns:
            The outputs of the cell
        """
        if cell_index < 0 or cell_index >= len(self.cells):
            raise IndexError(f"Cell index {cell_index} out of range")
        
        cell = self.cells[cell_index]
        
        # Execute the cell with the current state
        updated_state = cell.execute(self.state)
        
        # Update the notebook state
        self.state = updated_state
        self.updated_at = datetime.now().isoformat()
        
        return cell.outputs
    
    def execute_all_cells(self) -> None:
        """Execute all cells in the notebook in order."""
        for i in range(len(self.cells)):
            self.execute_cell(i)
    
    def get_cell_dependencies(self, cell_index: int) -> Set[int]:
        """Get the indices of cells that the specified cell depends on.
        
        Args:
            cell_index: The index of the cell
            
        Returns:
            Set of cell indices that the cell depends on
        """
        if cell_index < 0 or cell_index >= len(self.cells):
            raise IndexError(f"Cell index {cell_index} out of range")
        
        cell = self.cells[cell_index]
        dependencies = set()
        
        # Check each previous cell to see if it produces any state
        # that the current cell depends on
        for i in range(cell_index):
            prev_cell = self.cells[i]
            if any(var in cell.state_dependencies for var in prev_cell.state_produces):
                dependencies.add(i)
        
        return dependencies
    
    def get_dependent_cells(self, cell_index: int) -> Set[int]:
        """Get the indices of cells that depend on the specified cell.
        
        Args:
            cell_index: The index of the cell
            
        Returns:
            Set of cell indices that depend on the cell
        """
        if cell_index < 0 or cell_index >= len(self.cells):
            raise IndexError(f"Cell index {cell_index} out of range")
        
        cell = self.cells[cell_index]
        dependents = set()
        
        # Check each following cell to see if it depends on any state
        # produced by the current cell
        for i in range(cell_index + 1, len(self.cells)):
            next_cell = self.cells[i]
            if any(var in next_cell.state_dependencies for var in cell.state_produces):
                dependents.add(i)
        
        return dependents
    
    def get_execution_graph(self) -> Dict[int, Set[int]]:
        """Get the execution dependency graph of the notebook.
        
        Returns:
            Dictionary mapping cell indices to the set of cell indices they depend on
        """
        graph = {}
        for i in range(len(self.cells)):
            graph[i] = self.get_cell_dependencies(i)
        return graph
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notebook to a dictionary representation.
        
        Returns:
            Dictionary representation of the notebook
        """
        return {
            "notebook_id": self.notebook_id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "cells": [
                {
                    "cell_id": cell.cell_id,
                    "type": cell.__class__.__name__,
                    "content": cell.content,
                    "outputs": cell.outputs,
                    # Include any cell-specific attributes
                    **({"model": cell.model, "temperature": cell.temperature} 
                       if isinstance(cell, PromptCell) else {})
                }
                for cell in self.cells
            ],
            # Don't store the full state, just the keys
            "state_keys": list(self.state.keys())
        }
    
    def save(self, filepath: str) -> None:
        """Save the notebook to a file.
        
        Args:
            filepath: The path to save the notebook to
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        # Update the timestamp
        self.updated_at = datetime.now().isoformat()
        
        # Save as JSON
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'Notebook':
        """Load a notebook from a file.
        
        Args:
            filepath: The path to load the notebook from
            
        Returns:
            The loaded notebook
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        notebook = cls(name=data.get('name', 'Untitled Notebook'))
        notebook.notebook_id = data.get('notebook_id', str(uuid.uuid4()))
        notebook.created_at = data.get('created_at', datetime.now().isoformat())
        notebook.updated_at = data.get('updated_at', notebook.created_at)
        notebook.metadata = data.get('metadata', {})
        
        # Recreate cells
        for cell_data in data.get('cells', []):
            cell_type = cell_data.get('type')
            content = cell_data.get('content', '')
            cell_id = cell_data.get('cell_id')
            
            if cell_type == 'MarkdownCell':
                cell = MarkdownCell(content, cell_id=cell_id)
            elif cell_type == 'ComputationCell':
                cell = ComputationCell(content, cell_id=cell_id)
            elif cell_type == 'PromptCell':
                model = cell_data.get('model', 'gpt-4')
                temperature = cell_data.get('temperature', 0.7)
                cell = PromptCell(content, cell_id=cell_id, 
                                model=model, temperature=temperature)
            elif cell_type == 'MemoryCell':
                cell = MemoryCell(content, cell_id=cell_id)
            else:
                raise ValueError(f"Unknown cell type: {cell_type}")
            
            # Restore outputs
            cell.outputs = cell_data.get('outputs', [])
            
            notebook.add_cell(cell)
        
        return notebook
    
    def clear_outputs(self) -> None:
        """Clear all cell outputs in the notebook."""
        for cell in self.cells:
            cell.outputs = []
    
    def clear_state(self) -> None:
        """Clear the notebook state."""
        self.state = {}
