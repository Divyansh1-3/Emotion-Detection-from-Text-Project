"""Generate the official presentation deck for P_098 Emotion Detection from Text.

Produces:
    presentation/P098_Emotion_Detection.pptx

Follows the teacher's mandated demo structure:
1. Title & Project Overview
2. The Problem & End-User Personas
3. MVP Solution & Hybrid Architecture
4. The 6 Hybrid Engines (Rules, Models, RAG, Fusion, LLM, Validation)
5. Why RAG in Classification? (Grounding + Calibration)
6. Frontend <-> Backend Parity (/inspect & SQLite single source of truth)
7. Empirical Evaluation Results (Macro-F1, Accuracy, Sarcasm F1)
8. Edge Cases: Sarcasm Detection & Uncertainty Band
9. Safety Boundaries & Non-Diagnostic Limits
10. Production Deployment Roadmap & Key Takeaways

Usage:
    python scripts/build_presentation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


def add_slide_header(slide, title_text, category_text="HCL INDUSTRIAL TRAINING &bull; P_098"):
    # Header container
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(1.0))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = RGBColor(37, 99, 235)  # Primary blue

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(15, 23, 42)  # Dark slate


def add_bullet_point(tf, title, body, bold_title=True):
    p = tf.add_paragraph()
    p.space_after = Pt(12)
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(51, 65, 85)

    if bold_title:
        run_title = p.add_run()
        run_title.text = title + ": "
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(15, 23, 42)

    run_body = p.add_run()
    run_body.text = body


def build_deck(out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 1: Title Slide
    # ─────────────────────────────────────────────────────────────────────────
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.4), Inches(4.0))
    tf1 = bg1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "PROJECT P_098"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(37, 99, 235)

    p1 = tf1.add_paragraph()
    p1.text = "Emotion Detection from Text"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(15, 23, 42)
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "A Hybrid Multi-Engine NLP Architecture with Sarcasm Flagging and Calibrated Uncertainty"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(100, 116, 139)
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "Candidate: Divya  |  HCL Industrial Training  |  Backend: Flask & PyTorch Transformer"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(71, 85, 105)

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 2: Problem Statement & Industry Context
    # ─────────────────────────────────────────────────────────────────────────
    slide2 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide2, "1. Problem Statement & User Personas")
    box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf2 = box2.text_frame
    tf2.word_wrap = True

    add_bullet_point(tf2, "Affective Ambiguity", "Raw text often carries conflicting emotional markers, slang, and emojis that standard sentiment polarity (+/-) fails to resolve.")
    add_bullet_point(tf2, "The Sarcasm Trap", "Ironic utterances like 'Oh fantastic, another delayed flight' contain positive words but convey frustration; failing to detect sarcasm corrupts downstream metrics.")
    add_bullet_point(tf2, "Target Personas", "Customer Experience (CX) escalation triage, Social Listening Brand Analysts, and Voice-of-Customer conversational auditing.")
    add_bullet_point(tf2, "Core Objective", "Deliver a deterministic, explainable classification system across 7 discrete emotion labels + explicit sarcasm detection.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 3: Target Architecture: The 6 Hybrid Engines
    # ─────────────────────────────────────────────────────────────────────────
    slide3 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide3, "2. Target Architecture: The 6 Hybrid Engines")
    box3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf3 = box3.text_frame
    tf3.word_wrap = True

    add_bullet_point(tf3, "1. Rule Engine (rules.py)", "Deterministic emoji translation, slang normalization, contrast marker detection, and punctuation intensity analysis.")
    add_bullet_point(tf3, "2. Emotion Model (emotion_model.py)", "Pretrained DistilRoBERTa 7-class transformer (anger, disgust, fear, joy, neutral, sadness, surprise).")
    add_bullet_point(tf3, "3. Sarcasm Model (sarcasm_model.py)", "Specialized sarcasm transformer blended with punctuation contrast cues.")
    add_bullet_point(tf3, "4. Retrieval / RAG (retrieval.py)", "Semantic search over emotion knowledge base & exemplar corpus; yields k-NN vote + grounding evidence.")
    add_bullet_point(tf3, "5. Signal Fusion (fusion.py)", "Deterministic probability blending, margin calibration, and uncertainty calculation.")
    add_bullet_point(tf3, "6. Bounded LLM Rationale (llm.py)", "Generates grounded 1-2 sentence explanation; NEVER allowed to decide or flip labels.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 4: Deterministic Decision vs. Bounded LLM
    # ─────────────────────────────────────────────────────────────────────────
    slide4 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide4, "3. Deterministic Decision vs. Bounded Rationale")
    box4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf4 = box4.text_frame
    tf4.word_wrap = True

    add_bullet_point(tf4, "Anti-Hallucination Guardrail", "Classification decisions must be 100% reproducible and grounded in probabilistic model outputs, never in stochastic LLM generation.")
    add_bullet_point(tf4, "Bounded Explanations", "The LLM receives strictly: input utterance, predicted label, top score margin, and retrieved reference exemplars.")
    add_bullet_point(tf4, "Fallback Resilience", "If the OpenAI API is offline or unconfigured, the system immediately falls back to a deterministic rule-based template without breaking user experience.")
    add_bullet_point(tf4, "Structured JSON Contract", "LLM responds in verified JSON: { 'explanation': '...', 'confidence_reason': '...' } with auto-retry.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 5: Frontend <-> Backend Parity
    # ─────────────────────────────────────────────────────────────────────────
    slide5 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide5, "4. Single Source of Truth & /inspect Parity")
    box5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf5 = box5.text_frame
    tf5.word_wrap = True

    add_bullet_point(tf5, "True Parity Architecture", "The frontend computes zero metrics client-side. The backend executes the pipeline, persists the AnalysisResult to SQLite, and returns the response.")
    add_bullet_point(tf5, "Server-Rendered /inspect View", "Teachers and auditors can navigate to http://127.0.0.1:5000/inspect to review all persisted runs directly from the database.")
    add_bullet_point(tf5, "Full Execution Trace", "Every record stores the exact route taken (e.g. input_validation -> rules -> transformer -> fusion -> rationale), latency in ms, and grounding evidence.")
    add_bullet_point(tf5, "Structured Observability", "Structured JSON request logs written per transaction for production auditing.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 6: Empirical Evaluation Results
    # ─────────────────────────────────────────────────────────────────────────
    slide6 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide6, "5. Model Evaluation & Empirical Benchmark")
    box6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf6 = box6.text_frame
    tf6.word_wrap = True

    add_bullet_point(tf6, "Macro-F1 Emotion Score", "Exceeds the 0.70 project threshold on gold evaluation dataset across all 7 emotions.")
    add_bullet_point(tf6, "Sarcasm F1 Score", "Achieves robust precision/recall on ironic customer utterances with strong punctuation contrast.")
    add_bullet_point(tf6, "Latency Performance", "Mean CPU latency < 100 ms per text, enabling real-time interactive usage on standard 8 GB laptops.")
    add_bullet_point(tf6, "Reproducible Script", "Full benchmark re-generated via python scripts/evaluate.py with auto-generated charts and markdown reports.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 7: Hard Cases: Sarcasm & Uncertainty Calibration
    # ─────────────────────────────────────────────────────────────────────────
    slide7 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide7, "6. Hard Edge Cases: Sarcasm & Uncertainty")
    box7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf7 = box7.text_frame
    tf7.word_wrap = True

    add_bullet_point(tf7, "Sarcasm Handling Rule", "Sarcasm is surfaced as an explicit warning flag, NOT by silently flipping emotion polarity, preserving audit integrity.")
    add_bullet_point(tf7, "Confidence Margin Calibration", "When the top score is < 0.40 or top-two margin is < 0.10, the system flags 'Uncertain'.")
    add_bullet_point(tf7, "Human-in-the-Loop Safeguard", "Uncertain flags notify operators to review ambiguous cases rather than making overconfident automated mistakes.")
    add_bullet_point(tf7, "Contrasting Cues", "Handles sentences with lexical clash (e.g. 'Brilliant job crashing the server') via blended weights.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 8: Safety Boundaries & Non-Diagnostic Stance
    # ─────────────────────────────────────────────────────────────────────────
    slide8 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide8, "7. Safety Boundaries & Non-Diagnostic Constraints")
    box8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf8 = box8.text_frame
    tf8.word_wrap = True

    add_bullet_point(tf8, "Explicit Analysis Tool", "Designed strictly for linguistic tone analysis. Explicitly NOT a clinical psychiatric or medical diagnostic tool.")
    add_bullet_point(tf8, "Clinical Term Redaction", "Validator automatically strips clinical disorder terms ('bipolar', 'depression diagnosis') from outputs.")
    add_bullet_point(tf8, "Mandatory Disclaimer", "Every response payload and UI card embeds an automated non-diagnostic safety disclaimer.")
    add_bullet_point(tf8, "Prompt Injection Defense", "User input is sanitized and treated strictly as passive text data, preventing command injection.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 9: Scalability & Deployment Architecture
    # ─────────────────────────────────────────────────────────────────────────
    slide9 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide9, "8. Scalability & Production Readiness")
    box9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf9 = box9.text_frame
    tf9.word_wrap = True

    add_bullet_point(tf9, "Stateless Flask Backend", "Horizontally scalable; model weights loaded as lazy thread-safe process singletons.")
    add_bullet_point(tf9, "Database Agnostic", "SQLite for zero-config local dev; swappable to PostgreSQL in production via DATABASE_URL.")
    add_bullet_point(tf9, "Containerization", "Production-grade Dockerfile included with non-root user and multi-worker gunicorn setup.")
    add_bullet_point(tf9, "Batch Throughput", "Supports high-throughput CSV ingestion up to 500 rows per batch transaction.")

    # ─────────────────────────────────────────────────────────────────────────
    # Slide 10: Conclusion & Deliverables Summary
    # ─────────────────────────────────────────────────────────────────────────
    slide10 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide10, "9. Conclusion & Project Deliverables")
    box10 = slide10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(8.4), Inches(5.2))
    tf10 = box10.text_frame
    tf10.word_wrap = True

    add_bullet_point(tf10, "Comprehensive Codebase", "Clean backend/app modular tree adhering to the teacher's standard architecture.")
    add_bullet_point(tf10, "Full Product Handbook", "Comprehensive documentation in docs/handbook.md covering mechanics, architecture, and API reference.")
    add_bullet_point(tf10, "Empirical Validation", "Automated evaluate.py test harness proving accuracy and F1 score benchmarks.")
    add_bullet_point(tf10, "Presentation Ready", "End-to-end interactive demo ready with zero external API key requirements.")

    prs.save(str(out_path))
    print(f"[+] Presentation saved successfully to: {out_path}")


def main():
    out_file = ROOT / "presentation" / "P098_Emotion_Detection.pptx"
    build_deck(out_file)


if __name__ == "__main__":
    main()
