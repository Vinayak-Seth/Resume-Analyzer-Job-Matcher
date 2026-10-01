"""Thin wrapper around the Groq API with JSON validation and retries."""
import re
import time
from typing import TypeVar

from groq import Groq
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _strip_fences(text: str) -> str:
    """Remove ```json fences in case the model adds them despite instructions."""
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())


class LLMClient:
    def __init__(self, cfg: dict, api_key: str):
        self.cfg = cfg
        self.client = Groq(api_key=api_key)

    def _generate(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.cfg["model"],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=self.cfg["temperature"],
            max_tokens=self.cfg["max_output_tokens"],
            response_format={"type": "json_object"},  # JSON mode
        )
        return resp.choices[0].message.content or ""

    def structured(self, system: str, user: str, schema: type[T]) -> T:
        """Call the LLM and return a validated `schema` object.

        On invalid JSON / schema violations the error is fed back to the model
        so it can correct itself; API errors use exponential backoff.
        """
        prompt, last_err = user, None
        for attempt in range(self.cfg.get("max_retries", 2) + 1):
            try:
                raw = self._generate(system, prompt)
                return schema.model_validate_json(_strip_fences(raw))
            except ValueError as e:  # includes pydantic.ValidationError
                last_err = e
                prompt = (
                    f"{user}\n\nYour previous answer was invalid: {str(e)[:500]}\n"
                    "Return ONLY valid JSON that matches the schema."
                )
            except Exception as e:  # network / quota / API errors
                last_err = e
                time.sleep(2**attempt)
        raise RuntimeError(f"LLM call failed after retries: {last_err}")
