from dataclasses import dataclass
from trueskill import Rating, rate_1vs1, TrueSkill


@dataclass
class RatingConfig:
    mu: float = 25.0
    sigma: float = 8.333
    beta: float = 4.167
    tau: float = 0.083
    draw_probability: float = 0.1


class RatingEngine:
    def __init__(self, config: RatingConfig | None = None):
        self.config = config or RatingConfig()
        self.env = TrueSkill(
            mu=self.config.mu,
            sigma=self.config.sigma,
            beta=self.config.beta,
            tau=self.config.tau,
            draw_probability=self.config.draw_probability,
        )

    def update(self, left_rating: Rating, right_rating: Rating, result: int) -> tuple[Rating, Rating]:
        if result == -1:
            return self.env.rate_1vs1(left_rating, right_rating)
        if result == 1:
            return self.env.rate_1vs1(right_rating, left_rating)[::-1]
        return self.env.rate_1vs1(left_rating, right_rating, drawn=True)

    def to_display_score(self, rating: Rating) -> float:
        score = (rating.mu - 3 * rating.sigma) * (100 / 50)
        return max(0.0, min(100.0, score))
