import json
import re
from pathlib import Path
from typing import List, Dict, Any
from config import Config

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class KnowledgeService:
    """Service to load, index, and retrieve relevant verified FAQs and placement documents."""

    def __init__(self):
        self.faqs: List[Dict[str, Any]] = []
        self.documents: List[Dict[str, Any]] = []
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Loads FAQs and scans verified documents directory."""
        self._load_faqs()
        self._load_verified_docs()

    def _load_faqs(self):
        """Loads faqs.json file."""
        faq_path = Config.FAQS_FILE
        if faq_path.exists():
            try:
                with open(faq_path, 'r', encoding='utf-8') as f:
                    self.faqs = json.load(f)
            except Exception as e:
                print(f"[KnowledgeService] Error loading faqs.json: {e}")
                self.faqs = []
        else:
            self.faqs = []

    def _load_verified_docs(self):
        """Loads and extracts text chunks from verified_docs directory."""
        docs_dir = Config.VERIFIED_DOCS_DIR
        self.documents = []

        if not docs_dir.exists():
            return

        for file_path in docs_dir.glob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                doc_name = file_path.name

                if ext in ['.txt', '.md', '.markdown']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            text = f.read()
                            chunks = self._chunk_text(text)
                            for chunk in chunks:
                                self.documents.append({
                                    "content": chunk,
                                    "source": doc_name,
                                    "is_verified": True,
                                    "type": "document"
                                })
                    except Exception as e:
                        print(f"[KnowledgeService] Failed to read text file {doc_name}: {e}")

                elif ext == '.pdf' and PYPDF_AVAILABLE:
                    try:
                        reader = pypdf.PdfReader(str(file_path))
                        pdf_text = ""
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                pdf_text += text + "\n"
                        chunks = self._chunk_text(pdf_text)
                        for chunk in chunks:
                            self.documents.append({
                                "content": chunk,
                                "source": doc_name,
                                "is_verified": True,
                                "type": "document"
                            })
                    except Exception as e:
                        print(f"[KnowledgeService] Failed to read PDF {doc_name}: {e}")

    def _chunk_text(self, text: str, max_words: int = 250) -> List[str]:
        """Splits long text into manageable passages/paragraphs for retrieval."""
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        chunks = []
        current_chunk = []
        current_word_count = 0

        for para in paragraphs:
            words = para.split()
            word_count = len(words)

            if current_word_count + word_count <= max_words:
                current_chunk.append(para)
                current_word_count += word_count
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_word_count = word_count

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks if chunks else [text]

    def _tokenize(self, text: str) -> set:
        """Tokenizes text into normalized lowercase alphanumeric words."""
        words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', text.lower())
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'for',
            'of', 'or', 'by', 'with', 'from', 'be', 'this', 'that', 'it', 'are',
            'what', 'how', 'where', 'can', 'should', 'do', 'does', 'i', 'you', 'we'
        }
        return {w for w in words if w not in stop_words}

    def search_knowledge(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Searches FAQs and documents for relevant matches based on query terms.
        Returns top matches sorted by relevance score.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        results = []

        # 1. Search FAQs
        for faq in self.faqs:
            q_text = faq.get('question', '')
            a_text = faq.get('answer', '')
            combined = f"{q_text} {a_text}"
            doc_tokens = self._tokenize(combined)

            if not doc_tokens:
                continue

            matches = query_tokens.intersection(doc_tokens)
            score = len(matches) / len(query_tokens)

            # Boost if tokens match in the question specifically
            q_tokens = self._tokenize(q_text)
            q_matches = query_tokens.intersection(q_tokens)
            if q_matches:
                score += (len(q_matches) / len(query_tokens)) * 0.5

            if score > 0.15:
                results.append({
                    "content": f"Q: {q_text}\nA: {a_text}",
                    "source": faq.get('source', 'SNJB Placement FAQ'),
                    "is_verified": faq.get('is_verified', True),
                    "score": round(score, 3),
                    "type": "faq"
                })

        # 2. Search Documents
        for doc in self.documents:
            content = doc.get('content', '')
            doc_tokens = self._tokenize(content)

            if not doc_tokens:
                continue

            matches = query_tokens.intersection(doc_tokens)
            score = len(matches) / len(query_tokens)

            if score > 0.15:
                results.append({
                    "content": content,
                    "source": doc.get('source', 'Verified Document'),
                    "is_verified": doc.get('is_verified', True),
                    "score": round(score, 3),
                    "type": "document"
                })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]

    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Returns all loaded FAQs."""
        return self.faqs
