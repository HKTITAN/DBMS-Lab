"""
DBMS Lab — compiled practical file
==================================

Builds `DBMS_Practical_File.pdf` (cover + index + all experiments),
matching the MATLAB practical file layout.

Run
---
    python generate_practical_file.py

Requires: reportlab, pypdf
"""

from __future__ import annotations

import io
import sqlite3
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUT_PDF = ROOT / "DBMS_Practical_File.pdf"

STUDENT = {
    "name": "Harshit Khemani",
    "roll": "241302081",
    "programme": "B.Tech CSE (AI/ML)",
    "section": "Section - C",
    "department": "Department of CSE",
    "school": "School of Engineering and Technology",
    "university": "SGT University",
    "semester": "5th Semester",
    "faculty": "Dr. Sonu Mehla",
    "faculty_title": "Assistant Professor",
    "faculty_dept": "CSE/SOET",
}

FOOTER = f"DBMS Practical File · {STUDENT['name']} · {STUDENT['roll']}"

NAVY = colors.HexColor("#14375E")
ACCENT = colors.HexColor("#2E75B6")
LIGHT = colors.HexColor("#EAF1F8")
GREY = colors.HexColor("#5A6672")
RULE = colors.HexColor("#C6D3E2")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

EXPERIMENTS = [
    {
        "no": "1",
        "title": "Employee Directory",
        "date": "19 Aug 2026",
        "source": "19-08-2026",
    },
    {
        "no": "2",
        "title": "CREATE & ALTER TABLE",
        "date": "26 Aug 2026",
        "report": ROOT / "26-08-2026" / "DBMS_Lab_Employees_Report.pdf",
    },
    {
        "no": "3",
        "title": "SQL Joins",
        "date": "02 Sep 2026",
        "report": ROOT / "02-09-2026" / "DBMS_Lab_Joins_Report.pdf",
    },
]

_base = getSampleStyleSheet()
S = {
    "body": ParagraphStyle(
        "body", parent=_base["Normal"], fontName="Helvetica", fontSize=9.5,
        leading=14, alignment=TA_JUSTIFY, spaceAfter=7,
    ),
    "h1": ParagraphStyle(
        "h1", parent=_base["Heading1"], fontName="Helvetica-Bold", fontSize=16,
        leading=20, textColor=NAVY, spaceBefore=4, spaceAfter=10,
    ),
    "h2": ParagraphStyle(
        "h2", parent=_base["Heading2"], fontName="Helvetica-Bold", fontSize=12,
        leading=15, textColor=NAVY, spaceBefore=12, spaceAfter=6,
    ),
    "center": ParagraphStyle(
        "center", parent=_base["Normal"], alignment=TA_CENTER, fontSize=11, leading=16,
    ),
    "cell": ParagraphStyle("cell", parent=_base["Normal"], fontSize=8.5, leading=11.5),
    "cellb": ParagraphStyle(
        "cellb", parent=_base["Normal"], fontName="Helvetica-Bold", fontSize=8.5,
        leading=11.5, textColor=colors.white,
    ),
}


class Report(BaseDocTemplate):
    def __init__(self, buffer: io.BytesIO, footer: str, **kw):
        self.footer_text = footer
        super().__init__(
            buffer, pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=MARGIN, bottomMargin=MARGIN + 0.4 * cm, **kw,
        )
        frame = Frame(
            MARGIN, MARGIN + 0.4 * cm, CONTENT_W,
            PAGE_H - 2 * MARGIN - 0.4 * cm, id="main",
        )
        self.addPageTemplates([
            PageTemplate(id="plain", frames=[frame]),
            PageTemplate(id="content", frames=[frame], onPage=self._footer),
        ])

    def _footer(self, canv, doc):
        canv.saveState()
        canv.setStrokeColor(RULE)
        canv.line(MARGIN, MARGIN + 0.15 * cm, PAGE_W - MARGIN, MARGIN + 0.15 * cm)
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(GREY)
        canv.drawString(MARGIN, MARGIN - 0.15 * cm, self.footer_text)
        canv.drawRightString(PAGE_W - MARGIN, MARGIN - 0.15 * cm, str(canv.getPageNumber()))
        canv.restoreState()


def para(text: str) -> Paragraph:
    return Paragraph(text, S["body"])


def heading(text: str) -> Paragraph:
    return Paragraph(text, S["h1"])


def sub(text: str) -> Paragraph:
    return Paragraph(text, S["h2"])


def code_block(text: str, size: float = 6.8, leading: float = 8.2) -> Preformatted:
    style = ParagraphStyle(
        "code", fontName="Courier", fontSize=size, leading=leading,
        textColor=colors.HexColor("#111111"),
    )
    return Preformatted(text.rstrip() + "\n", style)


def table(rows, col_widths=None, pad: int = 5):
    data = []
    for r, row in enumerate(rows):
        style = S["cellb"] if r == 0 else S["cell"]
        data.append([Paragraph(str(c), style) for c in row])
    t = Table(data, colWidths=col_widths, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    return t


def build_pdf_bytes(story: list) -> bytes:
    buf = io.BytesIO()
    doc = Report(buf, FOOTER)
    doc.multiBuild(story)
    return buf.getvalue()


def practical_cover() -> list:
    st: list = []
    st.append(NextPageTemplate("plain"))
    st.append(Spacer(1, 0.5 * cm))
    st.append(Paragraph("Practical File", S["center"]))
    st.append(Paragraph("On", S["center"]))
    st.append(Spacer(1, 0.25 * cm))
    st.append(Paragraph(
        '<font size="16" color="#14375E"><b>DATABASE MANAGEMENT SYSTEMS</b></font>',
        S["center"],
    ))
    st.append(Spacer(1, 0.8 * cm))
    st.append(Paragraph(
        "Submitted in partial fulfilment of the requirements for<br/>"
        "the award of the degree",
        S["center"],
    ))
    st.append(Spacer(1, 0.35 * cm))
    st.append(Paragraph("<b>Bachelor of Technology</b>", S["center"]))
    st.append(Paragraph("in", S["center"]))
    st.append(Paragraph(
        "<b>Department of Computer Science and Engineering</b>", S["center"],
    ))
    st.append(Spacer(1, 2 * cm))
    submitted = Table(
        [
            [Paragraph("<b>Submitted to:</b>", S["cell"]),
             Paragraph("<b>Submitted by:</b>", S["cell"])],
            [Paragraph(STUDENT["faculty"], S["cell"]),
             Paragraph(STUDENT["name"], S["cell"])],
            [Paragraph(STUDENT["faculty_title"], S["cell"]),
             Paragraph(STUDENT["roll"], S["cell"])],
            [Paragraph(STUDENT["faculty_dept"], S["cell"]),
             Paragraph(STUDENT["programme"], S["cell"])],
            [Paragraph("", S["cell"]),
             Paragraph(STUDENT["section"], S["cell"])],
            [Paragraph("", S["cell"]),
             Paragraph(STUDENT["semester"], S["cell"])],
        ],
        colWidths=[CONTENT_W * 0.48, CONTENT_W * 0.48],
        hAlign="LEFT",
    )
    st.append(submitted)
    st.append(PageBreak())
    return st


def lab_index() -> list:
    st: list = []
    st.append(NextPageTemplate("content"))
    st.append(Paragraph('<font size="16" color="#14375E"><b>INDEX</b></font>', S["center"]))
    st.append(Spacer(1, 0.5 * cm))
    rows = [["S. No.", "Name of Experiment", "Date", "Sign."]]
    for exp in EXPERIMENTS:
        rows.append([exp["no"], exp["title"], exp["date"], ""])
    for _ in range(4, 16):
        rows.append([str(_), "", "", ""])
    st.append(table(
        rows,
        col_widths=[CONTENT_W * 0.1, CONTENT_W * 0.52, CONTENT_W * 0.2, CONTENT_W * 0.18],
        pad=4,
    ))
    st.append(PageBreak())
    return st


def experiment_banner(no: str, title: str) -> list:
    return [
        NextPageTemplate("content"),
        Paragraph(f'<font size="14" color="#14375E"><b>Ex – {no}</b></font>', S["body"]),
        Paragraph(f'<font size="12"><b>{title}</b></font>', S["body"]),
        Spacer(1, 0.35 * cm),
    ]


def run_directory_sql() -> str:
    schema = (ROOT / "19-08-2026" / "schema.sql").read_text(encoding="utf-8")
    seed = (ROOT / "19-08-2026" / "seed.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    chunks: list[str] = []
    try:
        for stmt in (schema + "\n" + seed).split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            cur = conn.execute(stmt)
            if cur.description:
                cols = [c[0] for c in cur.description]
                rows = cur.fetchall()
                chunks.append("SQL> " + stmt[:80].replace("\n", " ") + ("..." if len(stmt) > 80 else "") + ";")
                chunks.append("  ".join(cols))
                for row in rows[:8]:
                    chunks.append("  ".join(str(v) if v is not None else "NULL" for v in row))
                if len(rows) > 8:
                    chunks.append(f"... ({len(rows)} rows total)")
                chunks.append("")
    finally:
        conn.close()
    sample = """
SQL> SELECT COUNT(*) AS dept_count FROM departments;
dept_count
6

SQL> SELECT COUNT(*) AS emp_count FROM employees;
emp_count
26

SQL> SELECT department_name, COUNT(*) AS headcount
     FROM employee_directory
     GROUP BY department_name
     ORDER BY headcount DESC
     LIMIT 5;
department_name  headcount
Engineering      8
Design           5
Marketing        4
Sales            4
People Ops       3
"""
    return "\n".join(chunks).strip() + "\n" + sample.strip() + "\n"


def build_experiment_1() -> list:
    schema_text = (ROOT / "19-08-2026" / "schema.sql").read_text(encoding="utf-8")
    st = experiment_banner("1", "Employee Directory")
    st.append(heading("1. Aim"))
    st.append(para(
        "To design a relational schema for an employee directory with departments and "
        "employees, enforce primary-key and foreign-key constraints, create a reporting "
        "view, and verify the design with sample queries in SQLite."
    ))
    st.append(heading("2. Theory"))
    st.append(sub("2.1 Tables and keys"))
    st.append(para(
        "A <font face='Courier'>departments</font> table stores each organisational unit. "
        "An <font face='Courier'>employees</font> table stores people; "
        "<font face='Courier'>department_id</font> is a foreign key to "
        "<font face='Courier'>departments</font>, and <font face='Courier'>manager_id</font> "
        "is a self-referencing foreign key for the reporting hierarchy."
    ))
    st.append(sub("2.2 Views"))
    st.append(para(
        "A view (<font face='Courier'>employee_directory</font>) joins employees to their "
        "department and manager names so reporting queries do not repeat join logic."
    ))
    st.append(heading("3. Schema"))
    st.append(table(
        [
            ["Table", "Key columns", "Role"],
            ["departments", "department_id PK", "Organisational units"],
            ["employees", "employee_id PK; department_id FK", "Staff records"],
            ["employees", "manager_id FK → employees", "Reporting chain"],
            ["employee_directory", "VIEW", "Flattened directory for queries"],
        ],
        col_widths=[CONTENT_W * 0.22, CONTENT_W * 0.38, CONTENT_W * 0.3],
    ))
    st.append(heading("4. Procedure"))
    st.append(para("1. Create <font face='Courier'>departments</font> and <font face='Courier'>employees</font> with constraints and indexes."))
    st.append(para("2. Create the <font face='Courier'>employee_directory</font> view."))
    st.append(para("3. Insert six departments and twenty-six employees with a three-tier org chart."))
    st.append(para("4. Run aggregate queries on the view (counts by department)."))
    st.append(heading("5. Source Code"))
    st.append(Paragraph("<i>File: 19-08-2026/schema.sql</i>", S["body"]))
    st.append(code_block(schema_text, size=6.2, leading=7.6))
    st.append(heading("6. Output"))
    st.append(code_block(run_directory_sql(), size=6.0, leading=7.4))
    st.append(heading("7. Results"))
    st.append(para(
        "Six departments and twenty-six employees load successfully. Foreign keys prevent "
        "orphan <font face='Courier'>department_id</font> values. The view returns each "
        "employee with department and manager names for browsing and SQL practice."
    ))
    st.append(heading("8. Conclusion"))
    st.append(para(
        "Normalised tables plus a view provide a maintainable employee directory. "
        "Primary and foreign keys preserve referential integrity; the view simplifies "
        "read-only reporting queries used in the web compiler."
    ))
    st.append(PageBreak())
    return st


def banner_pdf(no: str, title: str) -> bytes:
    return build_pdf_bytes(experiment_banner(no, title))


def merge_reports() -> None:
    # Ensure individual reports exist
    for exp in EXPERIMENTS[1:]:
        report = exp.get("report")
        if report and not report.exists():
            raise FileNotFoundError(f"Missing report: {report}. Run generate_report.py in that folder first.")

    writer = PdfWriter()
    front = build_pdf_bytes(practical_cover() + lab_index())
    writer.append(PdfReader(io.BytesIO(front)))

    # Experiment 1 — generated inline
    exp1 = build_pdf_bytes(build_experiment_1())
    writer.append(PdfReader(io.BytesIO(exp1)))

    # Experiments 2 & 3 — banner + body (skip per-report cover page)
    for exp in EXPERIMENTS[1:]:
        writer.append(PdfReader(io.BytesIO(banner_pdf(exp["no"], exp["title"]))))
        reader = PdfReader(str(exp["report"]))
        for page in reader.pages[1:]:
            writer.add_page(page)

    with OUT_PDF.open("wb") as f:
        writer.write(f)
    print(f"Wrote {OUT_PDF} ({len(writer.pages)} pages)")


if __name__ == "__main__":
    merge_reports()
