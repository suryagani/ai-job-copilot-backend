from __future__ import annotations


def clean_text(value: str) -> str:
    text = str(value or '').replace('\r', '').strip()
    lines = [' '.join(line.split()) for line in text.splitlines()]
    blocks = [block.strip() for block in '\n'.join(lines).split('\n\n') if block.strip()]
    return '\n\n'.join(blocks).strip()


def clean_list(values, limit: int | None = None) -> list[str]:
    cleaned = []
    for value in values or []:
        text = str(value or '').strip().lstrip('-? ')
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit] if limit else cleaned
