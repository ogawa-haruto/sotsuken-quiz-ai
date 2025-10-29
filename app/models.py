from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete")
    answer_logs = relationship("AnswerLog", back_populates="user", cascade="all, delete")

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer  = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="quizzes")
    images = relationship("GeneratedImage", back_populates="quiz", cascade="all, delete")
    answer_logs = relationship("AnswerLog", back_populates="quiz", cascade="all, delete")

class GeneratedImage(Base):
    __tablename__ = "generated_images"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    prompt = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="images")

class AnswerLog(Base):
    __tablename__ = "answer_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    user_answer = Column(String)
    image_shown = Column(Boolean, default=False)  # 画像が表示されていたか（介入有無）
    answered_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="answer_logs")
    quiz = relationship("Quiz", back_populates="answer_logs")
