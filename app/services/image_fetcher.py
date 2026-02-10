import os
from pathlib import Path
import requests

from app.config import IMAGES_DIR, PLACEHOLDER_IMAGE, RAWG_API_KEY_ENV, RAWG_API_URL


class ImageFetcher:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv(RAWG_API_KEY_ENV)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    def fetch_image(self, game_name: str) -> Path:
        if not self.api_key:
            return PLACEHOLDER_IMAGE
        try:
            response = requests.get(
                RAWG_API_URL,
                params={"search": game_name, "key": self.api_key, "page_size": 1},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results") or []
            if not results:
                return PLACEHOLDER_IMAGE
            image_url = results[0].get("background_image")
            if not image_url:
                return PLACEHOLDER_IMAGE
            image_response = requests.get(image_url, timeout=10)
            image_response.raise_for_status()
            file_name = f"{game_name[:80].replace(' ', '_')}.jpg"
            image_path = IMAGES_DIR / file_name
            image_path.write_bytes(image_response.content)
            return image_path
        except requests.RequestException:
            return PLACEHOLDER_IMAGE
