"""Pipeline: resume extraction -> job extraction -> semantic matching."""
import hashlib
import json

from .config import load_prompts
from .llm_client import LLMClient
from .schemas import JobRequirements, MatchResult, ResumeProfile
from .scoring import evidence_is_verbatim, keyword_baseline, verdict_for


class Analyzer:
    def __init__(self, cfg: dict, api_key: str):
        self.cfg = cfg
        self.prompts = load_prompts(cfg["paths"]["prompts"])
        self.llm = LLMClient(cfg["llm"], api_key)
        self._cache: dict[str, dict] = {}

    def _run(self, task: str, schema, text: str, **extra):
        user = self.prompts[task]["user"].replace(
            "<<SCHEMA>>", json.dumps(schema.model_json_schema())
        )
        for key, value in extra.items():
            user = user.replace(f"<<{key}>>", value)
        user = user.replace("<<TEXT>>", text)  # untrusted text goes in last
        return self.llm.structured(self.prompts["system"], user, schema)

    def analyze(self, resume_text: str, job_text: str) -> dict:
        limit = self.cfg["input"]["max_chars"]
        resume_text, job_text = resume_text[:limit], job_text[:limit]

        key = hashlib.sha256((resume_text + "||" + job_text).encode()).hexdigest()
        if key in self._cache:
            return self._cache[key]

        resume = self._run("resume_extraction", ResumeProfile, resume_text)
        job = self._run("job_extraction", JobRequirements, job_text)
        match = self._run(
            "matching",
            MatchResult,
            resume_text,
            RESUME_JSON=resume.model_dump_json(),
            JOB_JSON=job.model_dump_json(),
        )

        result = {
            "resume": resume,
            "job": job,
            "match": match,
            "verdict": verdict_for(match.overall_score, self.cfg["scoring"]),
            "baseline": keyword_baseline(resume_text, job.must_have_skills),
            "evidence_ok": {
                m.requirement: evidence_is_verbatim(m.evidence, resume_text)
                for m in match.skill_matches
            },
        }
        self._cache[key] = result
        return result
