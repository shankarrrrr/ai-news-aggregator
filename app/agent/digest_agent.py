"""
Digest Agent for compiling ranked articles into formatted output.

This module implements the DigestAgent that compiles top-ranked articles
into a formatted digest with AI-generated introduction and conclusion.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.agent.abstract_agent import AbstractAgent, AgentConfig, AgentException


class DigestArticle(BaseModel):
    """
    Article data for digest compilation.
    
    Attributes:
        title: Article title
        summary: Article summary text
        category: Primary category
        score: Relevance score
        url: Article URL
        published_at: Publication timestamp
        key_facts: Important facts from the article
    """
    title: str
    summary: str
    category: str
    score: float = Field(ge=0.0, le=10.0)
    url: str
    published_at: datetime
    key_facts: List[str] = Field(default_factory=list)


class DigestResult(BaseModel):
    """
    Result of digest compilation.
    
    Attributes:
        introduction: AI-generated introduction
        articles_by_category: Articles grouped by category
        conclusion: AI-generated conclusion
        total_articles: Total number of articles in digest
        categories_covered: List of categories represented
        generation_timestamp: When the digest was generated
    """
    introduction: str
    articles_by_category: Dict[str, List[DigestArticle]]
    conclusion: str
    total_articles: int = Field(ge=0)
    categories_covered: List[str]
    generation_timestamp: datetime = Field(default_factory=datetime.now)


class DigestAgent(AbstractAgent):
    """
    Agent for compiling ranked articles into formatted digests.
    
    Inherits from AbstractAgent and implements digest compilation logic
    using the Gemini API for introduction and conclusion generation.
    Follows the Single Responsibility Principle - this class is only
    responsible for digest compilation and formatting.
    
    The agent:
    1. Groups articles by category
    2. Generates an AI-powered introduction
    3. Organizes content by category
    4. Generates an AI-powered conclusion
    5. Formats output for display
    
    Attributes:
        _config (AgentConfig): Agent configuration (inherited, private)
        _client (genai.Client): Gemini API client (inherited, private)
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the digest agent.
        
        Args:
            config: Agent configuration including API key
            
        Raises:
            AgentException: If initialization fails
        """
        super().__init__(config)
        self._log_execution_start("initialization")
        self._log_execution_complete("initialization")
    
    def execute(self, input_data: dict) -> DigestResult:
        """
        Compile ranked articles into a formatted digest.
        
        Implements the abstract execute() method from AbstractAgent.
        This demonstrates polymorphism - the method can be called on any
        AbstractAgent instance.
        
        Args:
            input_data: Dictionary with keys:
                - articles (List[DigestArticle]): Articles to include
                - exam_type (str, optional): Target exam type for context
                - date_range (str, optional): Date range description
                
        Returns:
            DigestResult with formatted digest
            
        Raises:
            AgentException: If digest compilation fails
        """
        self._log_execution_start("digest compilation")
        
        # Validate input
        if not isinstance(input_data, dict):
            raise AgentException("Input must be a dictionary")
        
        articles = input_data.get('articles', [])
        exam_type = input_data.get('exam_type', 'Competitive Exams')
        date_range = input_data.get('date_range', 'recent period')
        
        if not articles:
            raise AgentException("At least one article is required")
        
        # Validate articles are DigestArticle instances
        for article in articles:
            if not isinstance(article, DigestArticle):
                raise AgentException(
                    "All articles must be DigestArticle instances"
                )
        
        # Group articles by category
        articles_by_category = self._group_by_category(articles)
        
        # Get summary statistics
        top_categories = self._get_top_categories(articles_by_category)
        
        # Generate introduction
        introduction = self._generate_introduction(
            len(articles), top_categories, exam_type, date_range
        )
        
        # Generate conclusion
        conclusion = self._generate_conclusion(
            len(articles), top_categories, exam_type
        )
        
        # Create result
        result = DigestResult(
            introduction=introduction,
            articles_by_category=articles_by_category,
            conclusion=conclusion,
            total_articles=len(articles),
            categories_covered=list(articles_by_category.keys())
        )
        
        self._log_execution_complete("digest compilation")
        return result
    
    def _group_by_category(
        self, 
        articles: List[DigestArticle]
    ) -> Dict[str, List[DigestArticle]]:
        """
        Group articles by their primary category.
        
        Articles within each category are kept in their original order
        (assumed to be sorted by relevance score).
        
        Args:
            articles: List of articles to group
            
        Returns:
            Dictionary mapping category names to article lists
        """
        grouped: Dict[str, List[DigestArticle]] = {}
        
        for article in articles:
            category = article.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(article)
        
        return grouped
    
    def _get_top_categories(
        self, 
        articles_by_category: Dict[str, List[DigestArticle]]
    ) -> List[tuple[str, int]]:
        """
        Get top categories by article count.
        
        Returns categories sorted by number of articles (descending).
        
        Args:
            articles_by_category: Articles grouped by category
            
        Returns:
            List of (category_name, article_count) tuples, sorted by count
        """
        category_counts = [
            (category, len(articles))
            for category, articles in articles_by_category.items()
        ]
        
        # Sort by count (descending), then by category name (ascending)
        category_counts.sort(key=lambda x: (-x[1], x[0]))
        
        return category_counts
    
    def _generate_introduction(
        self,
        total_articles: int,
        top_categories: List[tuple[str, int]],
        exam_type: str,
        date_range: str
    ) -> str:
        """
        Generate AI-powered introduction for the digest.
        
        Creates an engaging introduction that summarizes the digest
        content and highlights key themes.
        
        Args:
            total_articles: Total number of articles
            top_categories: Top categories with counts
            exam_type: Target exam type
            date_range: Date range description
            
        Returns:
            Introduction text
        """
        try:
            # Build category summary
            category_summary = ", ".join([
                f"{cat} ({count})" for cat, count in top_categories[:5]
            ])
            
            prompt = f"""You are an expert in Indian competitive exams.

Write a brief, engaging introduction (2-3 sentences) for a current affairs digest.

**Digest Details:**
- Total Articles: {total_articles}
- Target Exam: {exam_type}
- Time Period: {date_range}
- Top Categories: {category_summary}

**Task:**
Write an introduction that:
1. Welcomes the reader
2. Highlights the key themes/categories covered
3. Emphasizes the exam relevance
4. Sets an encouraging tone

**Output:**
Return ONLY the introduction text (2-3 sentences), no JSON, no formatting.
"""
            
            self._log_api_call(len(prompt))
            introduction = self._call_gemini_api(prompt)
            
            # Clean up any markdown or extra formatting
            introduction = introduction.strip().replace('**', '').replace('*', '')
            
            return introduction
            
        except Exception as e:
            # Fallback to template introduction
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate AI introduction: {str(e)}")
            
            return (
                f"Welcome to your {exam_type} Current Affairs Digest! "
                f"This compilation features {total_articles} carefully selected articles "
                f"from {date_range}, covering key topics including {category_summary}. "
                f"Each article has been analyzed for exam relevance to support your preparation."
            )
    
    def _generate_conclusion(
        self,
        total_articles: int,
        top_categories: List[tuple[str, int]],
        exam_type: str
    ) -> str:
        """
        Generate AI-powered conclusion for the digest.
        
        Creates a motivating conclusion that encourages continued
        preparation and highlights next steps.
        
        Args:
            total_articles: Total number of articles
            top_categories: Top categories with counts
            exam_type: Target exam type
            
        Returns:
            Conclusion text
        """
        try:
            prompt = f"""You are an expert in Indian competitive exams.

Write a brief, motivating conclusion (2-3 sentences) for a current affairs digest.

**Digest Details:**
- Total Articles: {total_articles}
- Target Exam: {exam_type}
- Categories Covered: {len(top_categories)}

**Task:**
Write a conclusion that:
1. Summarizes the value of the digest
2. Encourages continued preparation
3. Provides actionable next steps
4. Ends on a positive, motivating note

**Output:**
Return ONLY the conclusion text (2-3 sentences), no JSON, no formatting.
"""
            
            self._log_api_call(len(prompt))
            conclusion = self._call_gemini_api(prompt)
            
            # Clean up any markdown or extra formatting
            conclusion = conclusion.strip().replace('**', '').replace('*', '')
            
            return conclusion
            
        except Exception as e:
            # Fallback to template conclusion
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate AI conclusion: {str(e)}")
            
            return (
                f"This digest covered {total_articles} important topics across "
                f"{len(top_categories)} categories. Review the key facts, practice "
                f"the possible questions, and integrate these insights into your "
                f"preparation strategy. Stay consistent, stay focused, and success will follow!"
            )
    
    def format_as_text(self, result: DigestResult) -> str:
        """
        Format the digest result as readable text.
        
        Converts the structured DigestResult into a human-readable
        format suitable for display, email, or export.
        
        Args:
            result: DigestResult to format
            
        Returns:
            Formatted text digest
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("COMPETITIVE EXAM CURRENT AFFAIRS DIGEST")
        lines.append("=" * 80)
        lines.append(f"Generated: {result.generation_timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Total Articles: {result.total_articles}")
        lines.append(f"Categories: {', '.join(result.categories_covered)}")
        lines.append("=" * 80)
        lines.append("")
        
        # Introduction
        lines.append("INTRODUCTION")
        lines.append("-" * 80)
        lines.append(result.introduction)
        lines.append("")
        lines.append("")
        
        # Articles by category
        for category in sorted(result.articles_by_category.keys()):
            articles = result.articles_by_category[category]
            
            lines.append("=" * 80)
            lines.append(f"CATEGORY: {category.upper()} ({len(articles)} articles)")
            lines.append("=" * 80)
            lines.append("")
            
            for i, article in enumerate(articles, 1):
                lines.append(f"{i}. {article.title}")
                lines.append(f"   Score: {article.score:.1f}/10.0")
                lines.append(f"   Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}")
                lines.append(f"   URL: {article.url}")
                lines.append("")
                lines.append("   SUMMARY:")
                # Indent summary text
                summary_lines = article.summary.split('\n')
                for line in summary_lines:
                    lines.append(f"   {line}")
                lines.append("")
                
                if article.key_facts:
                    lines.append("   KEY FACTS:")
                    for fact in article.key_facts:
                        lines.append(f"   • {fact}")
                    lines.append("")
                
                lines.append("-" * 80)
                lines.append("")
        
        # Conclusion
        lines.append("=" * 80)
        lines.append("CONCLUSION")
        lines.append("=" * 80)
        lines.append(result.conclusion)
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def format_as_html(self, result: DigestResult) -> str:
        """
        Format the digest result as HTML.
        
        Converts the structured DigestResult into HTML format
        suitable for email or web display.
        
        Args:
            result: DigestResult to format
            
        Returns:
            HTML formatted digest
        """
        html_parts = []
        
        # Header
        html_parts.append("<html><body>")
        html_parts.append("<h1>Competitive Exam Current Affairs Digest</h1>")
        html_parts.append(f"<p><strong>Generated:</strong> {result.generation_timestamp.strftime('%Y-%m-%d %H:%M')}</p>")
        html_parts.append(f"<p><strong>Total Articles:</strong> {result.total_articles}</p>")
        html_parts.append(f"<p><strong>Categories:</strong> {', '.join(result.categories_covered)}</p>")
        html_parts.append("<hr>")
        
        # Introduction
        html_parts.append("<h2>Introduction</h2>")
        html_parts.append(f"<p>{result.introduction}</p>")
        
        # Articles by category
        for category in sorted(result.articles_by_category.keys()):
            articles = result.articles_by_category[category]
            
            html_parts.append(f"<h2>{category} ({len(articles)} articles)</h2>")
            
            for i, article in enumerate(articles, 1):
                html_parts.append(f"<h3>{i}. {article.title}</h3>")
                html_parts.append(f"<p><strong>Score:</strong> {article.score:.1f}/10.0</p>")
                html_parts.append(f"<p><strong>Published:</strong> {article.published_at.strftime('%Y-%m-%d %H:%M')}</p>")
                html_parts.append(f"<p><strong>URL:</strong> <a href='{article.url}'>{article.url}</a></p>")
                html_parts.append(f"<p>{article.summary}</p>")
                
                if article.key_facts:
                    html_parts.append("<p><strong>Key Facts:</strong></p>")
                    html_parts.append("<ul>")
                    for fact in article.key_facts:
                        html_parts.append(f"<li>{fact}</li>")
                    html_parts.append("</ul>")
                
                html_parts.append("<hr>")
        
        # Conclusion
        html_parts.append("<h2>Conclusion</h2>")
        html_parts.append(f"<p>{result.conclusion}</p>")
        
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)
    
    def get_summary_stats(self, result: DigestResult) -> dict:
        """
        Get summary statistics for the digest.
        
        Args:
            result: DigestResult to analyze
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_articles': result.total_articles,
            'total_categories': len(result.categories_covered),
            'categories': result.categories_covered,
            'articles_per_category': {
                category: len(articles)
                for category, articles in result.articles_by_category.items()
            },
            'generation_time': result.generation_timestamp.isoformat()
        }
        
        return stats
