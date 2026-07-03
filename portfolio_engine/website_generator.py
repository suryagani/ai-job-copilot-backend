from __future__ import annotations

from .theme_selector import get_theme


def build_portfolio_html(content: dict, selected_theme: str) -> str:
    theme = get_theme(selected_theme)
    sections = [
        ('About', content.get('about_me', '')),
        ('Skills', '<br/>'.join(content.get('skills_section', []))),
        ('Projects', '<br/>'.join(content.get('project_showcase', []))),
        ('Case Studies', '<br/><br/>'.join(content.get('project_case_studies', []))),
        ('Timeline', '<br/>'.join(content.get('timeline', []))),
        ('Contact', '<br/>'.join(content.get('contact_section', []))),
    ]
    blocks = []
    for heading, body in sections:
        if str(body or '').strip():
            blocks.append(f"<section><h2>{heading}</h2><p>{body}</p></section>")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{content.get('seo_meta_title', '')}</title>
  <meta name="description" content="{content.get('seo_meta_description', '')}" />
  <style>
    :root {{
      --bg: {theme['background']};
      --surface: {theme['surface']};
      --text: {theme['text']};
      --muted: {theme['muted']};
      --accent: {theme['accent']};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: radial-gradient(circle at top right, rgba(79,209,197,0.18), transparent 28%), var(--bg); color: var(--text); line-height: 1.6; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 72px 24px; }}
    .hero {{ padding: 36px; border-radius: 28px; background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 60px rgba(0,0,0,0.32); }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.4rem); }}
    h2 {{ font-size: 1.25rem; color: var(--accent); margin-top: 32px; }}
    p {{ color: var(--muted); margin: 0; }}
    .tagline {{ color: var(--text); font-weight: 600; margin-top: 10px; }}
    section {{ margin-top: 28px; padding: 24px; border-radius: 22px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); }}
    footer {{ margin-top: 28px; color: var(--muted); font-size: 0.95rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <p>{content.get('professional_bio', '')}</p>
      <h1>{content.get('personal_tagline', '')}</h1>
      <p class="tagline">{content.get('seo_meta_description', '')}</p>
    </div>
    {''.join(blocks)}
    <footer>{content.get('professional_footer', '')}</footer>
  </div>
</body>
</html>'''
