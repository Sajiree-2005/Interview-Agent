"""FastAPI router for the interview endpoint."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.schemas import InterviewRequest, InterviewResponse
from app.agents.interview_agent import interview_agent
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["interview"])


@router.options("/interview")
async def options_interview(request: Request):
    """Handle CORS preflight explicitly."""
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        content={"ok": True},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        },
    )


@router.post("/interview", response_model=InterviewResponse)
async def interview(request: InterviewRequest, raw_request: Request):
    """Main interview endpoint with full request logging."""
    try:
        body = await raw_request.body()
        logger.info(
            "interview_request_received",
            session_id=request.sessionId,
            has_candidate=request.candidate is not None,
            has_message=request.message is not None,
            body_preview=body[:200].decode("utf-8", errors="replace") if body else "",
            origin=raw_request.headers.get("origin"),
        )
        response = await interview_agent.handle(request)
        logger.info(
            "interview_response_sent",
            session_id=request.sessionId,
            done=response.done,
            reply_preview=response.reply[:100] if response.reply else "",
        )
        return response
    except Exception as e:
        logger.error(
            "interview_error",
            session_id=request.sessionId,
            error_type=type(e).__name__,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Interview processing failed: {type(e).__name__}: {str(e)}")