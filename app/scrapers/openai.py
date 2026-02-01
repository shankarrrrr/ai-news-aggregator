from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from docling.document_converter import DocumentConverter
from pydantic import BaseModel


class OpenAIArticle(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None
    

class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"
        self.converter = DocumentConverter()

    def get_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        feed = feedparser.parse(self.rss_url)
        if not feed.entries:
            return []
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []
        
        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue
            
            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= cutoff_time:
                articles.append(OpenAIArticle(
                    title=entry.get("title", ""),
                    description=entry.get("description", ""),
                    url=entry.get("link", ""),
                    guid=entry.get("id", entry.get("link", "")),
                    published_at=published_time,
                    category=entry.get("tags", [{}])[0].get("term") if entry.get("tags") else None
                ))
        
        return articles

  
if __name__ == "__main__":
    scraper = OpenAIScraper()
    articles: List[OpenAIArticle] = scraper.get_articles(hours=50)