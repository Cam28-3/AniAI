from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)  # 72 bytes is bcrypt's hard limit


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class UserOut(BaseModel):
    id: int
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class HistoryRecommendationIn(BaseModel):
    anime_id: int
    title: str


class HistoryTurnIn(BaseModel):
    query: str
    message: str
    recommendations: list[HistoryRecommendationIn] = []


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    history: list[HistoryTurnIn] = Field(default_factory=list, max_length=20)
    spoiler_free: bool = True


class RecommendationOut(BaseModel):
    anime_id: int
    title: str
    rationale: str
    caveat: str | None
    score: float | None
    community_flag: str | None
    image_url: str | None


class ConversationTurnOut(BaseModel):
    query: str
    message: str
    recommendations: list[RecommendationOut]


class RecommendResponse(BaseModel):
    message: str
    recommendations: list[RecommendationOut]


class DiscoverItemOut(BaseModel):
    anime_id: int
    title: str
    score: float | None
    image_url: str | None
    genres: list[str]


class StreamingPlatformOut(BaseModel):
    name: str
    url: str


class AnimeDetailOut(BaseModel):
    id: int
    title: str
    synopsis: str | None
    genres: list[str]
    tags: list[str]
    episodes: int | None
    status: str | None
    score: float | None
    popularity_rank: int | None
    reception_summary: str | None
    review_sentiment_ratio: float | None
    community_flag: str | None
    image_url: str | None
    streaming: list[StreamingPlatformOut]
    streaming_unavailable: bool = False
    anilist_url: str
