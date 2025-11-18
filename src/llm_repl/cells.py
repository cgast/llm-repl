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

            # Create restricted globals to prevent access to dangerous functions
            # while still allowing common built-ins
            safe_builtins = {
                'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
                'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
                'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'hex': hex,
                'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map,
                'max': max, 'min': min, 'next': next, 'oct': oct,
                'ord': ord, 'pow': pow, 'print': print, 'range': range,
                'repr': repr, 'reversed': reversed, 'round': round,
                'set': set, 'slice': slice, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
                '__import__': __import__,  # Needed for imports but could be restricted further
            }

            safe_globals = {
                '__builtins__': safe_builtins,
                '__name__': '__main__',
                '__doc__': None,
            }

            # Parse AST for dependency analysis before execution
            self._analyze_dependencies(state)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exec(self.content, safe_globals, local_ns)

            stdout = buffer.getvalue()
            if stdout:
                self.outputs.append({"type": "stdout", "content": stdout})

            # Update the state with new or modified variables
            # Filter out private/dunder variables and builtins
            new_state = state.copy()
            for key, value in local_ns.items():
                # Skip private variables and builtins
                if key.startswith('_'):
                    continue
                # Skip if key is in original state and value hasn't changed
                if key in original_keys:
                    try:
                        if state[key] == value:
                            continue
                    except Exception:
                        # If comparison fails, consider it changed
                        pass

                new_state[key] = value
                self._state_produces.add(key)

            return new_state

        except Exception as e:
            self.outputs.append({"type": "error", "content": str(e)})
            return state

    def _analyze_dependencies(self, state: Dict[str, Any]) -> None:
        """Analyze code dependencies using AST parsing.

        Args:
            state: The current notebook state
        """
        try:
            import ast

            class DependencyVisitor(ast.NodeVisitor):
                """AST visitor to identify variable dependencies."""

                def __init__(self, state_vars: Set[str]):
                    self.state_vars = state_vars
                    self.dependencies = set()
                    self.assignments = set()

                def visit_Name(self, node: ast.Name) -> None:
                    """Visit a Name node (variable reference)."""
                    if isinstance(node.ctx, ast.Load) and node.id in self.state_vars:
                        # Variable is being read
                        if node.id not in self.assignments:
                            self.dependencies.add(node.id)
                    elif isinstance(node.ctx, ast.Store):
                        # Variable is being assigned
                        self.assignments.add(node.id)
                    self.generic_visit(node)

            tree = ast.parse(self.content)
            visitor = DependencyVisitor(set(state.keys()))
            visitor.visit(tree)
            self._state_dependencies = visitor.dependencies

        except SyntaxError:
            # If parsing fails, fall back to empty dependencies
            self._state_dependencies = set()


class PromptCell(Cell):
    """Cell for LLM interactions."""

    def __init__(self, content: str, cell_id: Optional[str] = None,
                 model: str = "gpt-4", temperature: float = 0.7,
                 response_var: Optional[str] = None):
        """Initialize a prompt cell.

        Args:
            content: The prompt template
            cell_id: Optional unique identifier for the cell
            model: The LLM model to use
            temperature: The sampling temperature for the LLM (0.0-2.0)
            response_var: Optional name for the response variable (defaults to auto-generated)

        Raises:
            ValueError: If parameters are invalid
        """
        super().__init__(content, cell_id)

        # Validate temperature
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temperature}")

        # Validate response_var if provided
        if response_var is not None:
            if not isinstance(response_var, str) or not response_var:
                raise ValueError("response_var must be a non-empty string")
            if not response_var.isidentifier():
                raise ValueError(f"response_var '{response_var}' is not a valid Python identifier")

        self.model = model
        self.temperature = temperature
        self.response_var = response_var
        self._cell_index = None  # Will be set during execution
        
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

            # Determine the response variable name
            if self.response_var:
                # Use custom response variable name
                response_var = self.response_var
            elif self._cell_index is not None:
                # Use cell index for predictable naming
                response_var = f"response_{self._cell_index}"
            else:
                # Fallback to shortened cell_id
                response_var = f"response_{self.cell_id[:8]}"

            # Update the state with the response
            new_state = state.copy()
            new_state[response_var] = response
            new_state['_'] = response  # IPython-style last response
            self._state_produces.add(response_var)
            self._state_produces.add('_')

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
                    try:
                        update_dict = ast.literal_eval(line[14:-1])
                        if not isinstance(update_dict, dict):
                            raise ValueError("memory.update() requires a dictionary")

                        # Track dependencies
                        for value in update_dict.values():
                            if isinstance(value, str) and value in state:
                                self._state_dependencies.add(value)

                        # Update the state
                        new_state.update(update_dict)

                        # Track produced variables
                        for key in update_dict:
                            self._state_produces.add(key)
                    except (ValueError, SyntaxError) as e:
                        self.outputs.append({
                            "type": "error",
                            "content": f"Error parsing memory.update(): {str(e)}"
                        })
                        continue

                elif '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
                    # Simple variable assignment (but not comparison)
                    var_name, value = line.split('=', 1)
                    var_name = var_name.strip()
                    value = value.strip()

                    # Try to safely evaluate the value
                    import ast
                    try:
                        # First try literal_eval for safe literals
                        evaluated_value = ast.literal_eval(value)
                        new_state[var_name] = evaluated_value
                        self._state_produces.add(var_name)
                    except (ValueError, SyntaxError):
                        # If not a literal, try to evaluate in restricted context
                        # This allows references to state variables
                        try:
                            # Use AST to detect dependencies
                            self._detect_dependencies_in_expression(value, state)

                            # Create safe evaluation environment
                            safe_builtins = {
                                'abs': abs, 'bool': bool, 'dict': dict, 'float': float,
                                'int': int, 'len': len, 'list': list, 'max': max,
                                'min': min, 'range': range, 'set': set, 'str': str,
                                'sum': sum, 'tuple': tuple,
                            }
                            safe_globals = {'__builtins__': safe_builtins}

                            # Evaluate with state as locals
                            evaluated_value = eval(value, safe_globals, new_state)
                            new_state[var_name] = evaluated_value
                            self._state_produces.add(var_name)
                        except Exception as e:
                            # If all evaluation fails, store as string with warning
                            new_state[var_name] = value
                            self._state_produces.add(var_name)
                            self.outputs.append({
                                "type": "warning",
                                "content": f"Could not evaluate '{value}', storing as string: {str(e)}"
                            })

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

    def _detect_dependencies_in_expression(self, expression: str, state: Dict[str, Any]) -> None:
        """Detect state variable dependencies in an expression using AST.

        Args:
            expression: The expression to analyze
            state: The current notebook state
        """
        try:
            import ast

            tree = ast.parse(expression, mode='eval')
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id in state:
                        self._state_dependencies.add(node.id)
        except SyntaxError:
            # If parsing fails, can't detect dependencies
            pass
