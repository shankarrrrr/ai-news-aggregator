"""
Categorization Agent for exam-relevant content classification.

This module implements the CategorizationAgent that classifies articles
into exam-relevant categories using the Google Gemini API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.agent.abstract_agent import AbstractAgent, AgentConfig, AgentException


class CategoryResult(BaseModel):
    """
    Result of categorization operation.
    
    Attributes:
        primary_category: Main category for the article
        secondary_categories: Up to 2 additional relevant categories
        confidence: Confidence score (0.0-1.0)
        reasoning: Explanation for category assignment
    """
    primary_category: str = Field(..., min_length=1)
    secondary_categories: List[str] = Field(default_factory=list, max_length=2)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=1)
    
    @field_validator('secondary_categories')
    @classmethod
    def validate_secondary_distinct(cls, v: List[str], info) -> List[str]:
        """Ensure secondary categories are distinct."""
        if len(v) != len(set(v)):
            raise ValueError("Secondary categories must be distinct")
        return v


class CategorizationAgent(AbstractAgent):
    """
    Agent for categorizing articles into exam-relevant categories.
    
    Inherits from AbstractAgent and implements exam-specific categorization
    logic using the Gemini API. Follows the Single Responsibility Principle -
    this class is only responsible for categorization.
    
    The agent assigns one primary category and up to two secondary categories
    to each article based on its content and relevance to competitive exams.
    
    Attributes:
        _config (AgentConfig): Agent configuration (inherited, private)
        _client (genai.Client): Gemini API client (inherited, private)
    """
    
    # Class constant: Exam-relevant categories
    EXAM_CATEGORIES = [
        "Polity",
        "Economy",
        "International Relations",
        "Science & Tech",
        "Environment & Ecology",
        "Defence & Security",
        "Government Schemes",
        "Social Issues"
    ]
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the categorization agent.
        
        Args:
            config: Agent configuration including API key
            
        Raises:
            AgentException: If initialization fails
        """
        super().__init__(config)
        self._log_execution_start("initialization")
        self._log_execution_complete("initialization")
    
    def execute(self, input_data: dict) -> CategoryResult:
        """
        Categorize an article into exam-relevant categories.
        
        Implements the abstract execute() method from AbstractAgent.
        This demonstrates polymorphism - the method can be called on any
        AbstractAgent instance.
        
        Args:
            input_data: Dictionary with keys:
                - title (str): Article title
                - content (str): Article content
                - source_type (str, optional): Source type for context
                
        Returns:
            CategoryResult with primary and secondary categories
            
        Raises:
            AgentException: If categorization fails
        """
        self._log_execution_start("categorization")
        
        # Validate input
        if not isinstance(input_data, dict):
            raise AgentException("Input must be a dictionary")
        
        title = input_data.get('title', '')
        content = input_data.get('content', '')
        source_type = input_data.get('source_type', 'unknown')
        
        if not title or not content:
            raise AgentException("Title and content are required")
        
        # Build prompt and call API
        prompt = self._build_categorization_prompt(title, content, source_type)
        self._log_api_call(len(prompt))
        
        response = self._call_gemini_api(prompt)
        result_dict = self._parse_json_response(response)
        
        # Validate and create result
        result = self._validate_and_create_result(result_dict)
        
        self._log_execution_complete("categorization")
        return result
    
    def _build_categorization_prompt(
        self, 
        title: str, 
        content: str,
        source_type: str
    ) -> str:
        """
        Build the categorization prompt for Gemini API.
        
        Creates a structured prompt that guides the model to produce
        JSON output with the required categorization format.
        
        Args:
            title: Article title
            content: Article content
            source_type: Source type (youtube, pib, government_schemes)
            
        Returns:
            Formatted prompt string
        """
        # Truncate content if too long (keep first 3000 chars)
        truncated_content = content[:3000] if len(content) > 3000 else content
        
        categories_list = "\n".join([f"- {cat}" for cat in self.EXAM_CATEGORIES])
        
        prompt = f"""You are an expert in Indian competitive exams (UPSC, SSC, Banking, etc.).

Analyze the following article and categorize it for exam preparation purposes.

**Article Title:** {title}

**Source Type:** {source_type}

**Article Content:**
{truncated_content}

**Available Categories:**
{categories_list}

**Task:**
1. Assign ONE primary category that best fits the article
2. Assign UP TO TWO secondary categories (can be 0, 1, or 2)
3. Ensure all categories are from the available list above
4. Ensure primary and secondary categories are distinct (no duplicates)
5. Provide a confidence score (0.0 to 1.0) for your categorization
6. Explain your reasoning briefly

**Output Format (JSON only, no markdown):**
{{
    "primary_category": "Category Name",
    "secondary_categories": ["Category Name 1", "Category Name 2"],
    "confidence": 0.85,
    "reasoning": "Brief explanation of why these categories were chosen"
}}

**Important:**
- Return ONLY valid JSON
- Use exact category names from the list
- Secondary categories array can be empty or have 1-2 items
- All categories must be distinct
"""
        return prompt
    
    def _validate_and_create_result(self, result_dict: dict) -> CategoryResult:
        """
        Validate API response and create CategoryResult.
        
        Ensures that the categories returned by the API are valid
        and meet all requirements.
        
        Args:
            result_dict: Parsed JSON response from API
            
        Returns:
            Validated CategoryResult
            
        Raises:
            AgentException: If validation fails
        """
        try:
            # Extract fields
            primary = result_dict.get('primary_category', '')
            secondary = result_dict.get('secondary_categories', [])
            confidence = result_dict.get('confidence', 0.0)
            reasoning = result_dict.get('reasoning', '')
            
            # Validate categories
            self._validate_categories(primary, secondary)
            
            # Create and return result
            return CategoryResult(
                primary_category=primary,
                secondary_categories=secondary,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            raise AgentException(f"Failed to validate categorization result: {str(e)}")
    
    def _validate_categories(
        self, 
        primary: str, 
        secondary: List[str]
    ) -> None:
        """
        Validate that assigned categories are valid and distinct.
        
        Ensures compliance with requirements:
        - Primary category must be from predefined list
        - Secondary categories must be from predefined list
        - All categories must be distinct
        - Maximum 2 secondary categories
        
        Args:
            primary: Primary category
            secondary: List of secondary categories
            
        Raises:
            AgentException: If validation fails
        """
        # Validate primary category
        if primary not in self.EXAM_CATEGORIES:
            raise AgentException(
                f"Invalid primary category '{primary}'. "
                f"Must be one of: {', '.join(self.EXAM_CATEGORIES)}"
            )
        
        # Validate secondary categories count
        if len(secondary) > 2:
            raise AgentException(
                f"Too many secondary categories ({len(secondary)}). Maximum is 2."
            )
        
        # Validate each secondary category
        for cat in secondary:
            if cat not in self.EXAM_CATEGORIES:
                raise AgentException(
                    f"Invalid secondary category '{cat}'. "
                    f"Must be one of: {', '.join(self.EXAM_CATEGORIES)}"
                )
        
        # Validate distinctness
        all_categories = [primary] + secondary
        if len(all_categories) != len(set(all_categories)):
            raise AgentException(
                "Categories must be distinct. "
                f"Found duplicates in: {all_categories}"
            )
    
    def get_available_categories(self) -> List[str]:
        """
        Get the list of available exam categories.
        
        Provides controlled access to the category list.
        
        Returns:
            List of category names
        """
        return self.EXAM_CATEGORIES.copy()
