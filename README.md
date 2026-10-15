# SNJB Placement Cell Assistant — Complete AI Chatbot

An AI-powered Placement Cell Assistant built specifically for **SNJB's Late Sau. Kantabai Bhavarlalji Jain College of Engineering, Chandwad, Nashik, Maharashtra, India**.

Designed to assist engineering students with campus recruitment procedures, eligibility requirements, placement policies, document checklists, resume formatting, aptitude practice, and technical/HR interview preparation while grounding institutional facts strictly in verified college documents.

---

## 🏛️ 1. Institutional Context

- **Official College Name**: SNJB's Late Sau. Kantabai Bhavarlalji Jain College of Engineering
- **Location**: Chandwad, Nashik district, Maharashtra, India - 423101
- **Official Website**: [https://www.snjb.org/](https://www.snjb.org/)
- **Target Audience**: Engineering students (Computer, AI&DS, E&TC, Mechanical, Civil), placement coordinators, and T&P cell staff.

---

## 💻 2. Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom academic design system with light/dark glassmorphism, responsive grid), Vanilla JavaScript (ES6+).
- **Backend**: Python 3.14+, Flask 3.1+, REST API architecture.
- **AI Integration**: Official Google Gen AI Python SDK (`google-genai`), Google Gemini API (`GEMINI_MODEL=gemini-2.5-flash`).
- **Knowledge Base & RAG**: Structured FAQ repository (`faqs.json`), verified policy documents (`.txt`, `.pdf`, `.md`), and keyword passage retriever.
- **Testing**: `pytest` automated test suite with mocked Gemini responses.

---

## 📁 3. Project Directory Structure

```
placement-cell-assistant/
├── app.py                      # Main Flask Web Server & REST API routes
├── config.py                   # Secure configuration manager & status helper
├── requirements.txt            # Python dependencies (Flask, google-genai, pypdf, etc.)
├── .env.example                # Template for environment variables
├── .env                        # Private environment variables (git-ignored)
├── .gitignore                  # Git exclusions (.env, .venv, uploads/, cache)
├── README.md                   # Complete system documentation & presentation guide
├── knowledge_base/
│   ├── faqs.json               # Structured verified and illustrative FAQs
│   ├── README.md               # Staff guidelines for adding circulars/notices
│   └── verified_docs/          # Official documents (.txt, .pdf, .md)
│       ├── placement_policy_guidelines.txt
│       ├── resume_interview_prep.txt
│       └── campus_recruitment_process.txt
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # Official google-genai SDK wrapper & fallback logic
│   └── knowledge_service.py    # Text parsing, chunking, and passage retrieval
├── templates/
│   └── index.html              # Modern academic chat UI template
├── static/
│   ├── css/
│   │   └── style.css           # Academic CSS design system (Light/Dark themes)
│   └── js/
│       └── app.js              # Interactive chat JS logic & API client
├── tests/
│   ├── __init__.py
│   ├── test_chat.py            # Flask route & input validation tests
│   ├── test_knowledge.py       # Knowledge retrieval unit tests
│   └── test_gemini.py          # Gemini service & offline fallback unit tests
└── uploads/                    # Upload directory for authorized documents
```

---

## 🔒 4. Gemini API Configuration & Security Rules

1. **Environment Configuration**:
   Create a `.env` file from `.env.example` in the root directory:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

2. **Security Safeguards**:
   - The `.env` file is excluded from git via `.gitignore`.
   - The server loads keys via `python-dotenv` and `os.getenv`.
   - The API key is **never sent to the frontend**.
   - Raw stack traces, request headers with secrets, and API key values are stripped from error logs and health checks.
   - The `/api/health` endpoint returns a masked status check (e.g. `AIKey...****`).

---

## ⚡ 5. Windows PowerShell Setup & Run Instructions

Follow these exact commands in **Windows PowerShell** inside VS Code:

### Step 1: Create & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure `.env` File
```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```
*(Open `.env` in VS Code and paste your secret `GEMINI_API_KEY=...`)*

### Step 4: Run Automated Test Suite
```powershell
.\.venv\Scripts\pytest -v
```

### Step 5: Run the Flask Application
```powershell
.\.venv\Scripts\python.exe app.py
```
Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 6. Test Suite & Verification Results

All 14 automated unit tests pass cleanly:
- ✅ `test_homepage_loads`: Homepage renders with title & branding.
- ✅ `test_health_endpoint_no_secrets`: Returns sanitized system health without leaking API secrets.
- ✅ `test_faqs_endpoint`: Returns FAQ list for UI card generation.
- ✅ `test_chat_empty_input_rejected`: 400 Bad Request on empty payload.
- ✅ `test_chat_whitespace_only_rejected`: Rejects whitespace messages.
- ✅ `test_chat_overlength_input_rejected`: Rejects messages exceeding length limit.
- ✅ `test_chat_valid_placement_query`: Returns grounded response with source citations.
- ✅ `test_chat_unknown_institutional_query`: Returns honest fallback when company details are unverified.
- ✅ `test_gemini_service_offline_fallback`: Intelligent fallback when API key is missing.
- ✅ `test_gemini_service_mocked_live_call`: Validates `google-genai` SDK response structure.
- ✅ `test_knowledge_base_loading`: Verifies FAQ & document indexing.
- ✅ `test_faq_search_match`: Verifies term match against document checklist FAQ.
- ✅ `test_document_policy_search_match`: Verifies policy retrieval.
- ✅ `test_no_match_returns_empty_or_low_score`: Filters out irrelevant queries.

---

## 🚀 7. Production Deployment Readiness

When deploying for production:
1. **WSGI Server**: Use a production server such as `gunicorn` or `waitress` instead of Flask's debug server:
   ```powershell
   python -m pip install waitress
   waitress-serve --port=5000 app:app
   ```
2. **Reverse Proxy & HTTPS**: Deploy behind Nginx or Cloudflare with SSL certificates to enforce HTTPS.
3. **Environment Secrets**: Set `GEMINI_API_KEY` directly in server environment variables or secret vaults.
4. **Rate Limiting**: Enable rate limiting middleware (e.g. `Flask-Limiter`) to prevent API abuse.

---

## 📝 8. Institutional Items Requiring Verification

The following items are marked as **requiring verification** and must be updated by authorized SNJB T&P staff before production release:
1. Exact annual drive schedules, company eligibility CGPA cutoffs, and bond terms for upcoming recruiting companies.
2. Official contact details and room numbers of the Head of Training & Placement Cell.
3. Official SNJB T&P logo graphics file (if authorized for UI branding).

---

## 🎓 9. How to Present & Defend This Project in College

When presenting this project to professors, external examiners, or T&P coordinators:
1. **Architecture Overview**: Explain the 3-tier structure (Vanilla JS Frontend -> Flask REST API -> Gemini AI / Local Passage Retriever).
2. **Anti-Hallucination Grounding**: Demonstrate how the prompt system instruction combined with local passage retrieval prevents the AI from inventing false placement statistics or company packages.
3. **Graceful Fallback**: Demonstrate that the chatbot operates seamlessly in **Offline Knowledge Base mode** even when no API key or internet is available.
4. **Security & Standards**: Highlight that `.env` secrets are kept strictly server-side, inputs are sanitized, and all code follows PEP8 standards.
