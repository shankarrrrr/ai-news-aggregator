import os
import json
from typing import Optional
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DigestOutput(BaseModel):
    title: str
    summary: str

PROMPT = """You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance

You MUST respond with valid JSON in this exact format:
{
  "title": "Your compelling title here",
  "summary": "Your 2-3 sentence summary here."
}"""


class DigestAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:
        try:
            user_prompt = f"{PROMPT}\n\nCreate a digest for this {article_type}:\nTitle: {title}\nContent: {content[:8000]}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=self.generation_config
            )
            
            if not response or not response.text:
                print(f"Empty response from Gemini for {article_type}")
                return None
            
            # Parse JSON response
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            parsed = json.loads(response_text)
            return DigestOutput(**parsed)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for {article_type}: {e}")
            print(f"Response text: {response.text[:200] if response else 'No response'}")
            return None
        except Exception as e:
            print(f"Error generating digest: {e}")
            return None

