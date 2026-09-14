from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models.conversation import ConversationTurn
from app.models.user import User
from app.schemas import ConversationTurnOut

router = APIRouter()


# Returns the logged-in user's persisted conversation turns, oldest first, so the frontend can
# seed its `turns` state on page load / after login. Capped at the most recent 200 turns.
@router.get("/conversations", response_model=list[ConversationTurnOut])
def list_conversations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ConversationTurnOut]:
    stmt = (
        select(ConversationTurn)
        .where(ConversationTurn.user_id == current_user.id)
        .order_by(ConversationTurn.created_at.desc(), ConversationTurn.id.desc())
        .limit(200)
    )
    rows = list(db.scalars(stmt).all())
    rows.reverse()  # chronological order for the frontend
    return [
        ConversationTurnOut(query=t.query, message=t.message, recommendations=t.recommendations)
        for t in rows
    ]
