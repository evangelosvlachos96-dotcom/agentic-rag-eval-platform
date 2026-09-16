"""Ingestion: turning raw sources into `Document` and `Chunk` objects.

Planned responsibilities (Milestone 2):

- loaders for text, Markdown, HTML and PDF sources
- structure-aware chunking (headings, paragraphs, token budgets, overlap)
- metadata extraction and propagation from document to chunk
- near-duplicate detection so the corpus does not contain repeated content
"""
