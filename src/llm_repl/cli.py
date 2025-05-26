"""
Command-line interface for LLM-REPL.

This module provides the command-line interface for creating, loading,
and interacting with LLM-REPL notebooks.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .notebook import Notebook
from .cells import MarkdownCell, ComputationCell, PromptCell, MemoryCell
from .llm import get_llm_provider, set_provider


console = Console()


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="LLM-REPL: A REPL-first approach to LLM interactions"
    )
    parser.add_argument(
        "notebook", nargs="?", help="Path to a notebook file to load"
    )
    parser.add_argument(
        "--new", "-n", action="store_true", help="Create a new notebook"
    )
    parser.add_argument(
        "--name", help="Name for the new notebook"
    )
    parser.add_argument(
        "--provider", choices=["openai", "mock"], 
        help="LLM provider to use"
    )
    parser.add_argument(
        "--api-key", help="API key for the LLM provider"
    )
    
    args = parser.parse_args()
    
    # Configure LLM provider if specified
    if args.provider:
        provider_args = {}
        if args.api_key:
            provider_args["api_key"] = args.api_key
        set_provider(args.provider, **provider_args)
    
    # Create or load a notebook
    if args.new or not args.notebook:
        notebook_name = args.name or "Untitled Notebook"
        notebook = Notebook(name=notebook_name)
        console.print(f"Created new notebook: [bold]{notebook_name}[/bold]")
    else:
        try:
            notebook = Notebook.load(args.notebook)
            console.print(f"Loaded notebook: [bold]{notebook.name}[/bold]")
        except Exception as e:
            console.print(f"[bold red]Error loading notebook:[/bold red] {str(e)}")
            sys.exit(1)
    
    # Start the REPL
    repl = NotebookREPL(notebook)
    repl.run()


class NotebookREPL:
    """Interactive REPL for working with notebooks."""
    
    def __init__(self, notebook: Notebook):
        """Initialize the REPL.
        
        Args:
            notebook: The notebook to work with
        """
        self.notebook = notebook
        self.console = Console()
        self.current_cell_index = len(notebook.cells)
    
    def run(self) -> None:
        """Run the REPL loop."""
        self.print_welcome()
        
        while True:
            try:
                command = Prompt.ask(
                    "\n[bold blue]llm-repl[/bold blue]", 
                    default="help"
                )
                
                if command == "exit" or command == "quit":
                    if self._confirm_exit():
                        break
                elif command == "help":
                    self.print_help()
                elif command.startswith("save"):
                    self._handle_save(command)
                elif command == "list":
                    self._list_cells()
                elif command.startswith("show"):
                    self._handle_show(command)
                elif command.startswith("exec"):
                    self._handle_exec(command)
                elif command == "run":
                    self._run_all()
                elif command.startswith("new"):
                    self._handle_new(command)
                elif command.startswith("edit"):
                    self._handle_edit(command)
                elif command.startswith("delete"):
                    self._handle_delete(command)
                elif command == "state":
                    self._show_state()
                elif command == "clear":
                    self._clear_outputs()
                elif command == "reset":
                    self._reset_state()
                elif command == "graph":
                    self._show_dependency_graph()
                else:
                    self.console.print("[yellow]Unknown command. Type 'help' for assistance.[/yellow]")
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled.[/yellow]")
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    def print_welcome(self) -> None:
        """Print the welcome message."""
        self.console.print(Panel(
            "[bold]Welcome to LLM-REPL[/bold]\n\n"
            "A REPL-first approach to LLM interactions, inspired by Jupyter notebooks.\n"
            "Type [bold]help[/bold] to see available commands.",
            title="LLM-REPL v0.1.0",
            expand=False
        ))
    
    def print_help(self) -> None:
        """Print the help message."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")
        
        commands = [
            ("help", "Show this help message"),
            ("list", "List all cells in the notebook"),
            ("show <index>", "Show the content of a cell"),
            ("new markdown", "Create a new markdown cell"),
            ("new code", "Create a new code cell"),
            ("new prompt", "Create a new prompt cell"),
            ("new memory", "Create a new memory cell"),
            ("edit <index>", "Edit a cell"),
            ("delete <index>", "Delete a cell"),
            ("exec <index>", "Execute a specific cell"),
            ("run", "Execute all cells in order"),
            ("save [path]", "Save the notebook"),
            ("state", "Show the current notebook state"),
            ("clear", "Clear all cell outputs"),
            ("reset", "Reset the notebook state"),
            ("graph", "Show the cell dependency graph"),
            ("exit", "Exit the REPL")
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        self.console.print(help_table)
    
    def _confirm_exit(self) -> bool:
        """Confirm exit if there are unsaved changes.
        
        Returns:
            True if the user wants to exit, False otherwise
        """
        # TODO: Track changes and ask for confirmation
        return True
    
    def _handle_save(self, command: str) -> None:
        """Handle the save command.
        
        Args:
            command: The save command
        """
        parts = command.split(maxsplit=1)
        if len(parts) > 1:
            filepath = parts[1]
        else:
            # Default filename based on notebook name
            safe_name = "".join(c if c.isalnum() else "_" for c in self.notebook.name)
            filepath = f"{safe_name}.llmn"
        
        try:
            self.notebook.save(filepath)
            self.console.print(f"Notebook saved to [bold]{filepath}[/bold]")
        except Exception as e:
            self.console.print(f"[bold red]Error saving notebook:[/bold red] {str(e)}")
    
    def _list_cells(self) -> None:
        """List all cells in the notebook."""
        if not self.notebook.cells:
            self.console.print("[yellow]No cells in notebook.[/yellow]")
            return
        
        table = Table(title=f"Cells in {self.notebook.name}")
        table.add_column("#", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content Preview")
        table.add_column("Outputs", style="yellow")
        
        for i, cell in enumerate(self.notebook.cells):
            # Get a preview of the cell content
            content_preview = cell.content.split("\n")[0][:50]
            if len(cell.content.split("\n")) > 1 or len(cell.content) > 50:
                content_preview += "..."
            
            # Count outputs
            output_count = len(cell.outputs)
            output_info = f"{output_count} output(s)" if output_count else "No outputs"
            
            table.add_row(
                str(i),
                cell.__class__.__name__.replace("Cell", ""),
                content_preview,
                output_info
            )
        
        self.console.print(table)
    
    def _handle_show(self, command: str) -> None:
        """Handle the show command.
        
        Args:
            command: The show command
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: show <index>[/yellow]")
            return
        
        try:
            index = int(parts[1])
            if index < 0 or index >= len(self.notebook.cells):
                self.console.print(f"[yellow]Cell index {index} out of range.[/yellow]")
                return
            
            cell = self.notebook.cells[index]
            
            # Display the cell content
            self.console.print(f"\n[bold]Cell {index} ({cell.__class__.__name__}):[/bold]")
            
            if isinstance(cell, MarkdownCell):
                self.console.print(Markdown(cell.content))
            else:
                self.console.print(Syntax(cell.content, "python"))
            
            # Display outputs
            if cell.outputs:
                self.console.print("\n[bold]Outputs:[/bold]")
                for i, output in enumerate(cell.outputs):
                    output_type = output.get("type", "unknown")
                    content = output.get("content", "")
                    
                    if output_type == "markdown":
                        self.console.print(Markdown(content))
                    elif output_type == "stdout":
                        self.console.print(Panel(content, title="stdout", border_style="green"))
                    elif output_type == "error":
                        self.console.print(Panel(content, title="error", border_style="red"))
                    elif output_type == "llm_response":
                        prompt = output.get("prompt", "")
                        self.console.print(Panel(prompt, title="prompt", border_style="blue"))
                        self.console.print(Panel(content, title="response", border_style="purple"))
                    elif output_type == "memory_update":
                        added = output.get("added", [])
                        updated_state = output.get("updated_state", {})
                        
                        table = Table(title="Memory Updates")
                        table.add_column("Variable", style="cyan")
                        table.add_column("Value")
                        
                        for var, value in updated_state.items():
                            table.add_row(var, str(value))
                        
                        self.console.print(table)
                    else:
                        self.console.print(f"Output {i} ({output_type}): {content}")
            else:
                self.console.print("\n[yellow]No outputs.[/yellow]")
                
        except ValueError:
            self.console.print("[yellow]Invalid cell index.[/yellow]")
    
    def _handle_exec(self, command: str) -> None:
        """Handle the exec command.
        
        Args:
            command: The exec command
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: exec <index>[/yellow]")
            return
        
        try:
            index = int(parts[1])
            if index < 0 or index >= len(self.notebook.cells):
                self.console.print(f"[yellow]Cell index {index} out of range.[/yellow]")
                return
            
            self.console.print(f"Executing cell {index}...")
            outputs = self.notebook.execute_cell(index)
            
            self.console.print("[bold green]Execution complete.[/bold green]")
            
            # Show the outputs
            if outputs:
                self.console.print("\n[bold]Outputs:[/bold]")
                for output in outputs:
                    output_type = output.get("type", "unknown")
                    content = output.get("content", "")
                    
                    if output_type == "markdown":
                        self.console.print(Markdown(content))
                    elif output_type == "stdout":
                        self.console.print(Panel(content, title="stdout", border_style="green"))
                    elif output_type == "error":
                        self.console.print(Panel(content, title="error", border_style="red"))
                    elif output_type == "llm_response":
                        prompt = output.get("prompt", "")
                        self.console.print(Panel(prompt, title="prompt", border_style="blue"))
                        self.console.print(Panel(content, title="response", border_style="purple"))
                    elif output_type == "memory_update":
                        added = output.get("added", [])
                        updated_state = output.get("updated_state", {})
                        
                        table = Table(title="Memory Updates")
                        table.add_column("Variable", style="cyan")
                        table.add_column("Value")
                        
                        for var, value in updated_state.items():
                            table.add_row(var, str(value))
                        
                        self.console.print(table)
            else:
                self.console.print("[yellow]No outputs.[/yellow]")
                
        except ValueError:
            self.console.print("[yellow]Invalid cell index.[/yellow]")
        except Exception as e:
            self.console.print(f"[bold red]Error executing cell:[/bold red] {str(e)}")
    
    def _run_all(self) -> None:
        """Execute all cells in the notebook."""
        if not self.notebook.cells:
            self.console.print("[yellow]No cells to execute.[/yellow]")
            return
        
        try:
            self.console.print("Executing all cells...")
            
            for i in range(len(self.notebook.cells)):
                self.console.print(f"Executing cell {i}...")
                self.notebook.execute_cell(i)
            
            self.console.print("[bold green]All cells executed successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Error executing cells:[/bold red] {str(e)}")
    
    def _handle_new(self, command: str) -> None:
        """Handle the new command.
        
        Args:
            command: The new command
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: new <cell_type>[/yellow]")
            return
        
        cell_type = parts[1].lower()
        
        try:
            if cell_type == "markdown":
                self._create_markdown_cell()
            elif cell_type == "code":
                self._create_code_cell()
            elif cell_type == "prompt":
                self._create_prompt_cell()
            elif cell_type == "memory":
                self._create_memory_cell()
            else:
                self.console.print(
                    "[yellow]Invalid cell type. "
                    "Available types: markdown, code, prompt, memory[/yellow]"
                )
        except Exception as e:
            self.console.print(f"[bold red]Error creating cell:[/bold red] {str(e)}")
    
    def _create_markdown_cell(self) -> None:
        """Create a new markdown cell."""
        self.console.print("\n[bold]Enter markdown content (Ctrl+D to finish):[/bold]")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        
        if not content.strip():
            self.console.print("[yellow]Cancelled: empty content.[/yellow]")
            return
        
        cell = self.notebook.create_markdown_cell(content)
        self.console.print(f"[bold green]Created markdown cell at index {len(self.notebook.cells) - 1}.[/bold green]")
    
    def _create_code_cell(self) -> None:
        """Create a new code cell."""
        self.console.print("\n[bold]Enter Python code (Ctrl+D to finish):[/bold]")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        
        if not content.strip():
            self.console.print("[yellow]Cancelled: empty content.[/yellow]")
            return
        
        cell = self.notebook.create_computation_cell(content)
        self.console.print(f"[bold green]Created code cell at index {len(self.notebook.cells) - 1}.[/bold green]")
    
    def _create_prompt_cell(self) -> None:
        """Create a new prompt cell."""
        self.console.print("\n[bold]Enter prompt template (Ctrl+D to finish):[/bold]")
        self.console.print("[italic]Use {variable} syntax to reference state variables[/italic]")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        
        if not content.strip():
            self.console.print("[yellow]Cancelled: empty content.[/yellow]")
            return
        
        model = Prompt.ask("Model", default="gpt-4")
        temperature = float(Prompt.ask("Temperature", default="0.7"))
        
        cell = self.notebook.create_prompt_cell(
            content, model=model, temperature=temperature
        )
        self.console.print(f"[bold green]Created prompt cell at index {len(self.notebook.cells) - 1}.[/bold green]")
    
    def _create_memory_cell(self) -> None:
        """Create a new memory cell."""
        self.console.print("\n[bold]Enter memory operations (Ctrl+D to finish):[/bold]")
        self.console.print("[italic]Use variable = value or memory.update({...}) syntax[/italic]")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        
        if not content.strip():
            self.console.print("[yellow]Cancelled: empty content.[/yellow]")
            return
        
        cell = self.notebook.create_memory_cell(content)
        self.console.print(f"[bold green]Created memory cell at index {len(self.notebook.cells) - 1}.[/bold green]")
    
    def _handle_edit(self, command: str) -> None:
        """Handle the edit command.
        
        Args:
            command: The edit command
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: edit <index>[/yellow]")
            return
        
        try:
            index = int(parts[1])
            if index < 0 or index >= len(self.notebook.cells):
                self.console.print(f"[yellow]Cell index {index} out of range.[/yellow]")
                return
            
            cell = self.notebook.cells[index]
            
            self.console.print(f"\n[bold]Editing cell {index} ({cell.__class__.__name__}):[/bold]")
            self.console.print("[italic]Current content:[/italic]")
            
            if isinstance(cell, MarkdownCell):
                self.console.print(Markdown(cell.content))
            else:
                self.console.print(Syntax(cell.content, "python"))
            
            self.console.print("\n[bold]Enter new content (Ctrl+D to finish):[/bold]")
            
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            
            new_content = "\n".join(lines)
            
            if not new_content.strip():
                self.console.print("[yellow]Cancelled: empty content.[/yellow]")
                return
            
            # Update the cell content
            cell.content = new_content
            
            # Clear outputs since the content has changed
            cell.outputs = []
            
            self.console.print(f"[bold green]Updated cell {index}.[/bold green]")
                
        except ValueError:
            self.console.print("[yellow]Invalid cell index.[/yellow]")
    
    def _handle_delete(self, command: str) -> None:
        """Handle the delete command.
        
        Args:
            command: The delete command
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: delete <index>[/yellow]")
            return
        
        try:
            index = int(parts[1])
            if index < 0 or index >= len(self.notebook.cells):
                self.console.print(f"[yellow]Cell index {index} out of range.[/yellow]")
                return
            
            if Confirm.ask(f"Are you sure you want to delete cell {index}?"):
                del self.notebook.cells[index]
                self.console.print(f"[bold green]Deleted cell {index}.[/bold green]")
                
        except ValueError:
            self.console.print("[yellow]Invalid cell index.[/yellow]")
    
    def _show_state(self) -> None:
        """Show the current notebook state."""
        if not self.notebook.state:
            self.console.print("[yellow]Notebook state is empty.[/yellow]")
            return
        
        table = Table(title="Notebook State")
        table.add_column("Variable", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Value")
        
        for key, value in self.notebook.state.items():
            # Truncate long values
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            
            table.add_row(
                key,
                type(value).__name__,
                value_str
            )
        
        self.console.print(table)
    
    def _clear_outputs(self) -> None:
        """Clear all cell outputs."""
        if Confirm.ask("Are you sure you want to clear all cell outputs?"):
            self.notebook.clear_outputs()
            self.console.print("[bold green]All cell outputs cleared.[/bold green]")
    
    def _reset_state(self) -> None:
        """Reset the notebook state."""
        if Confirm.ask("Are you sure you want to reset the notebook state?"):
            self.notebook.clear_state()
            self.console.print("[bold green]Notebook state reset.[/bold green]")
    
    def _show_dependency_graph(self) -> None:
        """Show the cell dependency graph."""
        if not self.notebook.cells:
            self.console.print("[yellow]No cells in notebook.[/yellow]")
            return
        
        graph = self.notebook.get_execution_graph()
        
        table = Table(title="Cell Dependencies")
        table.add_column("Cell", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Depends On", style="yellow")
        table.add_column("Required By", style="magenta")
        
        for i, cell in enumerate(self.notebook.cells):
            # Get dependencies
            deps = graph.get(i, set())
            dep_str = ", ".join(str(d) for d in sorted(deps)) if deps else "None"
            
            # Get dependents
            dependents = self.notebook.get_dependent_cells(i)
            dep_by_str = ", ".join(str(d) for d in sorted(dependents)) if dependents else "None"
            
            table.add_row(
                str(i),
                cell.__class__.__name__.replace("Cell", ""),
                dep_str,
                dep_by_str
            )
        
        self.console.print(table)


if __name__ == "__main__":
    main()
