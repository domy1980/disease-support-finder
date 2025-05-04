
mkdir -p backend/disease-support-backend/app/data/content_cache
mkdir -p backend/disease-support-backend/app/data/search_terms
mkdir -p backend/disease-support-backend/app/data/llm_organizations
mkdir -p backend/disease-support-backend/app/data/llm_stats

cd backend/disease-support-backend

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment and installing dependencies..."
  python -m venv .venv
  source .venv/bin/activate
  pip install poetry
  poetry install
else
  echo "Using existing virtual environment..."
  source .venv/bin/activate
fi

echo "Starting backend server with LLM endpoints..."
uvicorn app.main_llm_enhanced:app --host 0.0.0.0 --port 8000 --reload
