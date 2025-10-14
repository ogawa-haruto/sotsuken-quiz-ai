from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# ---- Quizzes ----
class QuizCreate(BaseModel):
    question: str
    answer: str

class QuizOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    class Config: from_attributes = True

# listクエリ用（検索/並び順/ページング）
class QuizListParams(BaseModel):
    q: Optional[str] = Field(default=None, description="部分一致検索（question/answer）")
    order: Literal["created_desc", "created_asc"] = "created_desc"
    offset: int = 0
    limit: int = 100

# ---- Images ----
class ImageCreate(BaseModel):
    quiz_id: int
    prompt: Optional[str] = None
    force: bool = False  # ← 追加：再生成を強制する

class ImageOut(BaseModel):
    id: int
    quiz_id: int
    file_path: str
    prompt: str
    created_at: datetime
    class Config: from_attributes = True
