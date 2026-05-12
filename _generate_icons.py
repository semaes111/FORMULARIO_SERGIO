"""
Generador de iconos para formulario1.nexthorizont.ai
Reproduce el logo de la clínica (.clinic-logo) en formato icono:
  - Fondo cuadrado redondeado con degradado linear-gradient(135deg, #2E6B9E, #1B3A5C)
  - Icono de edificio/clínica en blanco (mismo path SVG del index.html)
Genera: favicon.ico, favicon-32x32.png, apple-touch-icon*.png
"""

from PIL import Image, ImageDraw
from pathlib import Path

OUT_DIR = Path(__file__).parent

# Colores del theme (mismos del CSS root del index.html)
AZUL_MEDIO = (46, 107, 158)        # #2E6B9E
AZUL_PROFUNDO = (27, 58, 92)       # #1B3A5C
BLANCO = (255, 255, 255)


def make_gradient_rounded_square(size: int, radius_pct: float = 0.22) -> Image.Image:
    """
    Crea un cuadrado con esquinas redondeadas y degradado diagonal
    (135deg = top-left → bottom-right), color azul medio → azul profundo.
    radius_pct controla el redondeado (0.22 = estándar iOS app icon).
    """
    # 1) Generar degradado en imagen base
    base = Image.new("RGB", (size, size), AZUL_MEDIO)
    pixels = base.load()
    # Gradiente diagonal 135deg: progresa desde top-left (medio) a bottom-right (profundo)
    diag_max = (size - 1) * 2
    for y in range(size):
        for x in range(size):
            t = (x + y) / diag_max  # 0 → 1
            r = int(AZUL_MEDIO[0] * (1 - t) + AZUL_PROFUNDO[0] * t)
            g = int(AZUL_MEDIO[1] * (1 - t) + AZUL_PROFUNDO[1] * t)
            b = int(AZUL_MEDIO[2] * (1 - t) + AZUL_PROFUNDO[2] * t)
            pixels[x, y] = (r, g, b)

    # 2) Aplicar máscara redondeada vía alpha channel
    radius = int(size * radius_pct)
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)

    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(base, (0, 0), mask)
    return result


def draw_clinic_icon(img: Image.Image) -> Image.Image:
    """
    Dibuja el icono de clínica (edificio con ventanas) reproduciendo el
    path SVG de .clinic-logo del index.html del formulario.

    SVG original (viewBox 0 0 24 24, stroke-width 2):
        <path d="M3 21h18"/>                            base
        <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"/>  cuerpo
        <path d="M9 8h1"/><path d="M9 12h1"/><path d="M9 16h1"/>  ventanas izq
        <path d="M14 8h1"/><path d="M14 12h1"/><path d="M14 16h1"/> ventanas der
    """
    W = img.size[0]
    draw = ImageDraw.Draw(img)

    # Inset del icono respecto al cuadrado (deja padding ~22% para que respire)
    pad = W * 0.22
    iw = W - 2 * pad           # ancho útil del icono
    # Escala desde viewBox 24x24 al espacio útil
    scale = iw / 24.0
    # Stroke escalado (SVG usa stroke-width 2)
    stroke = max(2, int(2 * scale * 0.95))

    def sx(x): return pad + x * scale
    def sy(y): return pad + y * scale

    # 1) Base horizontal: M3 21 h18
    draw.line([(sx(3), sy(21)), (sx(21), sy(21))],
              fill=BLANCO, width=stroke)

    # 2) Cuerpo del edificio: M5 21 V5 a2 2 0 0 1 2-2 h10 a2 2 0 0 1 2 2 V21
    # Lo trazamos como dos verticales + un techo con esquinas redondeadas.
    body_left = sx(5)
    body_right = sx(19)
    body_top = sy(3)            # techo
    body_bottom = sy(21)
    corner_r = 2 * scale        # radio de las esquinas superiores (SVG dice a2)
    # Vertical izquierda (desde abajo hasta donde empieza el corner)
    draw.line([(body_left, body_bottom), (body_left, sy(5))],
              fill=BLANCO, width=stroke)
    # Vertical derecha
    draw.line([(body_right, body_bottom), (body_right, sy(5))],
              fill=BLANCO, width=stroke)
    # Techo recto entre los dos corners
    draw.line([(sx(7), body_top), (sx(17), body_top)],
              fill=BLANCO, width=stroke)
    # Corner top-left (arc) — aproximación con elipse
    bbox_tl = (body_left, body_top, body_left + 2 * corner_r, body_top + 2 * corner_r)
    draw.arc(bbox_tl, start=180, end=270, fill=BLANCO, width=stroke)
    # Corner top-right
    bbox_tr = (body_right - 2 * corner_r, body_top, body_right, body_top + 2 * corner_r)
    draw.arc(bbox_tr, start=270, end=360, fill=BLANCO, width=stroke)

    # 3) Ventanas: 2 columnas (x=9 y x=14) × 3 filas (y=8, 12, 16)
    win_w = 1 * scale          # ancho de ventana (SVG: h1)
    for col_x in (9, 14):
        for row_y in (8, 12, 16):
            x0 = sx(col_x)
            y0 = sy(row_y)
            x1 = x0 + win_w
            draw.line([(x0, y0), (x1, y0)], fill=BLANCO, width=stroke)

    return img


def render(size: int) -> Image.Image:
    """Renderiza el icono completo al tamaño pedido."""
    # Renderizamos siempre a 4x el tamaño objetivo y luego downsample
    # con filtro de alta calidad — produce bordes anti-aliased nítidos.
    work_size = size * 4
    img = make_gradient_rounded_square(work_size)
    img = draw_clinic_icon(img)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    print("Generando iconos del formulario clínico…")

    # ── favicon-32x32.png ─────────────────────────────────────────────
    p = OUT_DIR / "favicon-32x32.png"
    render(32).save(p, "PNG", optimize=True)
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    # ── favicon.ico (multi-resolution: 16, 32, 48) ─────────────────────
    p = OUT_DIR / "favicon.ico"
    # PIL puede empaquetar múltiples sizes en un .ico
    ico_base = render(48)
    ico_base.save(
        p, format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    # ── apple-touch-icon.png (180x180, estándar iOS modernos) ─────────
    apple_180 = render(180)
    p = OUT_DIR / "apple-touch-icon.png"
    apple_180.save(p, "PNG", optimize=True)
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    # ── apple-touch-icon-precomposed.png (mismo PNG, alias iOS antiguos) ─
    p = OUT_DIR / "apple-touch-icon-precomposed.png"
    apple_180.save(p, "PNG", optimize=True)
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    # ── apple-touch-icon-120x120.png (iPhone retina) ──────────────────
    apple_120 = render(120)
    p = OUT_DIR / "apple-touch-icon-120x120.png"
    apple_120.save(p, "PNG", optimize=True)
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    # ── apple-touch-icon-120x120-precomposed.png ───────────────────────
    p = OUT_DIR / "apple-touch-icon-120x120-precomposed.png"
    apple_120.save(p, "PNG", optimize=True)
    print(f"  ✓ {p.name}  ({p.stat().st_size} bytes)")

    print("Listo.")


if __name__ == "__main__":
    main()
