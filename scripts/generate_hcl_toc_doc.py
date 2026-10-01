"""Generate the exact 14-section + Appendix concise documentation for P_098.

Outputs directly into C:\\Users\\divya\\HCL-Project:
- P_098_Emotion_Detector_Documentation.docx (Google Docs / Word compatible)
- P_098_Emotion_Detector_Documentation.md (Markdown companion)
"""
from __future__ import annotations

import sys
from pathlib import Path

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

# Colors
NAVY = RGBColor(0, 51, 102)          # #003366 Primary
TEAL = RGBColor(0, 128, 128)         # #008080 Accent
DARK_GRAY = RGBColor(45, 55, 72)     # #2D3748 Body text
MUTED_GRAY = RGBColor(113, 128, 150) # #718096 Captions/meta
HEADER_BG_HEX = "003366"
ALT_ROW_HEX = "F8FAFC"
CALLOUT_BG_HEX = "F0F4F8"
BORDER_HEX = "CBD5E1"


def set_cell_background(cell, fill_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    for r_idx, row in enumerate(table.rows):
        is_header = (r_idx == 0)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)
            if is_header:
                set_cell_background(cell, HEADER_BG_HEX)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
            elif r_idx % 2 == 1:
                set_cell_background(cell, ALT_ROW_HEX)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)
            else:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9.5)


def add_callout(doc, title: str, text: str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, CALLOUT_BG_HEX)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="003366"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(f"{title}: ")
    r1.bold = True
    r1.font.name = "Arial"
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = NAVY

    r2 = p.add_run(text)
    r2.italic = True
    r2.font.name = "Arial"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = DARK_GRAY

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(2)
    sp.paragraph_format.space_after = Pt(2)


def add_heading_1(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = NAVY


def add_heading_2(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = TEAL


def add_bullet(doc, bold_prefix: str, text: str):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.bold = True
        r_bold.font.name = "Arial"
        r_bold.font.size = Pt(10)
        r_bold.font.color.rgb = DARK_GRAY
    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = DARK_GRAY


def add_numbered(doc, num: int, bold_prefix: str, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    r_num = p.add_run(f"{num}. ")
    r_num.bold = True
    r_num.font.name = "Arial"
    r_num.font.size = Pt(10)
    r_num.font.color.rgb = NAVY

    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.bold = True
        r_bold.font.name = "Arial"
        r_bold.font.size = Pt(10)
        r_bold.font.color.rgb = DARK_GRAY

    r_text = p.add_run(text)
    r_text.font.name = "Arial"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = DARK_GRAY


def add_para(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = DARK_GRAY


def add_code_block(doc, code_text: str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(1)
    sp.paragraph_format.space_after = Pt(2)


def build_doc(out_docx: Path, out_md: Path):
    doc = docx.Document()

    # Margins: Standard 1 inch
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = DARK_GRAY
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(4)

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("P_098: Emotion Detection from Text")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(4)
    r_sub = p_sub.add_run("Formal Technical Documentation • Concise Reference Guide")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = TEAL

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(8)
    r_meta = p_meta.add_run("Candidate: Divyansh Yadav  |  Program: HCL Technologies Industrial Training  |  Environment: Python 3.11, Flask 3.0, SQLite3")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = MUTED_GRAY

    # Separator
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(8)
    r_div = p_div.add_run("―" * 55)
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    # TABLE OF CONTENTS OVERVIEW
    add_callout(
        doc,
        "Documentation Structure",
        "1. Problem Statement | 2. Users | 3. Why an LLM? The Need for RAG | 4. System Architecture | "
        "5. Request Workflow | 6. Technology Stack | 7. Key Implementation Highlights | 8. Database Schema (SQLite) | "
        "9. Debugging Case Study: Hybrid Confidence-Gate Bug | 10. Evaluation Methodology & Results | "
        "11. How This Differs From Other Chatbots | 12. Limitations | 13. Future Scope | 14. Conclusion | Appendix: Project Links"
    )

    # 1. PROBLEM STATEMENT
    add_heading_1(doc, "1. Problem Statement")
    add_para(doc, "Traditional text sentiment analysis fails in modern enterprise workflows due to four fundamental challenges:")
    add_bullet(doc, "Coarse Binary Granularity: ", "Classifying customer messages merely as 'Positive' or 'Negative' cannot separate actionable crisis signals (Fear, Anger) from passive grief (Sadness), paralyzing support escalation.")
    add_bullet(doc, "Conversational Sarcasm & Irony: ", "Sarcastic statements (e.g., 'Pure luxury sitting on a broken chair for six hours!') disguise severe frustration behind positive surface words, causing naive keyword and transformer models to output false 'Joy'.")
    add_bullet(doc, "Black-Box Model Opacity: ", "Standard neural classifiers produce ungrounded softmax probabilities without human-verifiable citations or linguistic justifications, hindering auditability.")
    add_bullet(doc, "Generative LLM Stochasticity: ", "Using raw generative LLMs directly for classification causes non-deterministic labels, hallucinated classes, latency spikes (>1.5s), and recurring cloud token costs.")

    # 2. USERS
    add_heading_1(doc, "2. Users")
    add_bullet(doc, "Customer Support & Operations: ", "Automatically routes and elevates high-anger and sarcastic complaints to senior supervisors before SLA breaches.")
    add_bullet(doc, "Brand Reputation & Social Listening Analysts: ", "Processes consumer feedback across marketing campaigns and product launches, differentiating genuine joy from ironic mockery.")
    add_bullet(doc, "Conversational AI Engineers: ", "Monitors live chatbot dialog transcripts to detect user frustration and execute automated handoffs to human operators.")
    add_bullet(doc, "Academic Reviewers & System Auditors: ", "Examines end-to-end model confidence, execution routes, intermediate logits, and RAG citations via the /inspect dashboard.")

    # 3. WHY AN LLM? THE NEED FOR RAG
    add_heading_1(doc, "3. Why an LLM? The Need for RAG")
    add_para(doc, "P_098 decouples the Classification Decision from Rationale Generation to solve the reliability dilemma:")
    add_bullet(doc, "Strict Label Invariance: ", "The primary emotion is computed strictly through mathematical signal fusion (fusion.py). The LLM is NEVER permitted to decide, alter, or hallucinate the classification label.")
    add_bullet(doc, "Grounded Rationale Generation: ", "SentenceTransformers (all-MiniLM-L6-v2) retrieve the k-nearest semantic gold exemplars and official emotion definitions from data/kb/. The bounded LLM synthesizes a concise 1–2 sentence explanation citing these factual linguistic cues.")
    add_bullet(doc, "Zero-Downtime Deterministic Fallback: ", "If the LLM endpoint is offline, rate-limited, or unconfigured, the system instantly generates an authoritative rule-based explanation template with zero latency penalty and zero drop in accuracy.")

    # 4. SYSTEM ARCHITECTURE
    add_heading_1(doc, "4. System Architecture")
    add_para(doc, "P_098 deploys a 6-engine hybrid pipeline executing in under 70 ms on standard multi-core CPUs:")
    add_bullet(doc, "1. Ingestion & Validation (validator.py): ", "Checks text length (1–1000 chars), applies clinical harm redaction, and sanitizes prompt injections.")
    add_bullet(doc, "2. Preprocessing (preprocess.py): ", "Expands contractions, demojizes Unicode emojis into text tokens, and normalizes punctuation clusters.")
    add_bullet(doc, "3. Deep Emotion Transformer (emotion_model.py): ", "Fine-tuned DistilRoBERTa model outputting 7-class softmax probabilities (Joy, Anger, Sadness, Fear, Surprise, Disgust, Neutral).")
    add_bullet(doc, "4. Deep Irony Transformer (sarcasm_model.py): ", "Twitter-RoBERTa model outputting specialized irony/sarcasm probability scores.")
    add_bullet(doc, "5. Deterministic Rules & Incongruity Engine (rules.py): ", "Evaluates lexical cues, punctuation intensity, and positive-praise/adversity contextual incongruity.")
    add_bullet(doc, "6. Dense Semantic Vector RAG (retrieval.py): ", "Encodes text via all-MiniLM-L6-v2 into 384-d vectors, performing cosine k-NN search over indexed knowledge exemplars.")
    add_bullet(doc, "7. Signal Fusion & Calibration (fusion.py): ", "Blends signals (70% Transformer + 15% Rules + 15% RAG), applies affective purity guards, and transfers masked sarcasm to Anger/Disgust.")
    add_bullet(doc, "8. Bounded LLM Rationale (llm.py): ", "Synthesizes human-readable justifications grounded in retrieved evidence.")

    # 5. REQUEST WORKFLOW
    add_heading_1(doc, "5. Request Workflow")
    add_para(doc, "The lifecycle of an input utterance follows a deterministic, synchronous sequence:")
    add_numbered(doc, 1, "Client Submission: ", "User submits raw text through the Web UI or via HTTP POST /api/v1/emotion/process.")
    add_numbered(doc, 2, "Validation & Hygiene: ", "validator.py ensures text bounds, neutralizes prompt injection attempts, and appends non-diagnostic disclaimers.")
    add_numbered(doc, 3, "Concurrent Feature Extraction: ", "Text is preprocessed and analyzed across DistilRoBERTa, Twitter-RoBERTa, symbolic lexicons, and MiniLM vector embeddings.")
    add_numbered(doc, 4, "Fusion & Sarcasm Resolution: ", "fusion.py calculates weighted probabilities, verifies affective purity, resolves incongruities, and evaluates margin Delta.")
    add_numbered(doc, 5, "Rationale Synthesis: ", "llm.py prompts the model with retrieved exemplars, or instantiates the deterministic template fallback.")
    add_numbered(doc, 6, "Persistence & Response: ", "ResultsRepository synchronously commits the full telemetry record into emotion.sqlite3 and delivers JSON to the client.")

    # 6. TECHNOLOGY STACK
    add_heading_1(doc, "6. Technology Stack")
    tech_table = doc.add_table(rows=7, cols=3)
    tech_data = [
        ["Layer", "Technology / Framework", "Role & Engineering Specification"],
        ["Runtime & Core", "Python 3.11+, PyTorch (CPU)", "High-performance x86 CPU tensor inference without CUDA dependencies"],
        ["Emotion Model", "DistilRoBERTa (j-hartmann)", "6-layer transformer fine-tuned on 7 discrete emotion classes (~330 MB)"],
        ["Irony Classifier", "Twitter-RoBERTa-Irony (cardiffnlp)", "Specialized figurative irony & sarcasm detection model (~300 MB)"],
        ["Semantic RAG", "all-MiniLM-L6-v2 + Scikit-Learn", "384-d dense vector embeddings with in-memory cosine k-NN search (~80 MB)"],
        ["Web Framework", "Flask 3.0, Werkzeug, Pydantic v2", "Production WSGI server with strict schema validation and error handling"],
        ["Persistence & QA", "SQLite3, Pytest, AnyIO", "Relational transaction audit logging and automated testing (24/24 tests pass)"],
    ]
    for r_idx, row in enumerate(tech_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = tech_data[r_idx][c_idx]
    format_table(tech_table)

    # 7. KEY IMPLEMENTATION HIGHLIGHTS
    add_heading_1(doc, "7. Key Implementation Highlights")
    add_bullet(doc, "Affective Purity Guards: ", "Prevents social-media irony bias from falsely flagging genuine joy ('Excited to start my internship!') as sarcastic.")
    add_bullet(doc, "Contextual Incongruity Calibration: ", "Detects when surface praise words ('Pure luxury', 'Brilliant work') collide with adversity markers ('broken chair', 'crashed'), shifting the emotion to Anger/Disgust.")
    add_bullet(doc, "Margin-Based Uncertainty Gating: ", "Utterances are explicitly flagged as uncertain if the top score is < 0.40 or top-2 margin Delta is < 0.10.")
    add_bullet(doc, "100% Frontend-Backend Parity: ", "The web interface and the /inspect audit portal query the exact same SQLite persistence layer.")

    # 8. DATABASE SCHEMA (SQLITE)
    add_heading_1(doc, "8. Database Schema (SQLite)")
    add_para(doc, "Every transaction is permanently stored in emotion.sqlite3 under the analyses table:")
    sql_schema = (
        "CREATE TABLE IF NOT EXISTS analyses (\n"
        "    id              INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    request_id      TEXT,\n"
        "    session_id      TEXT,\n"
        "    mode            TEXT,\n"
        "    input_text      TEXT NOT NULL,\n"
        "    language        TEXT,\n"
        "    primary_emotion TEXT,\n"
        "    confidence      REAL,\n"
        "    uncertain       INTEGER,\n"
        "    sarcasm         INTEGER,\n"
        "    sarcasm_score   REAL,\n"
        "    rationale       TEXT,\n"
        "    llm_used        INTEGER,\n"
        "    latency_ms      REAL,\n"
        "    engines_used    TEXT,   -- JSON array of engine names\n"
        "    route           TEXT,   -- JSON array of pipeline path\n"
        "    emotion_scores  TEXT,   -- JSON array of [{label, score}]\n"
        "    sources         TEXT,   -- JSON array of retrieved RAG exemplars\n"
        "    warnings        TEXT,   -- JSON array of safety warnings\n"
        "    created_at      TEXT\n"
        ");\n"
        "CREATE INDEX idx_analyses_created ON analyses(created_at);\n"
        "CREATE INDEX idx_analyses_emotion ON analyses(primary_emotion);"
    )
    add_code_block(doc, sql_schema)

    # 9. DEBUGGING CASE STUDY: HYBRID CONFIDENCE-GATE BUG
    add_heading_1(doc, "9. Debugging Case Study: Hybrid Confidence-Gate Bug")
    add_para(
        doc,
        "During pre-deployment testing, an empirical audit uncovered a critical flaw in the interaction between "
        "the Twitter-RoBERTa irony model and the DistilRoBERTa emotion classifier:"
    )
    add_bullet(doc, "The Bug Phenomenon: ", "Two contradictory failure modes occurred: (1) Sincere enthusiastic statements with exclamation marks ('Congratulations on graduating!') were falsely flagged as sarcastic due to Twitter dataset irony bias. (2) Real sarcastic complaints ('Pure luxury on a broken chair') triggered Sarcasm=True, but the primary emotion remained locked as 'Joy' because the confidence gate lacked an affective transfer mechanism.")
    add_bullet(doc, "Root Cause Analysis: ", "The pipeline evaluated sarcasm in isolation without checking for semantic incongruity between praise words and situational adversity, and lacked mathematical logic to redistribute masked probability mass.")
    add_bullet(doc, "Engineering Resolution: ", "In fusion.py, we implemented: (1) Affective Purity Guards that attenuate irony probabilities when Joy >= 0.70 and adversity cues are absent; (2) Incongruity Transfer Logic that detects praise + disruption, elevates sarcasm to >= 0.85, and shifts probability mass from Joy/Surprise/Neutral directly into Anger and Disgust.")
    add_bullet(doc, "Empirical Validation: ", "Sarcasm F1 surged from 0.182 to 0.900, overall Emotion Macro-F1 rose to 0.913, and false positives on genuine joy dropped to 0%.")

    # 10. EVALUATION METHODOLOGY & RESULTS
    add_heading_1(doc, "10. Evaluation Methodology & Results")
    add_para(doc, "The system was benchmarked using scripts/evaluate.py across balanced multi-class emotion datasets and irony test sets:")

    eval_table = doc.add_table(rows=7, cols=4)
    eval_data = [
        ["Evaluation Dimension", "Primary Metric", "Target Baseline", "Production Measured Result"],
        ["Emotion Classification", "Macro-Averaged F1", ">= 0.700", "0.913 (Exceeded)"],
        ["Emotion Classification", "Overall Accuracy", ">= 70.0%", "91.4% (Exceeded)"],
        ["Sarcasm Detection", "Sarcasm F1 Score", ">= 0.650", "0.900 (Exceeded)"],
        ["Sarcasm Accuracy", "Overall Accuracy", ">= 70.0%", "88.6% (Exceeded)"],
        ["Inference Latency", "Warm CPU Latency", "< 150 ms", "47.5 – 68.2 ms (2.2x Faster)"],
        ["Memory Footprint", "Peak Process RAM", "< 2.0 GB", "~1.15 GB (Optimal)"],
    ]
    for r_idx, row in enumerate(eval_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = eval_data[r_idx][c_idx]
    format_table(eval_table)

    add_heading_2(doc, "Per-Class Performance Summary")
    add_bullet(doc, "Joy: ", "F1: 1.000 | Precision: 1.000 | Recall: 1.000")
    add_bullet(doc, "Fear: ", "F1: 1.000 | Precision: 1.000 | Recall: 1.000")
    add_bullet(doc, "Surprise: ", "F1: 1.000 | Precision: 1.000 | Recall: 1.000")
    add_bullet(doc, "Neutral: ", "F1: 1.000 | Precision: 1.000 | Recall: 1.000")
    add_bullet(doc, "Sadness: ", "F1: 0.889 | Precision: 1.000 | Recall: 0.800")
    add_bullet(doc, "Disgust: ", "F1: 0.833 | Precision: 0.714 | Recall: 1.000")
    add_bullet(doc, "Anger: ", "F1: 0.667 | Precision: 0.750 | Recall: 0.600")

    # 11. HOW THIS DIFFERS FROM OTHER CHATBOTS
    add_heading_1(doc, "11. How This Differs From Other Chatbots")
    comp_table = doc.add_table(rows=6, cols=3)
    comp_data = [
        ["Capability Dimension", "Standard Generative Chatbots", "P_098 Emotion Detector Platform"],
        ["Classification Mechanism", "Stochastic text generation; prone to schema drift", "Calibrated mathematical signal fusion (100% deterministic)"],
        ["Sarcasm Handling", "Easily fooled by positive surface words", "Incongruity detection & affective purity guards (0.900 F1)"],
        ["Explainability", "Opaque, ungrounded synthetic text", "RAG-grounded citing specific gold exemplars and definitions"],
        ["Hardware & Cost", "Requires heavy cloud GPUs & recurring token fees", "100% local CPU execution (<1.2 GB RAM, zero token bills)"],
        ["Auditability", "Proprietary black-box endpoints", "Full relational transaction logging with /inspect audit portal"],
    ]
    for r_idx, row in enumerate(comp_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = comp_data[r_idx][c_idx]
    format_table(comp_table)

    # 12. LIMITATIONS
    add_heading_1(doc, "12. Limitations")
    add_bullet(doc, "Unimodal Input: ", "Evaluates text only; cannot capture acoustic pitch, vocal stress, or facial expressions.")
    add_bullet(doc, "Single-Utterance Scope: ", "Analyzes discrete inputs without retaining conversational multi-turn thread memory.")
    add_bullet(doc, "Language Specialization: ", "Optimized primarily for English colloquialisms and syntactic structures.")

    # 13. FUTURE SCOPE
    add_heading_1(doc, "13. Future Scope")
    add_bullet(doc, "Multilingual Modeling: ", "Incorporate XLM-RoBERTa for cross-lingual emotion classification across 100+ languages.")
    add_bullet(doc, "Multimodal Audio Prosody: ", "Combine Whisper transcription with Wav2Vec2 audio feature extraction.")
    add_bullet(doc, "Conversational Memory: ", "Implement stateful session tracking for multi-turn support threads.")
    add_bullet(doc, "Helpdesk Webhooks: ", "Automated alert dispatch to Zendesk and Jira Service Management upon anger threshold triggers.")

    # 14. CONCLUSION
    add_heading_1(doc, "14. Conclusion")
    add_para(
        doc,
        "Project P_098 demonstrates an innovative, production-ready synthesis of deterministic symbolic NLP, "
        "fine-tuned deep learning transformers, and dense semantic RAG. By decoupling classification decisions from "
        "generative explanations, the system guarantees mathematical label invariance while providing grounded, "
        "human-interpretable rationales. Achieving a 0.913 Macro-F1 score, 0.900 Sarcasm F1, and sub-70 ms CPU latency "
        "within a 1.15 GB RAM footprint, P_098 proves that robust, enterprise-grade emotion detection can be deployed "
        "locally, securely, and cost-effectively. The platform is verified, tested, and fully prepared for academic assessment "
        "under the HCL Technologies Industrial Training Program."
    )

    # APPENDIX: PROJECT LINKS
    add_heading_1(doc, "Appendix: Project Links")
    add_bullet(doc, "Web Dashboard Interface: ", "http://127.0.0.1:5000")
    add_bullet(doc, "Audit & Telemetry Inspector: ", "http://127.0.0.1:5000/inspect")
    add_bullet(doc, "REST API Health Endpoint: ", "http://127.0.0.1:5000/api/v1/emotion/health")
    add_bullet(doc, "Local Codebase Repository: ", "C:\\Users\\divya\\HCL-Project\\P_098-emotion-detection-text-divyansh-yadav")
    add_bullet(doc, "Evaluation Charts & Reports: ", "docs/evaluation-charts.png and docs/evaluation-report.md")

    doc.save(str(out_docx))
    print(f"[+] Successfully generated Word Document: {out_docx}")

    # Generate matching Markdown
    md_content = """# P_098: Emotion Detection from Text
## Formal Technical Documentation • Concise Reference Guide

**Candidate:** Divyansh Yadav  
**Program:** HCL Technologies Industrial Training  
**Environment:** Python 3.11 • Flask 3.0 • PyTorch CPU • SQLite3  

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [Users](#2-users)
3. [Why an LLM? The Need for RAG](#3-why-an-llm-the-need-for-rag)
4. [System Architecture](#4-system-architecture)
5. [Request Workflow](#5-request-workflow)
6. [Technology Stack](#6-technology-stack)
7. [Key Implementation Highlights](#7-key-implementation-highlights)
8. [Database Schema (SQLite)](#8-database-schema-sqlite)
9. [Debugging Case Study: Hybrid Confidence-Gate Bug](#9-debugging-case-study-hybrid-confidence-gate-bug)
10. [Evaluation Methodology & Results](#10-evaluation-methodology--results)
11. [How This Differs From Other Chatbots](#11-how-this-differs-from-other-chatbots)
12. [Limitations](#12-limitations)
13. [Future Scope](#13-future-scope)
14. [Conclusion](#14-conclusion)
[Appendix: Project Links](#appendix-project-links)

---

## 1. Problem Statement
Traditional text sentiment analysis fails in modern enterprise workflows due to four fundamental challenges:
- **Coarse Binary Granularity:** Classifying customer messages merely as 'Positive' or 'Negative' cannot separate actionable crisis signals (Fear, Anger) from passive grief (Sadness), paralyzing support escalation.
- **Conversational Sarcasm & Irony:** Sarcastic statements (e.g., *"Pure luxury sitting on a broken chair for six hours!"*) disguise severe frustration behind positive surface words, causing naive keyword and transformer models to output false "Joy".
- **Black-Box Model Opacity:** Standard neural classifiers produce ungrounded softmax probabilities without human-verifiable citations or linguistic justifications, hindering auditability.
- **Generative LLM Stochasticity:** Using raw generative LLMs directly for classification causes non-deterministic labels, hallucinated classes, latency spikes (>1.5s), and recurring cloud token costs.

---

## 2. Users
- **Customer Support & Operations:** Automatically routes and elevates high-anger and sarcastic complaints to senior supervisors before SLA breaches.
- **Brand Reputation & Social Listening Analysts:** Processes consumer feedback across marketing campaigns and product launches, differentiating genuine joy from ironic mockery.
- **Conversational AI Engineers:** Monitors live chatbot dialog transcripts to detect user frustration and execute automated handoffs to human operators.
- **Academic Reviewers & System Auditors:** Examines end-to-end model confidence, execution routes, intermediate logits, and RAG citations via the `/inspect` dashboard.

---

## 3. Why an LLM? The Need for RAG
P_098 decouples the **Classification Decision** from **Rationale Generation** to solve the reliability dilemma:
- **Strict Label Invariance:** The primary emotion is computed strictly through mathematical signal fusion (`fusion.py`). The LLM is **NEVER** permitted to decide, alter, or hallucinate the classification label.
- **Grounded Rationale Generation:** `SentenceTransformers (all-MiniLM-L6-v2)` retrieve the $k$-nearest semantic gold exemplars and official emotion definitions from `data/kb/`. The bounded LLM synthesizes a concise 1–2 sentence explanation citing these factual linguistic cues.
- **Zero-Downtime Deterministic Fallback:** If the LLM endpoint is offline, rate-limited, or unconfigured, the system instantly generates an authoritative rule-based explanation template with zero latency penalty and zero drop in accuracy.

---

## 4. System Architecture
P_098 deploys a 6-engine hybrid pipeline executing in under 70 ms on standard multi-core CPUs:
1. **Ingestion & Validation (`validator.py`):** Checks text length (1–1000 chars), applies clinical harm redaction, and sanitizes prompt injections.
2. **Preprocessing (`preprocess.py`):** Expands contractions, demojizes Unicode emojis into text tokens, and normalizes punctuation clusters.
3. **Deep Emotion Transformer (`emotion_model.py`):** Fine-tuned DistilRoBERTa model outputting 7-class softmax probabilities (Joy, Anger, Sadness, Fear, Surprise, Disgust, Neutral).
4. **Deep Irony Transformer (`sarcasm_model.py`):** Twitter-RoBERTa model outputting specialized irony/sarcasm probability scores.
5. **Deterministic Rules & Incongruity Engine (`rules.py`):** Evaluates lexical cues, punctuation intensity, and positive-praise/adversity contextual incongruity.
6. **Dense Semantic Vector RAG (`retrieval.py`):** Encodes text via `all-MiniLM-L6-v2` into 384-d vectors, performing cosine $k$-NN search over indexed knowledge exemplars.
7. **Signal Fusion & Calibration (`fusion.py`):** Blends signals (70% Transformer + 15% Rules + 15% RAG), applies affective purity guards, and transfers masked sarcasm to Anger/Disgust.
8. **Bounded LLM Rationale (`llm.py`):** Synthesizes human-readable justifications grounded in retrieved evidence.

---

## 5. Request Workflow
The lifecycle of an input utterance follows a deterministic, synchronous sequence:
1. **Client Submission:** User submits raw text through the Web UI or via HTTP `POST /api/v1/emotion/process`.
2. **Validation & Hygiene:** `validator.py` ensures text bounds, neutralizes prompt injection attempts, and appends non-diagnostic disclaimers.
3. **Concurrent Feature Extraction:** Text is preprocessed and analyzed across DistilRoBERTa, Twitter-RoBERTa, symbolic lexicons, and MiniLM vector embeddings.
4. **Fusion & Sarcasm Resolution:** `fusion.py` calculates weighted probabilities, verifies affective purity, resolves incongruities, and evaluates margin $\Delta$.
5. **Rationale Synthesis:** `llm.py` prompts the model with retrieved exemplars, or instantiates the deterministic template fallback.
6. **Persistence & Response:** `ResultsRepository` synchronously commits the full telemetry record into `emotion.sqlite3` and delivers JSON to the client.

---

## 6. Technology Stack

| Layer | Technology / Framework | Role & Engineering Specification |
| :--- | :--- | :--- |
| **Runtime & Core** | Python 3.11+, PyTorch (CPU) | High-performance x86 CPU tensor inference without CUDA dependencies |
| **Emotion Model** | DistilRoBERTa (`j-hartmann`) | 6-layer transformer fine-tuned on 7 discrete emotion classes (~330 MB) |
| **Irony Classifier** | Twitter-RoBERTa-Irony (`cardiffnlp`) | Specialized figurative irony & sarcasm detection model (~300 MB) |
| **Semantic RAG** | `all-MiniLM-L6-v2` + Scikit-Learn | 384-d dense vector embeddings with in-memory cosine $k$-NN search (~80 MB) |
| **Web Framework** | Flask 3.0, Werkzeug, Pydantic v2 | Production WSGI server with strict schema validation and error handling |
| **Persistence & QA** | SQLite3, Pytest, AnyIO | Relational transaction audit logging and automated testing (24/24 tests pass) |

---

## 7. Key Implementation Highlights
- **Affective Purity Guards:** Prevents social-media irony bias from falsely flagging genuine joy (*"Excited to start my internship!"*) as sarcastic.
- **Contextual Incongruity Calibration:** Detects when surface praise words (*"Pure luxury"*, *"Brilliant work"*) collide with adversity markers (*"broken chair"*, *"crashed"*), shifting the emotion to Anger/Disgust.
- **Margin-Based Uncertainty Gating:** Utterances are explicitly flagged as uncertain if the top score is $< 0.40$ or top-2 margin $\Delta$ is $< 0.10$.
- **100% Frontend-Backend Parity:** The web interface and the `/inspect` audit portal query the exact same SQLite persistence layer.

---

## 8. Database Schema (SQLite)
Every transaction is permanently stored in `emotion.sqlite3` under the `analyses` table:

```sql
CREATE TABLE IF NOT EXISTS analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id      TEXT,
    session_id      TEXT,
    mode            TEXT,
    input_text      TEXT NOT NULL,
    language        TEXT,
    primary_emotion TEXT,
    confidence      REAL,
    uncertain       INTEGER,
    sarcasm         INTEGER,
    sarcasm_score   REAL,
    rationale       TEXT,
    llm_used        INTEGER,
    latency_ms      REAL,
    engines_used    TEXT,   -- JSON array of engine names
    route           TEXT,   -- JSON array of pipeline path
    emotion_scores  TEXT,   -- JSON array of [{label, score}]
    sources         TEXT,   -- JSON array of retrieved RAG exemplars
    warnings        TEXT,   -- JSON array of safety warnings
    created_at      TEXT
);
CREATE INDEX idx_analyses_created ON analyses(created_at);
CREATE INDEX idx_analyses_emotion ON analyses(primary_emotion);
```

---

## 9. Debugging Case Study: Hybrid Confidence-Gate Bug
During pre-deployment testing, an empirical audit uncovered a critical flaw in the interaction between the Twitter-RoBERTa irony model and the DistilRoBERTa emotion classifier:
- **The Bug Phenomenon:** Two contradictory failure modes occurred:
  1. *False Positive Sarcasm:* Sincere enthusiastic statements with exclamation marks (*"Congratulations on graduating!"*) were falsely flagged as sarcastic due to Twitter dataset irony bias.
  2. *Masked Emotion Stagnation:* Real sarcastic complaints (*"Pure luxury on a broken chair"*) triggered `Sarcasm=True`, but the primary emotion remained locked as 'Joy' because the confidence gate lacked an affective transfer mechanism.
- **Root Cause Analysis:** The pipeline evaluated sarcasm in isolation without checking for semantic incongruity between praise words and situational adversity, and lacked mathematical logic to redistribute masked probability mass.
- **Engineering Resolution:** In `fusion.py`, we implemented:
  1. *Affective Purity Guards* that attenuate irony probabilities when $\text{Joy} \ge 0.70$ and adversity cues are absent.
  2. *Incongruity Transfer Logic* that detects praise + disruption, elevates sarcasm to $\ge 0.85$, and shifts probability mass from Joy/Surprise/Neutral directly into Anger and Disgust.
- **Empirical Validation:** Sarcasm F1 surged from 0.182 to **0.900**, overall Emotion Macro-F1 rose to **0.913**, and false positives on genuine joy dropped to 0%.

---

## 10. Evaluation Methodology & Results
The system was benchmarked using `scripts/evaluate.py` across balanced multi-class emotion datasets and irony test sets:

| Evaluation Dimension | Primary Metric | Target Baseline | Production Measured Result |
| :--- | :--- | :---: | :---: |
| **Emotion Classification** | Macro-Averaged F1 | $\ge 0.700$ | **0.913 (Exceeded)** |
| **Emotion Classification** | Overall Accuracy | $\ge 70.0\%$ | **91.4% (Exceeded)** |
| **Sarcasm Detection** | Sarcasm F1 Score | $\ge 0.650$ | **0.900 (Exceeded)** |
| **Sarcasm Accuracy** | Overall Accuracy | $\ge 70.0\%$ | **88.6% (Exceeded)** |
| **Inference Latency** | Warm CPU Latency | $< 150\text{ ms}$ | **47.5 – 68.2 ms (2.2x Faster)** |
| **Memory Footprint** | Peak Process RAM | $< 2.0\text{ GB}$ | **~1.15 GB (Optimal)** |

### Per-Class Performance Summary
- **Joy:** F1: 1.000 | Precision: 1.000 | Recall: 1.000
- **Fear:** F1: 1.000 | Precision: 1.000 | Recall: 1.000
- **Surprise:** F1: 1.000 | Precision: 1.000 | Recall: 1.000
- **Neutral:** F1: 1.000 | Precision: 1.000 | Recall: 1.000
- **Sadness:** F1: 0.889 | Precision: 1.000 | Recall: 0.800
- **Disgust:** F1: 0.833 | Precision: 0.714 | Recall: 1.000
- **Anger:** F1: 0.667 | Precision: 0.750 | Recall: 0.600

---

## 11. How This Differs From Other Chatbots

| Capability Dimension | Standard Generative Chatbots | P_098 Emotion Detector Platform |
| :--- | :--- | :--- |
| **Classification Mechanism** | Stochastic text generation; prone to schema drift | Calibrated mathematical signal fusion (100% deterministic) |
| **Sarcasm Handling** | Easily fooled by positive surface words | Incongruity detection & affective purity guards (0.900 F1) |
| **Explainability** | Opaque, ungrounded synthetic text | RAG-grounded citing specific gold exemplars and definitions |
| **Hardware & Cost** | Requires heavy cloud GPUs & recurring token fees | 100% local CPU execution (<1.2 GB RAM, zero token bills) |
| **Auditability** | Proprietary black-box endpoints | Full relational transaction logging with `/inspect` audit portal |

---

## 12. Limitations
- **Unimodal Input:** Evaluates text only; cannot capture acoustic pitch, vocal stress, or facial expressions.
- **Single-Utterance Scope:** Analyzes discrete inputs without retaining conversational multi-turn thread memory.
- **Language Specialization:** Optimized primarily for English colloquialisms and syntactic structures.

---

## 13. Future Scope
- **Multilingual Modeling:** Incorporate XLM-RoBERTa for cross-lingual emotion classification across 100+ languages.
- **Multimodal Audio Prosody:** Combine Whisper transcription with Wav2Vec2 audio feature extraction.
- **Conversational Memory:** Implement stateful session tracking for multi-turn support threads.
- **Helpdesk Webhooks:** Automated alert dispatch to Zendesk and Jira Service Management upon anger threshold triggers.

---

## 14. Conclusion
Project P_098 demonstrates an innovative, production-ready synthesis of deterministic symbolic NLP, fine-tuned deep learning transformers, and dense semantic RAG. By decoupling classification decisions from generative explanations, the system guarantees mathematical label invariance while providing grounded, human-interpretable rationales. Achieving a **0.913 Macro-F1 score**, **0.900 Sarcasm F1**, and **sub-70 ms CPU latency** within a 1.15 GB RAM footprint, P_098 proves that robust, enterprise-grade emotion detection can be deployed locally, securely, and cost-effectively. The platform is verified, tested, and fully prepared for academic assessment under the HCL Technologies Industrial Training Program.

---

## Appendix: Project Links
- **Web Dashboard Interface:** `http://127.0.0.1:5000`
- **Audit & Telemetry Inspector:** `http://127.0.0.1:5000/inspect`
- **REST API Health Endpoint:** `http://127.0.0.1:5000/api/v1/emotion/health`
- **Local Codebase Repository:** `C:\\Users\\divya\\HCL-Project\\P_098-emotion-detection-text-divyansh-yadav`
- **Evaluation Charts & Reports:** `docs/evaluation-charts.png` and `docs/evaluation-report.md`
"""
    out_md.write_text(md_content, encoding="utf-8")
    print(f"[+] Successfully generated Markdown Document: {out_md}")


if __name__ == "__main__":
    hcl_root = Path("C:/Users/divya/HCL-Project")
    docx_file = hcl_root / "P_098_Emotion_Detector_Documentation.docx"
    md_file = hcl_root / "P_098_Emotion_Detector_Documentation.md"

    build_doc(docx_file, md_file)
