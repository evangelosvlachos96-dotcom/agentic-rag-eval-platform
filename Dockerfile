FROM python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.15
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --extra api
RUN useradd --uid 10001 --create-home appuser
USER appuser
ENV RAG_DATASET_DIR=/data/dataset
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "ragplatform.api.app:local_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

