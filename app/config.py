from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "database.sqlite"
IMAGES_DIR = DATA_DIR / "images"
PLACEHOLDER_IMAGE = BASE_DIR / "app" / "gui" / "assets" / "placeholder.jpg"

RAWG_API_URL = "https://api.rawg.io/api/games"
RAWG_API_KEY_ENV = "RAWG_API_KEY"
