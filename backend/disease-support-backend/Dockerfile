FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==1.4.2

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .

# Create necessary directories
RUN mkdir -p /app/app/data/content_cache
RUN mkdir -p /app/app/data/search_terms
RUN mkdir -p /app/app/data/llm_organizations
RUN mkdir -p /app/app/data/llm_stats

# Use main_llm_enhanced.py instead of main.py
CMD ["uvicorn", "app.main_llm_enhanced:app", "--host", "0.0.0.0", "--port", "8080"]
