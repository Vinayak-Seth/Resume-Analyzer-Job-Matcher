"""Deterministic helpers: verdict thresholds, keyword baseline, evidence check."""
import re


def verdict_for(score: int, cfg: dict) -> str:
    if score >= cfg["strong_fit_min"]:
        return "Strong fit"
    if score >= cfg["moderate_fit_min"]:
        return "Moderate fit"
    return "Weak fit"


def keyword_baseline(resume_text: str, must_have: list[str]) -> int:
    """Naive % of must-have skills literally present in the resume.
    Shown next to the LLM score to demonstrate what semantic matching adds."""
    if not must_have:
        return 0
    text = resume_text.lower()
    hits = sum(1 for s in must_have if s.lower() in text)
    return round(100 * hits / len(must_have))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).lower().strip()


def evidence_is_verbatim(evidence: str, resume_text: str) -> bool:
    """Guards against hallucinated quotes: evidence must appear in the resume."""
    return not evidence or _norm(evidence) in _norm(resume_text)
