"""
SWARMOS Tavily Context Retrieval Module
Optional bonus integration that queries Tavily for real-world Safety Data Sheets (SDS),
hazardous material protocols, and OSHA/warehouse quarantine standards to ground Nemotron's
mission decomposition in real-world physical safety regulations.

If TAVILY_API_KEY is unset or empty, this module gracefully reports unconfigured
without faking or synthesizing network responses.
"""
import logging
from typing import Optional, Dict, Any
import httpx
from backend.config import settings

logger = logging.getLogger("swarmos.tavily")

class TavilyContextRetriever:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def get_incident_safety_context(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves real-world regulatory and chemical safety handling context.
        Returns None or empty dict if unconfigured or if API request fails.
        """
        if not self.is_configured:
            logger.info("Tavily context retrieval skipped: TAVILY_API_KEY not configured.")
            return None

        payload = {
            "api_key": self.api_key,
            "query": f"warehouse safety protocol hazardous package containment {query}",
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 3
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(self.base_url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    logger.info("✅ Tavily regulatory context retrieved successfully.")
                    return {
                        "source": "Tavily Search API",
                        "answer": data.get("answer", ""),
                        "results": [
                            {"title": r.get("title"), "url": r.get("url"), "content": r.get("content")}
                            for r in data.get("results", [])
                        ]
                    }
                else:
                    logger.warning(f"Tavily API responded with status {res.status_code}: {res.text}")
                    return None
        except Exception as e:
            logger.warning(f"Tavily context fetch failed: {e}")
            return None

tavily_retriever = TavilyContextRetriever()
