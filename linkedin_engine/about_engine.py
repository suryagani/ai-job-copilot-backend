from __future__ import annotations


def clean_about(about: str) -> str:
    text = str(about or "").replace("\r", "").strip()
    paragraphs = [" ".join(line.split()) for line in text.splitlines()]
    blocks = [block.strip() for block in "\n".join(paragraphs).split("\n\n") if block.strip()]
    return "\n\n".join(blocks).strip()
