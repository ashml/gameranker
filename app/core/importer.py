from pathlib import Path
from docx import Document
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Game
from app.services.image_fetcher import ImageFetcher


class DocxImporter:
    def __init__(self, image_fetcher: ImageFetcher | None = None):
        self.image_fetcher = image_fetcher or ImageFetcher()

    def import_file(self, session: Session, file_path: Path) -> int:
        document = Document(str(file_path))
        names = [para.text.strip() for para in document.paragraphs if para.text.strip()]
        existing = set(session.execute(select(Game.name)).scalars().all())
        added = 0
        for name in names:
            if name in existing:
                continue
            image_path = self.image_fetcher.fetch_image(name)
            game = Game(name=name, image_path=str(image_path) if image_path else None)
            session.add(game)
            added += 1
        session.commit()
        return added
