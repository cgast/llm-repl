#!/usr/bin/env python3
"""
Setup script for the LLM-REPL package.
"""

from setuptools import setup, find_packages

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-repl",
    version="0.1.0",
    author="CGAST",
    description="A REPL-first approach to LLM interactions, inspired by Jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CGAST/llm-repl",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "rich>=10.0.0",
        "prompt-toolkit>=3.0.0",
        "pyyaml>=6.0",
        "ipython>=8.0.0",
        "jupyter-client>=7.0.0",
        "nbformat>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "llm-repl=llm_repl.cli:main",
        ],
    },
)
