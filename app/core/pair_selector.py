from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Comparison, Game


class PairSelector:
    def __init__(self, recent_limit: int = 50):
        self.recent_limit = recent_limit

    def _recent_pairs(self, session: Session) -> set[tuple[int, int]]:
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent = session.execute(
            select(Comparison).where(Comparison.timestamp >= cutoff).order_by(Comparison.timestamp.desc())
        ).scalars()
        pairs = set()
        for comp in recent:
            left, right = sorted([comp.game_left_id, comp.game_right_id])
            pairs.add((left, right))
        return pairs

    def select_pair(self, session: Session) -> tuple[Game, Game] | None:
        games = session.execute(select(Game)).scalars().all()
        if len(games) < 2:
            return None

        recent_pairs = self._recent_pairs(session)
        games_sorted = sorted(games, key=lambda g: (-g.uncertainty, g.created_at))
        anchor = games_sorted[0]

        candidates = [g for g in games if g.id != anchor.id]
        candidates.sort(key=lambda g: abs(g.rating - anchor.rating))

        for candidate in candidates:
            pair_key = tuple(sorted([anchor.id, candidate.id]))
            if pair_key not in recent_pairs:
                return anchor, candidate

        return anchor, candidates[0]
