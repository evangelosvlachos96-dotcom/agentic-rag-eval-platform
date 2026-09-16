"""Retrieval: finding the chunks most relevant to a query.

Planned responsibilities (Milestone 3):

- a pluggable `Embedder` interface with a local sentence-transformers default
- a vector store abstraction (in-memory first, swappable later)
- BM25 lexical retrieval
- hybrid search that fuses lexical and vector results with Reciprocal Rank Fusion
- cross-encoder reranking of the fused candidate list
"""
