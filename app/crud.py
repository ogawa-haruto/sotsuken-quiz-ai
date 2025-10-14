from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from . import models, schemas

# ---- Quiz ----
def create_quiz(db: Session, quiz_in: schemas.QuizCreate) -> models.Quiz:
    quiz = models.Quiz(question=quiz_in.question, answer=quiz_in.answer)
    db.add(quiz); db.commit(); db.refresh(quiz)
    return quiz

def list_quizzes(
    db: Session,
    params: schemas.QuizListParams
) -> List[models.Quiz]:
    q = db.query(models.Quiz)
    if params.q:
        like = f"%{params.q}%"
        q = q.filter(or_(models.Quiz.question.like(like), models.Quiz.answer.like(like)))
    if params.order == "created_desc":
        q = q.order_by(desc(models.Quiz.created_at))
    else:
        q = q.order_by(asc(models.Quiz.created_at))
    return q.offset(params.offset).limit(params.limit).all()

def get_quiz(db: Session, quiz_id: int) -> Optional[models.Quiz]:
    return db.query(models.Quiz).get(quiz_id)

def delete_quiz(db: Session, quiz_id: int) -> bool:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return False
    db.delete(quiz)
    db.commit()
    return True

# ---- Images ----
def get_images_by_quiz(db: Session, quiz_id: int) -> List[models.Image]:
    return db.query(models.Image).filter(models.Image.quiz_id == quiz_id).all()

def create_image(db: Session, quiz_id: int, file_path: str, prompt: str) -> models.Image:
    img = models.Image(quiz_id=quiz_id, file_path=file_path, prompt=prompt)
    db.add(img); db.commit(); db.refresh(img)
    return img

def delete_images_of_quiz(db: Session, quiz_id: int) -> List[str]:
    imgs = get_images_by_quiz(db, quiz_id)
    paths = [i.file_path for i in imgs]
    for i in imgs:
        db.delete(i)
    db.commit()
    return paths

