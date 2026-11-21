"""Une las secciones en un solo panel continuo: assets/profile.svg

Uso:
    python tools/build_profile.py
"""
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SECTIONS = ["hero", "about", "stack", "projects", "timeline", "contact"]
W = 1200
PAD_X = 56


def parse(name):
    src = (ASSETS / f"{name}.svg").read_text(encoding="utf-8")
    h = int(re.search(r'<svg[^>]*\bheight="(\d+)"', src).group(1))
    defs = re.search(r"<defs>(.*?)</defs>", src, re.S).group(1)
    body = src[src.index("</defs>") + len("</defs>"): src.rindex("</svg>")]

    # fondo y borde propios de cada tarjeta: se reemplazan por el panel común
    body = re.sub(r'<g clip-path="url\(#card\)">.*?</g>', "", body, count=1, flags=re.S)
    body = re.sub(r'<rect x="\.5" y="\.5"[^>]*/>', "", body, count=1)
    defs = re.sub(r'<pattern id="grid".*?</pattern>', "", defs, flags=re.S)
    defs = re.sub(r'<clipPath id="card">.*?</clipPath>', "", defs, flags=re.S)

    # ids únicos por sección
    for i in set(re.findall(r'id="([^"]+)"', defs)):
        defs = defs.replace(f'id="{i}"', f'id="{name}-{i}"')
        body = body.replace(f"url(#{i})", f"url(#{name}-{i})")

    style = "\n".join(re.findall(r"<style>(.*?)</style>", defs, re.S))
    defs = re.sub(r"<style>.*?</style>", "", defs, flags=re.S)
    return h, defs, style, body


def build():
    parts, y = [], 0
    all_defs, all_styles = [], []
    for i, name in enumerate(SECTIONS):
        h, defs, style, body = parse(name)
        all_defs.append(defs)
        all_styles.append(style)
        if i:
            parts.append(f'<line x1="{PAD_X}" y1="{y}" x2="{W - PAD_X}" y2="{y}" stroke="#1c2947"/>')
            parts.append(f'<circle cx="{PAD_X}" cy="{y}" r="2.5" fill="#3b82f6"/>'
                         f'<circle cx="{W - PAD_X}" cy="{y}" r="2.5" fill="#3b82f6"/>')
        parts.append(f'<g transform="translate(0 {y})">{body}</g>')
        y += h
    H = y

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Gabriel Read — Actuarial Mathematics, Financial Risk, Compliance &amp; Data">
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#111a30" stroke-width="1"/>
    </pattern>
    <radialGradient id="glowTop" cx="78%" cy="8%" r="40%">
      <stop offset="0" stop-color="#1d4ed8" stop-opacity=".22"/>
      <stop offset="1" stop-color="#1d4ed8" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="spine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3b82f6" stop-opacity=".0"/>
      <stop offset=".15" stop-color="#3b82f6" stop-opacity=".5"/>
      <stop offset=".85" stop-color="#8b5cf6" stop-opacity=".5"/>
      <stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="panel"><rect width="{W}" height="{H}" rx="22"/></clipPath>
    {"".join(all_defs)}
    <style>
      {"".join(dict.fromkeys(all_styles))}
    </style>
  </defs>
  <g clip-path="url(#panel)">
    <rect width="{W}" height="{H}" fill="#060a13"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <rect width="{W}" height="900" fill="url(#glowTop)"/>
    <rect x="24" y="0" width="1.5" height="{H}" fill="url(#spine)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="#1c2947"/>
  {chr(10).join(parts)}
</svg>
'''
    out = ASSETS / "profile.svg"
    out.write_text(svg, encoding="utf-8")
    print(out, f"{W}x{H}")


if __name__ == "__main__":
    build()
