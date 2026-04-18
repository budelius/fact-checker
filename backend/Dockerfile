FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:/workspace/backend/.venv/bin:${PATH}"

WORKDIR /workspace/backend

RUN rm -rf /var/cache/apt/* /var/lib/apt/lists/* \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl ffmpeg \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv tool install yt-dlp

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend ./

EXPOSE 8000

CMD ["/workspace/backend/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
