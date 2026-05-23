from __future__ import annotations

from .models import JobAnalysis, SkillProfile


def _profile_text(profile: SkillProfile) -> str:
    return f"""
Skills: {", ".join(profile.skills) or "(none listed)"}
Tools: {", ".join(profile.tools) or "(none listed)"}
Experience level: {profile.experience_level}
Domains: {", ".join(profile.domains) or "(none listed)"}
Weak or avoid areas: {", ".join(profile.weak_areas) or "(none listed)"}
Weekly income target (USD): {profile.weekly_income_target}
Available hours per week: {profile.available_hours_per_week}
Minimum acceptable hourly rate (USD): {profile.minimum_hourly_rate}
""".strip()


def analysis_messages(profile: SkillProfile, job_description: str) -> list[dict[str, str]]:
    system = """
You are a senior technical mentor and freelance risk advisor.
Be honest and protective of the freelancer's time.
Judge both delivery fit and business fit.
Return practical outputs, not motivational fluff.
""".strip()

    user = f"""
FREELANCER PROFILE
{_profile_text(profile)}

JOB DESCRIPTION
---
{job_description}
---

Evaluate whether this freelancer should take the job.

Scoring rules:
- skill_match_score: 0 to 100
- knowledge_gap: Low, Medium, or High
- task_complexity: Low, Medium, or High
- time_estimate_hours: realistic delivery time including communication and revisions
- risk_level: Low, Medium, or High
- scope_clarity: Low means clear scope, High means vague or risky scope creep
- income_fit: Good, Borderline, or Poor
- estimated_effective_hourly_rate: number in USD or null
- final_decision: Apply, Apply Carefully, Risky, or Skip

Also include:
- explanation: 2 to 4 sentences
- pricing_guidance: 1 to 2 sentences
- required_skills: main skills and tools detected in the job
- identified_gaps: concrete mismatches between the job and the profile
- risk_signals: practical red flags like vague scope, low budget, or rushed timelines
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def proposal_messages(profile: SkillProfile, job_description: str, analysis: JobAnalysis) -> list[dict[str, str]]:
    system = """
You are a freelance proposal writing expert.
Write a concise, professional, honest proposal in 2 or 3 short paragraphs.
Avoid generic filler. If the job is risky, keep the proposal scoped and boundary-aware.
Return only the proposal text.
""".strip()

    user = f"""
FREELANCER PROFILE
{_profile_text(profile)}

JOB DESCRIPTION
---
{job_description}
---

ANALYSIS DECISION: {analysis.final_decision}
ANALYSIS REASONING: {analysis.explanation}
IDENTIFIED GAPS: {", ".join(analysis.identified_gaps) or "(none)"}

Write the proposal.
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def resume_messages(profile: SkillProfile, job_description: str) -> list[dict[str, str]]:
    system = """
You are a resume tailoring expert.
Create realistic resume sections that match the job without inventing experience.
Return JSON only through the schema.
""".strip()

    user = f"""
FREELANCER PROFILE
{_profile_text(profile)}

JOB DESCRIPTION
---
{job_description}
---

Generate a tailored summary, relevant skills, experience highlights, and brief presentation tips.
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def roadmap_messages(
    profile: SkillProfile,
    job_description: str,
    identified_gaps: list[str],
) -> list[dict[str, str]]:
    system = """
You are a learning roadmap expert.
Create a realistic upskilling plan with priority, time estimates, concrete steps, and useful resource ideas.
Return JSON only through the schema.
""".strip()

    user = f"""
FREELANCER PROFILE
{_profile_text(profile)}

JOB DESCRIPTION
---
{job_description}
---

IDENTIFIED GAPS
{", ".join(identified_gaps) or "Analyze the description and infer the likely gaps."}

Generate a practical learning roadmap.
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
