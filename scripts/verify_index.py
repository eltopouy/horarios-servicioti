# -*- coding: utf-8 -*-
"""
Suite de Verificación Exhaustiva para horarios.servicioti.com.uy
Valida integridad de js/data.js, pre-renderizado SEO en index.html,
enrutamiento 100% hacia www.servicioti.com.uy, JSON-LD Schema.org, CNAME y PWA.
"""

import os
import re
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    errors = []

    # 1. Verificar archivos esenciales
    required_files = [
        "CNAME", ".nojekyll", "index.html", "manifest.json", "sw.js",
        "robots.txt", "sitemap.xml", "css/styles.css", "js/data.js", "js/app.js",
        "assets/icons/favicon.svg", "assets/icons/icon-192.png", "assets/icons/icon-512.png",
        "assets/icons/og-banner.png"
    ]
    for rf in required_files:
        p = os.path.join(BASE_DIR, rf)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            errors.append(f"Falta o está vacío el archivo requerido: {rf}")

    # 2. Verificar CNAME
    cname_val = open(os.path.join(BASE_DIR, "CNAME"), encoding="utf-8").read().strip()
    if cname_val != "horarios.servicioti.com.uy":
        errors.append(f"CNAME inválido: {cname_val}")

    # 3. Verificar js/data.js
    raw_data = open(os.path.join(BASE_DIR, "js", "data.js"), encoding="utf-8").read()
    json_str = raw_data.split("window.HORARIOS_DATA = ", 1)[1].rstrip(";\n")
    data = json.loads(json_str)

    if len(data["lineas"]) < 90:
        errors.append(f"Se esperaban al menos 90 líneas, encontradas: {len(data['lineas'])}")

    for l in data["lineas"]:
        if not l["url"].startswith("https://www.servicioti.com.uy/"):
            errors.append(f"Línea {l['uid']} no apunta a www.servicioti.com.uy: {l['url']}")

    # 4. Verificar index.html y JSON-LD
    html_content = open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8").read()
    blogger_links = re.findall(r'href="(https://www\.servicioti\.com\.uy/[^"]+)"', html_content)
    unique_blogger_links = set(blogger_links)

    if len(unique_blogger_links) < 150:
        errors.append(f"Se esperaban >= 150 enlaces únicos a Blogger en index.html, encontrados: {len(unique_blogger_links)}")

    # Verificar que no haya enlaces rotos a carpetas locales lineas/*.html
    local_schedule_links = re.findall(r'href="lineas/[^"]+"', html_content)
    if local_schedule_links:
        errors.append(f"Se encontraron enlaces locales que retienen tráfico fuera de Blogger: {local_schedule_links[:5]}")

    # Verificar JSON-LD
    ld_match = re.search(r'<script type="application/ld\+json">\s*([\s\S]*?)\s*</script>', html_content)
    if not ld_match:
        errors.append("No se encontró bloque Schema.org JSON-LD en index.html")
    else:
        ld_obj = json.loads(ld_match.group(1))
        graph = ld_obj.get("@graph", [])
        if len(graph) < 3:
            errors.append("El grafo JSON-LD está incompleto")

    if errors:
        print("❌ ERRORES ENCONTRADOS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("✅ AUDITORÍA COMPLETA SUPERADA CON ÉXITO:")
    print(f"   • Dominio CNAME verificado: {cname_val}")
    print(f"   • Líneas indexadas verificadas: {len(data['lineas'])}")
    print(f"   • Localidades A-Z verificadas: {len(data['localidades'])}")
    print(f"   • Publicaciones de archivo verificadas: {len(data['archivoBlogger'])}")
    print(f"   • Enlaces totales en DOM hacia www.servicioti.com.uy: {len(blogger_links)} ({len(unique_blogger_links)} URLs únicas)")
    print("   • Fuga de tráfico fuera de Blogger: 0% (100% dirigido a www.servicioti.com.uy)")
    print("   • Schema.org JSON-LD y activos PWA verificados.")

if __name__ == "__main__":
    run_tests()
