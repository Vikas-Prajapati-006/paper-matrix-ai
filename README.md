# PaperMatrix AI 📄⚡

> Production-grade Literature Review Matrix & Synthesis Engine for Academic Research.

PaperMatrix AI automates the tedious, multi-day manual effort of reading academic papers to generate literature survey tables for theses, capstone projects, and research papers.

---

## 🚀 Key Features

* **Smart Chunking:** PyMuPDF-driven in-memory parsing isolating Abstract, Methodology, Results, and Limitations without context bloat.
* **Ultra-Fast Synthesis:** Powered by Groq (`llama-3.3-70b-versatile`) with strict Pydantic JSON validation.
* **1-Click Exports:** Direct export to formatted Excel spreadsheets (`.xlsx`) and academic LaTeX tabular code (`.tex`).
* **Hardware Fingerprinting:** Abuse-resistant client credit rate limiting via Canvas/WebGL hashing and Redis.
* **Zero Overhead Frontend:** AstroJS server-first rendering with multi-language i18n (`en`, `es`, `pt`) and complete technical SEO markup.

---

## 🛠️ Architecture & Tech Stack

* **Frontend:** AstroJS 5, Tailwind CSS, TypeScript
* **Backend:** FastAPI, Python 3.10+, PyMuPDF, Pandas, OpenPyXL
* **LLM Engine:** Groq API (`llama-3.3-70b-versatile`)
* **Quota & State:** Redis / Upstash (Atomic Token Bucket)
* **Deployment:** Cloudflare Pages (Frontend) + Dockerized Container (Backend)

---

## 📦 Getting Started

### Prerequisites
* Python 3.10+
* Node.js 18+ (for frontend)
* Groq API Key

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/paper-matrix-ai.git
   cd paper-matrix-ai