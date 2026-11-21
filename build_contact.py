"""Genera assets/contact.svg con el retrato ASCII incrustado.

Uso:
    python tools/build_contact.py foto.jpg
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ascii_portrait import portrait_fragment

ROWS = [
    ("GITHUB", "@gabriel-read"),
    ("LINKEDIN", "linkedin.com/in/gabriel-read"),
    ("BASED IN", "Santo Domingo, DR"),
    ("FOCUS", "Risk · Treasury · Data"),
]

W, H = 1200, 440
CX, CY, R = 950, 222, 168


def build(photo, out):
    css, glow, body = portrait_fragment(photo, CX, CY, R)
    rows = []
    for i, (k, v) in enumerate(ROWS):
        y = 196 + i * 50
        rows.append(
            f'<circle cx="64" cy="{y - 5}" r="3" fill="#3b82f6"/>'
            f'<text x="84" y="{y}" class="mono lbl" font-size="11">{k}</text>'
            f'<text x="230" y="{y}" class="mono" font-size="16" fill="#e6edf7">{v}</text>'
            f'<line x1="56" y1="{y + 20}" x2="600" y2="{y + 20}" stroke="#141e36"/>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contact — Gabriel Read">
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#111a30" stroke-width="1"/>
    </pattern>
    {glow}
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
    <style>
      .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}}
      .lbl{{font-size:12px;letter-spacing:3px;fill:#5b6b8c}}
      .cursor{{animation:blink 1.1s steps(1) infinite}}
      @keyframes blink{{50%{{opacity:0}}}}
      {css}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="#060a13"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="#1c2947"/>

  <text x="56" y="56" class="mono lbl">CONTACT / OPEN CHANNEL</text>
  <text x="56" y="104" class="mono" font-size="28" font-weight="700" fill="#e6edf7">Let's talk risk, data &amp; automation<tspan fill="#3b82f6" class="cursor">_</tspan></text>
  <line x1="56" y1="134" x2="600" y2="134" stroke="#1c2947" stroke-dasharray="6 6"/>
  {"".join(rows)}

  {body}
</svg>
'''
    Path(out).write_text(svg, encoding="utf-8")
    print(out, "ok")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "assets/contact.svg")
