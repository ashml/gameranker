from pathlib import Path
from docx import Document
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rating import RatingEngine
from app.db.models import Game


class Exporter:
    def __init__(self, rating_engine: RatingEngine | None = None):
        self.rating_engine = rating_engine or RatingEngine()

    def export_txt(self, session: Session, file_path: Path, sort_by: str = "rating") -> None:
        games = self._get_games(session, sort_by)
        lines = []
        for game in games:
            score = self.rating_engine.to_display_score(self.rating_engine.env.Rating(game.rating, game.uncertainty))
            lines.append(f"{game.name} — {score:.0f}")
        file_path.write_text("\n".join(lines), encoding="utf-8")

    def export_docx(self, session: Session, file_path: Path, sort_by: str = "rating") -> None:
        games = self._get_games(session, sort_by)
        document = Document()
        for game in games:
            score = self.rating_engine.to_display_score(self.rating_engine.env.Rating(game.rating, game.uncertainty))
            document.add_paragraph(f"{game.name} — {score:.0f}")
        document.save(str(file_path))

    def _get_games(self, session: Session, sort_by: str):
        games = session.execute(select(Game)).scalars().all()
        if sort_by == "alpha":
            return sorted(games, key=lambda g: g.name.lower())
        return sorted(games, key=lambda g: g.rating, reverse=True)
