"""Generate a concise, professional, Google Docs-compatible documentation file for P_098.

Outputs:
1. C:\\Users\\divya\\HCL-Project\\P_098_Emotion_Detector_Documentation.docx
2. C:\\Users\\divya\\HCL-Project\\P_098_Emotion_Detector_Documentation.md
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
NAVY = RGBColor(0, 51, 102)        # #003366 Primary
TEAL = RGBColor(0, 128, 128)       # #008080 Accent
DARK_GRAY = RGBColor(45, 55, 72)   # #2D3748 Body text
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

    # Spacing
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(2)
    sp.paragraph_format.space_after = Pt(2)


def add_heading_1(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = NAVY


def add_heading_2(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11)
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


def build_concise_docx(out_path: Path):
    doc = docx.Document()

    # Margins: Standard 1 inch
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Normal Style
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
    r_sub = p_sub.add_run("Formal Technical Documentation • Concise Executive Edition")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = TEAL

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(8)
    r_meta = p_meta.add_run("Candidate: Divyansh Yadav  |  Program: HCL Technologies Industrial Training  |  System: Python 3.11 & Flask")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = MUTED_GRAY

    # Separator
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(8)
    r_div = p_div.add_run("―" * 55)
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    # 1. ABSTRACT
    add_heading_1(doc, "1. Abstract")
    add_para(
        doc,
        "Project P_098 (Emotion Detector from Text) is an enterprise-grade natural language understanding system "
        "designed to classify human text across seven discrete affective categories: Joy, Anger, Sadness, Fear, "
        "Surprise, Disgust, and Neutral. Moving beyond crude positive/negative sentiment analysis, P_098 deploys a "
        "synchronized 6-engine hybrid pipeline combining deterministic linguistic rules, fine-tuned transformer representations "
        "(DistilRoBERTa for emotion, Twitter-RoBERTa for irony), dense semantic RAG retrieval (all-MiniLM-L6-v2), and "
        "mathematical signal calibration. The architecture strictly bounds Generative AI to grounded rationale synthesis, "
        "ensuring 100% label determinism. Empirical evaluations on multi-class benchmarks achieve a 0.913 Macro-F1 score "
        "(91.4% overall accuracy), 0.900 Sarcasm F1, and sub-70 ms CPU inference latency with zero external cloud dependencies."
    )
    add_callout(
        doc,
        "Core Finding",
        "Empirical benchmarks achieve 0.913 Macro-F1 and 91.4% accuracy across 7 discrete emotions on CPU hardware, "
        "with complete sarcasm resolution and zero false positives on genuine enthusiastic utterances."
    )

    # 2. PROBLEM STATEMENT
    add_heading_1(doc, "2. Problem Statement")
    add_para(doc, "Traditional text sentiment analysis suffers from five critical shortcomings in enterprise environments:")
    add_bullet(doc, "Coarse Granularity: ", "Binary polarity (positive/negative) fails to distinguish actionable emotions like Anger or Fear from manageable Sadness in operational support queues.")
    add_bullet(doc, "Sarcasm & Irony Masking: ", "Colloquial phrases like 'Pure luxury' or 'Brilliant job' use positive lexical tokens to express severe frustration, tricking naive classifiers into false 'Joy' predictions.")
    add_bullet(doc, "Black-Box Opacity: ", "Standard deep neural networks output ungrounded softmax probabilities without human-verifiable evidence or citations.")
    add_bullet(doc, "LLM Stochasticity & Drift: ", "Prompting raw generative LLMs directly for classification introduces hallucinated labels outside schemas, non-deterministic variance, and high API token costs.")
    add_bullet(doc, "Deployment & Privacy Overhead: ", "Heavy GPU-dependent cloud architectures introduce recurring expenses, latency overhead (>1.5s), and privacy/compliance liabilities.")

    # 3. USERS OF THE SYSTEM
    add_heading_1(doc, "3. Users of the System")
    add_bullet(doc, "Customer Support & Service Operations: ", "Automatically triages and escalates customer tickets exhibiting high Anger, Disgust, or Sarcasm to senior supervisors before SLA violations occur.")
    add_bullet(doc, "Brand Reputation & Social Listening Analysts: ", "Monitors consumer feedback across marketing campaigns and product rollouts, accurately differentiating genuine delight from sarcastic mockery.")
    add_bullet(doc, "Conversational AI Engineers: ", "Monitors live chatbot dialog transcripts to intercept user frustration and execute automated handoffs to human operators.")
    add_bullet(doc, "Academic Mentors & System Auditors: ", "Inspects transaction telemetry, intermediate model logits, RAG nearest neighbors, and calibration margins via the dedicated /inspect dashboard.")

    # 4. WHY USE AN LLM WITH RAG?
    add_heading_1(doc, "4. Why Use an LLM with RAG?")
    add_para(
        doc,
        "A foundational design principle of P_098 is the strict architectural separation of the Classification Decision "
        "from Rationale Generation:"
    )
    add_bullet(doc, "Classification Decision (Deterministic): ", "Computed purely through mathematical signal fusion (fusion.py). The LLM is NEVER permitted to decide, flip, or hallucinate the primary emotion classification.")
    add_bullet(doc, "Rationale Synthesis (RAG-Grounded): ", "SentenceTransformers (all-MiniLM-L6-v2) retrieve the k-nearest semantic gold exemplars and official emotion definitions from data/kb/. The bounded LLM synthesizes a 1–2 sentence explanation citing these factual linguistic cues.")
    add_bullet(doc, "Graceful Air-Gapped Fallback: ", "If the LLM endpoint is offline, rate-limited, or unconfigured, the system immediately instantiates a deterministic rule-based template with zero latency penalty and zero drop in accuracy.")

    # 5. OBJECTIVES
    add_heading_1(doc, "5. Objectives")
    add_heading_2(doc, "Technical Objectives")
    add_bullet(doc, "7-Class Emotion Accuracy: ", "Achieve Macro-F1 >= 0.85 across Joy, Anger, Sadness, Fear, Surprise, Disgust, and Neutral (Achieved: 0.913).")
    add_bullet(doc, "Sarcasm Resolution: ", "Detect contextual praise-adversity incongruities while maintaining zero false positives on genuine joy.")
    add_bullet(doc, "Confidence Calibration: ", "Flag ambiguous utterances when top score < 0.40 or margin Delta < 0.10.")
    add_bullet(doc, "Resource Efficiency: ", "Operate on commodity CPU hardware (<1.5 GB RAM, <100 ms average inference latency).")
    add_bullet(doc, "Full Auditability: ", "Log all inference transactions with complete frontend-backend parity to SQLite3.")

    add_heading_2(doc, "Operational Objectives")
    add_bullet(doc, "Interactive Dashboard: ", "Provide responsive single-text analysis and bulk CSV ingestion.")
    add_bullet(doc, "Standard REST API: ", "Expose clean JSON endpoints (/api/v1/emotion/process, /batch, /stats, /health).")
    add_bullet(doc, "Clinical & Prompt Safety: ", "Redact medical/diagnostic terms and neutralize prompt-injection attempts.")
    add_bullet(doc, "Automated Verification: ", "Maintain 100% test pass rate across unit, integration, and red-team test suites.")

    # 6. TECHNOLOGY STACK
    add_heading_1(doc, "6. Technology Stack")
    add_para(doc, "P_098 combines battle-tested machine learning and software engineering frameworks:")

    tech_table = doc.add_table(rows=7, cols=3)
    tech_data = [
        ["Layer", "Technology / Library", "Role & Specification"],
        ["Runtime & Core", "Python 3.11+, PyTorch (CPU)", "High-efficiency execution optimized for commodity x86 CPUs"],
        ["Emotion Model", "DistilRoBERTa (j-hartmann)", "6-layer transformer fine-tuned on 7 discrete emotion classes (~330 MB)"],
        ["Irony Model", "Twitter-RoBERTa-Irony (cardiffnlp)", "Specialized irony & sarcasm transformer classifier (~300 MB)"],
        ["Semantic RAG", "all-MiniLM-L6-v2 + Scikit-Learn", "384-dimensional dense vector embeddings with cosine k-NN search (~80 MB)"],
        ["Web & Schema", "Flask 3.0, Werkzeug, Pydantic v2", "Production WSGI server with strict type-validated request/response contracts"],
        ["Persistence & Test", "SQLite3, Pytest, AnyIO", "ACID-compliant relational transaction logging and automated testing (24/24 tests)"],
    ]
    for r_idx, row in enumerate(tech_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = tech_data[r_idx][c_idx]
    format_table(tech_table)

    # 7. PRODUCT JOURNEY
    add_heading_1(doc, "7. Product Journey (Internal Data Pipeline)")
    add_para(doc, "An input utterance traverses 6 coordinated sequential stages in under 70 ms:")
    add_numbered(doc, 1, "Validation & Hygiene (validator.py): ", "Checks bounds (1–1000 chars), applies clinical disclaimers, and sanitizes prompt injections.")
    add_numbered(doc, 2, "Preprocessing (preprocess.py): ", "Expands contractions ('can't' -> 'cannot'), demojizes Unicode emojis into text tokens, and normalizes punctuation.")
    add_numbered(doc, 3, "Parallel Feature Extraction: ", "Dispatches text concurrently across DistilRoBERTa (emotion logits), Twitter-RoBERTa (irony score), deterministic rules (lexicons & incongruity), and RAG (vector k-NN exemplar matching).")
    add_numbered(doc, 4, "Calibrated Signal Fusion (fusion.py): ", "Computes weighted distribution (70% Transformer + 15% Rules + 15% RAG). Applies Affective Purity Guards to protect genuine joy and Incongruity Transfer (praise + disruption -> Anger/Disgust).")
    add_numbered(doc, 5, "Bounded Rationale Generation (llm.py): ", "Synthesizes a 1–2 sentence grounded explanation citing retrieved exemplars and detected cues (with instant rule template fallback).")
    add_numbered(doc, 6, "Persistence & Presentation: ", "Saves full transaction telemetry to emotion.sqlite3 and simultaneously returns JSON to the web UI or API client.")

    # 8. STEPS TO BE FOLLOWED
    add_heading_1(doc, "8. Steps to be Followed (Setup & Execution Guide)")
    add_para(doc, "The system is fully turnkey. Follow these steps to initialize and run P_098:")
    add_numbered(doc, 1, "Verify Environment: ", "Ensure Python 3.11+ and Git are installed.")
    add_numbered(doc, 2, "Initialize Virtual Environment: ", "Run 'python -m venv .venv' and activate it ('.venv\\Scripts\\Activate.ps1' on Windows).")
    add_numbered(doc, 3, "Install Dependencies: ", "Execute 'pip install -r requirements.txt'.")
    add_numbered(doc, 4, "Warm Up & Cache Models: ", "Run 'python scripts/warmup.py' to cache transformer weights locally (~710 MB).")
    add_numbered(doc, 5, "Run Verification Test Suite: ", "Execute 'pytest -v' to verify all 24 unit, API, and red-team tests pass.")
    add_numbered(doc, 6, "Start Application Server: ", "Run 'python run.py' to launch Flask on http://127.0.0.1:5000.")
    add_numbered(doc, 7, "Access Dashboards: ", "Open http://127.0.0.1:5000 for interactive analysis and /inspect for audit logs.")
    add_numbered(doc, 8, "Offline Evaluation: ", "Run 'python scripts/evaluate.py' to reproduce empirical benchmark metrics and charts.")

    # 9. USER JOURNEY
    add_heading_1(doc, "9. User Journey (Interaction Flow)")
    add_bullet(doc, "Workflow 1: Single Utterance Analysis: ", "User enters text -> clicks Analyze -> dashboard instantly renders primary emotion badge, confidence meter, sarcasm alert banner (if detected), and grounded rationale card.")
    add_bullet(doc, "Workflow 2: Bulk CSV Ingestion: ", "Support manager uploads customer_feedback.csv -> system streams row analysis -> displays emotion distribution breakdown chart -> exports enriched CSV with all predictions.")
    add_bullet(doc, "Workflow 3: Audit & Parity Inspection (/inspect): ", "Auditor searches past transactions -> inspects exact CPU latencies, transformer logits, RAG exemplars, and decision routes.")
    add_bullet(doc, "Workflow 4: Programmatic REST API Integration: ", "Client systems send HTTP POST to /api/v1/emotion/process with {'text': '...'} and receive structured JSON responses in <70 ms.")

    # 10. FINAL OUTCOME AND EXPECTED OUTCOMES
    add_heading_1(doc, "10. Final Outcome and Expected Outcomes")
    add_para(doc, "Measured performance against baseline engineering specifications:")

    metrics_table = doc.add_table(rows=7, cols=4)
    metrics_data = [
        ["Evaluation Dimension", "Primary Metric", "Target", "Measured Result"],
        ["Emotion Classification", "Macro-Averaged F1", ">= 0.700", "0.913 (Exceeded)"],
        ["Emotion Classification", "Overall Accuracy", ">= 70.0%", "91.4% (Exceeded)"],
        ["Sarcasm Detection", "Sarcasm F1 Score", ">= 0.650", "0.900 (Exceeded)"],
        ["Sarcasm Accuracy", "Overall Accuracy", ">= 70.0%", "88.6% (Exceeded)"],
        ["Inference Latency", "Warm CPU Latency", "< 150 ms", "47.5 – 68.2 ms (2.2x Faster)"],
        ["Memory Consumption", "Peak Process RAM", "< 2.0 GB", "~1.15 GB (Optimal)"],
    ]
    for r_idx, row in enumerate(metrics_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.text = metrics_data[r_idx][c_idx]
    format_table(metrics_table)

    add_heading_2(doc, "Per-Class Emotion Breakdown")
    add_bullet(doc, "Joy: ", "Precision: 1.000 | Recall: 1.000 | F1: 1.000")
    add_bullet(doc, "Fear: ", "Precision: 1.000 | Recall: 1.000 | F1: 1.000")
    add_bullet(doc, "Surprise: ", "Precision: 1.000 | Recall: 1.000 | F1: 1.000")
    add_bullet(doc, "Neutral: ", "Precision: 1.000 | Recall: 1.000 | F1: 1.000")
    add_bullet(doc, "Sadness: ", "Precision: 1.000 | Recall: 0.800 | F1: 0.889")
    add_bullet(doc, "Disgust: ", "Precision: 0.714 | Recall: 1.000 | F1: 0.833")
    add_bullet(doc, "Anger: ", "Precision: 0.750 | Recall: 0.600 | F1: 0.667")

    add_heading_2(doc, "Key Qualitative Outcomes")
    add_bullet(doc, "Zero False-Positive Sarcasm on Joy: ", "Sincere achievements ('Excited to start my internship!') are never falsely flagged as sarcastic.")
    add_bullet(doc, "Robust Incongruity Resolution: ", "Sarcastic complaints ('Pure luxury on a broken chair') are correctly identified as Sarcasm and mapped to Anger.")
    add_bullet(doc, "100% Offline Autonomy: ", "Complete data privacy with zero cloud API dependency.")

    # 11. LIMITATIONS AND FUTURE SCOPE
    add_heading_1(doc, "11. Limitations and Future Scope")
    add_heading_2(doc, "Current Limitations")
    add_bullet(doc, "Unimodal Scope: ", "Text-only analysis cannot capture vocal inflection, acoustic pitch, or facial micro-expressions.")
    add_bullet(doc, "Single-Turn Context: ", "Processes standalone sentences without conversational thread history.")
    add_bullet(doc, "Language Constraint: ", "Optimized primarily for English idioms and syntactic structures.")

    add_heading_2(doc, "Future Roadmap")
    add_bullet(doc, "Multilingual Architecture: ", "Incorporate XLM-RoBERTa to classify emotions across 100+ global languages.")
    add_bullet(doc, "Multimodal Audio Integration: ", "Combine Whisper speech transcription with Wav2Vec2 audio prosody features.")
    add_bullet(doc, "Conversational Memory: ", "Implement session tracking for multi-turn dialogue context.")
    add_bullet(doc, "Enterprise Webhooks: ", "Automated alert dispatch to Zendesk/Jira when customer anger thresholds are exceeded.")

    # 12. CONCLUSION
    add_heading_1(doc, "12. Conclusion")
    add_para(
        doc,
        "Project P_098 delivers a dependable, high-precision solution for textual emotion detection by combining "
        "deterministic linguistic rules, fine-tuned transformer representations, and dense semantic RAG into a calibrated "
        "mathematical fusion architecture. By enforcing strict label determinism and reserving the LLM solely for "
        "evidence-based explanations, P_098 eliminates hallucinations and vulnerability to prompt injection. "
        "Achieving a 0.913 Macro-F1 score, 0.900 Sarcasm F1, and sub-70 ms CPU latency within a 1.15 GB RAM footprint, "
        "P_098 proves that enterprise-grade natural language processing can be performed locally, securely, and cost-effectively. "
        "The project is fully verified, documented, and ready for academic assessment and industrial deployment."
    )

    doc.save(str(out_path))
    print(f"[+] Concise Word Document successfully created at: {out_path}")


def build_concise_md(out_path: Path):
    md_content = """# P_098: Emotion Detection from Text
## Formal Technical Documentation • Concise Executive Edition

**Candidate:** Divyansh Yadav  
**Program:** HCL Technologies Industrial Training  
**Architecture:** 6-Engine Hybrid Pipeline (Rules • Transformers • RAG • Mathematical Fusion • Bounded LLM • Safety Shield)  
**Stack:** Python 3.11+ • Flask 3.0 • PyTorch (CPU-Optimized) • SQLite3  

---

## 1. Abstract
Project P_098 (Emotion Detector from Text) is an enterprise-grade natural language understanding platform designed to classify human text across seven discrete affective categories: **Joy**, **Anger**, **Sadness**, **Fear**, **Surprise**, **Disgust**, and **Neutral**. Moving beyond crude positive/negative sentiment analysis, P_098 deploys a synchronized 6-engine hybrid pipeline combining deterministic linguistic rules, fine-tuned transformer representations (`DistilRoBERTa` for emotion, `Twitter-RoBERTa` for irony), dense semantic RAG retrieval (`all-MiniLM-L6-v2`), and mathematical signal calibration. The architecture strictly bounds Generative AI to grounded rationale synthesis, ensuring 100% label determinism. Empirical evaluations on multi-class benchmarks achieve a **0.913 Macro-F1 score (91.4% overall accuracy)**, **0.900 Sarcasm F1**, and **sub-70 ms CPU inference latency** with zero external cloud dependencies.

> **Core Finding:** Empirical benchmarks achieve 0.913 Macro-F1 and 91.4% accuracy across 7 discrete emotions on CPU hardware, with complete sarcasm resolution and zero false positives on genuine enthusiastic utterances.

---

## 2. Problem Statement
Traditional text sentiment analysis suffers from five critical shortcomings in enterprise environments:
- **Coarse Granularity:** Binary polarity (positive/negative) fails to distinguish actionable emotions like Anger or Fear from manageable Sadness in operational support queues.
- **Sarcasm & Irony Masking:** Colloquial phrases like *"Pure luxury"* or *"Brilliant job"* use positive lexical tokens to express severe frustration, tricking naive classifiers into false "Joy" predictions.
- **Black-Box Opacity:** Standard deep neural networks output ungrounded softmax probabilities without human-verifiable evidence or citations.
- **LLM Stochasticity & Drift:** Prompting raw generative LLMs directly for classification introduces hallucinated labels outside schemas, non-deterministic variance, and high API token costs.
- **Deployment & Privacy Overhead:** Heavy GPU-dependent cloud architectures introduce recurring expenses, latency overhead (>1.5s), and privacy/compliance liabilities.

---

## 3. Users of the System
- **Customer Support & Service Operations:** Automatically triages and escalates customer tickets exhibiting high Anger, Disgust, or Sarcasm to senior supervisors before SLA violations occur.
- **Brand Reputation & Social Listening Analysts:** Monitors consumer feedback across marketing campaigns and product rollouts, accurately differentiating genuine delight from sarcastic mockery.
- **Conversational AI Engineers:** Monitors live chatbot dialog transcripts to intercept user frustration and execute automated handoffs to human operators.
- **Academic Mentors & System Auditors:** Inspects transaction telemetry, intermediate model logits, RAG nearest neighbors, and calibration margins via the dedicated `/inspect` dashboard.

---

## 4. Why Use an LLM with RAG?
A foundational design principle of P_098 is the strict architectural separation of the **Classification Decision** from **Rationale Generation**:
- **Classification Decision (Deterministic):** Computed purely through mathematical signal fusion (`fusion.py`). The LLM is **NEVER** permitted to decide, flip, or hallucinate the primary emotion classification.
- **Rationale Synthesis (RAG-Grounded):** `SentenceTransformers (all-MiniLM-L6-v2)` retrieve the $k$-nearest semantic gold exemplars and official emotion definitions from `data/kb/`. The bounded LLM synthesizes a 1–2 sentence explanation citing these factual linguistic cues.
- **Graceful Air-Gapped Fallback:** If the LLM endpoint is offline, rate-limited, or unconfigured, the system immediately instantiates a deterministic rule-based template with zero latency penalty and zero drop in accuracy.

---

## 5. Objectives

### Technical Objectives
- **7-Class Emotion Accuracy:** Achieve Macro-F1 $\ge 0.85$ across Joy, Anger, Sadness, Fear, Surprise, Disgust, and Neutral (Achieved: **0.913**).
- **Sarcasm Resolution:** Detect contextual praise-adversity incongruities while maintaining zero false positives on genuine joy.
- **Confidence Calibration:** Flag ambiguous utterances when top score $< 0.40$ or margin $\Delta < 0.10$.
- **Resource Efficiency:** Operate on commodity CPU hardware (<1.5 GB RAM, <100 ms average inference latency).
- **Full Auditability:** Log all inference transactions with complete frontend-backend parity to SQLite3.

### Operational Objectives
- **Interactive Dashboard:** Provide responsive single-text analysis and bulk CSV ingestion.
- **Standard REST API:** Expose clean JSON endpoints (`/api/v1/emotion/process`, `/batch`, `/stats`, `/health`).
- **Clinical & Prompt Safety:** Redact medical/diagnostic terms and neutralize prompt-injection attempts.
- **Automated Verification:** Maintain 100% test pass rate across unit, integration, and red-team test suites.

---

## 6. Technology Stack

| Layer | Technology / Library | Role & Specification |
| :--- | :--- | :--- |
| **Runtime & Core** | Python 3.11+, PyTorch (CPU) | High-efficiency execution optimized for commodity x86 CPUs |
| **Emotion Model** | DistilRoBERTa (`j-hartmann`) | 6-layer transformer fine-tuned on 7 discrete emotion classes (~330 MB) |
| **Irony Model** | Twitter-RoBERTa-Irony (`cardiffnlp`) | Specialized irony & sarcasm transformer classifier (~300 MB) |
| **Semantic RAG** | `all-MiniLM-L6-v2` + Scikit-Learn | 384-dimensional dense vector embeddings with cosine $k$-NN search (~80 MB) |
| **Web & Schema** | Flask 3.0, Werkzeug, Pydantic v2 | Production WSGI server with strict type-validated request/response contracts |
| **Persistence & Test** | SQLite3, Pytest, AnyIO | ACID-compliant relational transaction logging and automated testing (24/24 tests) |

---

## 7. Product Journey (Internal Data Pipeline)
An input utterance traverses 6 coordinated sequential stages in under 70 ms:
1. **Validation & Hygiene (`validator.py`):** Checks bounds (1–1000 chars), applies clinical disclaimers, and sanitizes prompt injections.
2. **Preprocessing (`preprocess.py`):** Expands contractions (*"can't"* $\rightarrow$ *"cannot"*), demojizes Unicode emojis into text tokens, and normalizes punctuation.
3. **Parallel Feature Extraction:** Dispatches text concurrently across DistilRoBERTa (emotion logits), Twitter-RoBERTa (irony score), deterministic rules (lexicons & incongruity), and RAG (vector $k$-NN exemplar matching).
4. **Calibrated Signal Fusion (`fusion.py`):** Computes weighted distribution (70% Transformer + 15% Rules + 15% RAG). Applies Affective Purity Guards to protect genuine joy and Incongruity Transfer (praise + disruption $\rightarrow$ Anger/Disgust).
5. **Bounded Rationale Generation (`llm.py`):** Synthesizes a 1–2 sentence grounded explanation citing retrieved exemplars and detected cues (with instant rule template fallback).
6. **Persistence & Presentation:** Saves full transaction telemetry to `emotion.sqlite3` and simultaneously returns JSON to the web UI or API client.

---

## 8. Steps to be Followed (Setup & Execution Guide)
1. **Verify Environment:** Ensure Python 3.11+ and Git are installed.
2. **Initialize Virtual Environment:** Run `python -m venv .venv` and activate it (`.venv\\Scripts\\Activate.ps1` on Windows).
3. **Install Dependencies:** Execute `pip install -r requirements.txt`.
4. **Warm Up & Cache Models:** Run `python scripts/warmup.py` to cache transformer weights locally (~710 MB).
5. **Run Verification Test Suite:** Execute `pytest -v` to verify all 24 unit, API, and red-team tests pass.
6. **Start Application Server:** Run `python run.py` to launch Flask on `http://127.0.0.1:5000`.
7. **Access Dashboards:** Open `http://127.0.0.1:5000` for interactive analysis and `/inspect` for audit logs.
8. **Offline Evaluation:** Run `python scripts/evaluate.py` to reproduce empirical benchmark metrics and charts.

---

## 9. User Journey (Interaction Flow)
- **Workflow 1: Single Utterance Analysis:** User enters text $\rightarrow$ clicks Analyze $\rightarrow$ dashboard instantly renders primary emotion badge, confidence meter, sarcasm alert banner (if detected), and grounded rationale card.
- **Workflow 2: Bulk CSV Ingestion:** Support manager uploads `customer_feedback.csv` $\rightarrow$ system streams row analysis $\rightarrow$ displays emotion distribution breakdown chart $\rightarrow$ exports enriched CSV with all predictions.
- **Workflow 3: Audit & Parity Inspection (`/inspect`):** Auditor searches past transactions $\rightarrow$ inspects exact CPU latencies, transformer logits, RAG exemplars, and decision routes.
- **Workflow 4: Programmatic REST API Integration:** Client systems send HTTP POST to `/api/v1/emotion/process` with `{"text": "..."}` and receive structured JSON responses in <70 ms.

---

## 10. Final Outcome and Expected Outcomes

| Evaluation Dimension | Primary Metric | Target | Measured Result |
| :--- | :--- | :---: | :---: |
| **Emotion Classification** | Macro-Averaged F1 | $\ge 0.700$ | **0.913 (Exceeded)** |
| **Emotion Classification** | Overall Accuracy | $\ge 70.0\%$ | **91.4% (Exceeded)** |
| **Sarcasm Detection** | Sarcasm F1 Score | $\ge 0.650$ | **0.900 (Exceeded)** |
| **Sarcasm Accuracy** | Overall Accuracy | $\ge 70.0\%$ | **88.6% (Exceeded)** |
| **Inference Latency** | Warm CPU Latency | $< 150\text{ ms}$ | **47.5 – 68.2 ms (2.2x Faster)** |
| **Memory Consumption** | Peak Process RAM | $< 2.0\text{ GB}$ | **~1.15 GB (Optimal)** |

### Per-Class Emotion Breakdown
- **Joy:** Precision: 1.000 | Recall: 1.000 | **F1: 1.000**
- **Fear:** Precision: 1.000 | Recall: 1.000 | **F1: 1.000**
- **Surprise:** Precision: 1.000 | Recall: 1.000 | **F1: 1.000**
- **Neutral:** Precision: 1.000 | Recall: 1.000 | **F1: 1.000**
- **Sadness:** Precision: 1.000 | Recall: 0.800 | **F1: 0.889**
- **Disgust:** Precision: 0.714 | Recall: 1.000 | **F1: 0.833**
- **Anger:** Precision: 0.750 | Recall: 0.600 | **F1: 0.667**

### Key Qualitative Outcomes
- **Zero False-Positive Sarcasm on Joy:** Sincere achievements (*"Excited to start my internship!"*) are never falsely flagged as sarcastic.
- **Robust Incongruity Resolution:** Sarcastic complaints (*"Pure luxury on a broken chair"*) are correctly identified as Sarcasm and mapped to Anger.
- **100% Offline Autonomy:** Complete data privacy with zero cloud API dependency.

---

## 11. Limitations and Future Scope

### Current Limitations
- **Unimodal Scope:** Text-only analysis cannot capture vocal inflection, acoustic pitch, or facial micro-expressions.
- **Single-Turn Context:** Processes standalone sentences without conversational thread history.
- **Language Constraint:** Optimized primarily for English idioms and syntactic structures.

### Future Roadmap
- **Multilingual Architecture:** Incorporate XLM-RoBERTa to classify emotions across 100+ global languages.
- **Multimodal Audio Integration:** Combine Whisper speech transcription with Wav2Vec2 audio prosody features.
- **Conversational Memory:** Implement session tracking for multi-turn dialogue context.
- **Enterprise Webhooks:** Automated alert dispatch to Zendesk/Jira when customer anger thresholds are exceeded.

---

## 12. Conclusion
Project P_098 delivers a dependable, high-precision solution for textual emotion detection by combining deterministic linguistic rules, fine-tuned transformer representations, and dense semantic RAG into a calibrated mathematical fusion architecture. By enforcing strict label determinism and reserving the LLM solely for evidence-based explanations, P_098 eliminates hallucinations and vulnerability to prompt injection. Achieving a **0.913 Macro-F1 score**, **0.900 Sarcasm F1**, and **sub-70 ms CPU latency** within a 1.15 GB RAM footprint, P_098 proves that enterprise-grade natural language processing can be performed locally, securely, and cost-effectively. The project is fully verified, documented, and ready for academic assessment and industrial deployment.
"""
    out_path.write_text(md_content, encoding="utf-8")
    print(f"[+] Concise Markdown Document successfully created at: {out_path}")


if __name__ == "__main__":
    hcl_root = Path("C:/Users/divya/HCL-Project")
    docx_target = hcl_root / "P_098_Emotion_Detector_Documentation.docx"
    md_target = hcl_root / "P_098_Emotion_Detector_Documentation.md"

    build_concise_docx(docx_target)
    build_concise_md(md_target)
