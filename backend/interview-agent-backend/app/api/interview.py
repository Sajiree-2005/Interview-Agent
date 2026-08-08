"""FastAPI router for the interview endpoint."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import InterviewRequest, InterviewResponse
from app.agents.interview_agent import interview_agent
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["interview"])


@router.post("/interview", response_model=InterviewResponse)
async def interview(request: InterviewRequest):
    """Main interview endpoint."""
    try:
        logger.info("interview_request", session_id=request.sessionId, has_candidate=request.candidate is not None)
        response = await interview_agent.handle(request)
        return response
    except Exception as e:
        logger.error("interview_error", session_id=request.sessionId, error=str(e))
        raise HTTPException(status_code=500, detail="Interview processing failed")
