# -*- coding: utf-8 -*-
"""Genera íconos vectoriales y PNG (192, 512 y OpenGraph 1200x630) para horarios.servicioti.com.uy"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#072146"/>
      <stop offset="55%" stop-color="#0056b3"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg)"/>
  <circle cx="410" cy="102" r="46" fill="url(#gold)"/>
  <!-- Bus Body -->
  <rect x="96" y="116" width="320" height="248" rx="40" fill="#ffffff"/>
  <rect x="96" y="116" width="320" height="54" rx="26" fill="url(#gold)"/>
  <rect x="156" y="132" width="200" height="22" rx="11" fill="#072146"/>
  <!-- Windshield -->
  <rect x="120" y="186" width="272" height="96" rx="18" fill="#0f172a"/>
  <path d="M136 200 L220 200 L185 268 L136 268 Z" fill="#38bdf8" opacity="0.35"/>
  <!-- Headlights & Grille -->
  <circle cx="144" cy="322" r="18" fill="#f59e0b"/>
  <circle cx="368" cy="322" r="18" fill="#f59e0b"/>
  <rect x="192" y="312" width="128" height="20" rx="10" fill="#cbd5e1"/>
  <!-- Wheels -->
  <rect x="128" y="356" width="52" height="44" rx="16" fill="#0f172a"/>
  <rect x="332" y="356" width="52" height="44" rx="16" fill="#0f172a"/>
  <!-- Clock Hands on Gold Badge -->
  <circle cx="410" cy="102" r="34" fill="#072146"/>
  <line x1="410" y1="102" x2="410" y2="80" stroke="#fbbf24" stroke-width="6" stroke-linecap="round"/>
  <line x1="410" y1="102" x2="428" y2="102" stroke="#fbbf24" stroke-width="6" stroke-linecap="round"/>
</svg>"""

with open(os.path.join(ICONS_DIR, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)

def make_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 512.0
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(112 * s), fill=(7, 33, 70, 255))
    draw.rounded_rectangle([int(12 * s), int(12 * s), int(500 * s), int(500 * s)], radius=int(100 * s), fill=(0, 86, 179, 255))
    # Bus body
    draw.rounded_rectangle([int(96 * s), int(116 * s), int(416 * s), int(364 * s)], radius=int(40 * s), fill=(255, 255, 255, 255))
    draw.rounded_rectangle([int(96 * s), int(116 * s), int(416 * s), int(172 * s)], radius=int(24 * s), fill=(251, 191, 36, 255))
    draw.rounded_rectangle([int(156 * s), int(132 * s), int(356 * s), int(154 * s)], radius=int(10 * s), fill=(7, 33, 70, 255))
    # Windshield
    draw.rounded_rectangle([int(120 * s), int(186 * s), int(392 * s), int(282 * s)], radius=int(18 * s), fill=(15, 23, 42, 255))
    # Headlights
    draw.ellipse([int(126 * s), int(304 * s), int(162 * s), int(340 * s)], fill=(245, 158, 11, 255))
    draw.ellipse([int(350 * s), int(304 * s), int(386 * s), int(340 * s)], fill=(245, 158, 11, 255))
    draw.rounded_rectangle([int(192 * s), int(312 * s), int(320 * s), int(332 * s)], radius=int(10 * s), fill=(203, 213, 225, 255))
    # Wheels
    draw.rounded_rectangle([int(128 * s), int(356 * s), int(180 * s), int(404 * s)], radius=int(14 * s), fill=(15, 23, 42, 255))
    draw.rounded_rectangle([int(332 * s), int(356 * s), int(384 * s), int(404 * s)], radius=int(14 * s), fill=(15, 23, 42, 255))
    # Clock badge
    draw.ellipse([int(356 * s), int(48 * s), int(464 * s), int(156 * s)], fill=(251, 191, 36, 255))
    draw.ellipse([int(368 * s), int(60 * s), int(452 * s), int(144 * s)], fill=(7, 33, 70, 255))
    return img

make_icon(192).save(os.path.join(ICONS_DIR, "icon-192.png"))
make_icon(512).save(os.path.join(ICONS_DIR, "icon-512.png"))

# OpenGraph Banner 1200x630
og = Image.new("RGB", (1200, 630), (7, 33, 70))
draw = ImageDraw.Draw(og)
for y in range(630):
    r = int(7 + (y / 630) * 5)
    g = int(33 + (y / 630) * 53)
    b = int(70 + (y / 630) * 109)
    draw.line([(0, y), (1200, y)], fill=(r, g, b))

draw.rounded_rectangle([48, 48, 1152, 582], radius=32, outline=(251, 191, 36), width=4)
bus_icon = make_icon(240)
og.paste(bus_icon, (80, 195), bus_icon)

try:
    font_lg = ImageFont.truetype("arialbd.ttf", 54)
    font_md = ImageFont.truetype("arial.ttf", 30)
    font_sm = ImageFont.truetype("arialbd.ttf", 24)
except Exception:
    font_lg = ImageFont.load_default()
    font_md = ImageFont.load_default()
    font_sm = ImageFont.load_default()

draw.rounded_rectangle([360, 145, 780, 192], radius=22, fill=(251, 191, 36))
draw.text((382, 155), "ÍNDICE OFICIAL SERVICIOTI 2026", fill=(7, 33, 70), font=font_sm)
draw.text((360, 215), "Horarios de Ómnibus Uruguay", fill=(255, 255, 255), font=font_lg)
draw.text((360, 285), "COPSA • CUTCSA • Línea Este • COETC", fill=(56, 189, 248), font=font_lg)
draw.text((360, 370), "90 Líneas • 89 Localidades • Radar de Próximo Coche en Vivo", fill=(226, 232, 240), font=font_md)
draw.text((360, 425), "horarios.servicioti.com.uy  →  www.servicioti.com.uy", fill=(251, 191, 36), font=font_md)

og.save(os.path.join(ICONS_DIR, "og-banner.png"), optimize=True)
print("✅ Íconos y banner OpenGraph generados correctamente.")
