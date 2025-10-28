from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# --------- Quiz ----------
class QuizCreate(BaseModel):
    question: str
    answer: str

class QuizOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy -> Pydantic(v2) 変換

# --------- Image ----------
class ImageGenerateIn(BaseModel):
    quiz_id: int
    prompt: Optional[str] = None

class ImageOut(BaseModel):
    id: int
    quiz_id: int
    file_path: str
    prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
