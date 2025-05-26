# LLM-REPL

A REPL-first approach to LLM interactions, inspired by Jupyter notebooks.

## Concept

This project implements a notebook-style REPL (Read-Eval-Print Loop) for interacting with Large Language Models. Unlike traditional chat interfaces, LLM-REPL provides:

- **Transparency**: See the model's working memory and decision tree
- **Reproducibility**: Parameterize and version-control your LLM workflows
- **Composability**: Build reusable reasoning components
- **State management**: Persistent context and memory between interactions

## Features

- **Multiple cell types**:
  - **Markdown cells**: Documentation and context
  - **Prompt cells**: Inputs to the LLM with explicit state dependencies
  - **Computation cells**: Traditional Python code execution
  - **Memory cells**: Persistent context/variables that accumulate

- **State persistence**: Maintain a computational environment across cells
- **Reproducible workflows**: Re-run notebooks with different parameters
- **Explicit context management**: Control what information is passed to the LLM

## Installation

```bash
pip install llm-repl
```

## Quick Start

```bash
# Start the LLM-REPL interface
llm-repl

# Or load an existing notebook
llm-repl examples/analysis.llmn

# Start the web UI
cd web_ui && ./start.py
```

## Web UI

LLM-REPL includes a Jupyter notebook-style web interface that provides a more user-friendly way to interact with the LLM-REPL engine. The web UI is built with React and Flask, and provides the following features:

- **Notebook Management**: Create, edit, delete, save, and load notebooks
- **Cell Types**: Support for all LLM-REPL cell types (Markdown, Code, Prompt, Memory)
- **Cell Execution**: Execute individual cells or run all cells in a notebook
- **Real-time Updates**: WebSocket integration for real-time updates during cell execution
- **State Management**: View and manage the notebook state
- **LLM Provider Configuration**: Configure the LLM provider (OpenAI, Mock)

To start the web UI:

```bash
cd web_ui
./start.py
```

This will start both the backend Flask server and the frontend React development server, and open the web UI in your default browser.

For more information about the web UI, see the [Web UI README](web_ui/README.md).

## Example Workflow

```python
# [Cell 1 - Computation] Load and prepare data
dataset = load_csv("sales.csv")
analysis_context = "We're looking for seasonal trends in Q4"

# [Cell 2 - Prompt] Get LLM analysis
prompt: """
Analyze this dataset: {dataset.summary()} 
Context: {analysis_context}
"""
# -> llm_response = reasoning_chain + conclusions

# [Cell 3 - Computation] Validate findings
validated_trends = verify_trends(dataset, llm_response.trends)

# [Cell 4 - Memory] Update state for next prompt
memory.update({"validated_trends": validated_trends})
```

## Why REPL-first?

The REPL-first approach treats the notebook state as the persistent environment, rather than trying to make the LLM itself stateful. This creates true REPL semantics:

- **Read**: Gather cell inputs + accumulated state
- **Eval**: Execute LLM reasoning with full context
- **Print**: Display reasoning + results
- **Loop**: State persists for next cell

## Requirements

- Python 3.8+
- OpenAI API key or other compatible LLM provider

## License

MIT
