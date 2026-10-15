
"""ReportLab PDF generation for CyGRC audit packs."""

from datetime import datetime, timezone
from html import escape
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#18243A")
PURPLE = colors.HexColor("#6546A5")
LIGHT_GREY = colors.HexColor("#F2F4F7")
BORDER = colors.HexColor("#D7DCE5")


def _text(value: Any) -> str:
    """Escape supplied text before placing it in a ReportLab Paragraph."""
    if value is None or value == "":
        return "Not provided"
    return escape(str(value)).replace("\n", "<br/>")


def _styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=32,
            alignment=TA_CENTER,
            textColor=NAVY,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Cell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_LEFT,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
        )
    )

    return styles


def _paragraph(value: Any, styles, style: str = "Cell") -> Paragraph:
    return Paragraph(_text(value), styles[style])


def _table(rows, widths, styles, repeat_rows=1):
    """Create a consistently styled, repeating-header table."""
    converted = [
        [
            item if isinstance(item, Paragraph)
            else _paragraph(item, styles)
            for item in row
        ]
        for row in rows
    ]

    table = Table(
        converted,
        colWidths=widths,
        repeatRows=repeat_rows,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _header_footer(canvas, doc):
    """Draw a consistent header and footer on every page."""
    canvas.saveState()
    page_width, page_height = A4

    if doc.page > 1:
        canvas.setStrokeColor(BORDER)
        canvas.line(18 * mm, page_height - 17 * mm,
                    page_width - 18 * mm, page_height - 17 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(18 * mm, page_height - 13 * mm, "CyGRC | Audit Pack")

    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 15 * mm, page_width - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(18 * mm, 10 * mm, "Confidential")
    canvas.drawRightString(
        page_width - 18 * mm, 10 * mm, f"Page {doc.page}"
    )
    canvas.restoreState()


def generate_audit_pdf(audit: dict[str, Any]) -> bytes:
    """
    Generate an audit PDF from backend-supplied data.

    Expected fields:
      audit_id, title, organization, executive_summary,
      controls, evidence, findings, sign_off.

    Evidence items use name and sha256. Hashes are displayed exactly
    as supplied; this presentation layer does not recalculate them.
    """
    if not isinstance(audit, dict):
        raise ValueError("Audit data must be a dictionary.")

    if audit.get("audit_id") is None:
        raise ValueError("Audit ID is required.")

    if not any(
        audit.get(key)
        for key in ("title", "executive_summary", "controls", "evidence",
                    "findings", "sign_off")
    ):
        raise ValueError("Audit data is empty.")

    buffer = BytesIO()
    styles = _styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=23 * mm,
        bottomMargin=22 * mm,
        title=f"CyGRC Audit Pack - {audit['audit_id']}",
        author="CyGRC",
    )

    story = []

    # Cover page
    story.extend(
        [
            Spacer(1, 35 * mm),
            Paragraph("CyGRC", styles["CoverTitle"]),
            Paragraph("AUDIT PACK", styles["SectionHeading"]),
            Spacer(1, 8 * mm),
            Paragraph(_text(audit.get("title", "Audit Report")),
                      styles["CoverTitle"]),
            Spacer(1, 12 * mm),
            _paragraph("Audit ID", styles),
            _paragraph(audit["audit_id"], styles, "SmallText"),
            Spacer(1, 4 * mm),
            _paragraph("Organization", styles),
            _paragraph(audit.get("organization"), styles, "SmallText"),
            Spacer(1, 4 * mm),
            _paragraph(
                "Generated (UTC): "
                + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                styles,
                "SmallText",
            ),
            Spacer(1, 12 * mm),
            Paragraph(
                "Confidential — prepared from supplied audit data",
                styles["SmallText"],
            ),
            PageBreak(),
        ]
    )

    # Executive summary
    story.append(Paragraph("1. Executive Summary", styles["SectionHeading"]))
    story.append(
        _paragraph(
            audit.get("executive_summary", "No summary provided."),
            styles,
            "SmallText",
        )
    )
    story.append(Spacer(1, 8 * mm))

    # Control matrix
    story.append(Paragraph("2. Control Matrix", styles["SectionHeading"]))
    controls = audit.get("controls") or []
    control_rows = [["Control ID", "Control", "Status", "Notes"]]

    for item in controls:
        control_rows.append(
            [
                item.get("control_id", ""),
                item.get("title", ""),
                item.get("status", ""),
                item.get("notes", ""),
            ]
        )

    if not controls:
        control_rows.append(["No controls supplied", "", "", ""])

    story.append(
        _table(
            control_rows,
            [27 * mm, 48 * mm, 25 * mm, 56 * mm],
            styles,
        )
    )
    story.append(Spacer(1, 8 * mm))

    # Evidence and exact supplied hashes
    story.append(Paragraph("3. Evidence & SHA-256", styles["SectionHeading"]))
    evidence = audit.get("evidence") or []
    evidence_rows = [["Evidence", "SHA-256"]]

    for item in evidence:
        evidence_rows.append(
            [
                item.get("name", ""),
                item.get("sha256", ""),
            ]
        )

    if not evidence:
        evidence_rows.append(["No evidence supplied", ""])

    story.append(
        _table(evidence_rows, [65 * mm, 91 * mm], styles)
    )
    story.append(Spacer(1, 8 * mm))

    # Findings
    story.append(Paragraph("4. Findings", styles["SectionHeading"]))
    findings = audit.get("findings") or []

    if findings:
        finding_rows = [["Finding", "Severity", "Status"]]
        for item in findings:
            finding_rows.append(
                [
                    item.get("description", ""),
                    item.get("severity", ""),
                    item.get("status", ""),
                ]
            )
        story.append(
            _table(
                finding_rows,
                [92 * mm, 30 * mm, 34 * mm],
                styles,
            )
        )
    else:
        story.append(
            _paragraph("No findings supplied.", styles, "SmallText")
        )

    story.append(Spacer(1, 8 * mm))

    # Digital sign-off
    story.append(Paragraph("5. Audit Sign-Off", styles["SectionHeading"]))
    sign_off = audit.get("sign_off") or {}

    signoff_rows = [["Field", "Value"]]
    for label, key in [
        ("Approved By", "approved_by"),
        ("Role", "role"),
        ("Date", "date"),
        ("Status", "status"),
        ("Review Reference", "review_reference"),
    ]:
        signoff_rows.append([label, sign_off.get(key, "Not provided")])

    story.append(
        _table(signoff_rows, [48 * mm, 108 * mm], styles)
    )

    doc.build(
        story,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )

    return buffer.getvalue()
