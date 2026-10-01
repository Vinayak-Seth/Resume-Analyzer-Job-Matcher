"""Loads config.yaml, prompts.yaml and the API key."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def load_config(path: str = "config.yaml") -> dict:
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompts(path: str) -> dict:
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "your_api_key_here":
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")
    return key
