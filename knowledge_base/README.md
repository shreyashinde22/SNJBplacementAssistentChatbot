# SNJB Placement Cell Assistant - Knowledge Base Management

This directory contains the verified institutional knowledge base used by the AI Placement Assistant to provide accurate, grounded responses to engineering students.

## Directory Structure

- `faqs.json`: Structured FAQ repository containing standard placement questions, verified answers, and illustrative examples.
- `verified_docs/`: Authorized official college policy documents, drive notices, syllabus roadmaps, and preparation guides (`.txt`, `.pdf`, `.md`, `.json`).

## How Authorized Staff Can Add or Update Information

### 1. Adding/Updating FAQs in `faqs.json`
Open `faqs.json` and add a new JSON object following this format:
```json
{
  "id": "faq-009",
  "category": "Placement Policy",
  "question": "What is the policy for internship NOC?",
  "answer": "Students requiring an No Objection Certificate (NOC) for off-campus internships must submit their company offer letter to the T&P Cell for Dean/Principal approval.",
  "is_verified": true,
  "source": "SNJB T&P Internship Policy Circular 2025"
}
```

### 2. Adding Official Circulars & Drive Notices
Upload or copy authorized `.txt`, `.pdf`, or `.md` files directly into `knowledge_base/verified_docs/`.
The Knowledge Service will automatically parse and index these documents on server startup or next query.

> **Important Security & Privacy Notice:**
> - Never store confidential student records, passwords, or personal identity numbers in `verified_docs/`.
> - Only upload public or student-facing recruitment notices.
