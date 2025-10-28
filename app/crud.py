from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from . import models

# ---- User ----
def get_user_by_token(db: Session, token: str) -> models.User | None:
    return db.scalars(select(models.User).where(models.User.token == token)).first()

def create_user(db: Session, token: str) -> models.User:
    u = models.User(token=token)
    db.add(u); db.commit(); db.refresh(u)
    return u

def get_or_create_user(db: Session, token: str) -> models.User:
    return get_user_by_token(db, token) or create_user(db, token)

# ---- Quiz ----
def create_quiz(db: Session, *, user: models.User, question: str, answer: str) -> models.Quiz:
    q = models.Quiz(question=question, answer=answer, user_id=user.id)
    db.add(q); db.commit(); db.refresh(q)
    return q

def list_quizzes(db: Session, *, user: models.User, q: str | None, order: str, offset: int, limit: int):
    stmt = select(models.Quiz).where(models.Quiz.user_id == user.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((models.Quiz.question.ilike(like)) | (models.Quiz.answer.ilike(like)))
    stmt = stmt.order_by(models.Quiz.created_at.asc() if order == "created_asc" else models.Quiz.created_at.desc())
    stmt = stmt.offset(offset).limit(limit)
    return list(db.scalars(stmt).all())

def get_quiz_owned(db: Session, *, quiz_id: int, user: models.User) -> models.Quiz | None:
    return db.scalars(select(models.Quiz).where(models.Quiz.id == quiz_id, models.Quiz.user_id == user.id)).first()

def delete_quiz_owned(db: Session, *, quiz_id: int, user: models.User) -> bool:
    q = get_quiz_owned(db, quiz_id=quiz_id, user=user)
    if not q:
        return False
    db.delete(q)  # images はモデルの cascade 設定で行ごと削除される
    db.commit()
    return True

# ---- Images ----
def add_image(db: Session, *, quiz: models.Quiz, file_path: str, prompt: str | None):
    img = models.GeneratedImage(quiz_id=quiz.id, file_path=file_path, prompt=prompt)
    db.add(img); db.commit(); db.refresh(img)
    return img

def list_images_by_quiz(db: Session, *, quiz: models.Quiz) -> list[models.GeneratedImage]:
    return list(db.scalars(select(models.GeneratedImage).where(models.GeneratedImage.quiz_id == quiz.id)).all())

def delete_images_by_quiz(db: Session, *, quiz: models.Quiz) -> int:
    # DB上の画像レコードを削除（ファイル削除はサービス層で実施）
    result = db.execute(delete(models.GeneratedImage).where(models.GeneratedImage.quiz_id == quiz.id))
    db.commit()
    return result.rowcount

def get_latest_image_by_quiz(db: Session, *, quiz: models.Quiz) -> models.GeneratedImage | None:
    stmt = select(models.GeneratedImage).where(models.GeneratedImage.quiz_id == quiz.id).order_by(models.GeneratedImage.created_at.desc())
    return db.scalars(stmt).first()
