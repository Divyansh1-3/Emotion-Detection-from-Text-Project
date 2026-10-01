"""Generate pixel-perfect architectural and workflow diagrams matching the style of College_FAQ_Chatbot_Report.docx.

Outputs:
1. C:\\Users\\divya\\HCL-Project\\docs\\p098_layered_architecture.png
2. C:\\Users\\divya\\HCL-Project\\docs\\p098_request_flow.png
"""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Color Palette matching extracted reference images
COLOR_BLUE_BG = "#D3E3FD"
COLOR_BLUE_BORDER = "#7DA0FA"

COLOR_PEACH_BG = "#FBE2C5"
COLOR_PEACH_BORDER = "#E09F5B"

COLOR_PURPLE_BG = "#EADBFA"
COLOR_PURPLE_BORDER = "#9C6EC7"

COLOR_GRAY_BG = "#D9D9D9"
COLOR_GRAY_BORDER = "#777777"

COLOR_GREEN_BG = "#CEEAD6"
COLOR_GREEN_BORDER = "#5BB974"

ARROW_COLOR = "#666666"


def draw_layered_architecture(out_path: Path):
    fig, ax = plt.subplots(figsize=(15, 10), dpi=200)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(
        7.5, 9.6,
        "Layered Architecture — Emotion Detector from Text (P_098)",
        ha="center", va="center",
        fontsize=16, fontweight="bold", fontfamily="sans-serif", color="#000000"
    )

    layers = [
        {
            "name": "Presentation",
            "bg": COLOR_BLUE_BG,
            "border": COLOR_BLUE_BORDER,
            "y": 8.0,
            "components": ["Interactive Web UI", "Batch CSV Uploader", "Analytics & /inspect Dashboard"]
        },
        {
            "name": "API (Flask 3.0)",
            "bg": COLOR_BLUE_BG,
            "border": COLOR_BLUE_BORDER,
            "y": 6.2,
            "components": ["/api/v1/emotion/process", "/batch", "/stats", "/health", "/results"]
        },
        {
            "name": "Hybrid Engine",
            "bg": COLOR_PEACH_BG,
            "border": COLOR_PEACH_BORDER,
            "y": 4.4,
            "components": ["Input Validator", "Demojizer", "Rules & Incongruity", "Fusion & Sarcasm", "Confidence Gate"]
        },
        {
            "name": "AI / ML",
            "bg": COLOR_PURPLE_BG,
            "border": COLOR_PURPLE_BORDER,
            "y": 2.6,
            "components": ["DistilRoBERTa (Emotion)", "Twitter-RoBERTa (Irony)", "all-MiniLM-L6-v2 (RAG)", "Bounded LLM Rationale"]
        },
        {
            "name": "Data & Config",
            "bg": COLOR_GRAY_BG,
            "border": COLOR_GRAY_BORDER,
            "y": 0.8,
            "components": ["Knowledge Base (emotions.jsonl, exemplars.jsonl)", "SQLite Database (analyses table)"]
        }
    ]

    left_x = 0.8
    left_w = 2.4
    box_h = 1.15
    right_x_start = 3.6
    total_right_w = 10.6

    for idx, layer in enumerate(layers):
        y = layer["y"]

        # Left Header Box
        rect_left = patches.FancyBboxPatch(
            (left_x, y), left_w, box_h,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor=layer["bg"], edgecolor="none"
        )
        ax.add_patch(rect_left)
        ax.text(
            left_x + left_w / 2, y + box_h / 2,
            layer["name"],
            ha="center", va="center",
            fontsize=11.5, fontweight="bold", fontfamily="sans-serif", color="#000000"
        )

        # Right Component Boxes
        comps = layer["components"]
        n_comps = len(comps)
        gap = 0.22
        comp_w = (total_right_w - (n_comps - 1) * gap) / n_comps

        for c_idx, comp_text in enumerate(comps):
            cx = right_x_start + c_idx * (comp_w + gap)
            rect_comp = patches.FancyBboxPatch(
                (cx, y), comp_w, box_h,
                boxstyle="round,pad=0.04,rounding_size=0.08",
                facecolor="#FFFFFF", edgecolor=layer["border"], linewidth=1.5
            )
            ax.add_patch(rect_comp)

            # Auto wrap text if long
            fontsize = 9.5 if len(comp_text) > 22 else 10.5
            ax.text(
                cx + comp_w / 2, y + box_h / 2,
                comp_text,
                ha="center", va="center",
                fontsize=fontsize, fontfamily="sans-serif", color="#000000"
            )

        # Downward Arrow between layers
        if idx < len(layers) - 1:
            arrow_x = right_x_start + total_right_w / 2
            arrow_y_top = y - 0.08
            arrow_y_bot = y - 0.55
            ax.annotate(
                "",
                xy=(arrow_x, arrow_y_bot),
                xytext=(arrow_x, arrow_y_top),
                arrowprops=dict(arrowstyle="->", color=ARROW_COLOR, lw=1.8, mutation_scale=15)
            )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved Layered Architecture diagram: {out_path}")


def draw_request_flow(out_path: Path):
    fig, ax = plt.subplots(figsize=(14, 12), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Title
    ax.text(
        7.0, 11.6,
        "Request Flow — From User Text to Calibrated Affect Prediction",
        ha="center", va="center",
        fontsize=16, fontweight="bold", fontfamily="sans-serif", color="#000000"
    )

    steps = [
        {
            "num": "1",
            "title": "1. User Text Submission",
            "sub": "",
            "bg": COLOR_BLUE_BG,
            "y": 10.3,
            "note": ""
        },
        {
            "num": "2",
            "title": "2. Validation & Safety Check",
            "sub": "(Length check, prompt injection defense, clinical redaction)",
            "bg": COLOR_PEACH_BG,
            "y": 9.0,
            "note": "Invalid length / prompt injection ->\nsafe rejection"
        },
        {
            "num": "3",
            "title": "3. Preprocessing & Demojization",
            "sub": "(Emojis expanded to tokens, contractions normalized)",
            "bg": COLOR_PEACH_BG,
            "y": 7.7,
            "note": ""
        },
        {
            "num": "4",
            "title": "4. Parallel Feature Extraction",
            "sub": "(DistilRoBERTa + Twitter-RoBERTa + Symbolic Rules + MiniLM RAG)",
            "bg": COLOR_BLUE_BG,
            "y": 6.4,
            "note": "Deep neural logits & 384-d\nvector embeddings generated"
        },
        {
            "num": "5",
            "title": "5. Signal Fusion & Sarcasm Resolution",
            "sub": "(Affective purity guard on joy; praise + adversity transferred to Anger/Disgust)",
            "bg": COLOR_PEACH_BG,
            "y": 5.1,
            "note": "Purity guard eliminates\nTwitter sarcasm false-positives"
        },
        {
            "num": "6",
            "title": "6. Confidence & Margin Gating",
            "sub": "(Evaluates top-2 probability gap Delta; Delta < 0.10 flags Uncertain)",
            "bg": COLOR_PEACH_BG,
            "y": 3.8,
            "note": "Ambiguous input ->\nUncertain flag surfaced"
        },
        {
            "num": "7",
            "title": "7. Grounded Rationale Generation",
            "sub": "(Bounded LLM cites retrieved exemplars; deterministic template fallback)",
            "bg": COLOR_PURPLE_BG,
            "y": 2.5,
            "note": "Zero-downtime offline\ntemplate fallback"
        },
        {
            "num": "8",
            "title": "8. Synchronous Commit to SQLite",
            "sub": "(emotion.sqlite3 logs full telemetry with 100% /inspect audit parity)",
            "bg": COLOR_GRAY_BG,
            "y": 1.3,
            "note": ""
        },
        {
            "num": "9",
            "title": "9. Render Response & Dashboard Badges",
            "sub": "(Primary affect, calibrated confidence meter, sarcasm banner, rationale)",
            "bg": COLOR_GREEN_BG,
            "y": 0.1,
            "note": "Delivered in < 70 ms (CPU)"
        }
    ]

    box_x = 2.2
    box_w = 7.6
    box_h = 0.95

    for idx, step in enumerate(steps):
        y = step["y"]

        # Main Flow Box
        rect = patches.FancyBboxPatch(
            (box_x, y), box_w, box_h,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor=step["bg"], edgecolor="none"
        )
        ax.add_patch(rect)

        # Text inside box
        if step["sub"]:
            ax.text(
                box_x + box_w / 2, y + box_h * 0.64,
                step["title"],
                ha="center", va="center",
                fontsize=11.5, fontweight="bold", fontfamily="sans-serif", color="#000000"
            )
            ax.text(
                box_x + box_w / 2, y + box_h * 0.28,
                step["sub"],
                ha="center", va="center",
                fontsize=9.0, fontfamily="sans-serif", color="#333333"
            )
        else:
            ax.text(
                box_x + box_w / 2, y + box_h / 2,
                step["title"],
                ha="center", va="center",
                fontsize=12, fontweight="bold", fontfamily="sans-serif", color="#000000"
            )

        # Side Note if present
        if step["note"]:
            ax.text(
                box_x + box_w + 0.35, y + box_h / 2,
                step["note"],
                ha="left", va="center",
                fontsize=9.0, fontfamily="sans-serif", fontstyle="italic", color="#555555"
            )

        # Arrow down
        if idx < len(steps) - 1:
            arrow_x = box_x + box_w / 2
            arrow_y_top = y - 0.05
            arrow_y_bot = y - 0.30
            ax.annotate(
                "",
                xy=(arrow_x, arrow_y_bot),
                xytext=(arrow_x, arrow_y_top),
                arrowprops=dict(arrowstyle="->", color=ARROW_COLOR, lw=1.8, mutation_scale=15)
            )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] Saved Request Flow diagram: {out_path}")


if __name__ == "__main__":
    hcl_dir = Path("C:/Users/divya/HCL-Project")
    img0 = hcl_dir / "docs" / "p098_layered_architecture.png"
    img1 = hcl_dir / "docs" / "p098_request_flow.png"

    draw_layered_architecture(img0)
    draw_request_flow(img1)
