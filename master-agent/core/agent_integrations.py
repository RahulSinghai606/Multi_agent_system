"""
Multi-Agent Integrations

Concrete implementations for integrating with:
- Google Gemini
- GitHub Copilot
- OpenAI GPT-4
- Custom agents

Each integration provides:
- API client setup
- Request/response formatting
- Error handling
- Rate limiting
- Streaming support
"""

from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass
import logging
import os
import httpx
import json

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Standardized agent response"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any]


class GeminiIntegration:
    """
    Google Gemini API integration

    Capabilities:
    - Multimodal (text, images, audio, video)
    - Long context (1M+ tokens)
    - Real-time streaming
    - Code generation
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.logger = logging.getLogger(f"{__name__}.GeminiIntegration")

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        images: Optional[List[str]] = None
    ) -> AgentResponse:
        """
        Generate response from Gemini

        Args:
            prompt: User prompt
            system_instruction: System instruction for model behavior
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            images: Optional list of base64-encoded images

        Returns:
            Standardized agent response
        """
        url = f"{self.base_url}/models/{self.model}:generateContent"

        # Build request
        parts = [{"text": prompt}]

        # Add images if multimodal
        if images:
            for img_data in images:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_data
                    }
                })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()

                data = response.json()

                # Extract response
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                finish_reason = data["candidates"][0]["finishReason"]

                # Extract token usage
                usage = data.get("usageMetadata", {})
                tokens_used = usage.get("totalTokenCount", 0)

                self.logger.info(
                    f"Gemini response: {tokens_used} tokens, "
                    f"finish_reason={finish_reason}"
                )

                return AgentResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    finish_reason=finish_reason,
                    metadata={
                        "prompt_tokens": usage.get("promptTokenCount", 0),
                        "completion_tokens": usage.get("candidatesTokenCount", 0)
                    }
                )

            except httpx.HTTPStatusError as e:
                self.logger.error(f"Gemini API error: {e.response.text}")
                raise
            except Exception as e:
                self.logger.error(f"Gemini request failed: {e}")
                raise

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream response from Gemini (for real-time collaboration)"""
        url = f"{self.base_url}/models/{self.model}:streamGenerateContent"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature}
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key, "alt": "sse"}

        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=headers,
                params=params
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "candidates" in data:
                            text = data["candidates"][0]["content"]["parts"][0]["text"]
                            yield text


class CopilotIntegration:
    """
    GitHub Copilot integration

    Capabilities:
    - Code completion
    - Code generation
    - IDE integration
    """

    def __init__(self, github_token: str):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com/copilot"
        self.logger = logging.getLogger(f"{__name__}.CopilotIntegration")

    async def complete_code(
        self,
        code_context: str,
        language: str = "python",
        max_tokens: int = 500
    ) -> AgentResponse:
        """
        Get code completion from Copilot

        Args:
            code_context: Code context (existing code + cursor position)
            language: Programming language
            max_tokens: Maximum tokens to generate

        Returns:
            Code completion response
        """
        # Note: This is a simplified example
        # Actual Copilot API requires OAuth app setup
        # See: https://docs.github.com/en/copilot/building-copilot-extensions

        url = f"{self.base_url}/completions"

        payload = {
            "prompt": code_context,
            "language": language,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                completion = data.get("completion", "")
                tokens_used = len(completion.split())  # Approximate

                self.logger.info(f"Copilot completion: ~{tokens_used} tokens")

                return AgentResponse(
                    content=completion,
                    model="copilot",
                    tokens_used=tokens_used,
                    finish_reason="complete",
                    metadata={"language": language}
                )

            except httpx.HTTPStatusError as e:
                self.logger.error(f"Copilot API error: {e.response.text}")
                raise
            except Exception as e:
                self.logger.error(f"Copilot request failed: {e}")
                raise


class OpenAIIntegration:
    """
    OpenAI GPT-4 integration

    Capabilities:
    - Code generation
    - Documentation
    - General purpose tasks
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.logger = logging.getLogger(f"{__name__}.OpenAIIntegration")

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AgentResponse:
        """Generate response from GPT-4"""
        url = f"{self.base_url}/chat/completions"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                content = data["choices"][0]["message"]["content"]
                finish_reason = data["choices"][0]["finish_reason"]
                tokens_used = data["usage"]["total_tokens"]

                self.logger.info(
                    f"GPT-4 response: {tokens_used} tokens, "
                    f"finish_reason={finish_reason}"
                )

                return AgentResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    finish_reason=finish_reason,
                    metadata={
                        "prompt_tokens": data["usage"]["prompt_tokens"],
                        "completion_tokens": data["usage"]["completion_tokens"]
                    }
                )

            except httpx.HTTPStatusError as e:
                self.logger.error(f"OpenAI API error: {e.response.text}")
                raise
            except Exception as e:
                self.logger.error(f"OpenAI request failed: {e}")
                raise


# Factory function to get appropriate integration
def get_agent_integration(provider: str, **kwargs):
    """
    Get agent integration instance

    Args:
        provider: Agent provider (gemini, copilot, openai)
        **kwargs: Provider-specific configuration

    Returns:
        Agent integration instance
    """
    integrations = {
        "gemini": GeminiIntegration,
        "copilot": CopilotIntegration,
        "openai": OpenAIIntegration
    }

    integration_class = integrations.get(provider.lower())

    if not integration_class:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: {', '.join(integrations.keys())}"
        )

    return integration_class(**kwargs)
