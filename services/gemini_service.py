import os
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from config import Config

# Import official google-genai SDK
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_INSTRUCTION = f"""You are the official Placement Cell AI Assistant for {Config.COLLEGE_NAME}, located in {Config.COLLEGE_LOCATION}.

YOUR MANDATE:
1. Provide accurate, professional, and student-friendly placement guidance.
2. Ground all institutional claims (eligibility rules, campus drive procedures, document checklists, college policies) strictly in the VERIFIED CONTEXT provided below.
3. NEVER fabricate or invent college-specific placement statistics, drive dates, salary packages, recruiter lists, or contact details for SNJB.
4. IF a student asks about a specific company or college policy and the information is NOT present in the provided verified context, clearly inform them:
   "This institutional detail has not yet been verified in official SNJB T&P records. Please confirm directly with the SNJB Training & Placement Cell."
5. You CAN generate helpful general career guidance, resume building tips, aptitude strategies, and technical interview advice, but keep institutional policies strictly grounded.
6. Present all answers clearly using Markdown headers, lists, bold text, and code blocks where appropriate.
"""


class GeminiService:
    """Service wrapping Google Gemini API with fallback and strict grounding."""

    FALLBACK_MODELS = ['gemini-3.5-flash', 'gemini-3.8-flash', 'gemini-3.6-flash']

    def __init__(self):
        load_dotenv(override=True)
        self.api_key = os.getenv('GEMINI_API_KEY', '').strip()
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash').strip()
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes the official google-genai client if API key is present."""
        load_dotenv(override=True)
        self.api_key = os.getenv('GEMINI_API_KEY', '').strip()
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash').strip()

        if self.api_key and len(self.api_key) > 5 and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiService] Error initializing client: {e}")
                self.client = None
        else:
            self.client = None

    def test_connection(self) -> Tuple[bool, str]:
        """Tests live API connection without exposing secret key."""
        self._init_client()
        if not self.api_key:
            return False, "GEMINI_API_KEY is missing in environment (.env)."
        if not GENAI_AVAILABLE:
            return False, "google-genai SDK is not installed."

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]

        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents="Respond with the word 'OK' for connection test."
                )
                if response and response.text:
                    self.model_name = model
                    return True, f"Live connection successful! Model '{model}' responded."
            except Exception as e:
                err_msg = str(e)
                if self.api_key and self.api_key in err_msg:
                    err_msg = err_msg.replace(self.api_key, "[REDACTED_KEY]")
                print(f"[GeminiService] test_connection failed for model '{model}': {err_msg[:120]}")
                continue

        return False, "Gemini API request failed for configured model and fallbacks."

    def generate_response(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]] = None,
        retrieved_passages: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generates response using Gemini API or offline fallback."""
        if self.client is None and self.api_key:
            self._init_client()
        sources = []
        is_verified = True
        context_str = ""

        if retrieved_passages:
            context_str = "\n\n--- VERIFIED KNOWLEDGE BASE CONTEXT ---\n"
            for idx, item in enumerate(retrieved_passages, 1):
                src = item.get('source', 'SNJB Reference')
                content = item.get('content', '')
                verified_flag = item.get('is_verified', True)
                if src not in sources:
                    sources.append(src)
                if not verified_flag:
                    is_verified = False
                context_str += f"\n[Passage {idx} | Source: {src} | Verified: {verified_flag}]\n{content}\n"
            context_str += "---------------------------------------\n"

        prompt = f"{SYSTEM_INSTRUCTION}\n{context_str}\nStudent Question: {user_message}"

        if not self.api_key or not self.client:
            return self._generate_offline_fallback(user_message, retrieved_passages, sources)

        contents_payload = []
        if chat_history:
            for msg in chat_history[-6:]:
                role = "user" if msg.get("sender") == "user" else "model"
                contents_payload.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.get("text", ""))]
                ))

        contents_payload.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))

        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1500,
        )

        models_to_try = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]

        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents_payload,
                    config=config
                )

                if response and response.text:
                    reply_text = response.text.strip()
                    return {
                        "success": True,
                        "reply": reply_text,
                        "sources": sources,
                        "is_verified": is_verified,
                        "mode": "gemini_live",
                        "model": model,
                        "disclaimer": "Official SNJB policies and drive deadlines must be confirmed through official T&P circulars."
                    }
            except Exception as e:
                err_str = str(e)
                if self.api_key in err_str:
                    err_str = err_str.replace(self.api_key, "[REDACTED_KEY]")
                print(f"[GeminiService] Model '{model}' call failed: {err_str[:120]}")
                continue

        # If all models fail, return offline fallback cleanly
        return self._generate_offline_fallback(user_message, retrieved_passages, sources)

    def _generate_offline_fallback(
        self,
        user_message: str,
        retrieved_passages: List[Dict[str, Any]],
        sources: List[str]
    ) -> Dict[str, Any]:
        """Offline fallback response."""
        if retrieved_passages:
            best_passage = retrieved_passages[0]
            reply = f"### Verified Information from SNJB Placement Records\n\n"
            reply += f"{best_passage.get('content')}\n\n"
            reply += f"**Source Reference:** `{best_passage.get('source')}`\n\n"
            if len(retrieved_passages) > 1:
                reply += "### Additional Relevant Details\n"
                for p in retrieved_passages[1:]:
                    reply += f"- **{p.get('source')}**: {p.get('content')[:180]}...\n"

            return {
                "success": True,
                "reply": reply,
                "sources": sources,
                "is_verified": True,
                "mode": "knowledge_fallback",
                "disclaimer": "Operating in Offline Knowledge Base mode."
            }

        msg_lower = user_message.lower()
        if any(kw in msg_lower for kw in ['resume', 'cv', 'bio']):
            reply = """### SNJB General CV & Resume Guidance

1. **Format**: Single page, ATS-friendly layout in PDF format.
2. **Sections**: Contact Info, Objective, Academic Details (SNJB COE, CGPA), Core Skills, Projects, Internships, Extra-curriculars.
3. **Key Advice**: Highlight final year and mini engineering projects with exact tech stacks used."""
        else:
            reply = """### SNJB Placement Cell Assistant

I could not find a verified record matching your specific question in the local knowledge repository. For official company drive updates or eligibility criteria, please contact the **Head of Training & Placement Cell, SNJB COE, Chandwad**."""

        return {
            "success": True,
            "reply": reply,
            "sources": sources,
            "is_verified": False,
            "mode": "offline_fallback",
            "disclaimer": "Operating in Offline Mode."
        }
