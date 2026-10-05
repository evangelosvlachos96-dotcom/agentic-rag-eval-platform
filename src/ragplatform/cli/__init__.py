"""The ``rag`` command line interface (typer).

Commands are thin wrappers over library code so all logic stays tested:

- ``rag download-corpus``  -> :mod:`ragplatform.ingestion.corpus`
- ``rag ingest``           -> :mod:`ragplatform.ingestion.pipeline`
- ``rag index``            -> :mod:`ragplatform.retrieval.index`
- ``rag query``            -> :mod:`ragplatform.retrieval` + :mod:`ragplatform.generation`
- ``rag eval ...``         -> :mod:`ragplatform.evals`
"""

from __future__ import annotations

import typer

from ragplatform.cli.agent_cmds import agent_demo
from ragplatform.cli.eval_cmds import eval_app
from ragplatform.cli.ingest_cmds import register as _register_ingest
from ragplatform.cli.quality_cmds import quality_app
from ragplatform.cli.retrieval_cmds import register as _register_retrieval

app = typer.Typer(
    name="rag",
    help="Agentic RAG evaluation platform.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

_register_ingest(app)
_register_retrieval(app)
app.add_typer(eval_app, name="eval")
app.add_typer(quality_app, name="quality")


def main() -> None:
    app()


__all__ = ["app", "main"]


app.command("agent-demo")(agent_demo)
