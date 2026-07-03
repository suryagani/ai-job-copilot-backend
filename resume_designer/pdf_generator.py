from io import BytesIO

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def build_pdf(render_payload: dict) -> BytesIO:
    layout = render_payload["layout"]
    spacing = layout["spacing"]
    typography = layout["typography"]
    theme = layout["theme"]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=render_payload["page_size"],
        leftMargin=spacing["margins"],
        rightMargin=spacing["margins"],
        topMargin=spacing["margins"],
        bottomMargin=spacing["margins"],
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Title"],
        fontName=f"{theme['pdf_font']}-Bold",
        fontSize=typography["title_size"],
        leading=typography["title_size"] + 4,
        alignment=TA_LEFT,
        textColor=theme["heading_color"],
        spaceAfter=spacing["title_after"],
    )
    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        parent=styles["Normal"],
        fontName=f"{theme['pdf_font']}-Oblique",
        fontSize=typography["subtitle_size"],
        leading=typography["subtitle_size"] + 3,
        textColor=theme["accent_color"],
        spaceAfter=spacing["section_after"],
    )
    heading_style = ParagraphStyle(
        "ResumeHeading",
        parent=styles["Heading2"],
        fontName=f"{theme['pdf_font']}-Bold",
        fontSize=typography["heading_size"],
        leading=typography["heading_size"] + 3,
        textColor=theme["heading_color"],
        spaceBefore=spacing["section_before"],
        spaceAfter=spacing["section_after"],
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName=theme["pdf_font"],
        fontSize=typography["body_size"],
        leading=spacing["line_leading"],
        textColor=theme["body_color"],
        spaceAfter=spacing["bullet_gap"],
    )
    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
    )

    story = [Paragraph(render_payload["title"], title_style)]
    if render_payload["subtitle"]:
        story.append(Paragraph(render_payload["subtitle"], subtitle_style))

    for section in render_payload["sections"]:
        story.append(Paragraph(section["heading"], heading_style))
        for line in section["lines"]:
            if line.startswith("- "):
                story.append(Paragraph(f"• {line[2:].strip()}", bullet_style))
            else:
                story.append(Paragraph(line, body_style))
        story.append(Spacer(1, spacing["section_after"]))

    doc.build(story)
    buffer.seek(0)
    return buffer
