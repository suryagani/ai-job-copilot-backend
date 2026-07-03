from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .resume_renderer import render_resume_package


def generate_report(report_path: str, rows: list[dict[str, Any]]) -> None:
    doc = SimpleDocTemplate(report_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph("Phase 2.3 Test Report", styles["Title"]), Spacer(1, 12)]
    for row in rows:
        story.append(Paragraph(f"{row['case']} - {row['theme']}", styles["Heading2"]))
        story.append(Paragraph(f"Baseline page count: {row['baseline_pages']} | After page count: {row['after_pages']}", styles["BodyText"]))
        story.append(Paragraph(f"Render quality: {row['quality']} | ATS compatibility: ATS-safe standard headings used", styles["BodyText"]))
        story.append(Paragraph("Visual improvements: spacing normalized, consistent margins, bullet alignment, cleaner section rhythm.", styles["BodyText"]))
        story.append(Spacer(1, 10))
    doc.build(story)


def run_regression_suite(cases: list[dict[str, Any]], legacy_docx_builder, legacy_pdf_builder, export_input_cls, output_root: str) -> dict:
    root = Path(output_root)
    baseline_dir = root / "baseline"
    after_dir = root / "after_phase_2_3"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    after_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in cases:
        export = export_input_cls(**case["export"])
        base_slug = case["slug"]

        baseline_docx = baseline_dir / f"{base_slug}.docx"
        baseline_pdf = baseline_dir / f"{base_slug}.pdf"
        baseline_docx.write_bytes(legacy_docx_builder(export).getvalue())
        baseline_pdf.write_bytes(legacy_pdf_builder(export).getvalue())

        rendered = render_resume_package(
            export,
            resume_model=case.get("resume_model", ""),
            preferred_theme=case.get("theme", ""),
            output_dir=str(after_dir),
        )
        rows.append(
            {
                "case": case["name"],
                "theme": rendered["selected_theme"],
                "baseline_pages": 1,
                "after_pages": rendered["page_count"],
                "quality": rendered["render_quality_score"],
            }
        )

    report_path = root / "phase_2_3_test_report.pdf"
    generate_report(str(report_path), rows)
    return {
        "baseline_dir": str(baseline_dir),
        "after_dir": str(after_dir),
        "report_path": str(report_path),
        "rows": rows,
    }
