"""
Summarization Agent for exam-focused content summaries.

This module implements the SummarizationAgent that generates exam-focused
summaries with prelims/mains relevance using the Google Gemini API.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.agent.abstract_agent import AbstractAgent, AgentConfig, AgentException


class SummaryResult(BaseModel):
    """
    Result of summarization operation.
    
    Attributes:
        main_summary: Core content summary (150-250 words)
        why_important: Why this matters for exam preparation
        prelims_relevance: Relevance for preliminary exam (objective)
        mains_relevance: Relevance for mains exam (descriptive)
        possible_questions: List of potential exam questions (minimum 3)
        key_facts: Important facts and figures to remember
        word_count: Total word count of main summary
    """
    main_summary: str = Field(..., min_length=100)
    why_important: str = Field(..., min_length=20)
    prelims_relevance: str = Field(..., min_length=20)
    mains_relevance: str = Field(..., min_length=20)
    possible_questions: list[str] = Field(..., min_length=3)
    key_facts: list[str] = Field(default_factory=list)
    word_count: int = Field(default=0, ge=0)
    
    @field_validator('main_summary')
    @classmethod
    def validate_word_count(cls, v: str) -> str:
        """Validate summary is within 200-300 word range."""
        words = len(v.split())
        if words < 150 or words > 350:
            raise ValueError(
                f"Summary must be 150-350 words, got {words} words"
            )
        return v
    
    @field_validator('possible_questions')
    @classmethod
    def validate_questions_count(cls, v: list[str]) -> list[str]:
        """Ensure at least 3 questions are provided."""
        if len(v) < 3:
            raise ValueError(
                f"Must provide at least 3 possible questions, got {len(v)}"
            )
        return v


class SummarizationAgent(AbstractAgent):
    """
    Agent for generating exam-focused summaries of articles.
    
    Inherits from AbstractAgent and implements exam-specific summarization
    logic using the Gemini API. Follows the Single Responsibility Principle -
    this class is only responsible for summarization.
    
    The agent generates comprehensive summaries that include:
    - Main content summary (200-300 words)
    - Exam importance explanation
    - Prelims and Mains relevance
    - Possible exam questions
    - Key facts to remember
    
    Attributes:
        _config (AgentConfig): Agent configuration (inherited, private)
        _client (genai.Client): Gemini API client (inherited, private)
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the summarization agent.
        
        Args:
            config: Agent configuration including API key
            
        Raises:
            AgentException: If initialization fails
        """
        super().__init__(config)
        self._log_execution_start("initialization")
        self._log_execution_complete("initialization")
    
    def execute(self, input_data: dict) -> SummaryResult:
        """
        Generate an exam-focused summary for an article.
        
        Implements the abstract execute() method from AbstractAgent.
        This demonstrates polymorphism - the method can be called on any
        AbstractAgent instance.
        
        Args:
            input_data: Dictionary with keys:
                - title (str): Article title
                - content (str): Article content
                - category (str): Primary category
                - source_type (str, optional): Source type for context
                
        Returns:
            SummaryResult with all required sections
            
        Raises:
            AgentException: If summarization fails
        """
        self._log_execution_start("summarization")
        
        # Validate input
        if not isinstance(input_data, dict):
            raise AgentException("Input must be a dictionary")
        
        title = input_data.get('title', '')
        content = input_data.get('content', '')
        category = input_data.get('category', 'General')
        source_type = input_data.get('source_type', 'unknown')
        
        if not title or not content:
            raise AgentException("Title and content are required")
        
        # Build prompt and call API
        prompt = self._build_summarization_prompt(
            title, content, category, source_type
        )
        self._log_api_call(len(prompt))
        
        response = self._call_gemini_api(prompt)
        result_dict = self._parse_json_response(response)
        
        # Validate and create result
        result = self._validate_and_create_result(result_dict)
        
        self._log_execution_complete("summarization")
        return result
    
    def _build_summarization_prompt(
        self,
        title: str,
        content: str,
        category: str,
        source_type: str
    ) -> str:
        """
        Build the summarization prompt for Gemini API.
        
        Creates a category-aware prompt that guides the model to produce
        exam-focused summaries with all required sections.
        
        Args:
            title: Article title
            content: Article content
            category: Primary category
            source_type: Source type (youtube, pib, government_schemes)
            
        Returns:
            Formatted prompt string
        """
        # Truncate content if too long (keep first 4000 chars)
        truncated_content = content[:4000] if len(content) > 4000 else content
        
        prompt = f"""You are an expert in Indian competitive exams (UPSC, SSC, Banking, etc.).

Analyze the following article and create an exam-focused summary.

**Article Title:** {title}

**Category:** {category}

**Source Type:** {source_type}

**Article Content:**
{truncated_content}

**Task:**
Create a comprehensive exam-focused summary with the following sections:

1. **Main Summary** (200-300 words):
   - Summarize the key points and developments
   - Focus on facts, figures, and concrete information
   - Include specific examples from the source content
   - Write in clear, concise language suitable for exam preparation

2. **Why Important for Exams**:
   - Explain why this topic matters for competitive exam preparation
   - Connect to exam syllabus topics
   - Highlight current affairs relevance

3. **Prelims Relevance**:
   - How this could appear in objective-type questions
   - Key facts that could be tested
   - Potential MCQ angles

4. **Mains Relevance**:
   - How this could appear in descriptive questions
   - Essay/answer writing angles
   - Analytical perspectives needed

5. **Possible Questions** (minimum 3):
   - List at least 3 potential exam questions
   - Mix of prelims and mains style questions
   - Cover different difficulty levels

6. **Key Facts**:
   - Important dates, numbers, names, schemes
   - Facts to memorize for quick recall
   - At least 3-5 key facts

**Output Format (JSON only, no markdown):**
{{
    "main_summary": "200-300 word summary with specific facts from the article...",
    "why_important": "Explanation of exam relevance...",
    "prelims_relevance": "How this appears in objective questions...",
    "mains_relevance": "How this appears in descriptive questions...",
    "possible_questions": [
        "Question 1 (Prelims style)",
        "Question 2 (Mains style)",
        "Question 3 (Mixed)",
        "Question 4 (Optional)"
    ],
    "key_facts": [
        "Fact 1 with specific detail",
        "Fact 2 with specific detail",
        "Fact 3 with specific detail"
    ]
}}

**Important:**
- Return ONLY valid JSON
- Main summary must be 200-300 words
- Include at least 3 possible questions
- Include specific facts and examples from the source content
- Focus on exam preparation utility
"""
        return prompt
    
    def _validate_and_create_result(self, result_dict: dict) -> SummaryResult:
        """
        Validate API response and create SummaryResult.
        
        Ensures that the summary meets all requirements including
        word count, question count, and content quality.
        
        Args:
            result_dict: Parsed JSON response from API
            
        Returns:
            Validated SummaryResult
            
        Raises:
            AgentException: If validation fails
        """
        try:
            # Extract fields
            main_summary = result_dict.get('main_summary', '')
            why_important = result_dict.get('why_important', '')
            prelims_relevance = result_dict.get('prelims_relevance', '')
            mains_relevance = result_dict.get('mains_relevance', '')
            possible_questions = result_dict.get('possible_questions', [])
            key_facts = result_dict.get('key_facts', [])
            
            # Calculate word count
            word_count = len(main_summary.split())
            
            # Create and return result (Pydantic will validate)
            return SummaryResult(
                main_summary=main_summary,
                why_important=why_important,
                prelims_relevance=prelims_relevance,
                mains_relevance=mains_relevance,
                possible_questions=possible_questions,
                key_facts=key_facts,
                word_count=word_count
            )
            
        except Exception as e:
            raise AgentException(f"Failed to validate summary result: {str(e)}")
    
    def get_formatted_summary(self, result: SummaryResult) -> str:
        """
        Format the summary result as readable text.
        
        Converts the structured SummaryResult into a human-readable
        format suitable for display or export.
        
        Args:
            result: SummaryResult to format
            
        Returns:
            Formatted text summary
        """
        lines = []
        
        lines.append("=" * 80)
        lines.append("EXAM-FOCUSED SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("MAIN SUMMARY:")
        lines.append("-" * 80)
        lines.append(result.main_summary)
        lines.append(f"(Word count: {result.word_count})")
        lines.append("")
        
        lines.append("WHY IMPORTANT FOR EXAMS:")
        lines.append("-" * 80)
        lines.append(result.why_important)
        lines.append("")
        
        lines.append("PRELIMS RELEVANCE:")
        lines.append("-" * 80)
        lines.append(result.prelims_relevance)
        lines.append("")
        
        lines.append("MAINS RELEVANCE:")
        lines.append("-" * 80)
        lines.append(result.mains_relevance)
        lines.append("")
        
        lines.append("POSSIBLE EXAM QUESTIONS:")
        lines.append("-" * 80)
        for i, question in enumerate(result.possible_questions, 1):
            lines.append(f"{i}. {question}")
        lines.append("")
        
        if result.key_facts:
            lines.append("KEY FACTS TO REMEMBER:")
            lines.append("-" * 80)
            for i, fact in enumerate(result.key_facts, 1):
                lines.append(f"• {fact}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_compact_summary(self, result: SummaryResult) -> str:
        """
        Get a compact version of the summary for quick reference.
        
        Args:
            result: SummaryResult to format
            
        Returns:
            Compact summary text
        """
        lines = []
        
        lines.append(f"Summary ({result.word_count} words):")
        lines.append(result.main_summary[:200] + "...")
        lines.append("")
        lines.append(f"Questions: {len(result.possible_questions)}")
        lines.append(f"Key Facts: {len(result.key_facts)}")
        
        return "\n".join(lines)
