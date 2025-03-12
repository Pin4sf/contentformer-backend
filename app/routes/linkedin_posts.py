from fastapi import APIRouter, HTTPException, Body
from app.models.api_models import ApiConfig, LinkedInPost, ApiRequest, ApiResponse
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/generate-linkedin-post", response_model=LinkedInPost)
async def generate_linkedin_post(request: ApiRequest = Body(...)):
    """Generate a LinkedIn post from a video script"""
    try:
        if not request.script:
            raise HTTPException(status_code=400, detail="Video script is required")
        
        config = ApiConfig(
            anthropicApiKey=request.anthropicApiKey,
            openaiApiKey=request.openaiApiKey,
            preferredProvider=request.preferredProvider
        )
        
        ai_service = AIService(config)
        post = await ai_service.generate_linkedin_post(request.script)
        
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))