"""Ingestion: turning raw sources into `Document` and `Chunk` objects.

Responsibilities (Milestone 2):

- ``corpus``: download the pinned PEP corpus with a content-hash manifest
- ``loaders``: parse ``.rst``, ``.md`` and ``.txt`` files into a document plus
  its heading hierarchy (:class:`ParsedDocument`)
- ``tokens``: the token-counting interface used by the chunker
- ``chunking``: structure-aware chunking under a token budget with overlap
- ``dedup``: exact (hash) and near-duplicate (MinHash) chunk removal
- ``dataset``: versioned ``chunks.jsonl`` + ``manifest.json`` on disk
- ``pipeline``: the ``ingest`` entry point that wires the steps together
"""

from ragplatform.ingestion.chunking import ChunkingConfig, ChunkMetadata, chunk_document, index_text
from ragplatform.ingestion.dataset import DatasetManifest, dataset_dir, read_chunks
from ragplatform.ingestion.dedup import DedupConfig, DedupReport, dedup_chunks
from ragplatform.ingestion.loaders import ParsedDocument, Section, load_file
from ragplatform.ingestion.pipeline import IngestResult, ingest_directory
from ragplatform.ingestion.tokens import ApproxTokenCounter, TokenCounter

__all__ = [
    "ApproxTokenCounter",
    "ChunkMetadata",
    "ChunkingConfig",
    "DatasetManifest",
    "DedupConfig",
    "DedupReport",
    "IngestResult",
    "ParsedDocument",
    "Section",
    "TokenCounter",
    "chunk_document",
    "dataset_dir",
    "dedup_chunks",
    "index_text",
    "ingest_directory",
    "load_file",
    "read_chunks",
]
