from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .database import get_db
from . import crud, schemas
from .services.image_service import ImageService

router = APIRouter(prefix="/quiz", tags=["quiz"])

# ---- Quiz ----
@router.post("/create", response_model=schemas.QuizOut)
def create_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db)):
    return crud.create_quiz(db, quiz)

@router.get("/list", response_model=List[schemas.QuizOut])
def list_quizzes(
    q: Optional[str] = Query(default=None, description="部分一致検索"),
    order: str = Query(default="created_desc", pattern="^(created_desc|created_asc)$"),
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    params = schemas.QuizListParams(q=q, order=order, offset=offset, limit=limit)
    return crud.list_quizzes(db, params)

@router.delete("/{quiz_id}")
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    # 画像レコード→ファイル削除→クイズ削除
    paths = crud.delete_images_of_quiz(db, quiz_id)
    ImageService.remove_files(paths)
    ok = crud.delete_quiz(db, quiz_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"deleted": True, "quiz_id": quiz_id, "removed_files": paths}

# ---- Images ----
@router.post("/image/generate", response_model=schemas.ImageOut, tags=["image"])
def generate_image(payload: schemas.ImageCreate, db: Session = Depends(get_db)):
    svc = ImageService(db)
    try:
        img = svc.generate_for_quiz(quiz_id=payload.quiz_id, user_prompt=payload.prompt, force=payload.force)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return img

@router.get("/{quiz_id}/images", response_model=List[schemas.ImageOut], tags=["image"])
def list_images(quiz_id: int, db: Session = Depends(get_db)):
    return crud.get_images_by_quiz(db, quiz_id)
