from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

from .models import JobAnalysis, LearningRoadmap, ResumeTailoring, SkillProfile
from .prompts import analysis_messages, proposal_messages, resume_messages, roadmap_messages

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to a .env file in the project root.")
    return OpenAI(api_key=api_key)


def generate_analysis(profile: SkillProfile, job_description: str) -> JobAnalysis:
    response = _client().responses.parse(
        model=MODEL_NAME,
        input=analysis_messages(profile, job_description),
        text_format=JobAnalysis,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return a structured analysis.")
    return response.output_parsed


def generate_proposal(profile: SkillProfile, job_description: str, analysis: JobAnalysis) -> str:
    response = _client().responses.create(
        model=MODEL_NAME,
        input=proposal_messages(profile, job_description, analysis),
    )
    proposal = response.output_text.strip()
    if not proposal:
        raise RuntimeError("The model did not return a proposal.")
    return proposal


def generate_resume(profile: SkillProfile, job_description: str) -> ResumeTailoring:
    response = _client().responses.parse(
        model=MODEL_NAME,
        input=resume_messages(profile, job_description),
        text_format=ResumeTailoring,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return structured resume content.")
    return response.output_parsed


def generate_roadmap(
    profile: SkillProfile,
    job_description: str,
    identified_gaps: list[str],
) -> LearningRoadmap:
    response = _client().responses.parse(
        model=MODEL_NAME,
        input=roadmap_messages(profile, job_description, identified_gaps),
        text_format=LearningRoadmap,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model did not return a structured roadmap.")
    return response.output_parsed
