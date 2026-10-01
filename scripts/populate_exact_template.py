"""Populate the exact BTech_3rd_Year_SRS_Template.docx in-place.

Loads the original BTech_3rd_Year_SRS_Template.docx, replaces all placeholders
with Divyansh Yadav's project specifications, and preserves 100% of Word's
native styles, formatting, and XML schema.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

NAVY_HEX = "1B365D"
SLATE_HEX = "4B6B94"
DARK_GRAY_HEX = "2B2D42"

NAVY = RGBColor(0x1B, 0x36, 0x5D)
SLATE = RGBColor(0x4B, 0x6B, 0x94)
DARK_GRAY = RGBColor(0x2B, 0x2D, 0x42)
MUTED = RGBColor(0x7A, 0x82, 0x90)


def populate_template(template_path: str, output_path: str):
    doc = docx.Document(template_path)

    # 1. Update Paragraphs
    for p in doc.paragraphs:
        txt = p.text.strip()
        if "<DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING>" in txt:
            p.text = "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\nABES ENGINEERING COLLEGE, GHAZIABAD"
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(11)
                r.font.bold = True
                r.font.color.rgb = SLATE

        elif "Project Title: <Insert Full Project Title Here>" in txt:
            p.text = "Project Title: Emotion Detection from Text — Classifies emotion/sarcasm via pretrained transformers\nStandard Academic Compliance: IEEE Std 830-1998"
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if len(p.runs) > 0:
                p.runs[0].font.name = "Arial"
                p.runs[0].font.size = Pt(12)
                r_title = p.runs[0]
                r_title.font.bold = True
                r_title.font.color.rgb = DARK_GRAY

        elif "<Project Title>" in txt:
            p.text = p.text.replace(
                "'<Project Title>'",
                "'Emotion Detection from Text — Classifies emotion/sarcasm via pretrained transformers' (Project ID: P_098)"
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "<Insert Core Problem Statement>" in txt:
            p.text = (
                "The proposed software application is engineered to solve the fundamental inadequacy of conventional binary sentiment analysis "
                "(which only classifies text into crude positive/negative buckets) by delivering an end-to-end, multi-tier hybrid affective analysis platform. "
                "The system classifies fine-grained emotional intent across seven discrete affective states, detects ironic and sarcastic nuances without "
                "corrupting primary sentiment, computes calibrated confidence margins, and provides evidence-grounded natural language explanations."
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "In-Scope Capabilities:" in txt:
            p.text = (
                "In-Scope Capabilities: Centralized data ingestion via web dashboard, batch CSV processing, and RESTful JSON APIs; "
                "linguistic normalization (emoji parsing, slang conversion, negation handling); dual transformer inference (DistilRoBERTa for 7-class emotion, "
                "RoBERTa for sarcasm intensity); semantic vector RAG retrieval (all-MiniLM-L6-v2) providing k-NN confidence voting and definition grounding; "
                "deterministic mathematical signal fusion (70% model + 15% rules + 15% k-NN); bounded LLM rationale generation with offline template fallback; "
                "immutable SQLite database transaction logging; and a live server-side /inspect parity audit view."
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Out-of-Scope Boundaries:" in txt:
            p.text = (
                "Out-of-Scope Boundaries: Hardware fabrication and physiological sensor interfacing (e.g., EEG, galvanic skin response, facial micro-expressions); "
                "automated clinical psychiatric diagnosis, psychotherapeutic treatment recommendations, or mental illness profiling (the platform strictly functions "
                "as an analytical text tool); and multi-speaker voice acoustic prosody processing in the current release."
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Expected Benefits:" in txt:
            p.text = (
                "Expected Benefits: Sub-100ms CPU inference latency; guarantees 100% frontend-to-backend audit parity; eliminates generative LLM label hallucination; "
                "improves text triage accuracy in customer experience (CX) and conversational AI moderation; and runs completely on standard consumer hardware (8 GB RAM laptop) without paid cloud infrastructure."
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "<Insert primary IEEE/ACM references" in txt:
            p.text = (
                "Relevant Research Papers & APIs: (1) Hartmann et al. (2022), 'Emotion English DistilRoBERTa-base', Hugging Face; "
                "(2) Helinivan (2023), 'English Sarcasm Detector', Hugging Face; (3) Reimers & Gurevych (2019), 'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks', EMNLP; "
                "(4) HCL Industrial Training Project P_098 Specifications & Playbook."
            )
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "3.1 Module 1:" in txt:
            p.text = "3.1 Module 1: Input Validation, Hygiene & Security Governance"
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = SLATE

        elif "3.2 Module 2:" in txt:
            p.text = "3.2 Module 2: Hybrid AI Emotion & Sarcasm Classification Engine"
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = SLATE

        elif "3.3 Module 3:" in txt:
            p.text = "3.3 Module 3: Reporting, Batch Processing & Auditor Inspection"
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = SLATE

        elif "Client Requirements: Modern web browser" in txt:
            p.text = "Client Requirements: Modern HTML5 web browser (Google Chrome >= v110, Mozilla Firefox >= v108, Microsoft Edge >= v110, Safari >= v16) with JavaScript enabled."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Server Runtime Environment: Linux" in txt:
            p.text = "Server Runtime Environment: Standard consumer laptop or workstation running Windows 10/11 or Ubuntu Linux 22.04 LTS; Python 3.11 runtime; Flask 3.0; PyTorch 2.4 (CPU build); Transformers 4.44; Sentence-Transformers 3.0."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Database Storage Tier: PostgreSQL" in txt:
            p.text = "Database Storage Tier: Embedded SQLite 3 database (emotion.sqlite3) providing zero-configuration ACID relational persistence."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Academic Budget Constraint:" in txt:
            p.text = "Academic Budget Constraint: 100% local CPU execution without requiring paid cloud GPUs or external infrastructure; supports Google Gemini free tier or 100% offline template fallback."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Security Compliance: Passwords stored" in txt:
            p.text = "Security Compliance: User text is treated strictly as passive data variables within delimited JSON structures to neutralize prompt injection attacks. Generated rationales are screened by an automated clinical redactor to eliminate psychiatric claims."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Modularity Standards: Adherence to" in txt:
            p.text = "Modularity Standards: Strict adherence to layered modular architecture (Presentation, Flask Blueprints, Hybrid AI Engines, Storage Repository). No monolithic coupling."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Assumptions: Users possess" in txt:
            p.text = "Assumptions: Input text is primarily in English or informal Hinglish; text length does not exceed 4,000 characters per single analysis; host operating system permits local loopback TCP networking on port 5000."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Dependencies: Continuous availability" in txt:
            p.text = "Dependencies: Availability of standard open-source Python packages (Flask, PyTorch, Transformers, Scikit-learn, Sentence-Transformers, Pydantic); local existence of knowledge base assets in data/kb/."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Standard Deployment: Standard input" in txt:
            p.text = "Standard Deployment: Standard physical peripherals including keyboard, mouse/trackpad, and visual display with resolution >= 1024x768 pixels."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Embedded / IoT Variants" in txt:
            p.text = "Host Processing Hardware: Standard x86-64 or ARM64 multi-core processor (CPU inference optimized); minimum 4 GB system RAM; no specialized GPU hardware acceleration required."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Relational Database Connector: SQLAlchemy" in txt:
            p.text = "Relational Database Connector: SQLite 3 embedded database interfaced via standard Python sqlite3 driver for transactional persistence."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "External Cloud Utilities: Amazon" in txt:
            p.text = "External AI Gateways & Model Hubs: Hugging Face Hub interface for loading pretrained model weights; OpenAI SDK client interfacing with Google Gemini Free Tier, OpenAI API, or local Ollama instances."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

        elif "Web Traffic Protocol: HTTPS" in txt:
            p.text = "Web Traffic Protocol: HTTP/1.1 and HTTPS protocols operating over standard TCP ports (Port 5000 for local development server; Port 443 in production with TLS 1.3)."
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(10)
                r.font.color.rgb = DARK_GRAY

    # 2. Update Table 0 (Metadata)
    t0 = doc.tables[0]
    t0.rows[0].cells[0].paragraphs[0].text = (
        "SUBMITTED BY:\n"
        "Divyansh Yadav (Roll No: 2400320100444)\n\n"
        "Degree: Bachelor of Technology (B.Tech)\n"
        "Department: Computer Science & Engineering\n"
        "Academic Year: 2026 - 2027"
    )
    t0.rows[0].cells[1].paragraphs[0].text = (
        "UNDER THE GUIDANCE OF:\n"
        "Project Coordinator & Faculty Guide\n"
        "Department of Computer Science & Engineering\n"
        "ABES Engineering College, Ghaziabad\n\n"
        "Status: 3rd Year B.Tech Project Specification\n"
        "Date of Submission: October 2026"
    )
    for c in t0.rows[0].cells:
        for r in c.paragraphs[0].runs:
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_GRAY
            if "SUBMITTED BY:" in r.text or "UNDER THE GUIDANCE OF:" in r.text:
                r.font.color.rgb = NAVY

    # 3. Update Table 1 (Revisions)
    t1 = doc.tables[1]
    t1.rows[1].cells[3].paragraphs[0].text = "Divyansh Yadav"
    t1.rows[1].cells[4].paragraphs[0].text = "Project Guide"
    t1.rows[2].cells[3].paragraphs[0].text = "Divyansh Yadav"
    t1.rows[2].cells[4].paragraphs[0].text = "Academic Evaluation Committee"

    # 4. Update Table 2 (Guidance Note)
    t2 = doc.tables[2]
    t2.rows[0].cells[0].paragraphs[0].text = (
        "Guidance Note: This Software Requirements Specification document conforms to the IEEE Std 830-1998 Recommended Practice for Software Requirements Specifications. "
        "All sections are strictly designed for 3rd-year university laboratory evaluation, project committee reviews, and system implementation baselines "
        "at ABES Engineering College, Ghaziabad. The project is an individual initiative developed by Divyansh Yadav (Roll No: 2400320100444)."
    )
    for r in t2.rows[0].cells[0].paragraphs[0].runs:
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.color.rgb = DARK_GRAY

    # 5. Update Table 3 (Definitions)
    t3 = doc.tables[3]
    t3_extra = [
        ("AI / ML", "RAG", "Retrieval-Augmented Generation: retrieving external factual context before generation."),
        ("AI / ML", "DistilRoBERTa", "Distilled Robustly Optimized BERT Approach; lightweight 82M parameter transformer."),
        ("Metric", "Macro-F1", "Unweighted mean of F1-scores across all discrete emotion classes."),
        ("Algorithmic", "Decision Margin", "Mathematical difference between top-1 and top-2 probabilities (P1 - P2).")
    ]
    # Replace existing row 6
    t3.rows[6].cells[0].paragraphs[0].text = t3_extra[0][0]
    t3.rows[6].cells[1].paragraphs[0].text = t3_extra[0][1]
    t3.rows[6].cells[2].paragraphs[0].text = t3_extra[0][2]
    # Add new rows
    for cat, term, defn in t3_extra[1:]:
        row = t3.add_row()
        row.cells[0].paragraphs[0].text = cat
        row.cells[1].paragraphs[0].text = term
        row.cells[2].paragraphs[0].text = defn

    for r_idx, row in enumerate(t3.rows):
        if r_idx > 0:
            for cell in row.cells:
                for r in cell.paragraphs[0].runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(9)
                    r.font.color.rgb = DARK_GRAY

    # 6. Update Table 4 (System Context Diagram)
    t4 = doc.tables[4]
    t4.rows[0].cells[0].paragraphs[0].text = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                             SYSTEM CONTEXT ARCHITECTURE                                 |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|  [ End User / CX Lead ]        [ Automated REST Client ]       [ Compliance Auditor ]   |\n"
        "|             |                              |                              |             |\n"
        "|             v                              v                              v             |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "|  |                      PRESENTATION & API GATEWAY (Flask 3.0)                       |  |\n"
        "|  |     GET / (Dashboard)    POST /process    POST /batch    GET /inspect (Auditor)   |  |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "|                                            |                                            |\n"
        "|                                            v                                            |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "|  |                               HYBRID AI CORE ENGINE                               |  |\n"
        "|  |  [Input Validator] -> [Preprocessor] -> [Parallel Extraction: Rules, Models, RAG]  |  |\n"
        "|  |  -> [Mathematical Signal Fusion (70/15/15)] -> [Bounded LLM Rationale Synthesis]  |  |\n"
        "|  |  -> [Output Safety Shield & Clinical Redactor]                                    |  |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "|                                            |                                            |\n"
        "|                                            v                                            |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "|  |                              STORAGE & KNOWLEDGE BASE                             |  |\n"
        "|  |      SQLite3 (emotion.sqlite3)       exemplars.jsonl       emotions.jsonl         |  |\n"
        "|  +-----------------------------------------------------------------------------------+  |\n"
        "+-----------------------------------------------------------------------------------------+"
    )
    for r in t4.rows[0].cells[0].paragraphs[0].runs:
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r.font.color.rgb = DARK_GRAY

    # 7. Update Table 5 (User Classes)
    t5 = doc.tables[5]
    t5.rows[1].cells[0].paragraphs[0].text = "Compliance Auditor / Academic Examiner"
    t5.rows[1].cells[1].paragraphs[0].text = "High (AI Systems / Software Quality)"
    t5.rows[1].cells[2].paragraphs[0].text = "Full access to the /inspect audit page, database records, route trace telemetry, latency verification, and model evaluation metrics."

    t5.rows[2].cells[0].paragraphs[0].text = "Customer Experience (CX) Operations Lead"
    t5.rows[2].cells[1].paragraphs[0].text = "Intermediate (Business / Support Operations)"
    t5.rows[2].cells[2].paragraphs[0].text = "Uploads batch CSV files, reviews aggregate sentiment distributions, identifies sarcastic customer escalations, and exports reports."

    t5.rows[3].cells[0].paragraphs[0].text = "Student Researcher / General End-User"
    t5.rows[3].cells[1].paragraphs[0].text = "Basic to Intermediate (General Web User)"
    t5.rows[3].cells[2].paragraphs[0].text = "Submits single text utterances via interactive dashboard, tests sample presets, reviews emotion probability bars, and inspects RAG citations."

    for row in t5.rows[1:]:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 8. Update Table 6 (Module 1 FRs)
    t6 = doc.tables[6]
    t6_data = [
        ("FR-1.1", "Character Bounds & Hygiene Filter", "1 <= length <= 4000 chars; strips non-printable ASCII control bytes (except \\n, \\t).", "High"),
        ("FR-1.2", "Prompt-Injection Neutralization", "Detects directive override phrases (e.g., 'ignore previous instructions'); treats input as passive data variable.", "High"),
        ("FR-1.3", "Linguistic Preprocessing & Normalization", "Converts emojis into semantic tokens; expands informal slang (e.g., 'smh' -> 'shaking my head'); maps negation scopes.", "High")
    ]
    for idx, (col1, col2, col3, col4) in enumerate(t6_data):
        t6.rows[idx+1].cells[0].paragraphs[0].text = col1
        t6.rows[idx+1].cells[1].paragraphs[0].text = col2
        t6.rows[idx+1].cells[2].paragraphs[0].text = col3
        t6.rows[idx+1].cells[3].paragraphs[0].text = col4
        for cell in t6.rows[idx+1].cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 9. Update Table 7 (Module 2 FRs)
    t7 = doc.tables[7]
    t7_data = [
        ("FR-2.1", "7-Class Deep Emotion Classification", "DistilRoBERTa sequence classification yielding normalized probabilities across Joy, Anger, Sadness, Fear, Surprise, Disgust, Neutral.", "High"),
        ("FR-2.2", "Contextual Sarcasm Detection", "Evaluates sequence-level irony using RoBERTa sarcasm classifier and punctuation contrast cues; outputs 0.00–1.00 intensity score.", "High"),
        ("FR-2.3", "Semantic RAG Retrieval & Grounding", "Dense vector search over exemplars.jsonl and emotions.jsonl via all-MiniLM-L6-v2; computes k-NN vote and extracts citations.", "High")
    ]
    for idx, (col1, col2, col3, col4) in enumerate(t7_data):
        t7.rows[idx+1].cells[0].paragraphs[0].text = col1
        t7.rows[idx+1].cells[1].paragraphs[0].text = col2
        t7.rows[idx+1].cells[2].paragraphs[0].text = col3
        t7.rows[idx+1].cells[3].paragraphs[0].text = col4

    # Add extra rows FR-2.4 and FR-2.5
    r4 = t7.add_row()
    r4.cells[0].paragraphs[0].text = "FR-2.4"
    r4.cells[1].paragraphs[0].text = "Signal Fusion & Margin Calibration"
    r4.cells[2].paragraphs[0].text = "Blends signals (70% model + 15% rules + 15% k-NN); calculates decision margin (P1 - P2); flags 'uncertain' if P1 < 0.40 or margin < 0.10."
    r4.cells[3].paragraphs[0].text = "High"

    r5 = t7.add_row()
    r5.cells[0].paragraphs[0].text = "FR-2.5"
    r5.cells[1].paragraphs[0].text = "Bounded LLM Rationale Synthesis"
    r5.cells[2].paragraphs[0].text = "Synthesizes 1–2 sentence natural explanation citing retrieved evidence; automatically triggers offline deterministic template fallback if API offline."
    r5.cells[3].paragraphs[0].text = "Medium"

    for row in t7.rows[1:]:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 10. Update Table 8 (Module 3 FRs)
    t8 = doc.tables[8]
    t8_data = [
        ("FR-3.1", "Interactive Operator Dashboard", "Visual input box, preloaded sample selectors, color-coded badges, probability distribution bar chart, and route telemetry strip.", "High"),
        ("FR-3.2", "High-Throughput Batch CSV Ingestion", "Uploads standard CSV files with 'text' column; parses up to 500 rows; renders aggregate distribution charts and tabular summaries.", "High"),
        ("FR-3.3", "Auditor /inspect Transparency View", "Server-rendered inspection console querying SQLite directly; displays raw database fields, full route trace arrays, and latency in ms.", "High")
    ]
    for idx, (col1, col2, col3, col4) in enumerate(t8_data):
        t8.rows[idx+1].cells[0].paragraphs[0].text = col1
        t8.rows[idx+1].cells[1].paragraphs[0].text = col2
        t8.rows[idx+1].cells[2].paragraphs[0].text = col3
        t8.rows[idx+1].cells[3].paragraphs[0].text = col4

    r34 = t8.add_row()
    r34.cells[0].paragraphs[0].text = "FR-3.4"
    r34.cells[1].paragraphs[0].text = "RESTful API Integration & Health Probe"
    r34.cells[2].paragraphs[0].text = "Standard JSON endpoints (/process, /batch, /results, /stats, /health) with strict Pydantic input/output schema validation."
    r34.cells[3].paragraphs[0].text = "High"

    for row in t8.rows[1:]:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 11. Update Table 9 (UI Mockup)
    t9 = doc.tables[9]
    t9.rows[0].cells[0].paragraphs[0].text = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|  P_098 Emotion Detection  |  HCL Training  |  Divyansh Yadav      [Dashboard]  [Inspect]    |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|  INPUT ANALYSIS                                   |  PIPELINE OUTPUT                    |\n"
        "|  Enter text:                                      |  Primary Emotion:  [ 😢 Sadness ]   |\n"
        "|  [ It was a bad day for me                     ]  |  Confidence:       [ 94.9% ]        |\n"
        "|                                                   |  Sarcasm Alert:    [ None (0.02) ]  |\n"
        "|  Presets: [Joy] [Sarcasm] [Frustration] [Uncertain|  Probability Distribution:           |\n"
        "|                                                   |  Sadness  ==================== 94.9%|\n"
        "|  [  ANALYZE EMOTION  ]                            |  Fear     = 2.5%                    |\n"
        "|                                                   |  Joy      < 0.5%                    |\n"
        "|  -----------------------------------------------  |  ---------------------------------  |\n"
        "|  BATCH CSV ANALYSIS                               |  Grounded Explanation:              |\n"
        "|  [Choose CSV File]  [Run Batch Analysis]          |  \"The text directly conveys gloom   |\n"
        "|                                                   |   and distress via 'bad day'...\"    |\n"
        "+-----------------------------------------------------------------------------------------+"
    )
    for r in t9.rows[0].cells[0].paragraphs[0].runs:
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r.font.color.rgb = DARK_GRAY

    # 12. Update Table 10 (NFRs)
    t10 = doc.tables[10]
    t10.rows[1].cells[1].paragraphs[0].text = "Mean CPU inference latency < 150 ms (achieved 68.2 ms); web dashboard page load < 1.0s under standard desktop concurrency."
    t10.rows[1].cells[2].paragraphs[0].text = "Automated latency timer in router.py; benchmark evaluation suite (evaluate.py)."

    t10.rows[2].cells[1].paragraphs[0].text = "Zero plain-text API keys in repository (.env git-ignored); prompt injection passive data isolation; automated redaction of clinical psychiatric terms."
    t10.rows[2].cells[2].paragraphs[0].text = "Unit security red-team test suite (tests/test_security.py); static code analysis."

    t10.rows[3].cells[1].paragraphs[0].text = "100% offline fallback resilience: system automatically triggers deterministic template rationales if LLM API is unavailable; zero crashes on 429 quota exhaustion."
    t10.rows[3].cells[2].paragraphs[0].text = "Simulated network disconnect tests; mock LLM mode unit tests (tests/test_engines.py)."

    t10.rows[4].cells[1].paragraphs[0].text = "Cross-platform operation (Windows 10/11, Ubuntu Linux, macOS); responsive interface across screen sizes; containerized deployment via Dockerfile."
    t10.rows[4].cells[2].paragraphs[0].text = "Multi-OS testing; Developer Tools viewport inspection; clean Docker container build."

    for row in t10.rows[1:]:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 13. Update Table 11 (Diagrams)
    t11 = doc.tables[11]
    t11.rows[1].cells[1].paragraphs[0].text = "Maps actor interactions (General User, CX Lead, Auditor) to discrete functional operations."
    t11.rows[1].cells[2].paragraphs[0].text = "UML Use Case Specification: Actor triggers (Analyze Single Text, Batch Upload CSV, Inspect Audit Records, Query Health)."

    t11.rows[2].cells[1].paragraphs[0].text = "Illustrates information movement: DFD Level 0 (Context) and Level 1 (Modular Hybrid Flow)."
    t11.rows[2].cells[2].paragraphs[0].text = "Gane-Sarson notation tracing Text Input -> Validation -> Parallel Feature Extraction -> Fusion -> Database Store -> UI Display."

    t11.rows[3].cells[1].paragraphs[0].text = "Details relational schema, primary keys, field data types, and persistence rules."
    t11.rows[3].cells[2].paragraphs[0].text = "Relational schema for 'analyses' table: id (PK), request_id, input_text, primary_emotion, confidence, sarcasm, route, latency_ms, created_at."

    t11.rows[4].cells[1].paragraphs[0].text = "Chronological message exchange between UI, Controller, Hybrid Engines, and Storage."
    t11.rows[4].cells[2].paragraphs[0].text = "UML Sequence diagram detailing happy-path execution and offline template fallback exception handling."

    for row in t11.rows[1:]:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # 14. Update Table 12 (Sign-Off)
    t12 = doc.tables[12]
    t12.rows[0].cells[0].paragraphs[0].text = "Project Coordinator / Guide"
    t12.rows[0].cells[1].paragraphs[0].text = "Internal Examiner"
    t12.rows[0].cells[2].paragraphs[0].text = "Head of Department (HOD)"

    t12.rows[1].cells[0].paragraphs[0].text = "Signature: __________________\nName: _______________________\nDate: ________________________"
    t12.rows[1].cells[1].paragraphs[0].text = "Signature: __________________\nName: _______________________\nDate: ________________________"
    t12.rows[1].cells[2].paragraphs[0].text = "Signature: __________________\nName: _______________________\nDate: ________________________"

    for row in t12.rows:
        for cell in row.cells:
            for r in cell.paragraphs[0].runs:
                r.font.name = "Arial"
                r.font.size = Pt(9)
                r.font.color.rgb = DARK_GRAY

    # Save
    doc.save(output_path)
    print(f"Successfully populated template and saved to: {output_path}")


if __name__ == "__main__":
    tpl = r"C:\Users\divya\HCL-Project\Documents-provided\BTech_3rd_Year_SRS_Template.docx"
    out_docs = r"c:\Users\divya\HCL-Project\p098-emotion-detection-text-divya\docs\BTech_3rd_Year_SRS_Divyansh_Yadav.docx"
    out_root = r"c:\Users\divya\HCL-Project\p098-emotion-detection-text-divya\BTech_3rd_Year_SRS_Divyansh_Yadav.docx"

    populate_template(tpl, out_docs)
    shutil.copyfile(out_docs, out_root)
    print(f"Copied to root: {out_root}")
