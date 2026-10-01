"""Pydantic models: they define the JSON contract the LLM must follow."""
from typing import Literal

from pydantic import BaseModel, Field


class Education(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""


class Experience(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    highlights: list[str] = []


class ResumeProfile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = []
    education: list[Education] = []
    experience: list[Experience] = []
    projects: list[str] = []
    certifications: list[str] = []
    total_experience_years: float = 0


class JobRequirements(BaseModel):
    title: str = ""
    must_have_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    min_experience_years: float = 0
    education_requirement: str = ""
    responsibilities: list[str] = []


class SkillMatch(BaseModel):
    requirement: str
    status: Literal["match", "partial", "missing"]
    evidence: str = ""


class MatchResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    skill_matches: list[SkillMatch]
    transferable_skills: list[str] = []
    missing_requirements: list[str] = []
    strengths: list[str] = []
    improvement_suggestions: list[str] = []
    summary: str = ""
