from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.api_enhanced import router as api_enhanced_router

app = FastAPI(title="Disease Support Finder API")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api")

app.include_router(api_enhanced_router, prefix="/api/v2")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "Disease Support Finder API",
        "docs": "/docs",
        "endpoints": {
            "diseases": "/api/diseases",
            "search": "/api/search",
            "disease_with_organizations": "/api/disease/{disease_id}",
            "organizations": "/api/organizations/{disease_id}",
            "enhanced_api": {
                "all_diseases": "/api/v2/diseases/all",
                "search_stats": "/api/v2/stats",
                "disease_stats": "/api/v2/stats/{disease_id}",
                "all_organizations": "/api/v2/organizations/all",
                "disease_organizations": "/api/v2/organizations/collection/{disease_id}",
                "manual_entries": "/api/v2/manual",
                "website_status": "/api/v2/websites/status"
            }
        }
    }
