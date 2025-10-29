import os, requests, base64, datetime
from ..config import settings

class ImageService:
    def __init__(self):
        self.base_url = settings.A1111_BASE_URL
        self.output_dir = settings.IMAGE_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def _request(self, payload: dict):
        url = f"{self.base_url}/sdapi/v1/txt2img"
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()

    def generate_image_for_quiz(self, quiz_id: int, prompt: str | None, force_delete_before=False) -> str:
        prompt = prompt or f"Educational illustration of the quiz concept, clear and simple, no humans"
        payload = {"prompt": prompt, "steps": 20, "width": 512, "height": 512}
        data = self._request(payload)
        img_b64 = data["images"][0]
        img_bytes = base64.b64decode(img_b64)

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"quiz_{quiz_id}_{ts}.png"
        rel_path = os.path.join(self.output_dir, file_name)
        abs_path = os.path.abspath(rel_path)
        with open(abs_path, "wb") as f:
            f.write(img_bytes)
        return rel_path.replace("\\", "/")

    def delete_files(self, file_paths: list[str]):
        for p in file_paths:
            try:
                os.remove(p)
            except Exception:
                pass
