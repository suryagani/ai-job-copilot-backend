from __future__ import annotations

from .bio_generator import clean_text


def normalize_readme(value: str) -> str:
    return clean_text(value)


def fallback_readme(full_name: str, tagline: str, skills: list[str], projects: list[str], contact_lines: list[str]) -> str:
    skill_line = ', '.join(skills[:8]) if skills else 'Professional strengths tailored to the target role'
    project_lines = '\n'.join(f'- {item}' for item in projects[:4]) if projects else '- Highlighted project case studies available in the portfolio'
    contact_block = '\n'.join(f'- {line}' for line in contact_lines[:4]) if contact_lines else '- Contact details available on request'
    return clean_text(f'''# {full_name or 'Professional Portfolio'}

## Professional Banner
{tagline}

## Introduction
{tagline}

## Tech Stack / Core Strengths
{skill_line}

## Featured Projects
{project_lines}

## Contact
{contact_block}
''')
