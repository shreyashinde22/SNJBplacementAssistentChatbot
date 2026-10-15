import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from services.knowledge_service import KnowledgeService
from services.gemini_service import GeminiService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload directory exists
os.makedirs(Config.UPLOADS_DIR, exist_ok=True)
os.makedirs(Config.VERIFIED_DOCS_DIR, exist_ok=True)

# Initialize Services
knowledge_service = KnowledgeService()
gemini_service = GeminiService()


@app.route('/')
def index():
    """Renders the main SNJB Placement Cell Assistant frontend."""
    return render_template('index.html', config=Config.get_sanitized_status())


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main Chat API Endpoint.
    Expects JSON payload: { "message": str, "history": list (optional) }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Invalid request. 'message' field is required."
            }), 400

        user_message = str(data['message']).strip()
        chat_history = data.get('history', [])

        # Input Validation & Length Check
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty."
            }), 400

        if len(user_message) > Config.MAX_MESSAGE_LENGTH:
            return jsonify({
                "success": False,
                "error": f"Message exceeds maximum allowed limit of {Config.MAX_MESSAGE_LENGTH} characters."
            }), 400

        # Step 1: Retrieve relevant passages from Knowledge Service
        passages = knowledge_service.search_knowledge(user_message, max_results=3)

        # Step 2: Generate answer using Gemini Service or Fallback
        response_data = gemini_service.generate_response(
            user_message=user_message,
            chat_history=chat_history,
            retrieved_passages=passages
        )

        return jsonify(response_data), 200

    except Exception as e:
        print(f"[app.py] Exception in /api/chat: {e}")
        return jsonify({
            "success": False,
            "error": "An internal server error occurred. Please try again later.",
            "reply": "Sorry, an internal error occurred while processing your request. Please try again."
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Returns application health and configuration status without exposing secrets."""
    status_info = Config.get_sanitized_status()
    status_info["faq_count"] = len(knowledge_service.faqs)
    status_info["doc_count"] = len(knowledge_service.documents)
    status_info["server_status"] = "running"
    return jsonify(status_info), 200


@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Returns list of placement FAQs for frontend quick-cards."""
    faqs = knowledge_service.get_all_faqs()
    return jsonify({
        "success": True,
        "count": len(faqs),
        "faqs": faqs
    }), 200


@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """Tests live connection to Google Gemini API securely."""
    success, message = gemini_service.test_connection()
    return jsonify({
        "success": success,
        "message": message,
        "model": Config.GEMINI_MODEL,
        "is_configured": Config.is_gemini_configured()
    }), 200 if success else 400


@app.route('/api/upload-doc', methods=['POST'])
def upload_doc():
    """
    Endpoint allowing staff to upload placement documents (.txt, .pdf, .md).
    Documents are saved to verified_docs directory and indexed immediately.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded."}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file."}), 400

        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ['.txt', '.pdf', '.md']:
            return jsonify({"success": False, "error": "Unsupported file format. Use .txt, .pdf, or .md"}), 400

        save_path = Config.VERIFIED_DOCS_DIR / filename
        file.save(save_path)

        # Reload knowledge base
        knowledge_service.load_knowledge_base()

        return jsonify({
            "success": True,
            "message": f"Document '{filename}' uploaded and indexed successfully.",
            "doc_count": len(knowledge_service.documents)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting SNJB Placement Cell Assistant Server on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
