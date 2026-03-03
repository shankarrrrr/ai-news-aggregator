"""
Ranking services package.

Contains ranking strategies and related components for scoring articles
by exam relevance.
"""

from app.services.ranking.abstract_ranking_strategy import (
    AbstractRankingStrategy,
    ArticleMetadata,
    RankingResult
)
from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
from app.services.ranking.ssc_ranking_strategy import SSCRankingStrategy
from app.services.ranking.banking_ranking_strategy import BankingRankingStrategy

__all__ = [
    "AbstractRankingStrategy",
    "ArticleMetadata",
    "RankingResult",
    "UPSCRankingStrategy",
    "SSCRankingStrategy",
    "BankingRankingStrategy",
]
