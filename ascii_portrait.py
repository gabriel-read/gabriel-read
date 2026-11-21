"""Convierte una foto en un retrato ASCII (fragmento SVG animado).

Uso independiente (vista previa):
    python tools/ascii_portrait.py foto.jpg salida.svg
"""
import sys
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

RAMP = " .,:;-=+*x#%@"   # de vacío a denso (fondo oscuro: brillo = densidad)
FONT = 7.0               # tamaño de letra en px
BG_CUT = 128             # sensibilidad para apagar el fondo (0-255)
CELL_W, CELL_H = FONT * 0.6, FONT * 1.0


def _load(path):
    img = ImageOps.exif_transpose(Image.open(path))
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (0, 0, 0))
        bg.paste(img, mask=img.getchannel("A"))
        img = bg
    img = img.convert("RGB")
    w, h = img.size
    s = min(w, h)
    return img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))


def _subject_mask(img):
    """Separa a la persona del fondo con GrabCut (OpenCV). Sin OpenCV, no recorta."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return Image.new("L", img.size, 255)
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    h, w = arr.shape[:2]
    m = np.zeros((h, w), np.uint8)
    rect = (int(w * 0.04), int(h * 0.02), int(w * 0.92), int(h * 0.98))
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(arr, m, rect, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    fg = np.where((m == 1) | (m == 3), 255, 0).astype("uint8")
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    return Image.fromarray(fg).filter(ImageFilter.GaussianBlur(3))


def _local_contrast(gray):
    """Realza rasgos (ojos, barba, contornos) con CLAHE; sin OpenCV usa autocontraste."""
    try:
        import cv2
        import numpy as np
        out = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(np.array(gray))
        return Image.fromarray(out).filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
    except ImportError:
        return ImageOps.autocontrast(gray, cutoff=1)


def portrait_fragment(src, cx, cy, r, tint=(147, 197, 253), tint_mix=0.5):
    """Devuelve (defs_css, cuerpo_svg) del retrato dentro de un círculo de radio r."""
    img = _load(src)
    cols = int(2 * r / CELL_W)
    rows = int(2 * r / CELL_H)
    small = img.resize((cols, rows), Image.LANCZOS)
    mask = _subject_mask(img)
    big = _local_contrast(ImageOps.grayscale(img))
    gray = big.resize((cols, rows), Image.LANCZOS)
    edge = mask.resize((cols, rows), Image.LANCZOS)
    color = ImageEnhance.Color(small).enhance(1.5)

    ox, oy = cx - cols * CELL_W / 2, cy - rows * CELL_H / 2
    chars = []
    for y in range(rows):
        for x in range(cols):
            px, py = ox + x * CELL_W, oy + (y + 1) * CELL_H
            if (px + CELL_W / 2 - cx) ** 2 + (py - CELL_H / 2 - cy) ** 2 > (r - 4) ** 2:
                continue
            lum = gray.getpixel((x, y)) / 255
            if edge.getpixel((x, y)) < BG_CUT:
                lum *= 0.0
            ch = RAMP[min(len(RAMP) - 1, int(lum ** 1.15 * len(RAMP)))]
            if ch == " ":
                continue
            rr, gg, bb = color.getpixel((x, y))
            mix = lambda a, b: int(a * (1 - tint_mix) + b * tint_mix)
            fill = "#%02x%02x%02x" % (mix(rr, tint[0]), mix(gg, tint[1]), mix(bb, tint[2]))
            delay = round(y / rows * 1.8, 2)
            chars.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{fill}" style="animation-delay:{delay}s">{ch}</text>')

    css = (
        "g.ascii text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
        f"font-size:{FONT}px;font-weight:700;opacity:0;animation:asciiIn .5s ease forwards}}"
        "@keyframes asciiIn{to{opacity:1}}"
        f".ring{{transform-origin:{cx}px {cy}px;animation:ringSpin 40s linear infinite}}"
        "@keyframes ringSpin{to{transform:rotate(360deg)}}"
    )
    R = r + 10
    body = f'''<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#portraitGlow)"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1c2947"/>
  <g class="ring" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round">
    <path d="M{cx} {cy - R} A{R} {R} 0 0 1 {cx + R} {cy}" opacity=".7"/>
    <path d="M{cx} {cy + R} A{R} {R} 0 0 1 {cx - R} {cy}" opacity=".35"/>
  </g>
  <g class="ascii">
{chr(10).join(chars)}
  </g>'''
    glow = '''<radialGradient id="portraitGlow" cx="50%" cy="45%" r="55%">
      <stop offset="0" stop-color="#1d4ed8" stop-opacity=".22"/>
      <stop offset="1" stop-color="#1d4ed8" stop-opacity="0"/>
    </radialGradient>'''
    return css, glow, body


if __name__ == "__main__":
    css, glow, body = portrait_fragment(sys.argv[1], 220, 220, 190)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="440" height="440" viewBox="0 0 440 440">
  <defs>{glow}<style>{css}</style></defs>
  <rect width="440" height="440" fill="#060a13"/>
  {body}
</svg>''')
