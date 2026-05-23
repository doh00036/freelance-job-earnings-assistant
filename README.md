# Freelance Job Assistant (Python + Streamlit)

This is a lighter Python rewrite of the original Next.js app from `my_study_assistant`.

It keeps the same core workflow:

- analyze whether a freelance job is worth taking
- generate a proposal
- tailor resume sections
- build a learning roadmap

## Why this version

- much smaller runtime footprint than a live Next.js dev server
- easier to read if you already know Streamlit
- simpler to run locally

## Project structure

```text
freelance_job_assistant_streamlit/
  app.py
  requirements.txt
  .env.example
  data/
  freelance_job_assistant/
    ai.py
    models.py
    prompts.py
    storage.py
```

## Setup

1. Create and activate a virtual environment.

```powershell
cd C:\APP_projects\freelance_job_assistant_streamlit
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Add your OpenAI key.

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

4. Run the app.

```powershell
streamlit run app.py
```

## Notes

- The profile is saved locally to `data/profile.json`.
- The default model is `gpt-4o-mini`, but you can change it with `OPENAI_MODEL`.
- This version uses the OpenAI Python Responses API with structured outputs for the JSON-based tools.

