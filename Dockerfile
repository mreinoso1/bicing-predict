FROM python:3.12-slim 
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .
COPY README.md .
COPY ./src ./src
RUN uv pip install --system --no-cache .
