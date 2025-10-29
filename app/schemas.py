from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# ==== Quiz ====
class QuizCreate(BaseModel):
    question: str
    answer: str

class QuizOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime
    class Config:
        from_attributes = True

class QuizWithStatusOut(QuizOut):
    attempts: int                 # 回答試行回数
    last_correct: Optional[bool]  # 直近の正誤（未回答なら None）

# ==== Image ====
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

# ==== Answer ====
class AnswerIn(BaseModel):
    answer: str
    image_shown: bool  # 送信時点で画像が表示されていたか

class AnswerResultOut(BaseModel):
    quiz_id: int
    correct: bool
    image_shown: bool

# ==== Stats ====
class StatsSummary(BaseModel):
    total_quizzes: int
    attempts: int
    correct_attempts: int
    accuracy: float  # 0.0 - 1.0
