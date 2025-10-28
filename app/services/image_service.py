import os, base64, datetime, requests
from typing import Optional, Iterable
from ..config import settings

class ImageService:
    def __init__(self):
        self.base_url = settings.A1111_BASE_URL.rstrip("/")
        self.image_dir = settings.IMAGE_DIR
        os.makedirs(self.image_dir, exist_ok=True)

    def _a1111_txt2img(self, prompt: str) -> bytes:
        # AUTOMATIC1111 /sdapi/v1/txt2img
        url = f"{self.base_url}/sdapi/v1/txt2img"
        payload = {
            "prompt": prompt,
            "width": 768,
            "height": 512,
            "steps": 20,
            "sampler_index": "Euler a",
            "cfg_scale": 7.0,
            "seed": -1,
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        # images[0] は base64 PNG
        return base64.b64decode(data["images"][0])

    def _save_png(self, png_bytes: bytes, *, quiz_id: int) -> str:
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"quiz_{quiz_id}_{ts}.png"
        abspath = os.path.join(self.image_dir, fname)
        with open(abspath, "wb") as f:
            f.write(png_bytes)
        # API では /static から配信する前提
        return f"static/images/{fname}"

    def _safe_unlink(self, path: str):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            # ログは省略（不要なら pass）
            pass

    def delete_files(self, file_paths: Iterable[str]):
        # file_paths は "static/images/..." 形式 → 実ファイルに変換
        for rel in file_paths:
            # "static/images/xxx.png" → settings.IMAGE_DIR/xxx.png
            name = os.path.basename(rel)
            abs_path = os.path.join(self.image_dir, name)
            self._safe_unlink(abs_path)

    def generate_image_for_quiz(self, *, quiz_id: int, prompt: Optional[str], force_delete_before: bool = False) -> str:
        # プロンプトのデフォルト：クイズIDだけでも一旦生成
        effective_prompt = prompt or f"simple, clear, single object icon, minimal, no people, topic id {quiz_id}"
        img_bytes = self._a1111_txt2img(effective_prompt)
        rel_path = self._save_png(img_bytes, quiz_id=quiz_id)
        return rel_path
