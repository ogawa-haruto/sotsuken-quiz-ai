import base64, os, datetime, requests
from typing import Optional
from sqlalchemy.orm import Session
from ..config import settings
from .. import models, crud

class ImageService:
    def __init__(self, db: Session):
        self.db = db
        os.makedirs(settings.IMAGE_DIR, exist_ok=True)

    def ensure_reuse(self, quiz_id: int) -> Optional[models.Image]:
        images = crud.get_images_by_quiz(self.db, quiz_id)
        return images[0] if images else None

    def build_prompt(self, quiz: models.Quiz, user_prompt: Optional[str]) -> str:
        if user_prompt:
            return user_prompt
        return (
            f"Create a clear, mnemonic illustration for vocabulary learning. "
            f"Keyword: '{quiz.question}'. Simple background, high contrast, "
            f"descriptive details, educational style."
        )

    def txt2img_a1111(self, prompt: str, seed: int = -1) -> bytes:
        """A1111で画像生成（seed=-1はランダム生成）"""
        url = f"{settings.A1111_BASE_URL}/sdapi/v1/txt2img"
        payload = {
            "prompt": prompt,
            "steps": 20,
            "width": 768,
            "height": 512,
            "sampler_name": "Euler a",
            "seed": seed
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        b64 = resp.json()["images"][0]
        return base64.b64decode(b64)

    def save_image(self, quiz_id: int, png_bytes: bytes, prompt: str) -> models.Image:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"quiz_{quiz_id}_{ts}.png"
        fpath = os.path.join(settings.IMAGE_DIR, fname)
        with open(fpath, "wb") as f:
            f.write(png_bytes)
        return crud.create_image(self.db, quiz_id=quiz_id, file_path=fpath.replace("\\","/"), prompt=prompt)

    @staticmethod
    def remove_files(paths: list[str]):
        for p in paths:
            try:
                if p and os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    def generate_for_quiz(self, quiz_id: int, user_prompt: Optional[str] = None, force: bool = False) -> models.Image:
        """画像生成。force=Trueなら旧画像を削除してから新規生成"""
        quiz = self.db.query(models.Quiz).get(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        if not force:
            reuse = self.ensure_reuse(quiz_id)
            if reuse:
                return reuse
        else:
            # --- 🔹ここで旧画像を削除 ---
            old_imgs = crud.get_images_by_quiz(self.db, quiz_id)
            if old_imgs:
                paths = [img.file_path for img in old_imgs]
                for img in old_imgs:
                    self.db.delete(img)
                self.db.commit()
                self.remove_files(paths)

        prompt = self.build_prompt(quiz, user_prompt)
        png = self.txt2img_a1111(prompt, seed=-1)
        return self.save_image(quiz_id, png, prompt)
