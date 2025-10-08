"""
Unified LLM client for Vertex AI Claude and Gemini API.
"""
import os
import json
import logging
from typing import Optional, Dict
from enum import Enum

import google.generativeai as genai
from anthropic import AnthropicVertex
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)

# Get configuration
PROJECT_ID = os.getenv("PROJECT_ID", "bq-demos-469816")
LOCATION = os.getenv("LOCATION", "global")


class ModelType(Enum):
    """Supported model types."""
    GEMINI_API = "gemini-2.5-pro"
    GEMINI_VERTEX = "gemini-2.0-flash-exp"  # Gemini via Vertex AI
    GEMINI_PRO_VERTEX = "gemini-2.5-pro"  # Gemini 2.5 Pro via Vertex AI
    CLAUDE_45 = "claude-sonnet-4-5@20250929"


class VertexLLMClient:
    """Unified client for Vertex AI Claude and Gemini API."""

    def __init__(self, model_type: ModelType):
        """
        Initialize LLM client.

        Args:
            model_type: Which model to use (GEMINI_API, GEMINI_VERTEX, GEMINI_PRO_VERTEX, or CLAUDE_45)
        """
        self.model_type = model_type

        if model_type in [ModelType.GEMINI_VERTEX, ModelType.GEMINI_PRO_VERTEX]:
            # Initialize Vertex AI for Gemini (check this FIRST before GEMINI_API)
            # Gemini requires a specific region (us-central1), not "global"
            gemini_location = "us-central1" if LOCATION == "global" else LOCATION
            vertexai.init(project=PROJECT_ID, location=gemini_location)
            self.gemini_vertex_model = GenerativeModel(model_type.value)
            logger.info(f"Initialized Gemini via Vertex AI: {model_type.value} in project {PROJECT_ID}, region {gemini_location}")
        elif model_type == ModelType.GEMINI_API:
            # Configure Gemini API with key
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel(model_type.value)
            logger.info(f"Initialized Gemini API client: {model_type.value}")
        elif model_type == ModelType.CLAUDE_45:
            # Claude requires us-east5, not "global"
            claude_location = "us-east5" if LOCATION == "global" else LOCATION
            self.claude_client = AnthropicVertex(region=claude_location, project_id=PROJECT_ID)
            logger.info(f"Initialized Claude via Vertex AI in project {PROJECT_ID}, region {claude_location}")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content using the configured model.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens to generate
            system_instruction: Optional system instruction

        Returns:
            Generated text
        """
        try:
            if self.model_type in [ModelType.GEMINI_VERTEX, ModelType.GEMINI_PRO_VERTEX]:
                # Check Vertex AI Gemini FIRST
                return await self._generate_gemini_vertex(
                    prompt, temperature, max_output_tokens, system_instruction
                )
            elif self.model_type == ModelType.GEMINI_API:
                return await self._generate_gemini(
                    prompt, temperature, max_output_tokens, system_instruction
                )
            elif self.model_type == ModelType.CLAUDE_45:
                return await self._generate_claude_vertex(
                    prompt, temperature, max_output_tokens, system_instruction
                )
        except Exception as e:
            logger.error(f"Generation failed with {self.model_type.name}: {e}")
            raise

    async def _generate_gemini(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Gemini API."""
        import asyncio

        # Create model with system instruction if provided
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_type.value,
                system_instruction=system_instruction
            )
        else:
            model = self.gemini_model

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=0.95,
        )

        # Run blocking SDK call in thread pool for true async parallelization
        response = await asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=generation_config
        )

        return response.text

    async def _generate_gemini_vertex(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Gemini via Vertex AI."""
        import asyncio
        from vertexai.generative_models import GenerationConfig

        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=0.95,
            response_mime_type="application/json",  # Ensures pure JSON output without markdown
        )

        # Combine system instruction with prompt if provided
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"

        # Run blocking SDK call in thread pool for true async parallelization
        response = await asyncio.to_thread(
            self.gemini_vertex_model.generate_content,
            full_prompt,
            generation_config=generation_config
        )

        return response.text

    async def _generate_claude_vertex(
        self,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate content using Claude via Anthropic Vertex SDK."""
        import asyncio

        # Run blocking SDK call in thread pool for true async parallelization
        # This allows multiple Claude calls to execute concurrently
        response = await asyncio.to_thread(
            self.claude_client.messages.create,
            model=self.model_type.value,
            max_tokens=max_output_tokens,
            temperature=temperature,
            system=system_instruction or "",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            timeout=600.0  # 10 minute timeout for long responses
        )

        return response.content[0].text

    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Generate with automatic retry on failure."""
        import asyncio

        for attempt in range(max_retries):
            try:
                return await self.generate_content(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                await asyncio.sleep(2 ** attempt)

    def parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from LLM response with repair logic for incomplete output."""
        # Simple and robust extraction - just find and remove code block markers
        json_text = response_text.strip()

        # Remove ```json if present at start
        if json_text.startswith("```json"):
            json_text = json_text[7:]  # Remove ```json
        elif json_text.startswith("```"):
            json_text = json_text[3:]  # Remove ```

        # Remove ``` if present at end
        if json_text.endswith("```"):
            json_text = json_text[:-3]

        # Clean up whitespace
        json_text = json_text.strip()

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")
            logger.warning(f"Attempting JSON repair for unterminated strings/objects...")

            # Try to repair common JSON errors (unterminated strings, unclosed objects/arrays)
            try:
                repaired = self._repair_json(json_text, e)
                logger.info(f"✅ JSON repair successful! Fixed {len(json_text) - len(repaired)} characters")
                return json.loads(repaired)
            except Exception as repair_error:
                logger.error(f"JSON repair failed: {repair_error}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}...")
                logger.error(f"Extracted JSON text (first 500 chars): {json_text[:500]}...")
                logger.error(f"Extracted JSON text length: {len(json_text)}")
                logger.error(f"Last 200 chars: ...{json_text[-200:]}")
                raise ValueError(f"Invalid JSON response: {str(e)}")

    def _repair_json(self, json_text: str, error: json.JSONDecodeError) -> str:
        """Attempt to repair malformed JSON."""
        import re

        # Get the error position
        error_pos = getattr(error, 'pos', None)
        error_msg = str(error)

        # Strategy 1: Remove trailing commas (common Gemini error)
        if "Expecting property name" in error_msg or "Expecting '}'" in error_msg:
            logger.info("Attempting to fix trailing commas...")
            # Remove commas before closing braces/brackets
            repaired = re.sub(r',\s*([}\]])', r'\1', json_text)
            return repaired

        # Strategy 2: If unterminated string, try to close it and truncate
        if "Unterminated string" in error_msg:
            # Find the last complete object/array before the error
            # Walk backwards from error position to find last complete '}' or ']'
            if error_pos:
                # Find the last complete array or object
                truncate_pos = error_pos
                depth = 0
                in_string = False

                for i in range(error_pos - 1, -1, -1):
                    c = json_text[i]

                    if c == '"' and (i == 0 or json_text[i-1] != '\\'):
                        in_string = not in_string
                    elif not in_string:
                        if c in ['}', ']']:
                            if depth == 0:
                                truncate_pos = i + 1
                                break
                            depth -= 1
                        elif c in ['{', '[']:
                            depth += 1

                # Truncate at the last complete object and close root
                repaired = json_text[:truncate_pos]

                # Count unclosed brackets/braces from the start
                open_braces = repaired.count('{') - repaired.count('}')
                open_brackets = repaired.count('[') - repaired.count(']')

                # Close them
                repaired += ']' * open_brackets + '}' * open_braces

                logger.info(f"Repaired JSON by truncating at position {truncate_pos} and closing {open_brackets} arrays and {open_braces} objects")
                return repaired

        # Strategy 3: Try removing content after error position
        if error_pos and error_pos < len(json_text):
            logger.info(f"Attempting to truncate JSON at error position {error_pos}...")
            # Truncate at error and try to close properly
            truncated = json_text[:error_pos]
            # Count unclosed brackets
            open_braces = truncated.count('{') - truncated.count('}')
            open_brackets = truncated.count('[') - truncated.count(']')
            repaired = truncated + ']' * open_brackets + '}' * open_braces
            return repaired

        raise ValueError(f"Cannot repair JSON: {error}")


# ============================================================================
# Convenience Functions
# ============================================================================

def get_claude_vertex_client() -> VertexLLMClient:
    """Get Claude (via Vertex AI) client."""
    return VertexLLMClient(ModelType.CLAUDE_45)


def get_gemini_client() -> VertexLLMClient:
    """Get Gemini API client."""
    return VertexLLMClient(ModelType.GEMINI_API)


def get_gemini_vertex_client() -> VertexLLMClient:
    """Get Gemini 2.0 Flash (via Vertex AI) client."""
    return VertexLLMClient(ModelType.GEMINI_VERTEX)


def get_gemini_pro_vertex_client() -> VertexLLMClient:
    """Get Gemini 2.5 Pro (via Vertex AI) client."""
    return VertexLLMClient(ModelType.GEMINI_PRO_VERTEX)
