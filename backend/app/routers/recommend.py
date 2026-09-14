from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.agent.loop import run_agent
from app.auth import get_current_user_optional
from app.db import get_db
from app.models.conversation import ConversationTurn
from app.models.user import User
from app.rate_limit import limiter
from app.schemas import RecommendationOut, RecommendRequest, RecommendResponse

router = APIRouter()


# Main app entry point: runs the full agent tool-use loop for a user query and shapes the
# result into the response schema. The only route that spends real Anthropic money, hence
# the rate limit. Works fully logged-out (no auth required); when a valid token is present,
# the turn is also persisted so it's restorable via GET /conversations.
@router.post("/recommend", response_model=RecommendResponse)
@limiter.limit("10/minute")
def recommend(
    request: Request,
    body: RecommendRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> RecommendResponse:
    history = [turn.model_dump() for turn in body.history]
    result = run_agent(db, body.query, history=history, spoiler_free=body.spoiler_free)
    recommendations_out = [
        RecommendationOut(
            anime_id=rec.anime_id,
            title=rec.title,
            rationale=rec.rationale,
            caveat=rec.caveat,
            score=rec.score,
            community_flag=rec.community_flag,
            image_url=rec.image_url,
        )
        for rec in result.recommendations
    ]

    if current_user is not None:
        db.add(
            ConversationTurn(
                user_id=current_user.id,
                query=body.query,
                message=result.message,
                recommendations=[r.model_dump() for r in recommendations_out],
            )
        )
        db.commit()

    return RecommendResponse(message=result.message, recommendations=recommendations_out)
