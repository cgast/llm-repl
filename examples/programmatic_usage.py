#!/usr/bin/env python3
"""
Example of programmatic usage of the LLM-REPL library.

This script demonstrates how to create and manipulate notebooks
programmatically, without using the CLI interface.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_repl.notebook import Notebook
from src.llm_repl.llm import set_provider, MockProvider


def main():
    """Run the example."""
    # Use the mock provider for this example
    set_provider("mock")
    
    # Create a new notebook
    notebook = Notebook(name="Programmatic Example")
    
    # Add a markdown cell
    notebook.create_markdown_cell("""
# Programmatic LLM-REPL Example

This notebook was created programmatically to demonstrate the API.
    """)
    
    # Add a computation cell
    notebook.create_computation_cell("""
# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create some sample data
data = pd.DataFrame({
    'x': np.linspace(0, 10, 100),
    'y': np.sin(np.linspace(0, 10, 100))
})

# Display basic info
print(f"Data shape: {data.shape}")
print(data.head())

# Store the data for later use
context = "This is a sine wave dataset."
    """)
    
    # Add a prompt cell
    notebook.create_prompt_cell("""
Analyze this dataset:

x values range from {data['x'].min()} to {data['x'].max()}
y values range from {data['y'].min()} to {data['y'].max()}

Context: {context}

What patterns do you observe in this data?
    """)
    
    # Add a memory cell
    notebook.create_memory_cell("""
# Store the analysis
analysis_summary = response_u1v2w3  # This would be the actual variable name from the prompt cell

# Extract key points
key_points = [
    "Sine wave pattern",
    "Regular oscillation",
    "Period of 2π"
]

# Store for future reference
memory.update({
    "key_points": key_points,
    "data_type": "sine_wave"
})
    """)
    
    # Execute all cells
    print("Executing all cells...")
    notebook.execute_all_cells()
    
    # Print the notebook state
    print("\nNotebook state after execution:")
    for key, value in notebook.state.items():
        print(f"  {key}: {type(value).__name__} = {str(value)[:50]}...")
    
    # Save the notebook
    output_path = "programmatic_example.llmn"
    notebook.save(output_path)
    print(f"\nNotebook saved to {output_path}")
    
    # Demonstrate loading a notebook
    print("\nLoading the notebook back...")
    loaded_notebook = Notebook.load(output_path)
    print(f"Loaded notebook: {loaded_notebook.name}")
    print(f"Number of cells: {len(loaded_notebook.cells)}")
    
    # Clean up
    os.remove(output_path)
    print(f"Removed {output_path}")


if __name__ == "__main__":
    main()
