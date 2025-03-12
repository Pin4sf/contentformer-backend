from fastapi import APIRouter, HTTPException, Body
from app.models.api_models import ApiConfig, ContentIdea, ApiRequest, ApiResponse, TestConnectionResponse
from app.services.ai_service import AIService
from typing import List

router = APIRouter()

@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_api_connection(config: ApiConfig = Body(...)):
    """Test connection to the AI service provider"""
    try:
        ai_service = AIService(config)
        result = await ai_service.test_connection()
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"API connection test failed: {str(e)}",
            "error": str(e)
        }

@router.post("/generate-ideas", response_model=List[ContentIdea])
async def generate_content_ideas(request: ApiRequest = Body(...)):
    """Generate content ideas from transcript"""
    try:
        if not request.transcript or request.transcript.strip() == "":
            raise HTTPException(status_code=400, detail="Transcript is required")
        
        config = ApiConfig(
            anthropicApiKey=request.anthropicApiKey,
            openaiApiKey=request.openaiApiKey,
            preferredProvider=request.preferredProvider
        )
        
        ai_service = AIService(config)
        ideas = await ai_service.generate_content_ideas(
            request.transcript,
            request.instructions or ""
        )
        
        return ideas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))