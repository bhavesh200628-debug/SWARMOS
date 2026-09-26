"""
SWARMOS Nebius Token Factory Client
Handles live runtime inference with NVIDIA Nemotron models hosted on Nebius Token Factory.
Fully OpenAI-compatible client with model discovery, latency tracking, and robust error recovery.
"""
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from backend.config import settings

logger = logging.getLogger("swarmos.nebius")
logging.basicConfig(level=logging.INFO)

class NebiusClient:
    def __init__(self):
        self.base_url = settings.NEBIUS_BASE_URL.rstrip("/")
        self.api_key = settings.NEBIUS_API_KEY
        self.model = settings.NEBIUS_MODEL
        self.fallback_model = settings.NEBIUS_FALLBACK_MODEL
        self.mock_mode = settings.MOCK_AI
        
        # Verify initial operational mode
        if not self.api_key:
            self.mock_mode = True
            logger.info("ℹ️ NEBIUS_API_KEY not configured. SWARMOS operating in deterministic local mode.")
        else:
            logger.info(f"🚀 Nebius Token Factory client initialized. Endpoint: {self.base_url}, Target Model: {self.model}")

    async def list_models(self) -> List[Dict[str, Any]]:
        """Fetch models currently accessible via the Nebius Token Factory account."""
        if self.mock_mode or not self.api_key:
            return [
                {"id": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF", "owned_by": "nvidia"},
                {"id": "nvidia/nemotron-mini-4b-instruct", "owned_by": "nvidia"},
                {"id": "nvidia/Llama-3.1-Nemotron-Ultra-253B-v1", "owned_by": "nvidia"},
            ]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/models", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"Nebius model list query returned status {response.status_code}: {response.text}")
                    return []
            except Exception as e:
                logger.error(f"Failed to query Nebius models: {str(e)}")
                return []

    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a real runtime inference call to Nebius Token Factory.
        Records exact request latency, token counts, and model ID.
        """
        if self.mock_mode or not self.api_key:
            raise RuntimeError("Live inference called while in MOCK_AI mode or missing API key.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if response_format:
            payload["response_format"] = response_format

        start_time = time.time()
        
        # Primary attempt with selected model
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info(f"Invoking Nebius Token Factory inference with model '{self.model}'...")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                latency_ms = (time.time() - start_time) * 1000.0

                if response.status_code == 200:
                    data = response.json()
                    choice = data["choices"][0]
                    content = choice["message"]["content"]
                    usage = data.get("usage", {})
                    
                    return {
                        "content": content,
                        "model": data.get("model", self.model),
                        "latency_ms": latency_ms,
                        "usage": usage,
                        "is_mock": False
                    }
                elif response.status_code == 404 and self.fallback_model != self.model:
                    # Retry with fallback model if model ID differs on account
                    logger.warning(f"Model {self.model} not found (404). Retrying with fallback {self.fallback_model}...")
                    payload["model"] = self.fallback_model
                    fb_response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    fb_latency_ms = (time.time() - start_time) * 1000.0
                    if fb_response.status_code == 200:
                        fb_data = fb_response.json()
                        return {
                            "content": fb_data["choices"][0]["message"]["content"],
                            "model": fb_data.get("model", self.fallback_model),
                            "latency_ms": fb_latency_ms,
                            "usage": fb_data.get("usage", {}),
                            "is_mock": False
                        }
                    else:
                        raise RuntimeError(f"Nebius API error ({fb_response.status_code}): {fb_response.text}")
                else:
                    raise RuntimeError(f"Nebius API error ({response.status_code}): {response.text}")

            except httpx.RequestError as exc:
                logger.error(f"HTTP request error during Nebius inference: {exc}")
                raise exc

# Global client singleton
nebius_client = NebiusClient()
