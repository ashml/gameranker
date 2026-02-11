import re
from pathlib import Path

from docx import Document
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.rating import RatingEngine
from app.db.models import Game
from app.services.image_fetcher import ImageFetcher

RATING_PATTERN = re.compile(r"^(?P<name>.*?)\s*(?:\[(?P<score>\d{1,3}(?:\.\d+)?)\])?\s*$")


class DocxImporter:
    def __init__(self, image_fetcher: ImageFetcher | None = None, rating_engine: RatingEngine | None = None):
        self.image_fetcher = image_fetcher or ImageFetcher()
        self.rating_engine = rating_engine or RatingEngine()

    def import_file(self, session: Session, file_path: Path) -> int:
        parsed_rows = self._read_rows(file_path)
        if not parsed_rows:
            return 0

        existing = {name.casefold() for name in session.execute(select(Game.name)).scalars().all()}
        pending: list[Game] = []
        for name, score in parsed_rows:
            normalized = name.casefold()
            if not name or normalized in existing:
                continue
            image_path = self.image_fetcher.fetch_image(name)
            mu = self.rating_engine.mu_from_score(score if score is not None else 50.0)
            sigma = self.rating_engine.config.sigma
            pending.append(
                Game(
                    name=name,
                    rating=mu,
                    uncertainty=sigma,
                    image_path=str(image_path) if image_path else None,
                )
            )
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

    def _read_rows(self, file_path: Path) -> list[tuple[str, float | None]]:
        if file_path.suffix.lower() == ".txt":
            content = file_path.read_text(encoding="utf-8")
            lines = [line.strip() for line in content.splitlines() if line.strip()]
        else:
            document = Document(str(file_path))
            lines = [para.text.strip() for para in document.paragraphs if para.text.strip()]

        rows: list[tuple[str, float | None]] = []
        for line in lines:
            parsed = self._parse_line(line)
            if parsed[0]:
                rows.append(parsed)
        return rows

    def _parse_line(self, line: str) -> tuple[str, float | None]:
        match = RATING_PATTERN.match(line.strip())
        if not match:
            return line.strip(), None
        name = (match.group("name") or "").strip()
        raw_score = match.group("score")
        if raw_score is None:
            return name, None
        score = max(0.0, min(100.0, float(raw_score)))
        return name, score
