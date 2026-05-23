from __future__ import annotations

import math

import streamlit as st

from freelance_job_assistant.ai import (
    MODEL_NAME,
    generate_analysis,
    generate_proposal,
    generate_resume,
    generate_roadmap,
)
from freelance_job_assistant.models import JobAnalysis, LearningRoadmap, ResumeTailoring, SkillProfile
from freelance_job_assistant.storage import load_profile, save_profile


st.set_page_config(
    page_title="Freelance Job Assistant",
    page_icon="briefcase",
    layout="wide",
)


def parse_list(value: str) -> list[str]:
    items = []
    for chunk in value.replace(";", ",").replace("/", ",").splitlines():
        for item in chunk.split(","):
            cleaned = item.strip()
            if cleaned:
                items.append(cleaned)
    return items


def format_list(values: list[str]) -> str:
    return ", ".join(values)


def format_money(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "Unknown"
    return f"${value:,.0f}"


def current_profile_from_state() -> SkillProfile:
    return SkillProfile(
        skills=parse_list(st.session_state.skills_text),
        tools=parse_list(st.session_state.tools_text),
        experience_level=st.session_state.experience_level,
        domains=parse_list(st.session_state.domains_text),
        weak_areas=parse_list(st.session_state.weak_areas_text),
        weekly_income_target=int(st.session_state.weekly_income_target or 0),
        available_hours_per_week=int(st.session_state.available_hours_per_week or 0),
        minimum_hourly_rate=int(st.session_state.minimum_hourly_rate or 0),
    )


def seed_state() -> None:
    if st.session_state.get("_seeded"):
        return

    profile = load_profile()
    st.session_state.skills_text = format_list(profile.skills)
    st.session_state.tools_text = format_list(profile.tools)
    st.session_state.domains_text = format_list(profile.domains)
    st.session_state.weak_areas_text = format_list(profile.weak_areas)
    st.session_state.experience_level = profile.experience_level
    st.session_state.weekly_income_target = profile.weekly_income_target
    st.session_state.available_hours_per_week = profile.available_hours_per_week
    st.session_state.minimum_hourly_rate = profile.minimum_hourly_rate
    st.session_state.job_description = ""
    st.session_state.analysis = None
    st.session_state.proposal = None
    st.session_state.resume = None
    st.session_state.roadmap = None
    st.session_state._seeded = True


def reset_generated_outputs() -> None:
    st.session_state.proposal = None
    st.session_state.resume = None
    st.session_state.roadmap = None


seed_state()
profile = current_profile_from_state()
save_profile(profile)

target_hourly_rate = None
if profile.available_hours_per_week > 0 and profile.weekly_income_target > 0:
    target_hourly_rate = profile.weekly_income_target / profile.available_hours_per_week

hourly_floor = profile.minimum_hourly_rate
if target_hourly_rate is not None:
    hourly_floor = max(hourly_floor, math.ceil(target_hourly_rate))

st.title("Freelance Job Assistant")
st.caption("Analyze jobs by delivery fit, pricing safety, and whether the work is worth your week.")

with st.sidebar:
    st.subheader("Your profile")
    st.text_area("Skills", key="skills_text", height=90, placeholder="React, Python, SQL")
    st.text_area("Tools", key="tools_text", height=90, placeholder="Git, Docker, Figma")
    st.selectbox(
        "Experience level",
        options=["beginner", "intermediate", "advanced", "expert"],
        key="experience_level",
    )
    st.text_input("Domains", key="domains_text", placeholder="Dashboards, Shopify, landing pages")
    st.text_input("Weak areas / avoid", key="weak_areas_text", placeholder="Mobile apps, DevOps")
    st.number_input("Weekly income target (USD)", min_value=0, step=50, key="weekly_income_target")
    st.number_input("Available hours per week", min_value=0, step=1, key="available_hours_per_week")
    st.number_input("Minimum hourly rate (USD)", min_value=0, step=5, key="minimum_hourly_rate")
    st.info(f"Current model: {MODEL_NAME}")

left, right, extra, pace = st.columns(4)
left.metric("Weekly target", format_money(float(profile.weekly_income_target)))
right.metric("Available hours", f"{profile.available_hours_per_week}h")
extra.metric("Minimum rate", f"{format_money(float(profile.minimum_hourly_rate))}/hr")
pace.metric("Target hourly pace", f"{format_money(float(hourly_floor))}/hr")

st.subheader("Job description")
st.text_area(
    "Paste the full freelance job post",
    key="job_description",
    height=240,
    label_visibility="collapsed",
    placeholder="Paste the full job description from Upwork, Fiverr, or another platform.",
)

analyze_col, proposal_col, resume_col, roadmap_col = st.columns(4)

with analyze_col:
    if st.button("Analyze job", use_container_width=True, type="primary"):
        if not st.session_state.job_description.strip():
            st.error("Paste a job description first.")
        else:
            reset_generated_outputs()
            with st.spinner("Checking fit, pricing, and scope risk..."):
                try:
                    st.session_state.analysis = generate_analysis(profile, st.session_state.job_description.strip())
                except Exception as exc:
                    st.session_state.analysis = None
                    st.error(str(exc))

analysis: JobAnalysis | None = st.session_state.analysis

with proposal_col:
    if st.button("Generate proposal", use_container_width=True, disabled=analysis is None):
        with st.spinner("Writing proposal..."):
            try:
                st.session_state.proposal = generate_proposal(profile, st.session_state.job_description.strip(), analysis)
            except Exception as exc:
                st.error(str(exc))

with resume_col:
    if st.button("Tailor resume", use_container_width=True, disabled=analysis is None):
        with st.spinner("Tailoring resume..."):
            try:
                st.session_state.resume = generate_resume(profile, st.session_state.job_description.strip())
            except Exception as exc:
                st.error(str(exc))

with roadmap_col:
    if st.button("Learning roadmap", use_container_width=True, disabled=analysis is None):
        with st.spinner("Building roadmap..."):
            try:
                gaps = analysis.identified_gaps if analysis else []
                st.session_state.roadmap = generate_roadmap(profile, st.session_state.job_description.strip(), gaps)
            except Exception as exc:
                st.error(str(exc))

if analysis:
    estimated_job_revenue = None
    if analysis.estimated_effective_hourly_rate is not None:
        estimated_job_revenue = analysis.estimated_effective_hourly_rate * analysis.time_estimate_hours

    st.divider()
    st.subheader(f"Decision: {analysis.final_decision}")

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Skill match", f"{analysis.skill_match_score}/100")
    m2.metric("Knowledge gap", analysis.knowledge_gap)
    m3.metric("Complexity", analysis.task_complexity)
    m4.metric("Time estimate", f"{analysis.time_estimate_hours:.1f}h")
    m5.metric("Risk level", analysis.risk_level)
    m6.metric("Effective hourly", f"{format_money(analysis.estimated_effective_hourly_rate)}/hr")

    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Income fit", analysis.income_fit)
    n2.metric("Scope clarity", analysis.scope_clarity)
    n3.metric("Your rate floor", f"{format_money(float(hourly_floor))}/hr")
    n4.metric("Estimated job revenue", format_money(estimated_job_revenue))

    why_col, pricing_col = st.columns(2)
    with why_col:
        st.markdown("**Why this decision**")
        st.write(analysis.explanation)
    with pricing_col:
        st.markdown("**Pricing guidance**")
        st.write(analysis.pricing_guidance)

    if analysis.risk_signals:
        st.markdown("**Risk signals**")
        for signal in analysis.risk_signals:
            st.write(f"- {signal}")

    if analysis.identified_gaps:
        st.markdown("**Identified gaps**")
        for gap in analysis.identified_gaps:
            st.write(f"- {gap}")

    if analysis.required_skills:
        st.markdown("**Required skills detected**")
        st.write(", ".join(analysis.required_skills))

proposal: str | None = st.session_state.proposal
resume: ResumeTailoring | None = st.session_state.resume
roadmap: LearningRoadmap | None = st.session_state.roadmap

if proposal or resume or roadmap:
    st.divider()
    tabs = st.tabs(["Proposal", "Resume", "Roadmap"])

    with tabs[0]:
        if proposal:
            st.text_area("Generated proposal", proposal, height=220)
        else:
            st.caption("Generate a proposal after analyzing the job.")

    with tabs[1]:
        if resume:
            st.markdown("**Professional summary**")
            st.write(resume.summary)
            st.markdown("**Key skills**")
            st.write(", ".join(resume.skills))
            st.markdown("**Experience highlights**")
            for item in resume.experience_highlights:
                st.write(f"- {item}")
            st.markdown("**Tips**")
            st.write(resume.tips)
        else:
            st.caption("Generate tailored resume content after analyzing the job.")

    with tabs[2]:
        if roadmap:
            st.markdown("**Overview**")
            st.write(roadmap.overview)
            for skill in roadmap.skills:
                st.markdown(f"**{skill.skill}**")
                st.write(f"Priority: {skill.priority}")
                st.write(f"Time estimate: {skill.time_estimate}")
                if skill.steps:
                    st.write("Steps:")
                    for step in skill.steps:
                        st.write(f"- {step}")
                if skill.resources:
                    st.write("Resources:")
                    for resource in skill.resources:
                        st.write(f"- {resource}")
            st.markdown("**Timeline**")
            st.write(roadmap.timeline)
            if roadmap.next_steps:
                st.markdown("**Next steps**")
                for step in roadmap.next_steps:
                    st.write(f"- {step}")
        else:
            st.caption("Generate a learning roadmap after analyzing the job.")
