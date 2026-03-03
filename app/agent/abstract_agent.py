"""
Abstract base class for AI-powered agents.

This module defines the interface for all agents that process content
using the Google Gemini API.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
import json
import time
import random
import logging
import google.generativeai as genai
from pydantic import BaseModel, Field
from ..exceptions import TransientError, PermanentError, APIError, APIRateLimitError


class AgentConfig(BaseModel):
    """
    Configuration for AI agents.
    
    Attributes:
        model_name: Gemini model to use
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum output tokens
        api_key: Gemini API key
    """
    model_name: str = Field(default="gemini-1.5-flash")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, gt=0)
    api_key: str = Field(..., min_length=1)


class AgentException(Exception):
    """Exception raised by agents during processing."""
    pass


class AbstractAgent(ABC):
    """
    Abstract base class for all AI-powered agents.
    
    Provides common Gemini API client initialization and error handling.
    Subclasses implement specific processing logic via the execute() method.
    This design follows the Interface Segregation Principle - agents only
    depend on the methods they need (execute and helper methods).
    
    Attributes:
        _config (AgentConfig): Agent configuration (private, encapsulated)
        _client (genai.GenerativeModel): Gemini API client (private, encapsulated)
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with Gemini API configuration.
        
        Args:
            config: Agent configuration including API key and model settings
            
        Raises:
            AgentException: If initialization fails
        """
        self._config = config
        try:
            genai.configure(api_key=config.api_key)
            self._model = genai.GenerativeModel(config.model_name)
        except Exception as e:
            raise AgentException(f"Failed to initialize Gemini client: {str(e)}")
    
    @property
    def model_name(self) -> str:
        """
        Get the model name being used (encapsulation via property accessor).
        
        Returns:
            The Gemini model name
        """
        return self._config.model_name
    
    @property
    def temperature(self) -> float:
        """
        Get the temperature setting (encapsulation via property accessor).
        
        Returns:
            The temperature value
        """
        return self._config.temperature
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the agent's processing logic.
        
        This abstract method must be implemented by all concrete agents,
        enforcing the Liskov Substitution Principle - all agent subclasses
        must provide this functionality and be substitutable for the base class.
        
        Args:
            input_data: Input data to process (type varies by agent)
            
        Returns:
            Processed output (type varies by agent)
            
        Raises:
            AgentException: If processing fails
        """
        pass
    
    def execute_with_fallback(
        self,
        input_data: Any,
        fallback_strategies: Optional[list] = None,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Any:
        """
        Execute agent processing with fallback strategies and retry logic.
        
        This method wraps the abstract execute() method with retry logic
        for handling API rate limits, temporary failures, and fallback strategies.
        
        Args:
            input_data: Input data to process
            fallback_strategies: List of fallback functions to try if main execution fails
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            
        Returns:
            Processed output
            
        Raises:
            PermanentError: If error is not retryable
            TransientError: If all retries and fallbacks are exhausted
        """
        logger = logging.getLogger(__name__)
        
        # Try main execution with retries
        for attempt in range(max_retries + 1):
            try:
                return self.execute(input_data)
                
            except PermanentError:
                logger.error(f"Permanent error in {self.__class__.__name__}, not retrying")
                break  # Skip to fallback strategies
                
            except APIRateLimitError as e:
                if attempt == max_retries:
                    logger.error(f"Rate limit exceeded, all retries exhausted")
                    break
                
                # Use retry_after from exception or calculate backoff
                delay = getattr(e, 'retry_after', base_delay * (2 ** attempt))
                delay = min(delay + random.uniform(0, 1), 300)  # Max 5 minutes
                
                logger.warning(
                    f"Rate limit hit in {self.__class__.__name__} "
                    f"(attempt {attempt + 1}/{max_retries + 1}). "
                    f"Retrying in {delay:.1f} seconds"
                )
                
                time.sleep(delay)
                
            except TransientError as e:
                if attempt == max_retries:
                    logger.error(f"Transient error, all retries exhausted: {str(e)}")
                    break
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                delay = min(delay, 60)  # Max 1 minute
                
                logger.warning(
                    f"Transient error in {self.__class__.__name__} "
                    f"(attempt {attempt + 1}/{max_retries + 1}): {str(e)}. "
                    f"Retrying in {delay:.1f} seconds"
                )
                
                time.sleep(delay)
                
            except Exception as e:
                logger.warning(
                    f"Unknown error in {self.__class__.__name__}, treating as transient: {str(e)}"
                )
                
                if attempt == max_retries:
                    break
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(min(delay, 60))
        
        # Try fallback strategies if main execution failed
        if fallback_strategies:
            logger.info(f"Trying {len(fallback_strategies)} fallback strategies")
            
            for i, fallback in enumerate(fallback_strategies):
                try:
                    logger.info(f"Attempting fallback strategy {i + 1}")
                    result = fallback(input_data)
                    logger.info(f"Fallback strategy {i + 1} succeeded")
                    return result
                except Exception as e:
                    logger.warning(f"Fallback strategy {i + 1} failed: {str(e)}")
                    continue
        
        # All strategies failed
        raise TransientError(
            f"All execution attempts and fallback strategies failed for {self.__class__.__name__}"
        )
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Common method to call Gemini API with comprehensive error handling.
        
        Provides consistent API interaction across all agents with proper
        error classification and retry logic.
        Private method (prefixed with _) for internal use only.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            API response text
            
        Raises:
            APIRateLimitError: If rate limit is exceeded
            PermanentError: For authentication or quota errors
            TransientError: For temporary API issues
        """
        logger = logging.getLogger(__name__)
        
        try:
            self._log_api_call(len(prompt))
            
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "temperature": self._config.temperature,
                    "max_output_tokens": self._config.max_tokens,
                }
            )
            
            # Handle blocked or empty responses
            if not response.text:
                raise TransientError("Gemini API returned empty response")
            
            return response.text
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Classify errors for appropriate handling
            if "rate limit" in error_msg or "quota" in error_msg:
                if "exceeded" in error_msg and "daily" in error_msg:
                    raise PermanentError(f"Daily API quota exceeded: {str(e)}", cause=e)
                else:
                    # Extract retry-after if available
                    retry_after = self._extract_retry_after(str(e))
                    raise APIRateLimitError(
                        f"API rate limit exceeded: {str(e)}", 
                        retry_after=retry_after,
                        cause=e
                    )
            elif "authentication" in error_msg or "api key" in error_msg:
                raise PermanentError(f"API authentication failed: {str(e)}", cause=e)
            elif "timeout" in error_msg or "connection" in error_msg:
                raise TransientError(f"API connection failed: {str(e)}", cause=e)
            else:
                # Default to transient for unknown API errors
                logger.warning(f"Unknown API error, treating as transient: {str(e)}")
                raise TransientError(f"Gemini API call failed: {str(e)}", cause=e)
    
    def _extract_retry_after(self, error_message: str) -> Optional[int]:
        """
        Extract retry-after value from error message.
        
        Args:
            error_message: Error message from API
            
        Returns:
            Retry delay in seconds, or None if not found
        """
        import re
        
        # Look for patterns like "retry after 60 seconds" or "wait 30s"
        patterns = [
            r'retry after (\d+) seconds?',
            r'wait (\d+)s',
            r'try again in (\d+) seconds?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _parse_json_response(self, response: str) -> dict:
        """
        Parse JSON response from Gemini API.
        
        Handles both raw JSON and JSON wrapped in markdown code blocks,
        which Gemini sometimes returns.
        
        Args:
            response: JSON string from API
            
        Returns:
            Parsed dictionary
            
        Raises:
            AgentException: If JSON parsing fails
        """
        try:
            # Try parsing as raw JSON first
            return json.loads(response)
        except json.JSONDecodeError:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                try:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except (IndexError, json.JSONDecodeError) as e:
                    raise AgentException(f"Failed to parse JSON from markdown: {str(e)}")
            elif "```" in response:
                # Try generic code block extraction
                try:
                    json_str = response.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except (IndexError, json.JSONDecodeError) as e:
                    raise AgentException(f"Failed to parse JSON from code block: {str(e)}")
            else:
                raise AgentException(f"Response is not valid JSON: {response[:100]}...")
    
    def _log_execution_start(self, operation: str) -> None:
        """
        Log the start of an agent execution.
        
        Args:
            operation: Description of the operation being performed
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {self.__class__.__name__}: {operation}")
    
    def _log_execution_complete(self, operation: str) -> None:
        """
        Log the completion of an agent execution.
        
        Args:
            operation: Description of the operation that completed
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Completed {self.__class__.__name__}: {operation}")
    
    def _log_api_call(self, prompt_length: int) -> None:
        """
        Log an API call for monitoring purposes.
        
        Args:
            prompt_length: Length of the prompt being sent
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(
            f"{self.__class__.__name__} calling Gemini API "
            f"(prompt length: {prompt_length} chars)"
        )
