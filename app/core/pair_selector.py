import random
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Comparison, Game


class PairSelector:
    def __init__(self, recent_limit: int = 100, recent_days: int = 7):
        self.recent_limit = recent_limit
        self.recent_days = recent_days

    def _recent_pairs(self, session: Session) -> set[tuple[int, int]]:
        cutoff = datetime.utcnow() - timedelta(days=self.recent_days)
        recent = (
            session.execute(
                select(Comparison)
                .where(Comparison.timestamp >= cutoff)
                .order_by(Comparison.timestamp.desc())
                .limit(self.recent_limit)
            )
            .scalars()
            .all()
        )
        pairs = set()
        for comp in recent:
            left, right = sorted([comp.game_left_id, comp.game_right_id])
            pairs.add((left, right))
        return pairs

    def _comparison_counts(self, session: Session, games: list[Game]) -> dict[int, int]:
        counts = defaultdict(int)
        comps = session.execute(select(Comparison.game_left_id, Comparison.game_right_id)).all()
        for left_id, right_id in comps:
            counts[left_id] += 1
            counts[right_id] += 1
        for game in games:
            counts[game.id] += 0
        return counts

    def select_pair(self, session: Session) -> tuple[Game, Game] | None:
        games = session.execute(select(Game)).scalars().all()
        if len(games) < 2:
            return None

        counts = self._comparison_counts(session, games)
        recent_pairs = self._recent_pairs(session)

        min_compared = min(counts[g.id] for g in games)
        new_games = [g for g in games if counts[g.id] == min_compared]

        anchor_pool = sorted(new_games, key=lambda g: g.uncertainty, reverse=True)[: min(5, len(new_games))]
        anchor = random.choice(anchor_pool)

        candidates = [g for g in games if g.id != anchor.id]
        random.shuffle(candidates)
        candidates.sort(key=lambda g: (abs(g.rating - anchor.rating), counts[g.id], -g.uncertainty))

        for candidate in candidates:
            pair_key = tuple(sorted([anchor.id, candidate.id]))
            if pair_key not in recent_pairs:
                return anchor, candidate

        return anchor, candidates[0]
