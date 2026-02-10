from pathlib import Path
from docx import Document
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Game
from app.services.image_fetcher import ImageFetcher


class DocxImporter:
    def __init__(self, image_fetcher: ImageFetcher | None = None):
        self.image_fetcher = image_fetcher or ImageFetcher()

    def import_file(self, session: Session, file_path: Path) -> int:
        names = self._read_names(file_path)
        if not names:
            return 0
        existing = {
            name.casefold()
            for name in session.execute(select(Game.name)).scalars().all()
        }
        added = 0
        pending: list[Game] = []
        for name in names:
            normalized = name.casefold()
            if normalized in existing:
                continue
            image_path = self.image_fetcher.fetch_image(name)
            game = Game(name=name, image_path=str(image_path) if image_path else None)
            pending.append(game)
            existing.add(normalized)
        session.add_all(pending)
        try:
            session.commit()
            return len(pending)
        except IntegrityError:
            session.rollback()
            added = 0
            for game in pending:
                try:
                    session.add(game)
                    session.commit()
                    added += 1
                except IntegrityError:
                    session.rollback()
            return added

    def _read_names(self, file_path: Path) -> list[str]:
        if file_path.suffix.lower() == ".txt":
            content = file_path.read_text(encoding="utf-8")
            return [line.strip() for line in content.splitlines() if line.strip()]
        document = Document(str(file_path))
        return [para.text.strip() for para in document.paragraphs if para.text.strip()]
