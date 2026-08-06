from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import A4, letter

from .docx_generator import build_docx
from .layout_engine import build_layout_config
from .pdf_generator import build_pdf


def _slug(value: str) -> str:
    cleaned = "-".join("".join(char if char.isalnum() else " " for char in (value or "")).split()).lower()
    return cleaned or "resume"


def _page_size_for_country(country: str):
    normalized = (country or "").strip().lower()
    if "united states" in normalized or "canada" in normalized or normalized == "usa":
        return letter
    return A4


def _normalize_sections(sections):
    normalized = []
    for section in sections:
        if hasattr(section, "heading"):
            heading = str(section.heading).strip()
            body = str(section.body).strip()
        else:
            heading = str(section.get("heading", "")).strip()
            body = str(section.get("body", "")).strip()
        if not heading or not body:
            continue
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if lines:
            normalized.append({"heading": heading, "lines": lines})
    return normalized


def _validate_render_output(docx_path: Path, pdf_path: Path) -> None:
    if not docx_path.exists() or docx_path.stat().st_size <= 0:
        raise RuntimeError("DOCX render failed validation.")
    if not pdf_path.exists() or pdf_path.stat().st_size <= 0:
        raise RuntimeError("PDF render failed validation.")
    if not pdf_path.read_bytes().startswith(b"%PDF"):
        raise RuntimeError("PDF render is invalid.")
    Document(str(docx_path))


def render_resume_package(export, resume_model: str = "", preferred_theme: str = "", output_dir: str | None = None) -> dict:
    sections = _normalize_sections(export.sections)
    word_count = sum(len(" ".join(section["lines"]).split()) for section in sections)
    layout = build_layout_config(resume_model, preferred_theme or getattr(export, "selected_theme", ""), getattr(export, "experience_level", ""), word_count)
    page_size = _page_size_for_country(export.target_country)

    render_payload = {
        "title": (export.full_name or export.target_role or "Resume").strip(),
        "subtitle": export.target_role.strip(),
        "sections": sections,
        "layout": layout,
        "page_size": page_size,
    }

    docx_buffer = build_docx(render_payload)
    pdf_buffer = build_pdf(render_payload)

    output_root = Path(output_dir or Path(__file__).resolve().parents[1] / "rendered")
    output_root.mkdir(parents=True, exist_ok=True)
    base_name = _slug(export.full_name or export.target_role or "resume")
    docx_path = output_root / f"{base_name}.docx"
    pdf_path = output_root / f"{base_name}.pdf"
    docx_path.write_bytes(docx_buffer.getvalue())
    pdf_path.write_bytes(pdf_buffer.getvalue())
    _validate_render_output(docx_path, pdf_path)

    return {
        "docx_buffer": docx_buffer,
        "pdf_buffer": pdf_buffer,
        "resume_docx_path": str(docx_path),
        "resume_pdf_path": str(pdf_path),
        "selected_theme": layout["selected_theme"],
        "page_count": layout["page_count"],
        "render_quality_score": layout["render_quality_score"],
    }
