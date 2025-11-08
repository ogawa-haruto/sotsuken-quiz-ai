from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, crud, schemas
from app.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/create", response_model=schemas.QuizRead)
def create_quiz(payload: schemas.QuizCreate,
                db: Session = Depends(get_db),
                me: CurrentUser = Depends(get_current_user)):
    q = models.Quiz(
        question=payload.question,
        answer=payload.answer,
        prompt=payload.prompt,
        user_id=me.id,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@router.get("/list", response_model=list[schemas.QuizRead])
def list_my_quizzes(limit: int = 200, offset: int = 0,
                    db: Session = Depends(get_db),
                    me: CurrentUser = Depends(get_current_user)):
    return crud.list_quizzes_for_user(db, user_id=me.id, limit=limit, offset=offset)

@router.delete("/{quiz_id}", status_code=204)
def delete_my_quiz(quiz_id: int,
                   db: Session = Depends(get_db),
                   me: CurrentUser = Depends(get_current_user)):
    q = crud.get_quiz_for_user(db, quiz_id=quiz_id, user_id=me.id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    db.delete(q)
    db.commit()
    return None

# 画像生成/再生成も所有者チェック
@router.post("/image/generate")
def generate_image_for_my_quiz(quiz_id: int, force: bool = False,
                               db: Session = Depends(get_db),
                               me: CurrentUser = Depends(get_current_user)):
    q = crud.get_quiz_for_user(db, quiz_id=quiz_id, user_id=me.id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    # --- ここに既存の画像生成ロジックを呼び出す ---
    # file_path = image_service.generate(..., prompt=q.prompt, force=force)
    # q.image_path = file_path
    db.commit()
    # return {"id": q.id, "file_path": q.image_path}
    return {"ok": True}
