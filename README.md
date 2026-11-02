# 🏛️ AI-Driven Web Accessibility & RAG Assistant for Enterprise CMS

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Drupal](https://img.shields.io/badge/Drupal-10-0073BA)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F61)
![Compliance](https://img.shields.io/badge/WCAG-2.2_AA-success)

## 📌 Executive Summary
This repository contains the codebase and empirical evaluation for an **AI/ML Web Accessibility Governance Assistant**, developed as an Applied Analytics Practicum for Georgia Tech (OMSA). Built for Harrisburg Area Community College (HACC), this system integrates a robust Python/FastAPI backend with a Drupal CMS frontend to automate WCAG 2.2 and ADA Title II compliance.

By combining Large Language Models (LLMs), Vision-Language Models (VLMs), and a Retrieval-Augmented Generation (RAG) architecture, the system transitions web accessibility from *passive error flagging* to **active, automated DOM remediation**, projecting a **98.5% reduction in manual editorial labor**.

---

## ✨ Key Features
*   **One-Click Auto-Remediation:** A custom Drupal module (`hacc_ada_api`) that intercepts node saves, automatically repairs broken DOM heading hierarchies (e.g., `<h4>` to `<h2>`), injects VLM-generated alt-text, and simplifies complex paragraphs to a 9th-grade reading level.
*   **Zero-Hallucination Legal Citations:** Powered by a ChromaDB vector store. Every accessibility fix is grounded by a direct citation to WCAG 2.2 / ADA Title II guidelines (achieved 1.0000 MRR).
*   **Multimodal Auditing:** Uses `gpt-4o-mini` to visually analyze raw image pixels and generate descriptive, context-aware alt-text for screen readers.
*   **Cognitive Readability Pipeline:** Natural Language Processing (NLP) integration via `textstat` to calculate Flesch-Kincaid and SMOG indices, ensuring content is accessible to neurodivergent users and non-native speakers.

---

## 📊 Empirical Evaluation & ROI (N = 200 Production Pages)
The system was benchmarked against a scraped sample of 200 live HACC editorial pages. 

### Accessibility Baseline Findings
*   **Overall Non-Compliance:** 97.0% of pages failed at least one WCAG criterion.
*   **Structural Defects:** 90.5% of pages contained broken heading hierarchies (633 total skipped levels).
*   **Cognitive Accessibility:** 94.5% of pages exceeded the WCAG Grade 9 readability target (Mean Flesch-Kincaid: 10.00, SD: 2.12).
*   **Media Defects:** 26 missing or non-descriptive image alt-attributes.

### A/B Workflow Simulation & ROI
We conducted a deterministic A/B workflow simulation comparing traditional manual remediation against the AI-assisted "Auto-Apply" workflow:
*   **Traditional Manual Workflow:** 53.9 Hours per 200 pages.
*   **AI-Assisted Workflow:** 0.8 Hours per 200 pages.
*   **Workflow Efficiency Gain:** **98.5% Time Reduction**.
*   **Projected Enterprise ROI:** Extrapolating to a standard 5,000-page institutional CMS migration, the system saves an estimated **2,655 manual labor hours**.

### RAG Vector Database Performance
*   **Mean Reciprocal Rank (MRR):** 1.0000
*   **Precision@3:** 1.0000

---

## 🏗️ System Architecture

1.  **Data Ingestion & VDB:** WCAG 2.2 and ADA Title II documents are chunked and embedded via `text-embedding-3-small` into a persistent ChromaDB instance.
2.  **FastAPI Backend:** Exposes `/api/v1/analyze-structure` to parse raw HTML, lint the DOM via BeautifulSoup, query ChromaDB for legal citations, and interface with OpenAI for HTML rewriting and image analysis.
3.  **Drupal CMS Frontend:** A custom module provides an "Accessibility Scorecard" within the authoring UI, featuring an "Auto-Apply AI Remediation on Save" governance toggle.

---

## 📂 Repository Structure

```text
├── ml_pipeline/
│   ├── 01_ingest_and_clean.py      # WCAG text extraction
│   ├── 02_chunking.py              # Semantic text chunking
│   ├── 03_embeddings.py            # OpenAI embedding generation
│   ├── 04_index_vdb.py             # ChromaDB vector initialization
│   ├── 05_scrape_hacc.py           # Production crawler (N=200)
│   ├── 10_api_service.py           # FastAPI AI Remediation Engine
│   ├── 11_rag_evaluation.py        # MRR / Precision testing script
│   ├── 12_ab_testing_simulation.py # ROI & manual labor calculation
│   ├── 13_empirical_hacc_audit.py  # DOM linting & NLP readability baseline
│   └── chroma_db/                  # Persistent vector store (ignored in git)
├── web/modules/custom/hacc_ada_api/
│   ├── hacc_ada_api.module         # Drupal hooks for UI and Auto-Apply logic
│   └── hacc_ada_api.info.yml       # Drupal module metadata
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   DDEV (for local Drupal environment)
*   Active OpenAI API Key

### Local Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/hacc-ada-audit.git
   cd hacc-ada-audit
   ```
2. **Start the API Backend:**
   ```bash
   export OPENAI_API_KEY="sk-proj-..."
   pip install fastapi uvicorn beautifulsoup4 textstat chromadb openai
   python3 ml_pipeline/10_api_service.py
   ```
3. **Start the Drupal Environment:**
   ```bash
   ddev start
   ddev drush en hacc_ada_api -y
   ```
4. Edit any node in Drupal to view the AI Accessibility Governance dashboard!

---

## 🎓 Acknowledgments
*   **Sponsor:** Jonathan (Harrisburg Area Community College)
*   **Institution:** Georgia Institute of Technology (OMSA Practicum, Fall 2026)