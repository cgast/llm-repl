"""
Cell types for LLM-REPL.

This module defines the different types of cells that can be used in an LLM-REPL notebook:
- MarkdownCell: Documentation and context
- PromptCell: Inputs to the LLM with explicit state dependencies
- ComputationCell: Traditional Python code execution
- MemoryCell: Persistent context/variables that accumulate
"""

from abc import ABC, abstractmethod
import inspect
from typing import Any, Dict, List, Optional, Set, Union
import uuid


class Cell(ABC):
    """Base class for all cell types."""

    def __init__(self, content: str, cell_id: Optional[str] = None):
        """Initialize a cell.
        
        Args:
            content: The content of the cell
            cell_id: Optional unique identifier for the cell
        """
        self.content = content
        self.cell_id = cell_id or str(uuid.uuid4())
        self.outputs = []
        self._state_dependencies = set()
        self._state_produces = set()
        
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the cell and return the updated state.
        
        Args:
            state: The current notebook state
            
        Returns:
            The updated state after cell execution
        """
        pass
    
    @property
    def state_dependencies(self) -> Set[str]:
        """Get the variables from the state that this cell depends on."""
        return self._state_dependencies
    
    @property
    def state_produces(self) -> Set[str]:
        """Get the variables that this cell adds to the state."""
        return self._state_produces


class MarkdownCell(Cell):
    """Cell for Markdown documentation."""

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Render the markdown content.
        
        Args:
            state: The current notebook state
            
        Returns:
            The unchanged state
        """
        # For an MVP, we just store the markdown as an output
        # In a real implementation, we would render it
        self.outputs = [{"type": "markdown", "content": self.content}]
        return state


class ComputationCell(Cell):
    """Cell for executing Python code."""

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python code in the cell.
        
        Args:
            state: The current notebook state
            
        Returns:
            The updated state after code execution
        """
        # Clear previous outputs
        self.outputs = []
        
        # Create a local namespace with the current state
        local_ns = state.copy()
        
        # Track the original state keys to identify new additions
        original_keys = set(state.keys())
        
        # Execute the code
        try:
            # Capture stdout for code execution
            import io
            import sys
            from contextlib import redirect_stdout
            
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exec(self.content, globals(), local_ns)
            
            stdout = buffer.getvalue()
            if stdout:
                self.outputs.append({"type": "stdout", "content": stdout})
            
            # Update the state dependencies based on variables accessed
            # This is a simplified approach for the MVP
            for line in self.content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    # Very basic parsing to extract variable assignments
                    var_name = line.split('=')[0].strip()
                    if var_name in state:
                        self._state_dependencies.add(var_name)
            
            # Update the state with new or modified variables
            new_state = state.copy()
            for key, value in local_ns.items():
                if key not in original_keys or state[key] != value:
                    new_state[key] = value
                    self._state_produces.add(key)
            
            return new_state
            
        except Exception as e:
            self.outputs.append({"type": "error", "content": str(e)})
            return state


class PromptCell(Cell):
    """Cell for LLM interactions."""

    def __init__(self, content: str, cell_id: Optional[str] = None, 
                 model: str = "gpt-4", temperature: float = 0.7):
        """Initialize a prompt cell.
        
        Args:
            content: The prompt template
            cell_id: Optional unique identifier for the cell
            model: The LLM model to use
            temperature: The sampling temperature for the LLM
        """
        super().__init__(content, cell_id)
        self.model = model
        self.temperature = temperature
        
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the prompt with the LLM.
        
        Args:
            state: The current notebook state
            
        Returns:
            The updated state with the LLM response
        """
        from .llm import get_llm_provider
        
        # Clear previous outputs
        self.outputs = []
        
        # Format the prompt template with values from the state
        formatted_prompt = self.content
        
        # Find all variables referenced in the prompt using {} format syntax
        import re
        state_vars = re.findall(r'{(\w+)(?:\.\w+\(\))?}', self.content)
        
        # Add them to dependencies
        for var in state_vars:
            if var in state:
                self._state_dependencies.add(var)
                
        try:
            # Basic string formatting for the MVP
            # A more robust implementation would handle nested attributes and method calls
            formatted_prompt = self.content.format(**state)
            
            # Get the LLM provider
            llm = get_llm_provider()
            
            # Generate a response
            response = llm.generate(
                prompt=formatted_prompt,
                model=self.model,
                temperature=self.temperature
            )
            
            # Store the response
            self.outputs.append({
                "type": "llm_response",
                "prompt": formatted_prompt,
                "content": response
            })
            
            # Update the state with the response
            response_var = f"response_{self.cell_id.split('-')[0]}"
            new_state = state.copy()
            new_state[response_var] = response
            self._state_produces.add(response_var)
            
            return new_state
            
        except KeyError as e:
            self.outputs.append({
                "type": "error", 
                "content": f"Missing variable in state: {str(e)}"
            })
            return state
        except Exception as e:
            self.outputs.append({"type": "error", "content": str(e)})
            return state


class MemoryCell(Cell):
    """Cell for explicitly managing state."""

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update the state based on memory operations.
        
        Args:
            state: The current notebook state
            
        Returns:
            The updated state
        """
        # Clear previous outputs
        self.outputs = []
        
        try:
            # For the MVP, we'll use a simple format:
            # Each line is a key-value pair or operation
            new_state = state.copy()
            
            for line in self.content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('memory.update('):
                    # Parse the update dictionary
                    import ast
                    update_dict = ast.literal_eval(line[14:-1])
                    
                    # Track dependencies
                    for value in update_dict.values():
                        if isinstance(value, str) and value in state:
                            self._state_dependencies.add(value)
                    
                    # Update the state
                    new_state.update(update_dict)
                    
                    # Track produced variables
                    for key in update_dict:
                        self._state_produces.add(key)
                
                elif '=' in line:
                    # Simple variable assignment
                    var_name, value = line.split('=', 1)
                    var_name = var_name.strip()
                    value = value.strip()
                    
                    # Try to evaluate the value in the context of the state
                    try:
                        evaluated_value = eval(value, globals(), new_state)
                        new_state[var_name] = evaluated_value
                        self._state_produces.add(var_name)
                        
                        # Check for dependencies
                        for state_var in state:
                            if state_var in value:
                                self._state_dependencies.add(state_var)
                    except:
                        # If evaluation fails, store as string
                        new_state[var_name] = value
                        self._state_produces.add(var_name)
            
            # Record the memory operations
            self.outputs.append({
                "type": "memory_update",
                "added": list(self._state_produces),
                "updated_state": {k: str(v) for k, v in new_state.items() 
                                 if k in self._state_produces}
            })
            
            return new_state
            
        except Exception as e:
            self.outputs.append({"type": "error", "content": str(e)})
            return state
