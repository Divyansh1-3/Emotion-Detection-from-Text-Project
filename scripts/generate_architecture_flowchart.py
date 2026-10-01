"""Generate high-resolution architecture flowchart for P_098 Emotion Detector SRS.

Matches the exact clean, publication-grade visual styling of the reference SRS flowchart:
- Clear multi-tier topology (Presentation -> API Gateway -> Parallel Feature Engines & DB -> Fusion -> Rationale)
- Authentic cylinder database icon for SQLite
- Soft pastel fills, crisp slate/navy borders, rounded rectangles
- Labeled connector arrows with curved return loop on the right
- 300 DPI output suitable for high-quality IEEE docx embedding.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse, Arc


def create_product_architecture_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(11.5, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Background pure white
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Color Palette (Matching academic reference)
    NAVY = "#1B365D"
    SLATE = "#3B6998"
    DARK_GRAY = "#2B2D42"
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

        # Title
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
        # Subtitle
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
        # Database cylinder
        ell_h = h * 0.25
        body_h = h - ell_h
        # Body rect
        rect = patches.Rectangle(
            (x - w / 2, y - h / 2 + ell_h / 2),
            w,
            body_h,
            facecolor=bg_color,
            edgecolor="none",
            zorder=2,
        )
        ax.add_patch(rect)
        # Side lines
        ax.plot([x - w / 2, x - w / 2], [y - h / 2 + ell_h / 2, y + h / 2 - ell_h / 2], color=border_color, lw=lw, zorder=3)
        ax.plot([x + w / 2, x + w / 2], [y - h / 2 + ell_h / 2, y + h / 2 - ell_h / 2], color=border_color, lw=lw, zorder=3)
        # Bottom curve
        arc_bottom = patches.Arc(
            (x, y - h / 2 + ell_h / 2),
            w,
            ell_h,
            angle=0,
            theta1=180,
            theta2=360,
            color=border_color,
            lw=lw,
            zorder=3,
        )
        ax.add_patch(arc_bottom)
        # Bottom fill
        wedge_b = patches.Wedge(
            (x, y - h / 2 + ell_h / 2),
            w / 2,
            180,
            360,
            facecolor=bg_color,
            edgecolor="none",
            zorder=2,
        )
        # Scale to ellipse height
        # Simpler: an Ellipse at the bottom with facecolor
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
        # Top ellipse
        ell_t = Ellipse(
            (x, y + h / 2 - ell_h / 2),
            w,
            ell_h,
            facecolor=bg_color,
            edgecolor=border_color,
            lw=lw,
            zorder=3,
        )
        ax.add_patch(ell_t)

        # Title & subtitle
        ax.text(
            x,
            y + h * 0.08,
            title,
            ha="center",
            va="center",
            fontsize=8.6,
            fontweight="bold",
            color=NAVY,
            zorder=4,
            family="DejaVu Sans",
        )
        ax.text(
            x,
            y - h * 0.22,
            subtitle,
            ha="center",
            va="center",
            fontsize=7.0,
            color=TEXT_MUTED,
            zorder=4,
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
            zorder=1,
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
                zorder=5,
                family="DejaVu Sans",
            )

    # -------------------------------------------------------------
    # 1. TOP NODE: Frontend / Client
    # -------------------------------------------------------------
    # Center X = 46, Y = 92
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

    # -------------------------------------------------------------
    # 2. MIDDLE NODE: Flask API Gateway
    # -------------------------------------------------------------
    # Center X = 46, Y = 73
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

    # -------------------------------------------------------------
    # 3. PARALLEL FEATURE EXTRACTION & STORAGE TIER (Row Y = 51)
    # 5 Components cleanly spaced across X: 11, 29, 47, 65, 83
    # -------------------------------------------------------------
    # Box 1: DistilRoBERTa Emotion Model
    draw_node(
        11,
        51,
        17.5,
        11.5,
        "DistilRoBERTa Model",
        "7-Class Emotion Backbone\n82M Parameters (CPU)",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    # Box 2: Twitter-RoBERTa-Irony Model
    draw_node(
        29,
        51,
        17.5,
        11.5,
        "Twitter-RoBERTa-Irony",
        "Deep Irony / Sarcasm\ncardiffnlp • SemEval",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    # Box 3: Lexical & Rule Engine
    draw_node(
        47,
        51,
        17.5,
        11.5,
        "Lexical & Rule Engine",
        "Emoji, Slang & Negations\nPunctuation Contrast Cues",
        bg_color="#F0FAF4",
        border_color="#48BB78",
        lw=1.2,
    )

    # Box 4: Semantic Vector RAG
    draw_node(
        65,
        51,
        17.5,
        11.5,
        "Semantic Vector RAG",
        "all-MiniLM-L6-v2 Embeddings\nexemplars.jsonl • k-NN",
        bg_color="#EBF5FB",
        border_color="#5DADE2",
        lw=1.2,
    )

    # Box 5: SQLite Database (Cylinder)
    draw_cylinder(
        83,
        51,
        17.5,
        11.5,
        "SQLite 3 Persistence",
        "emotion.sqlite3 • WAL Mode\nRequest Logs & Audit Records",
        bg_color="#F2F4F8",
        border_color="#5D6D7E",
        lw=1.2,
    )

    # Arrows from Flask Backend down to 5 engines
    draw_arrow((36, 67.7), (13, 56.8), label="deep classification", label_pos=(22, 62.8))
    draw_arrow((41, 67.7), (29, 56.8), label="irony inference", label_pos=(33, 62.0))
    draw_arrow((46, 67.7), (47, 56.8), label="rule extraction", label_pos=(48, 62.5))
    draw_arrow((52, 67.7), (65, 56.8), label="dense vector search", label_pos=(61, 62.0))
    draw_arrow((58, 67.7), (81, 56.8), label="SQLAlchemy ORM logging", label_pos=(75, 62.8))

    # -------------------------------------------------------------
    # 4. FUSION & CALIBRATION ENGINE (Y = 28)
    # -------------------------------------------------------------
    draw_node(
        38,
        28,
        48,
        12.0,
        "Mathematical Signal Fusion & Calibration Layer",
        "70% Model + 15% Rules + 15% k-NN • Margin Δ = P1 - P2\nAffective Purity Guards & Contextual Incongruity Shift",
        bg_color="#FEF9E7",
        border_color="#F5B041",
        lw=1.5,
    )

    # Arrows from 4 feature engines into Fusion
    draw_arrow((11, 45.2), (22, 34.0), label="7-class logits", label_pos=(14.5, 39.5))
    draw_arrow((29, 45.2), (32, 34.0), label="irony score", label_pos=(29, 39.5))
    draw_arrow((47, 45.2), (43, 34.0), label="rule priors", label_pos=(47.5, 39.5))
    draw_arrow((65, 45.2), (54, 34.0), label="k-NN vote & citations", label_pos=(64.5, 39.5))

    # -------------------------------------------------------------
    # 5. RATIONALE SYNTHESIS ENGINE (Y = 10)
    # -------------------------------------------------------------
    draw_node(
        38,
        10,
        48,
        10.5,
        "Bounded LLM Rationale Synthesis",
        "Google Gemini 1.5 Flash • Clinical Sanitization Redactor\nDeterministic Offline Template Fallback",
        bg_color="#F4ECF7",
        border_color="#AF7AC5",
        lw=1.4,
    )

    # Arrow from Fusion down to LLM Rationale
    draw_arrow((38, 22.0), (38, 15.3), label="fused emotion & evidence context", label_pos=(38, 18.6))

    # -------------------------------------------------------------
    # 6. CURVED RETURN LOOP: Right side back to Flask Backend
    # -------------------------------------------------------------
    # Path from (62, 10) looping up the right side around X=94 to (63, 73)
    loop_arrow = patches.FancyArrowPatch(
        (62, 10),
        (63, 73),
        connectionstyle="arc3,rad=-0.42",
        arrowstyle="-|>",
        mutation_scale=11,
        color="#2980B9",
        linewidth=1.4,
        zorder=1,
    )
    ax.add_patch(loop_arrow)

    ax.text(
        88.5,
        28.0,
        "calibrated prediction,\nsarcasm & rationale",
        ha="center",
        va="center",
        fontsize=7.2,
        color="#2980B9",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#FFFFFF", edgecolor="#A9CCE3", alpha=0.95),
        zorder=5,
        family="DejaVu Sans",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()
    print(f"Product architecture diagram generated: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_file = out_dir / "p098_product_architecture_flowchart.png"
    create_product_architecture_diagram(str(out_file))
