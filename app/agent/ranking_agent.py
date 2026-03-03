"""
Ranking Agent for scoring article relevance using strategy pattern.

This module implements the RankingAgent that scores articles based on
exam relevance using pluggable ranking strategies.
"""

from typing import Optional
from app.agent.abstract_agent import AbstractAgent, AgentConfig, AgentException
from app.services.ranking.abstract_ranking_strategy import (
    AbstractRankingStrategy,
    ArticleMetadata,
    RankingResult
)


class RankingAgent(AbstractAgent):
    """
    Agent for ranking articles by exam relevance.
    
    Inherits from AbstractAgent and implements the Strategy pattern by
    accepting an AbstractRankingStrategy instance. This demonstrates the
    Dependency Inversion Principle - the agent depends on the abstract
    strategy interface, not concrete implementations.
    
    The agent can use different ranking strategies for different exam types
    (UPSC, SSC, Banking) and can switch strategies at runtime. For borderline
    scores (4.0-6.0), the agent can optionally enhance the ranking with AI
    analysis for more nuanced scoring.
    
    Attributes:
        _config (AgentConfig): Agent configuration (inherited, private)
        _client (genai.Client): Gemini API client (inherited, private)
        _strategy (AbstractRankingStrategy): Current ranking strategy (private)
    """
    
    # Threshold for AI enhancement (borderline scores)
    AI_ENHANCEMENT_MIN_SCORE = 4.0
    AI_ENHANCEMENT_MAX_SCORE = 6.0
    
    def __init__(
        self, 
        config: AgentConfig, 
        strategy: AbstractRankingStrategy
    ):
        """
        Initialize the ranking agent with a strategy.
        
        Demonstrates dependency injection - the strategy is provided
        from outside rather than created internally.
        
        Args:
            config: Agent configuration including API key
            strategy: Ranking strategy to use
            
        Raises:
            AgentException: If initialization fails
        """
        super().__init__(config)
        
        if not isinstance(strategy, AbstractRankingStrategy):
            raise AgentException(
                "Strategy must be an instance of AbstractRankingStrategy"
            )
        
        self._strategy = strategy
        self._log_execution_start(f"initialization with {strategy.exam_type} strategy")
        self._log_execution_complete("initialization")
    
    @property
    def current_strategy(self) -> str:
        """
        Get the current strategy's exam type.
        
        Returns:
            Exam type of current strategy
        """
        return self._strategy.exam_type
    
    def execute(self, input_data: dict) -> RankingResult:
        """
        Rank an article using the current strategy.
        
        Implements the abstract execute() method from AbstractAgent.
        This demonstrates polymorphism - the method can be called on any
        AbstractAgent instance.
        
        The method delegates scoring to the strategy (Strategy pattern)
        and optionally enhances borderline scores with AI analysis.
        
        Args:
            input_data: Dictionary with keys:
                - content (str): Article content
                - metadata (ArticleMetadata): Article metadata
                - use_ai_enhancement (bool, optional): Enable AI enhancement
                
        Returns:
            RankingResult with score and reasoning
            
        Raises:
            AgentException: If ranking fails
        """
        self._log_execution_start("ranking")
        
        # Validate input
        if not isinstance(input_data, dict):
            raise AgentException("Input must be a dictionary")
        
        content = input_data.get('content', '')
        metadata = input_data.get('metadata')
        use_ai_enhancement = input_data.get('use_ai_enhancement', False)
        
        if not content:
            raise AgentException("Content is required")
        
        if not isinstance(metadata, ArticleMetadata):
            raise AgentException("Metadata must be an ArticleMetadata instance")
        
        # Delegate to strategy for initial scoring
        result = self._strategy.calculate_score(content, metadata)
        
        # Optionally enhance with AI for borderline scores
        if use_ai_enhancement and self._should_use_ai_enhancement(result.score):
            result = self._enhance_with_ai(content, metadata, result)
        
        self._log_execution_complete("ranking")
        return result
    
    def set_strategy(self, strategy: AbstractRankingStrategy) -> None:
        """
        Change the ranking strategy at runtime.
        
        Demonstrates the Strategy pattern's flexibility - strategies
        can be swapped without changing the agent's code.
        
        Args:
            strategy: New ranking strategy to use
            
        Raises:
            AgentException: If strategy is invalid
        """
        if not isinstance(strategy, AbstractRankingStrategy):
            raise AgentException(
                "Strategy must be an instance of AbstractRankingStrategy"
            )
        
        old_strategy = self._strategy.exam_type
        self._strategy = strategy
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"RankingAgent strategy changed: {old_strategy} -> {strategy.exam_type}"
        )
    
    def _should_use_ai_enhancement(self, score: float) -> bool:
        """
        Determine if AI enhancement should be used for this score.
        
        AI enhancement is used for borderline scores (4.0-6.0) where
        additional nuanced analysis could improve accuracy.
        
        Args:
            score: Initial score from strategy
            
        Returns:
            True if AI enhancement should be used
        """
        return (
            self.AI_ENHANCEMENT_MIN_SCORE <= score <= self.AI_ENHANCEMENT_MAX_SCORE
        )
    
    def _enhance_with_ai(
        self,
        content: str,
        metadata: ArticleMetadata,
        initial_result: RankingResult
    ) -> RankingResult:
        """
        Enhance ranking with AI analysis for borderline cases.
        
        Uses Gemini API to perform deeper analysis of content relevance
        when the rule-based strategy produces a borderline score.
        This hybrid approach combines algorithmic and AI-based ranking.
        
        Args:
            content: Article content
            metadata: Article metadata
            initial_result: Initial ranking from strategy
            
        Returns:
            Enhanced RankingResult
        """
        try:
            prompt = self._build_enhancement_prompt(
                content, metadata, initial_result
            )
            self._log_api_call(len(prompt))
            
            response = self._call_gemini_api(prompt)
            enhancement_dict = self._parse_json_response(response)
            
            # Extract AI-suggested adjustments
            ai_score_adjustment = enhancement_dict.get('score_adjustment', 0.0)
            ai_reasoning = enhancement_dict.get('reasoning', '')
            
            # Apply adjustment (limit to ±2.0 points)
            adjusted_score = initial_result.score + max(-2.0, min(2.0, ai_score_adjustment))
            adjusted_score = max(0.0, min(10.0, adjusted_score))
            
            # Combine reasoning
            combined_reasoning = (
                f"{initial_result.reasoning}\n\n"
                f"AI Enhancement: {ai_reasoning}\n"
                f"Adjusted score: {initial_result.score:.1f} -> {adjusted_score:.1f}"
            )
            
            # Create enhanced result
            enhanced_factors = initial_result.factors.copy()
            enhanced_factors['ai_adjustment'] = ai_score_adjustment
            
            return RankingResult(
                score=adjusted_score,
                reasoning=combined_reasoning,
                factors=enhanced_factors
            )
            
        except Exception as e:
            # If AI enhancement fails, return original result
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"AI enhancement failed, using original score: {str(e)}")
            return initial_result
    
    def _build_enhancement_prompt(
        self,
        content: str,
        metadata: ArticleMetadata,
        initial_result: RankingResult
    ) -> str:
        """
        Build prompt for AI-based ranking enhancement.
        
        Args:
            content: Article content
            metadata: Article metadata
            initial_result: Initial ranking result
            
        Returns:
            Formatted prompt string
        """
        # Truncate content if too long
        truncated_content = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""You are an expert in Indian competitive exams ({self._strategy.exam_type}).

An article has been scored by an algorithmic ranking system, but the score is borderline.
Provide a nuanced analysis to refine the ranking.

**Article Content:**
{truncated_content}

**Metadata:**
- Category: {metadata.category}
- Source: {metadata.source_type}
- Published: {metadata.published_at.strftime('%Y-%m-%d %H:%M')}
- Length: {metadata.content_length} characters

**Initial Algorithmic Score:** {initial_result.score:.1f} / 10.0

**Initial Reasoning:**
{initial_result.reasoning}

**Task:**
Analyze the article's exam relevance more deeply and suggest a score adjustment.

Consider:
1. Depth of analysis and insights
2. Relevance to current exam patterns
3. Quality of information (facts, data, examples)
4. Potential for exam questions
5. Connection to syllabus topics

**Output Format (JSON only, no markdown):**
{{
    "score_adjustment": 0.5,
    "reasoning": "Brief explanation of why the score should be adjusted up or down"
}}

**Important:**
- score_adjustment should be between -2.0 and +2.0
- Positive adjustment means more relevant than initial score suggests
- Negative adjustment means less relevant than initial score suggests
- Return ONLY valid JSON
"""
        return prompt
    
    def get_strategy_info(self) -> dict:
        """
        Get information about the current strategy.
        
        Returns:
            Dictionary with strategy details
        """
        return {
            'exam_type': self._strategy.exam_type,
            'weights': self._strategy.weights,
            'strategy_class': self._strategy.__class__.__name__
        }
    
    def rank_batch(
        self,
        articles: list[dict],
        use_ai_enhancement: bool = False
    ) -> list[RankingResult]:
        """
        Rank multiple articles in batch.
        
        Convenience method for ranking multiple articles with the
        same strategy.
        
        Args:
            articles: List of article dictionaries (content + metadata)
            use_ai_enhancement: Enable AI enhancement for all articles
            
        Returns:
            List of RankingResults in same order as input
        """
        results = []
        
        for article in articles:
            try:
                article['use_ai_enhancement'] = use_ai_enhancement
                result = self.execute(article)
                results.append(result)
            except Exception as e:
                # Log error and append a default low score
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to rank article: {str(e)}")
                
                results.append(RankingResult(
                    score=0.0,
                    reasoning=f"Ranking failed: {str(e)}",
                    factors={}
                ))
        
        return results
