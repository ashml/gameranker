from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    rating = Column(Float, nullable=False, default=25.0)
    uncertainty = Column(Float, nullable=False, default=8.333)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    comparisons_left = relationship(
        "Comparison",
        foreign_keys="Comparison.game_left_id",
        back_populates="left_game",
    )
    comparisons_right = relationship(
        "Comparison",
        foreign_keys="Comparison.game_right_id",
        back_populates="right_game",
    )


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True)
    game_left_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    game_right_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    result = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    left_game = relationship("Game", foreign_keys=[game_left_id], back_populates="comparisons_left")
    right_game = relationship("Game", foreign_keys=[game_right_id], back_populates="comparisons_right")
