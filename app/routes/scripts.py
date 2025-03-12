from fastapi import APIRouter, HTTPException, Body
from app.models.api_models import ApiConfig, VideoScript, ApiRequest, ApiResponse
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/generate-script", response_model=VideoScript)
async def generate_video_script(request: ApiRequest = Body(...)):
    """Generate a video script from a content idea"""
    try:
        if not request.idea:
            raise HTTPException(status_code=400, detail="Content idea is required")
        
        if not request.transcript or request.transcript.strip() == "":
            raise HTTPException(status_code=400, detail="Transcript is required")
        
        config = ApiConfig(
            anthropicApiKey=request.anthropicApiKey,
            openaiApiKey=request.openaiApiKey,
            preferredProvider=request.preferredProvider
        )
        
        ai_service = AIService(config)
        script = await ai_service.generate_video_script(
            request.idea,
            request.transcript,
            request.instructions or ""
        )
        
        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine-script", response_model=VideoScript)
async def refine_video_script(request: ApiRequest = Body(...)):
    """Refine an existing video script"""
    try:
        if not request.script:
            raise HTTPException(status_code=400, detail="Video script is required")
        
        if not request.instructions or request.instructions.strip() == "":
            raise HTTPException(status_code=400, detail="Instructions are required for refinement")
        
        config = ApiConfig(
            anthropicApiKey=request.anthropicApiKey,
            openaiApiKey=request.openaiApiKey,
            preferredProvider=request.preferredProvider
        )
        
        ai_service = AIService(config)
        refined_script = await ai_service.refine_video_script(
            request.script,
            request.instructions
        )
        
        return refined_script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-script", response_model=VideoScript)
async def regenerate_video_script(request: ApiRequest = Body(...)):
    """Regenerate a video script completely"""
    try:
        if not request.idea:
            raise HTTPException(status_code=400, detail="Content idea is required")
        
        if not request.transcript or request.transcript.strip() == "":
            raise HTTPException(status_code=400, detail="Transcript is required")
        
        if not request.instructions or request.instructions.strip() == "":
            raise HTTPException(status_code=400, detail="Instructions are required for regeneration")
        
        config = ApiConfig(
            anthropicApiKey=request.anthropicApiKey,
            openaiApiKey=request.openaiApiKey,
            preferredProvider=request.preferredProvider
        )
        
        ai_service = AIService(config)
        new_script = await ai_service.regenerate_video_script(
            request.idea,
            request.transcript,
            request.instructions
        )
        
        return new_script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))