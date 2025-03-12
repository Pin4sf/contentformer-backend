from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Contentformer API",
    description="Backend API for the Contentformer application",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.routes.content_ideas import router as content_ideas_router
from app.routes.scripts import router as scripts_router
from app.routes.linkedin_posts import router as linkedin_posts_router

# Include routers
app.include_router(content_ideas_router, prefix="/api", tags=["content ideas"])
app.include_router(scripts_router, prefix="/api", tags=["scripts"])
app.include_router(linkedin_posts_router, prefix="/api", tags=["linkedin posts"])

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "Contentformer API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)