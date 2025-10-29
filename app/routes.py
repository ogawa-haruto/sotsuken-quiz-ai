from typing import Optional, List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Header, Response, Query
from sqlalchemy.orm import Session

from .database import get_db
from . import crud, schemas, models
from .services.image_service import ImageService

router = APIRouter()

def get_current_user(
    response: Response,
    db: Session = Depends(get_db),
    x_token: Optional[str] = Header(default=None, alias="X-Token"),
) -> models.User:
    token = x_token or str(uuid4())
    user = crud.get_or_create_user(db, token)
    if x_token is None:
        response.headers["X-Token-Issued"] = token
    return user

# ----- Quiz CRUD -----
@router.post("/quiz/create", response_model=schemas.QuizOut)
def create_quiz(payload: schemas.QuizCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.create_quiz(db, user=user, question=payload.question, answer=payload.answer)

@router.get("/quiz/list", response_model=List[schemas.QuizWithStatusOut])
def list_quizzes(
    q: Optional[str] = Query(default=None, description="部分一致検索"),
    order: str = Query(default="created_desc", pattern="^(created_desc|created_asc)$"),
    status: str = Query(default="all", pattern="^(all|incorrect_only|unanswered_only)$"),
    offset: int = 0, limit: int = 200,
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user),
):
    return crud.list_quizzes_with_status(db, user, q, order, offset, limit, status)

@router.delete("/quiz/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ok = crud.delete_quiz_owned(db, quiz_id=quiz_id, user=user)
    if not ok:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return Response(status_code=204)

# ----- Image -----
@router.get("/quiz/{quiz_id}/images/latest", response_model=Optional[schemas.ImageOut])
def latest_image(quiz_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    quiz = crud.get_quiz_owned(db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return crud.get_latest_image_by_quiz(db, quiz=quiz)

@router.post("/quiz/image/generate", response_model=schemas.ImageOut)
def generate_image(
    body: schemas.ImageGenerateIn,
    force: bool = Query(default=False, description="旧画像を全削除してから生成"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    quiz = crud.get_quiz_owned(db, quiz_id=body.quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    service = ImageService()

    if force:
        imgs = crud.list_images_by_quiz(db, quiz=quiz)
        # 旧画像ファイル削除
        service.delete_files([im.file_path for im in imgs])
        # DBレコード削除
        crud.delete_images_by_quiz(db, quiz=quiz)

    rel_path = service.generate_image_for_quiz(quiz_id=quiz.id, prompt=body.prompt, force_delete_before=False)
    return crud.add_image(db, quiz=quiz, file_path=rel_path, prompt=body.prompt)

# ----- Answer & Stats -----
@router.post("/quiz/{quiz_id}/answer", response_model=schemas.AnswerResultOut)
def answer_quiz(
    quiz_id: int,
    body: schemas.AnswerIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    quiz = crud.get_quiz_owned(db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    ok, _ = crud.log_answer(db, user=user, quiz=quiz, user_answer=body.answer, image_shown=body.image_shown)
    return {"quiz_id": quiz.id, "correct": ok, "image_shown": body.image_shown}

@router.get("/stats/summary", response_model=schemas.StatsSummary)
def stats_summary(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.get_stats_summary(db, user=user)
