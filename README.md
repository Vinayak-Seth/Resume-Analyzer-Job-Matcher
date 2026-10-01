# Resume Analyzer & Job Matcher

NLP project that uses an LLM (Groq API (Llama 3.3 70B)) for:
- **Information extraction / NER** – resume and job description -> structured JSON
- **Semantic matching** – skill-by-skill comparison with verbatim evidence from the resume
- **Scoring + advice** – rubric-based 0-100 score, gaps, transferable skills, resume improvements

## Structure
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `prompts.yaml` | **Prompt file** (system + 3 task prompts) |
| `config.yaml` | **Configuration file** (model, retries, thresholds) |
| `src/llm_client.py` | API call, JSON validation, retry with error feedback |
| `src/schemas.py` | Pydantic output contracts |
| `src/analyzer.py` | 3-step pipeline + caching |
| `src/scoring.py` | Deterministic verdict, keyword baseline, quote verification |
| `tests/` | Unit tests (no API key needed) |

## Run
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then paste your GROQ_API_KEY
streamlit run app.py
```
Tests: `pytest`

## Design notes
- Temperature 0.1 and JSON mode for stable output; invalid JSON is retried with the validation error fed back.
- Resume text is wrapped in `<document>` tags and treated as data (prompt-injection guard).
- Evidence quotes are checked in code against the resume; unverifiable quotes are flagged.
- Verdict is computed in code from the score, not by the LLM.
- Results are cached per (resume, job) pair to avoid repeat API calls.
