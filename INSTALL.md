# Installation Guide for LLM-REPL

This guide will help you install and set up the LLM-REPL package on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/CGAST/llm-repl.git
   cd llm-repl
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   This will install the package in "editable" mode, allowing you to make changes to the code and have them immediately reflected without reinstalling.

### Method 2: Install from PyPI (Coming Soon)

Once the package is published to PyPI, you can install it directly using pip:

```bash
pip install llm-repl
```

## Configuration

After installation, you'll need to configure your LLM provider. By default, LLM-REPL uses a mock provider for testing.

### OpenAI Configuration

To use OpenAI's models, you'll need to set your API key:

1. Set the API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```

2. Or create a configuration file:
   ```bash
   mkdir -p ~/.llm-repl
   echo "provider:
     type: openai
     api_key: your-api-key-here" > ~/.llm-repl/config.yaml
   ```

## Verifying Installation

To verify that LLM-REPL is installed correctly, run:

```bash
llm-repl --help
```

You should see the help message for the LLM-REPL command-line interface.

## Running the Examples

The package includes several examples to help you get started:

1. Run the sample notebook:
   ```bash
   llm-repl examples/sample_notebook.llmn
   ```

2. Run the programmatic usage example:
   ```bash
   python examples/programmatic_usage.py
   ```

## Troubleshooting

If you encounter any issues during installation or usage:

1. Make sure you're using Python 3.8 or higher:
   ```bash
   python --version
   ```

2. Check that all dependencies are installed:
   ```bash
   pip list | grep -E 'openai|rich|prompt-toolkit|pyyaml|ipython|jupyter-client|nbformat'
   ```

3. Verify your configuration:
   ```bash
   cat ~/.llm-repl/config.yaml
   ```

4. If you're using OpenAI, make sure your API key is valid and has sufficient credits.

## Next Steps

Once you have LLM-REPL installed, check out the [README.md](README.md) for more information on how to use the package.
