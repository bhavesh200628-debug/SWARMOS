"""
SWARMOS Configuration Module
Centralized settings for Nebius Token Factory, NVIDIA Nemotron, simulation parameters, and server settings.
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # App Settings
    PROJECT_NAME: str = "SWARMOS"
    TAGLINE: str = "One nervous system for an entire robot fleet."
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("SWARMOS_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SWARMOS_PORT", "8000"))
    DEBUG: bool = os.getenv("SWARMOS_DEBUG", "false").lower() == "true"
    
    # Nebius Token Factory & AI Inference
    # Official Nebius Token Factory API base URL
    NEBIUS_BASE_URL: str = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1")
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")
    
    # Optional Tavily API for incident context retrieval
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # NVIDIA Nemotron Model Selection
    # Default: NVIDIA Llama-3.1-Nemotron-70B-Instruct-HF
    # Fallback/Fast: nvidia/nemotron-mini-4b-instruct
    # Ultra: nvidia/Llama-3.1-Nemotron-Ultra-253B-v1
    NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF")
    NEBIUS_FALLBACK_MODEL: str = os.getenv("NEBIUS_FALLBACK_MODEL", "nvidia/nemotron-mini-4b-instruct")
    
    # AI Execution Mode
    # If True or if NEBIUS_API_KEY is not set, operates in transparent deterministic local mode
    MOCK_AI: bool = os.getenv("MOCK_AI", "false").lower() == "true" or not os.getenv("NEBIUS_API_KEY", "")
    
    # Simulation Settings
    SIMULATION_TICK_RATE_HZ: float = float(os.getenv("SIMULATION_TICK_RATE_HZ", "10.0"))
    TELEMETRY_BROADCAST_RATE_HZ: float = float(os.getenv("TELEMETRY_BROADCAST_RATE_HZ", "5.0"))
    
    # Safety Thresholds
    MIN_BATTERY_FOR_MISSION: float = 20.0  # percent
    CRITICAL_BATTERY_LEVEL: float = 15.0    # percent
    COLLISION_PROXIMITY_LIMIT: float = 1.0  # meters
    ALLOWED_ACTIONS: list = [
        "navigate",
        "inspect",
        "transport",
        "stop",
        "report_status",
        "return_to_base"
    ]

settings = Settings()
