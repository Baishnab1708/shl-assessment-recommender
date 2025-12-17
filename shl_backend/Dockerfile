FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/tmp/hf
ENV TRANSFORMERS_CACHE=/tmp/hf

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libomp5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY src ./src
COPY data ./data

CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
