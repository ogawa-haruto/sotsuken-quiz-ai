from __future__ import annotations
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc, delete, func
from . import models

# ---- User ----
def get_user_by_token(db: Session, token: str) -> Optional[models.User]:
    return db.execute(select(models.User).where(models.User.token == token)).scalar_one_or_none()

def get_or_create_user(db: Session, token: str) -> models.User:
    u = get_user_by_token(db, token)
    if u: return u
    u = models.User(token=token)
    db.add(u); db.commit(); db.refresh(u)
    return u

# ---- Quiz ----
def create_quiz(db: Session, user: models.User, question: str, answer: str) -> models.Quiz:
    qz = models.Quiz(question=question, answer=answer, user_id=user.id)
    db.add(qz); db.commit(); db.refresh(qz)
    return qz

def list_quizzes(db: Session, user: models.User, q: Optional[str], order: str, offset: int, limit: int) -> List[models.Quiz]:
    stmt = select(models.Quiz).where(models.Quiz.user_id == user.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((models.Quiz.question.ilike(like)) | (models.Quiz.answer.ilike(like)))
    stmt = stmt.order_by(desc(models.Quiz.created_at) if order == "created_desc" else asc(models.Quiz.created_at))
    stmt = stmt.offset(offset).limit(limit)
    return list(db.execute(stmt).scalars())

def get_quiz_owned(db: Session, quiz_id: int, user: models.User) -> Optional[models.Quiz]:
    return db.execute(
        select(models.Quiz).where(models.Quiz.id == quiz_id, models.Quiz.user_id == user.id)
    ).scalar_one_or_none()

def delete_quiz_owned(db: Session, quiz_id: int, user: models.User) -> bool:
    qz = get_quiz_owned(db, quiz_id, user)
    if not qz: return False
    db.delete(qz); db.commit()
    return True

# ---- Image ----
def list_images_by_quiz(db: Session, quiz: models.Quiz):
    return list(db.execute(
        select(models.GeneratedImage).where(models.GeneratedImage.quiz_id == quiz.id).order_by(desc(models.GeneratedImage.created_at))
    ).scalars())

def delete_images_by_quiz(db: Session, quiz: models.Quiz) -> int:
    res = db.execute(delete(models.GeneratedImage).where(models.GeneratedImage.quiz_id == quiz.id))
    db.commit()
    return res.rowcount or 0

def add_image(db: Session, quiz: models.Quiz, file_path: str, prompt: Optional[str]) -> models.GeneratedImage:
    im = models.GeneratedImage(quiz_id=quiz.id, file_path=file_path, prompt=prompt)
    db.add(im); db.commit(); db.refresh(im)
    return im

def get_latest_image_by_quiz(db: Session, quiz: models.Quiz) -> Optional[models.GeneratedImage]:
    return db.execute(
        select(models.GeneratedImage)
        .where(models.GeneratedImage.quiz_id == quiz.id)
        .order_by(desc(models.GeneratedImage.created_at))
        .limit(1)
    ).scalar_one_or_none()

# ---- Answer / Stats ----
def _norm(s: str) -> str:
    try:
        return s.strip().lower()
    except Exception:
        return s

def log_answer(db: Session, user: models.User, quiz: models.Quiz, user_answer: str, image_shown: bool) -> Tuple[bool, models.AnswerLog]:
    correct = _norm(user_answer) == _norm(quiz.answer)
    rec = models.AnswerLog(
        user_id=user.id,
        quiz_id=quiz.id,
        is_correct=correct,
        user_answer=user_answer,
        image_shown=image_shown,
    )
    db.add(rec); db.commit(); db.refresh(rec)
    return correct, rec

def get_quiz_attempts(db: Session, user: models.User, quiz: models.Quiz) -> int:
    return db.execute(
        select(func.count(models.AnswerLog.id)).where(
            models.AnswerLog.user_id == user.id,
            models.AnswerLog.quiz_id == quiz.id
        )
    ).scalar_one()

def get_quiz_last_correct(db: Session, user: models.User, quiz: models.Quiz) -> Optional[bool]:
    row = db.execute(
        select(models.AnswerLog.is_correct)
        .where(models.AnswerLog.user_id == user.id, models.AnswerLog.quiz_id == quiz.id)
        .order_by(desc(models.AnswerLog.answered_at))
        .limit(1)
    ).first()
    return None if not row else bool(row[0])

def list_quizzes_with_status(
    db: Session,
    user: models.User,
    q: Optional[str],
    order: str,
    offset: int,
    limit: int,
    status_filter: str,   # "all" | "incorrect_only" | "unanswered_only"
):
    quizzes = list_quizzes(db, user, q, order, offset, limit)
    out = []
    for quiz in quizzes:
        attempts = get_quiz_attempts(db, user, quiz)
        last_correct = get_quiz_last_correct(db, user, quiz)
        if status_filter == "incorrect_only" and not (attempts > 0 and last_correct is False):
            continue
        if status_filter == "unanswered_only" and not (attempts == 0):
            continue
        out.append({
            "id": quiz.id,
            "question": quiz.question,
            "answer": quiz.answer,
            "created_at": quiz.created_at,
            "attempts": attempts,
            "last_correct": last_correct
        })
    return out

def get_stats_summary(db: Session, user: models.User):
    total_quizzes = db.execute(
        select(func.count(models.Quiz.id)).where(models.Quiz.user_id == user.id)
    ).scalar_one()

    attempts = db.execute(
        select(func.count(models.AnswerLog.id)).where(models.AnswerLog.user_id == user.id)
    ).scalar_one()

    correct_attempts = db.execute(
        select(func.count(models.AnswerLog.id)).where(
            models.AnswerLog.user_id == user.id,
            models.AnswerLog.is_correct == True
        )
    ).scalar_one()

    accuracy = float(correct_attempts) / attempts if attempts else 0.0
    return {
        "total_quizzes": int(total_quizzes),
        "attempts": int(attempts),
        "correct_attempts": int(correct_attempts),
        "accuracy": accuracy
    }
