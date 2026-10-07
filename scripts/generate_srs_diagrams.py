"""Generate publication-quality architectural flowcharts and UI diagrams for P_098 SRS.

Matches the clean, academic reference style (media_1790893970064.png):
1. Figure 2.1: High-Level Product Architecture Flowchart (Section 2.1)
   - Multi-tier topology: Dashboard -> Flask API Gateway -> 5 Parallel Engines & DB -> Fusion -> Rationale
   - Smooth spline return loop around the right side back into Flask Backend
   - Symmetrical layout, authentic database cylinder, soft pastel palette
2. Figure 4.1: Interactive Operator Dashboard & Pipeline Output UI Wireframe (Section 4.1)
   - Modern clean split-pane mockup showing live input controls, probability bars, sarcasm badges, and telemetry
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np
from scipy.interpolate import splprep, splev


def generate_architecture_flowchart(output_path: str):
    fig, ax = plt.subplots(figsize=(11.8, 7.8), dpi=300)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    NAVY = "#1B365D"
    SLATE = "#3B6998"
    TEXT_MUTED = "#555A64"
    ARROW_COLOR = "#5D738A"

    def draw_node(x, y, w, h, title, subtitle, bg_color="#F4F7FB", border_color=SLATE, lw=1.3):
        rect = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.3,rounding_size=1.8",
            facecolor=bg_color,
            edgecolor=border_color,
            linewidth=lw,
            zorder=3,
        )
        ax.add_patch(rect)

        ax.text(
            x,
            y + h * 0.17,
            title,
            ha="center",
            va="center",
            fontsize=8.8,
            fontweight="bold",
            color=NAVY,
            zorder=4,
            family="DejaVu Sans",
        )
        ax.text(
            x,
            y - h * 0.20,
            subtitle,
            ha="center",
            va="center",
            fontsize=7.2,
            color=TEXT_MUTED,
            zorder=4,
            family="DejaVu Sans",
        )
        return (x, y, w, h)

    def draw_cylinder(x, y, w, h, title, subtitle, bg_color="#F2F4F8", border_color="#5D6D7E", lw=1.3):
        ell_h = h * 0.24
        body_h = h - ell_h
        rect = patches.Rectangle(
            (x - w / 2, y - h / 2 + ell_h / 2),
            w,
            body_h,
            facecolor=bg_color,
            edgecolor="none",
            zorder=2,
        )
        ax.add_patch(rect)
        ax.plot([x - w / 2, x - w / 2], [y - h / 2 + ell_h / 2, y + h / 2 - ell_h / 2], color=border_color, lw=lw, zorder=3)
        ax.plot([x + w / 2, x + w / 2], [y - h / 2 + ell_h / 2, y + h / 2 - ell_h / 2], color=border_color, lw=lw, zorder=3)

        ell_b = Ellipse(
            (x, y - h / 2 + ell_h / 2),
            w,
            ell_h,
            facecolor=bg_color,
            edgecolor=border_color,
            lw=lw,
            zorder=2,
        )
        ax.add_patch(ell_b)

        ell_t = Ellipse(
            (x, y + h / 2 - ell_h / 2),
            w,
            ell_h,
            facecolor="#E5E8ED",
            edgecolor=border_color,
            lw=lw,
            zorder=4,
        )
        ax.add_patch(ell_t)

        ax.text(
            x,
            y + h * 0.06,
            title,
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color=NAVY,
            zorder=5,
            family="DejaVu Sans",
        )
        ax.text(
            x,
            y - h * 0.23,
            subtitle,
            ha="center",
            va="center",
            fontsize=6.9,
            color=TEXT_MUTED,
            zorder=5,
            family="DejaVu Sans",
        )
        return (x, y, w, h)

    def draw_arrow(start_xy, end_xy, label="", label_pos=(0, 0), rad=0.0):
        arrow = patches.FancyArrowPatch(
            start_xy,
            end_xy,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=10.5,
            color=ARROW_COLOR,
            linewidth=1.2,
            zorder=2,
        )
        ax.add_patch(arrow)

        if label:
            if label_pos == (0, 0):
                mx = (start_xy[0] + end_xy[0]) / 2
                my = (start_xy[1] + end_xy[1]) / 2 + 1.1
            else:
                mx, my = label_pos

            ax.text(
                mx,
                my,
                label,
                ha="center",
                va="center",
                fontsize=6.8,
                color=TEXT_MUTED,
                bbox=dict(boxstyle="square,pad=0.15", facecolor="#FFFFFF", edgecolor="none", alpha=0.92),
                zorder=6,
                family="DejaVu Sans",
            )

    # 1. TOP: Frontend Client (Center X = 46, Y = 92)
    draw_node(
        46,
        92,
        28,
        9.5,
        "Interactive Web Dashboard",
        "HTML5 • Vanilla JS • Bootstrap 5 • REST Client",
        bg_color="#FFFFFF",
        border_color=SLATE,
        lw=1.3,
    )

    # 2. MIDDLE: Flask API Gateway (Center X = 46, Y = 73)
    draw_node(
        46,
        73,
        34,
        10.5,
        "Flask 3.0 API Gateway & Router",
        "REST API Controller • router.py • Pydantic Schema",
        bg_color="#F4F8FD",
        border_color=NAVY,
        lw=1.5,
    )

    # Arrow: Frontend -> Backend
    draw_arrow((46, 87.2), (46, 78.3), label="HTTP POST /process • UTF-8 JSON", label_pos=(46, 82.8))

    # 3. ROW 3: Feature Engines & Database (Symmetrically spaced around X = 46)
    # Centers: X = 10, 28, 46, 64, 82 (Y = 51)
    draw_node(
        10,
        51,
        16.8,
        11.5,
        "DistilRoBERTa Model",
        "7-Class Emotion Backbone\n82M Parameters (CPU)",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    draw_node(
        28,
        51,
        16.8,
        11.5,
        "Twitter-RoBERTa-Irony",
        "Deep Irony / Sarcasm\ncardiffnlp • SemEval",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    draw_node(
        46,
        51,
        16.8,
        11.5,
        "Lexical & Rule Engine",
        "Emoji, Slang & Negations\nPunctuation Contrast Cues",
        bg_color="#F0FAF4",
        border_color="#48BB78",
        lw=1.2,
    )

    draw_node(
        64,
        51,
        16.8,
        11.5,
        "Semantic Vector RAG",
        "all-MiniLM-L6-v2 Embeddings\nexemplars.jsonl • k-NN",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    draw_cylinder(
        82,
        51,
        16.8,
        11.5,
        "SQLite 3 Persistence",
        "emotion.sqlite3 • WAL Mode\nRequest Logs & Audit Records",
        bg_color="#F2F4F8",
        border_color="#5D6D7E",
        lw=1.2,
    )

    # Arrows from Flask Backend down to 5 components
    draw_arrow((36, 67.7), (12, 56.8), label="deep classification", label_pos=(21, 62.8))
    draw_arrow((41, 67.7), (28, 56.8), label="irony inference", label_pos=(32.5, 62.0))
    draw_arrow((46, 67.7), (46, 56.8), label="rule extraction", label_pos=(46, 62.3))
    draw_arrow((51, 67.7), (64, 56.8), label="dense vector search", label_pos=(59.5, 62.0))
    draw_arrow((56, 67.7), (79, 56.8), label="SQLAlchemy ORM logging", label_pos=(73, 62.8))

    # 4. ROW 4: Fusion & Calibration Layer (Center X = 46, Y = 29)
    draw_node(
        46,
        29,
        52,
        12.0,
        "Mathematical Signal Fusion & Calibration Layer",
        "70% Model + 15% Rules + 15% k-NN • Decision Margin Δ = P1 - P2\nAffective Purity Guards & Contextual Incongruity Calibration",
        bg_color="#FEF9E7",
        border_color="#F5B041",
        lw=1.5,
    )

    # Arrows from 4 feature engines into Fusion
    draw_arrow((10, 45.2), (28, 35.0), label="7-class logits", label_pos=(16.5, 40.5))
    draw_arrow((28, 45.2), (37, 35.0), label="irony score", label_pos=(30.5, 40.5))
    draw_arrow((46, 45.2), (46, 35.0), label="rule priors", label_pos=(46.0, 40.5))
    draw_arrow((64, 45.2), (55, 35.0), label="k-NN vote & citations", label_pos=(62.5, 40.5))

    # 5. ROW 5: Rationale Synthesis (Center X = 46, Y = 11)
    draw_node(
        46,
        11,
        52,
        10.5,
        "Bounded LLM Rationale Synthesis",
        "Google Gemini 1.5 Flash • Clinical Sanitization Redactor\nDeterministic Offline Template Fallback",
        bg_color="#F4ECF7",
        border_color="#AF7AC5",
        lw=1.4,
    )

    # Arrow from Fusion down to LLM Rationale
    draw_arrow((46, 23.0), (46, 16.3), label="fused emotion & evidence context", label_pos=(46, 19.6))

    # 6. CURVED RETURN LOOP: Smooth spline sweeping outside SQLite around right side
    pts = np.array([[72.0, 11.0], [88.0, 16.0], [97.5, 34.0], [97.5, 52.0], [89.0, 70.0], [63.2, 73.0]])
    tck, u = splprep([pts[:, 0], pts[:, 1]], s=0, k=3)
    u_new = np.linspace(0, 1, 120)
    x_new, y_new = splev(u_new, tck)
    ax.plot(x_new, y_new, color="#2980B9", lw=1.5, zorder=2)
    ax.annotate(
        "",
        xy=(63.0, 73.0),
        xytext=(65.2, 73.0),
        arrowprops=dict(arrowstyle="-|>", color="#2980B9", lw=1.5, mutation_scale=12),
        zorder=3,
    )

    ax.text(
        97.0,
        38.0,
        "calibrated prediction,\nsarcasm & rationale",
        ha="center",
        va="center",
        fontsize=7.0,
        color="#2980B9",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor="#A9CCE3", alpha=0.96),
        zorder=6,
        family="DejaVu Sans",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print(f"Product architecture diagram generated: {output_path}")


def generate_ui_wireframe_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(11.5, 7.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    NAVY = "#1B365D"
    SLATE = "#3B6998"
    TEXT_MUTED = "#555A64"
    BORDER_LIGHT = "#CBD5E1"

    # Outer Browser / Application Frame
    outer_box = FancyBboxPatch(
        (2, 2),
        96,
        96,
        boxstyle="round,pad=0.5,rounding_size=2.0",
        facecolor="#F8FAFC",
        edgecolor=SLATE,
        linewidth=1.5,
        zorder=1,
    )
    ax.add_patch(outer_box)

    # Top Navbar (Y: 89.5 to 97.5)
    nav_box = FancyBboxPatch(
        (2.5, 89.5),
        95,
        8.0,
        boxstyle="round,pad=0.3,rounding_size=1.5",
        facecolor=NAVY,
        edgecolor=NAVY,
        zorder=2,
    )
    ax.add_patch(nav_box)

    ax.text(
        6.0,
        93.5,
        "P_098 Emotion Detection from Text  |  HCL Industrial Training",
        ha="left",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color="#FFFFFF",
        zorder=3,
        family="DejaVu Sans",
    )

    # Nav Buttons on right
    ax.text(
        78.0,
        93.5,
        "[ Dashboard ]",
        ha="center",
        va="center",
        fontsize=8.0,
        fontweight="bold",
        color="#FFFFFF",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#3B6998", edgecolor="none"),
        zorder=3,
        family="DejaVu Sans",
    )
    ax.text(
        89.0,
        93.5,
        "[ /inspect Audit ]",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#E2E8F0",
        zorder=3,
        family="DejaVu Sans",
    )

    # Sub-header bar
    ax.text(
        6.0,
        86.5,
        "Candidate: Divyansh Yadav (Roll No: 2400320100444)  •  ABES Engineering College, Ghaziabad",
        ha="left",
        va="center",
        fontsize=7.8,
        color=TEXT_MUTED,
        zorder=3,
        family="DejaVu Sans",
    )

    # -------------------------------------------------------------
    # LEFT PANEL: Input & Batch Operations (X: 4 to 48, Y: 5 to 83)
    # -------------------------------------------------------------
    left_panel = FancyBboxPatch(
        (4, 5),
        44,
        78,
        boxstyle="round,pad=0.4,rounding_size=1.5",
        facecolor="#FFFFFF",
        edgecolor=BORDER_LIGHT,
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(left_panel)

    ax.text(
        6.5,
        80.0,
        "INPUT ANALYSIS CONTROLS",
        ha="left",
        va="center",
        fontsize=8.8,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    ax.text(
        6.5,
        76.0,
        "Enter text utterance for affective classification:",
        ha="left",
        va="center",
        fontsize=7.5,
        color=TEXT_MUTED,
        zorder=3,
        family="DejaVu Sans",
    )

    # Text Input Box
    input_box = FancyBboxPatch(
        (6.5, 59.0),
        39,
        15.0,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F8FAFC",
        edgecolor="#94A3B8",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(input_box)
    ax.text(
        8.0,
        68.0,
        "\"It was a bad day for me and everything felt completely exhausting.\"",
        ha="left",
        va="center",
        fontsize=7.5,
        color="#1E293B",
        zorder=4,
        style="italic",
        family="DejaVu Sans",
    )
    ax.text(
        43.5,
        61.5,
        "67 / 4000 chars",
        ha="right",
        va="center",
        fontsize=6.5,
        color="#94A3B8",
        zorder=4,
        family="DejaVu Sans",
    )

    # Presets Chips (Well-spaced)
    ax.text(
        6.5,
        55.5,
        "Presets:",
        ha="left",
        va="center",
        fontsize=7.2,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    chips = [("Genuine Joy", 16.0), ("Pure Sarcasm", 26.5), ("Hinglish Distress", 38.5)]
    for label, cx in chips:
        ax.text(
            cx,
            55.5,
            label,
            ha="center",
            va="center",
            fontsize=6.5,
            color="#1E293B",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#E2E8F0", edgecolor="#CBD5E1"),
            zorder=4,
            family="DejaVu Sans",
        )

    # Analyze Button
    btn_box = FancyBboxPatch(
        (6.5, 45.0),
        24,
        6.5,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#1A73E8",
        edgecolor="#1A73E8",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(btn_box)
    ax.text(
        18.5,
        48.2,
        "ANALYZE EMOTION",
        ha="center",
        va="center",
        fontsize=8.0,
        fontweight="bold",
        color="#FFFFFF",
        zorder=4,
        family="DejaVu Sans",
    )

    # Clear button
    clear_box = FancyBboxPatch(
        (32.0, 45.0),
        13.5,
        6.5,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F1F5F9",
        edgecolor="#CBD5E1",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(clear_box)
    ax.text(
        38.7,
        48.2,
        "Reset",
        ha="center",
        va="center",
        fontsize=7.5,
        color="#475569",
        zorder=4,
        family="DejaVu Sans",
    )

    # Divider line
    ax.plot([6.5, 45.5], [40.0, 40.0], color="#E2E8F0", lw=1.0, zorder=3)

    # Batch Operations Box
    ax.text(
        6.5,
        36.5,
        "HIGH-THROUGHPUT BATCH INGESTION (CSV)",
        ha="left",
        va="center",
        fontsize=8.0,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    csv_drop = FancyBboxPatch(
        (6.5, 17.0),
        39,
        16.0,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F8FAFC",
        edgecolor="#94A3B8",
        linestyle="--",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(csv_drop)
    ax.text(
        26.0,
        26.5,
        "Drag & Drop CSV File (with 'text' column)",
        ha="center",
        va="center",
        fontsize=7.2,
        fontweight="bold",
        color="#475569",
        zorder=4,
        family="DejaVu Sans",
    )
    ax.text(
        26.0,
        21.5,
        "Supported size: up to 500 rows per batch  •  Exports CSV with sentiment labels",
        ha="center",
        va="center",
        fontsize=6.5,
        color="#94A3B8",
        zorder=4,
        family="DejaVu Sans",
    )

    batch_btn = FancyBboxPatch(
        (6.5, 8.5),
        39,
        5.5,
        boxstyle="round,pad=0.2,rounding_size=0.8",
        facecolor="#059669",
        edgecolor="#059669",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(batch_btn)
    ax.text(
        26.0,
        11.2,
        "UPLOAD & RUN BATCH ANALYSIS",
        ha="center",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color="#FFFFFF",
        zorder=4,
        family="DejaVu Sans",
    )

    # -------------------------------------------------------------
    # RIGHT PANEL: Pipeline Output Visualization (X: 52 to 96, Y: 5 to 83)
    # -------------------------------------------------------------
    right_panel = FancyBboxPatch(
        (52, 5),
        44,
        78,
        boxstyle="round,pad=0.4,rounding_size=1.5",
        facecolor="#FFFFFF",
        edgecolor=BORDER_LIGHT,
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(right_panel)

    ax.text(
        54.5,
        80.0,
        "PIPELINE INFERENCE RESULTS",
        ha="left",
        va="center",
        fontsize=8.8,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    # Primary Badge & Sarcasm Badge Row
    badge_emotion = FancyBboxPatch(
        (54.5, 69.5),
        19.0,
        7.5,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#EFF6FF",
        edgecolor="#3B82F6",
        linewidth=1.2,
        zorder=3,
    )
    ax.add_patch(badge_emotion)
    ax.text(
        64.0,
        74.5,
        "PRIMARY EMOTION",
        ha="center",
        va="center",
        fontsize=6.0,
        fontweight="bold",
        color="#1E40AF",
        zorder=4,
        family="DejaVu Sans",
    )
    ax.text(
        64.0,
        71.5,
        "😢 Sadness (94.9%)",
        ha="center",
        va="center",
        fontsize=7.8,
        fontweight="bold",
        color="#1D4ED8",
        zorder=4,
        family="DejaVu Sans",
    )

    badge_sarcasm = FancyBboxPatch(
        (75.5, 69.5),
        18.5,
        7.5,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F0FDF4",
        edgecolor="#22C55E",
        linewidth=1.2,
        zorder=3,
    )
    ax.add_patch(badge_sarcasm)
    ax.text(
        84.7,
        74.5,
        "SARCASM / IRONY ALERT",
        ha="center",
        va="center",
        fontsize=6.0,
        fontweight="bold",
        color="#166534",
        zorder=4,
        family="DejaVu Sans",
    )
    ax.text(
        84.7,
        71.5,
        "None / Sincere (0.02)",
        ha="center",
        va="center",
        fontsize=7.8,
        fontweight="bold",
        color="#15803D",
        zorder=4,
        family="DejaVu Sans",
    )

    # 7-Class Probability Distribution Bars
    ax.text(
        54.5,
        65.0,
        "7-Class Posterior Probability Distribution:",
        ha="left",
        va="center",
        fontsize=7.2,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    bars_data = [
        ("Sadness", 94.9, "#3B82F6"),
        ("Fear", 2.5, "#F59E0B"),
        ("Anger", 1.2, "#EF4444"),
        ("Surprise", 0.6, "#06B6D4"),
        ("Disgust", 0.4, "#8B5CF6"),
        ("Joy", 0.3, "#10B981"),
        ("Neutral", 0.1, "#94A3B8"),
    ]

    by = 61.5
    for label, val, color in bars_data:
        ax.text(
            54.5,
            by,
            f"{label:8s}",
            ha="left",
            va="center",
            fontsize=6.6,
            color="#334155",
            zorder=3,
            family="DejaVu Sans",
        )
        ax.plot([64.0, 88.0], [by, by], color="#E2E8F0", lw=5.0, solid_capstyle="round", zorder=3)
        fill_len = 64.0 + (24.0 * (val / 100.0))
        ax.plot([64.0, max(64.5, fill_len)], [by, by], color=color, lw=5.0, solid_capstyle="round", zorder=4)
        ax.text(
            90.0,
            by,
            f"{val:4.1f}%",
            ha="left",
            va="center",
            fontsize=6.5,
            color="#475569",
            zorder=4,
            family="DejaVu Sans",
        )
        by -= 3.2

    # Grounded Evidence & Rationale Card
    ax.plot([54.5, 93.5], [38.0, 38.0], color="#E2E8F0", lw=1.0, zorder=3)

    ax.text(
        54.5,
        34.5,
        "EVIDENCE-GROUNDED RATIONALE & CITATIONS",
        ha="left",
        va="center",
        fontsize=7.5,
        fontweight="bold",
        color=NAVY,
        zorder=3,
        family="DejaVu Sans",
    )

    rationale_box = FancyBboxPatch(
        (54.5, 17.5),
        39.5,
        14.5,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        facecolor="#F8FAFC",
        edgecolor="#CBD5E1",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(rationale_box)

    ax.text(
        56.0,
        28.0,
        "\"The utterance conveys profound sadness and emotional exhaustion through",
        ha="left",
        va="center",
        fontsize=6.7,
        color="#1E293B",
        zorder=4,
        style="italic",
        family="DejaVu Sans",
    )
    ax.text(
        56.0,
        25.0,
        "explicit cues ('bad day', 'exhausting'). The semantic RAG engine retrieved",
        ha="left",
        va="center",
        fontsize=6.7,
        color="#1E293B",
        zorder=4,
        style="italic",
        family="DejaVu Sans",
    )
    ax.text(
        56.0,
        22.0,
        "matching sorrow exemplars with 0.94 similarity. Zero sarcasm markers detected.\"",
        ha="left",
        va="center",
        fontsize=6.7,
        color="#1E293B",
        zorder=4,
        style="italic",
        family="DejaVu Sans",
    )
    ax.text(
        56.0,
        19.0,
        "Citations: emotions.jsonl#sadness-def-01  •  Decision Margin: Δ = 0.924",
        ha="left",
        va="center",
        fontsize=6.2,
        fontweight="bold",
        color="#2563EB",
        zorder=4,
        family="DejaVu Sans",
    )

    # Route Telemetry Strip
    telemetry_box = FancyBboxPatch(
        (54.5, 7.5),
        39.5,
        7.5,
        boxstyle="round,pad=0.2,rounding_size=0.8",
        facecolor="#FEF3C7",
        edgecolor="#F59E0B",
        linewidth=1.0,
        zorder=3,
    )
    ax.add_patch(telemetry_box)

    ax.text(
        56.0,
        12.0,
        "ROUTE TRACE TELEMETRY & AUDIT STATUS",
        ha="left",
        va="center",
        fontsize=6.2,
        fontweight="bold",
        color="#92400E",
        zorder=4,
        family="DejaVu Sans",
    )
    ax.text(
        56.0,
        9.2,
        "Route: deep+rag+gemini  |  Audit Record: Saved to emotion.sqlite3",
        ha="left",
        va="center",
        fontsize=6.4,
        color="#78350F",
        zorder=4,
        family="DejaVu Sans",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print(f"UI wireframe diagram generated: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_arch = out_dir / "p098_product_architecture_flowchart.png"
    out_ui = out_dir / "p098_ui_wireframe_diagram.png"

    generate_architecture_flowchart(str(out_arch))
    generate_ui_wireframe_diagram(str(out_ui))
