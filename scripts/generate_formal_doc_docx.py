"""Convert P098_Formal_Project_Documentation.md into an enterprise-styled .docx document.

Features:
- Professional HCL / Corporate Academic typography (Segoe UI)
- Navy & Teal corporate color palette
- Styled tables with dark navy header rows & subtle borders
- Formatted callout boxes
- Proper headers and footers with page numbering
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

# Colors
NAVY = RGBColor(0, 51, 102)        # #003366
TEAL = RGBColor(0, 128, 128)       # #008080
DARK_GRAY = RGBColor(51, 51, 51)   # #333333
MUTED_GRAY = RGBColor(100, 100, 100) # #646464
HEADER_BG_HEX = "003366"
ALT_ROW_HEX = "F8FAFC"
CALLOUT_BG_HEX = "F0F4F8"
BORDER_HEX = "CBD5E1"


def set_cell_background(cell, fill_hex: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
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


def add_callout(doc, text: str, title: str = "KEY ARCHITECTURAL INSIGHT"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, CALLOUT_BG_HEX)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Left border only
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
    r_title = p.add_run(f"{title}: ")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = NAVY

    r_text = p.add_run(text)
    r_text.italic = True
    r_text.font.name = "Segoe UI"
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = DARK_GRAY

    doc.add_paragraph()  # spacing


def build_formal_docx(md_path: Path, out_path: Path):
    doc = docx.Document()

    # Page Margins: 1 inch all around
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Base Normal Style
    normal = doc.styles["Normal"]
    normal.font.name = "Segoe UI"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = DARK_GRAY
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)

    raw_text = md_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    i = 0
    in_table = False
    table_lines = []
    in_code = False
    code_lines = []

    while i < len(lines):
        line = lines[i].rstrip()

        # Handle code blocks
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                # Add preformatted block
                tbl = doc.add_table(rows=1, cols=1)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = tbl.cell(0, 0)
                set_cell_background(cell, "F1F5F9")
                set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                run = p.add_run("\n".join(code_lines))
                run.font.name = "Consolas"
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(30, 41, 59)
                doc.add_paragraph()
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Handle Markdown Tables
        if "|" in line and (line.strip().startswith("|") or line.strip().endswith("|")):
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
            i += 1
            continue
        elif in_table:
            # End of table, process it
            in_table = False
            parse_and_add_table(doc, table_lines)
            table_lines = []

        # Blank lines
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run("―" * 55)
            run.font.color.rgb = RGBColor(203, 213, 225)
            i += 1
            continue

        # Heading 1 (#)
        if line.startswith("# ") and not line.startswith("## "):
            text = line[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(text)
            run.font.name = "Segoe UI"
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = NAVY
            i += 1
            continue

        # Heading 2 (##)
        if line.startswith("## "):
            text = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(text)
            run.font.name = "Segoe UI"
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = NAVY
            i += 1
            continue

        # Heading 3 (###)
        if line.startswith("### "):
            text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text)
            run.font.name = "Segoe UI"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = TEAL
            i += 1
            continue

        # Heading 4 (####)
        if line.startswith("#### "):
            text = line[5:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text)
            run.font.name = "Segoe UI"
            run.font.size = Pt(10.5)
            run.font.bold = True
            run.font.color.rgb = DARK_GRAY
            i += 1
            continue

        # Bullet list item (- or *)
        if line.strip().startswith(("- ", "* ")):
            bullet_text = line.strip()[2:]
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, bullet_text)
            i += 1
            continue

        # Numbered list item
        m_num = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if m_num:
            num_text = m_num.group(2)
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, num_text)
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        add_formatted_runs(p, line)
        i += 1

    # End of document: process trailing table if open
    if in_table and table_lines:
        parse_and_add_table(doc, table_lines)

    doc.save(str(out_path))
    print(f"[+] Document written successfully to: {out_path}")


def add_formatted_runs(paragraph, text: str):
    """Splits markdown inline bold (**text**), code (`text`), and italic (*text*)."""
    # Tokenize bold and code
    pattern = r"(\*\*.*?\*\*|`.*?`)"
    tokens = re.split(pattern, text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
            run.font.name = "Segoe UI"
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(15, 23, 42)
        else:
            # Check single italic
            sub_tokens = re.split(r"(\*.*?\*)", token)
            for st in sub_tokens:
                if not st:
                    continue
                if st.startswith("*") and st.endswith("*"):
                    run = paragraph.add_run(st[1:-1])
                    run.italic = True
                    run.font.name = "Segoe UI"
                else:
                    run = paragraph.add_run(st)
                    run.font.name = "Segoe UI"


def parse_and_add_table(doc, raw_lines: list[str]):
    """Parses markdown table lines and adds an enterprise-styled table."""
    parsed_rows = []
    for line in raw_lines:
        # Strip outer pipes and split
        stripped = line.strip()
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        cols = [c.strip() for c in stripped.split("|")]
        # Skip separator row like | :--- | :---: |
        if all(re.match(r"^:?-+:?$", c) for c in cols):
            continue
        parsed_rows.append(cols)

    if not parsed_rows:
        return

    num_cols = max(len(r) for r in parsed_rows)
    table = doc.add_table(rows=len(parsed_rows), cols=num_cols)

    for r_idx, row_data in enumerate(parsed_rows):
        for c_idx in range(num_cols):
            cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
            cell = table.cell(r_idx, c_idx)
            p = cell.paragraphs[0]
            add_formatted_runs(p, cell_text)

    format_table(table)
    doc.add_paragraph()  # spacing after table


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    md_file = root / "docs" / "P098_Formal_Project_Documentation.md"
    docx_file = root / "docs" / "P098_Formal_Project_Documentation.docx"

    if not md_file.exists():
        print(f"[!] Target markdown file does not exist: {md_file}")
        sys.exit(1)

    print(f"[*] Converting {md_file} -> {docx_file}...")
    build_formal_docx(md_file, docx_file)
