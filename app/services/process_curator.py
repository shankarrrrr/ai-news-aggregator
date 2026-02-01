import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.curator_agent import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.database.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def curate_digests(hours: int = 24) -> dict:
    curator = CuratorAgent(USER_PROFILE)
    repo = Repository()
    
    digests = repo.get_recent_digests(hours=hours)
    total = len(digests)
    
    if total == 0:
        logger.warning(f"No digests found from the last {hours} hours")
        return {"total": 0, "ranked": 0}
    
    logger.info(f"Curating {total} digests from the last {hours} hours")
    logger.info(f"User profile: {USER_PROFILE['name']} - {USER_PROFILE['background']}")
    
    ranked_articles = curator.rank_digests(digests)
    
    if not ranked_articles:
        logger.error("Failed to rank digests")
        return {"total": total, "ranked": 0}
    
    logger.info(f"Successfully ranked {len(ranked_articles)} articles")
    logger.info("\n=== Top 10 Ranked Articles ===")
    
    for article in ranked_articles[:10]:
        digest = next((d for d in digests if d["id"] == article.digest_id), None)
        if digest:
            logger.info(f"\nRank {article.rank} | Score: {article.relevance_score:.1f}/10.0")
            logger.info(f"Title: {digest['title']}")
            logger.info(f"Type: {digest['article_type']}")
            logger.info(f"Reasoning: {article.reasoning}")
    
    return {
        "total": total,
        "ranked": len(ranked_articles),
        "articles": [
            {
                "digest_id": a.digest_id,
                "rank": a.rank,
                "relevance_score": a.relevance_score,
                "reasoning": a.reasoning
            }
            for a in ranked_articles
        ]
    }


if __name__ == "__main__":
    result = curate_digests(hours=24)
    print(f"\n=== Curation Results ===")
    print(f"Total digests: {result['total']}")
    print(f"Ranked: {result['ranked']}")

