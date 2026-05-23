from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Level = Literal["Low", "Medium", "High"]
IncomeFit = Literal["Good", "Borderline", "Poor"]
FinalDecision = Literal["Apply", "Apply Carefully", "Risky", "Skip"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced", "expert"]


class SkillProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    experience_level: ExperienceLevel = "intermediate"
    domains: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    weekly_income_target: int = 500
    available_hours_per_week: int = 20
    minimum_hourly_rate: int = 25


class JobAnalysis(BaseModel):
    skill_match_score: int = Field(ge=0, le=100)
    knowledge_gap: Level
    task_complexity: Level
    time_estimate_hours: float = Field(ge=0)
    risk_level: Level
    scope_clarity: Level
    income_fit: IncomeFit
    estimated_effective_hourly_rate: float | None = Field(default=None, ge=0)
    final_decision: FinalDecision
    explanation: str
    pricing_guidance: str
    required_skills: list[str] = Field(default_factory=list)
    identified_gaps: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)


class ResumeTailoring(BaseModel):
    summary: str
    skills: list[str] = Field(default_factory=list)
    experience_highlights: list[str] = Field(default_factory=list)
    tips: str


class RoadmapSkill(BaseModel):
    skill: str
    priority: Level
    time_estimate: str
    resources: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class LearningRoadmap(BaseModel):
    overview: str
    skills: list[RoadmapSkill] = Field(default_factory=list)
    timeline: str
    next_steps: list[str] = Field(default_factory=list)
