"""Pipelines: reproducible dataset versions and experiment runs.

Current responsibilities:

- ``run_config``: the YAML run configuration (retrieval + generation + judge)
  shared by ``rag query`` and ``rag eval run``

Planned (Milestone 8 and 9):

- an async batch runner with retries for large evaluation sweeps
- experiment sweeps over chunking, retrieval mode and reranking
"""
