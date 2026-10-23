# -*- coding: utf-8 -*-
"""
Compilador Maestro de Datos y Pre-Renderizador SEO para horarios.servicioti.com.uy
Extrae el 100% de las líneas, frecuencias, próximas salidas y URLs de Blogger
desde los proyectos de automatización de COPSA, CUTCSA, COPSA Este y archivo histórico.
"""

import os
import re
import sys
import io
import json
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRATCH_DIR = r"C:\Users\Andrés\.gemini\antigravity\scratch"
PROJECT_DIR = os.path.join(SCRATCH_DIR, "horarios_servicioti")
JS_DIR = os.path.join(PROJECT_DIR, "js")
ASSETS_ICONS_DIR = os.path.join(PROJECT_DIR, "assets", "icons")

os.makedirs(JS_DIR, exist_ok=True)
os.makedirs(ASSETS_ICONS_DIR, exist_ok=True)

# 1. Cargar fuentes de datos
copsa_pub_path = os.path.join(SCRATCH_DIR, "copsa_blogger_automation", "copsa_blogger_publicados.json")
copsa_rep_path = os.path.join(SCRATCH_DIR, "copsa_horarios_completos", "reporte_extraccion.json")
copsa_lineas_dir = os.path.join(SCRATCH_DIR, "copsa_horarios_completos", "lineas")

cutcsa_pub_path = os.path.join(SCRATCH_DIR, "cutcsa_blogger_automation", "cutcsa_blogger_publicados.json")
cutcsa_all_path = os.path.join(SCRATCH_DIR, "cutcsa_horarios_completos", "datos_json", "cutcsa_horarios_todos.json")

este_pub_path = os.path.join(SCRATCH_DIR, "copsa_este_blogger", "copsa_este_publicados.json")
este_all_path = os.path.join(SCRATCH_DIR, "copsa_este_horarios", "datos_json", "copsa_este_horarios.json")

progreso_antiguos_path = os.path.join(SCRATCH_DIR, "copsa_blogger_automation", "progreso_posts_antiguos.json")
posts_antiguos_path = os.path.join(SCRATCH_DIR, "copsa_blogger_automation", "posts_antiguos_copsa.json")
cutcsa_hist_path = os.path.join(SCRATCH_DIR, "cutcsa_blogger_automation", "cutcsa_historicos_final.json")

copsa_pub = json.load(open(copsa_pub_path, encoding="utf-8"))
copsa_rep = {x["id"]: x for x in json.load(open(copsa_rep_path, encoding="utf-8"))}
cutcsa_pub = json.load(open(cutcsa_pub_path, encoding="utf-8"))
cutcsa_all = {x["id"]: x for x in json.load(open(cutcsa_all_path, encoding="utf-8"))}
este_pub = json.load(open(este_pub_path, encoding="utf-8"))
este_all = json.load(open(este_all_path, encoding="utf-8"))
progreso_antiguos = json.load(open(progreso_antiguos_path, encoding="utf-8"))
posts_antiguos = json.load(open(posts_antiguos_path, encoding="utf-8"))
cutcsa_hist = json.load(open(cutcsa_hist_path, encoding="utf-8"))

# Mapa de localidades enriquecido por línea / palabras clave
LOCALIDAD_CANONICAL = {
    "MONTEVIDEO": "Montevideo (Tres Cruces / Río Branco)",
    "TRES CRUCES": "Montevideo (Tres Cruces / Río Branco)",
    "MDEO": "Montevideo (Tres Cruces / Río Branco)",
    "MDEO.": "Montevideo (Tres Cruces / Río Branco)",
    "CIUDAD VIEJA": "Ciudad Vieja",
    "TEATRO SOLÍS": "Ciudad Vieja",
    "CANELONES": "Canelones",
    "SANTA LUCÍA": "Santa Lucía",
    "SANTA LUCIA": "Santa Lucía",
    "PARQUE DEL PLATA": "Parque del Plata",
    "PARQUE DEL PLATA NORTE": "Parque del Plata",
    "PINAR": "El Pinar",
    "EL PINAR": "El Pinar",
    "VILLA EL TATO": "Villa El Tato",
    "PANDO": "Pando",
    "AEROPUERTO": "Aeropuerto de Carrasco",
    "SOLYMAR": "Solymar",
    "SOLYMAR NORTE": "Solymar Norte",
    "COLINAS DE SOLYMAR": "Colinas de Solymar",
    "MARINDIA": "Marindia",
    "SALINAS": "Salinas",
    "PINAMAR": "Pinamar",
    "NEPTUNIA": "Neptunia",
    "BELLO HORIZONTE": "Bello Horizonte",
    "LA FLORESTA": "La Floresta",
    "ESTACIÓN FLORESTA": "Estación Floresta",
    "GUAZUVIRÁ": "Guazuvirá",
    "SAN LUIS": "San Luis",
    "SANTA LUCÍA DEL ESTE": "Santa Lucía del Este",
    "STA. LUCIA DEL ESTE": "Santa Lucía del Este",
    "CUCHILLA ALTA": "Cuchilla Alta",
    "SANTA ANA": "Santa Ana",
    "ARAMINDA": "Araminda",
    "JAUREGUIBERRY": "Jaureguiberry",
    "ATLÁNTIDA": "Atlántida",
    "ESTACIÓN ATLÁNTIDA": "Estación Atlántida",
    "LAS TOSCAS": "Las Toscas",
    "SUÁREZ": "Joaquín Suárez",
    "SUAREZ": "Joaquín Suárez",
    "BARRIO OBRERO": "Barrio Obrero",
    "VILLA HADITA": "Villa Hadita",
    "LAS PIEDRAS": "Las Piedras",
    "PROGRESO": "Progreso",
    "CERRILLOS": "Los Cerrillos",
    "VILLA ALEGRIA": "Villa Alegría",
    "ALM.CALCAGNO": "Almirante Calcagno",
    "JUANICO": "Juanicó",
    "SOCA": "Soca",
    "TOLEDO": "Toledo",
    "P.CARRASCO": "Paso Carrasco",
    "PASO CARRASCO": "Paso Carrasco",
    "CARRASCO": "Carrasco",
    "ZONAMERICA": "Zonamerica",
    "TNAL.ZONAMERICA": "Zonamerica",
    "PTA.CARRETAS": "Punta Carretas",
    "PUNTA CARRETAS": "Punta Carretas",
    "TERMINAL GEANT": "Parque Roosevelt / Géant",
    "GEANT": "Parque Roosevelt / Géant",
    "TERMINAL ROOSEVELT": "Parque Roosevelt / Géant",
    "COL.NICOLICH": "Colonia Nicolich",
    "LA PAZ": "La Paz",
    "RUTA 8 KM 21": "Ruta 8 (Villa García / Km 21)",
    "RUTA 8 KM 16": "Ruta 8 (Km 16 / Punta de Rieles)",
    "KM. 26.500 R.8": "Barros Blancos (Ruta 8 Km 26.5)",
    "R.8 KM 22.500": "Barros Blancos (Ruta 8 Km 22.5)",
    "PAJAS BLANCAS": "Pajas Blancas",
    "PASO DE LA ARENA": "Paso de la Arena",
    "BELLONI": "Intercambiador Belloni",
    "INT. BELLONI": "Intercambiador Belloni",
    "TERMINAL COLÓN": "Colón",
    "PASO MOLINO": "Paso Molino",
    "LA BOYADA": "La Boyada",
    "TERMINAL CERRO": "Cerro",
    "SANTA CATALINA": "Santa Catalina",
    "PORTONES": "Portones",
    "BARRIO CAPRA": "Barrio Capra",
    "GRUTA DE LOURDES": "Gruta de Lourdes",
    "POCITOS": "Pocitos",
    "BELVEDERE": "Belvedere",
    "PLANTA ISLAS CANARIAS": "Islas Canarias",
    "PUNTA DE RIELES": "Punta de Rieles",
    "COMPLEJO CARCELARIO": "Punta de Rieles",
    "PUNTA ESPINILLO": "Punta Espinillo",
    "PAURÚ": "Paurú",
    "VISTA LINDA": "Vista Linda",
    "PUNTA DEL ESTE": "Punta del Este",
    "MALDONADO": "Maldonado",
    "PIRIÁPOLIS": "Piriápolis",
    "BALNEARIO SAN FRANCISCO": "Balneario San Francisco",
    "PUNTA COLORADA": "Punta Colorada",
    "PUNTA NEGRA": "Punta Negra",
    "PORTEZUELO": "Portezuelo",
    "LA BARRA": "La Barra",
    "JOSÉ IGNACIO": "José Ignacio",
    "LAGUNA GARZÓN": "Laguna Garzón"
}

EXTRA_STOPS_BY_LINE = {
    "710": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar", "Neptunia", "Pinamar", "Salinas", "Marindia", "Atlántida", "Estación Atlántida", "Las Toscas", "Parque del Plata"],
    "711": ["Montevideo (Tres Cruces / Río Branco)", "Salinas", "Atlántida", "Parque del Plata", "Las Vegas", "La Floresta", "Estación Floresta", "Costa Azul", "Bello Horizonte", "Guazuvirá"],
    "712": ["Montevideo (Tres Cruces / Río Branco)", "Atlántida", "La Floresta", "Bello Horizonte", "Guazuvirá", "San Luis", "Los Titanes", "La Tuna", "Araminda", "Santa Lucía del Este", "Biritz", "Cuchilla Alta", "El Galeón", "Santa Ana", "Balneario Argentino", "Jaureguiberry"],
    "713": ["Montevideo (Tres Cruces / Río Branco)", "Araminda", "Santa Lucía del Este", "Cuchilla Alta", "Santa Ana", "Jaureguiberry"],
    "ESTE": ["Montevideo (Tres Cruces / Río Branco)", "Aeropuerto de Carrasco", "Piriápolis", "Balneario San Francisco", "Punta Colorada", "Punta Negra", "Portezuelo", "Maldonado", "Punta del Este", "La Barra", "José Ignacio", "Laguna Garzón"],
    "709": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar", "Neptunia", "Pinamar", "Salinas", "Marindia"],
    "700": ["Montevideo (Tres Cruces / Río Branco)", "Paso Carrasco", "Parque Roosevelt / Géant", "Lagomar", "Solymar", "El Pinar"],
    "714": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "Lomas de Solymar", "El Pinar"],
    "707": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar"],
    "708": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar"],
    "705": ["Montevideo (Tres Cruces / Río Branco)", "Solymar", "Colinas de Solymar", "El Pinar"],
    "7E5": ["Montevideo (Tres Cruces / Río Branco)", "Colinas de Solymar"],
    "7E7R": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar"],
    "7E8D": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar"],
    "7E8R": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar"],
    "8E7R": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar Norte"],
    "8E8R": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar Norte"],
    "7A": ["Montevideo (Tres Cruces / Río Branco)", "Ruta 8 (Km 16 / Punta de Rieles)", "Ruta 8 (Villa García / Km 21)", "Barros Blancos (Ruta 8 Km 26.5)", "Pando"],
    "8A": ["Montevideo (Tres Cruces / Río Branco)", "Barros Blancos (Ruta 8 Km 26.5)", "Pando", "Empalme Olmos", "Soca"],
    "701": ["Montevideo (Tres Cruces / Río Branco)", "Aeropuerto de Carrasco", "Colonia Nicolich", "Villa El Tato", "Pando"],
    "703": ["Montevideo (Tres Cruces / Río Branco)", "Paso Carrasco", "Aeropuerto de Carrasco"],
    "704": ["Montevideo (Tres Cruces / Río Branco)", "Paso Carrasco", "Aeropuerto de Carrasco"],
    "706": ["Montevideo (Tres Cruces / Río Branco)", "Aeropuerto de Carrasco", "Pando"],
    "724": ["Montevideo (Tres Cruces / Río Branco)", "Aeropuerto de Carrasco", "Pando"],
    "747": ["Montevideo (Tres Cruces / Río Branco)", "Toledo", "Joaquín Suárez", "Pando"],
    "748": ["Montevideo (Tres Cruces / Río Branco)", "Toledo", "Joaquín Suárez", "Pando"],
    "750": ["Montevideo (Tres Cruces / Río Branco)", "Toledo", "Joaquín Suárez", "Barrio Obrero"],
    "751": ["Montevideo (Tres Cruces / Río Branco)", "Toledo", "Joaquín Suárez"],
    "752": ["Montevideo (Tres Cruces / Río Branco)", "Toledo", "Joaquín Suárez", "Villa Hadita"],
    "757": ["El Pinar", "Solymar", "Aeropuerto de Carrasco", "Zonamerica", "Toledo", "Las Piedras"],
    "1A": ["Montevideo (Tres Cruces / Río Branco)", "La Paz", "Las Piedras", "Progreso", "Juanicó", "Canelones"],
    "2A": ["Montevideo (Tres Cruces / Río Branco)", "La Paz", "Las Piedras", "Progreso", "Juanicó", "Canelones", "Santa Lucía"],
    "802": ["Montevideo (Tres Cruces / Río Branco)", "Las Piedras", "Los Cerrillos"],
    "803": ["Montevideo (Tres Cruces / Río Branco)", "Las Piedras", "Los Cerrillos", "Santa Lucía"],
    "804": ["Montevideo (Tres Cruces / Río Branco)", "Las Piedras", "Los Cerrillos", "Santa Lucía"],
    "807": ["Montevideo (Tres Cruces / Río Branco)", "Las Piedras", "Villa Alegría"],
    "808": ["Montevideo (Tres Cruces / Río Branco)", "Las Piedras", "Almirante Calcagno"],
    "809": ["Montevideo (Tres Cruces / Río Branco)", "La Paz", "Las Piedras", "Progreso"],
    "810": ["Montevideo (Tres Cruces / Río Branco)", "La Paz", "Las Piedras", "Progreso", "Juanicó"],
    "C1": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar", "Neptunia", "Pinamar", "Salinas"],
    "C1SD": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar", "Pinamar", "Salinas"],
    "C2": ["Montevideo (Tres Cruces / Río Branco)", "Parque Roosevelt / Géant", "Lagomar", "Solymar", "El Pinar", "Pinamar", "Salinas"],
    "C2SD": ["Montevideo (Tres Cruces / Río Branco)", "Parque Roosevelt / Géant", "Lagomar", "Solymar", "El Pinar", "Pinamar", "Salinas"],
    "C3": ["Montevideo (Tres Cruces / Río Branco)", "El Pinar", "Salinas", "Marindia", "Atlántida", "Las Toscas", "Parque del Plata"],
    "C4": ["Montevideo (Tres Cruces / Río Branco)", "Parque Roosevelt / Géant", "Lagomar", "Solymar", "El Pinar", "Salinas", "Atlántida", "Las Toscas", "Parque del Plata"],
    "C4D": ["Montevideo (Tres Cruces / Río Branco)", "Salinas", "Atlántida", "Las Toscas", "Parque del Plata"],
    "C5": ["Montevideo (Tres Cruces / Río Branco)", "Salinas", "Marindia", "Atlántida", "Estación Atlántida"],
    "CE1": ["Montevideo (Tres Cruces / Río Branco)", "Ciudad Vieja"],
    "D1": ["Ciudad Vieja", "Pocitos", "Carrasco"],
    "D5": ["Ciudad Vieja", "Paso Molino", "Colón", "La Paz"],
    "D8": ["Ciudad Vieja", "Intercambiador Belloni", "Ruta 8 (Km 16 / Punta de Rieles)", "Ruta 8 (Villa García / Km 21)"],
    "D10": ["Ciudad Vieja", "Parque Roosevelt / Géant", "Paso Carrasco"],
    "DM1": ["Punta Carretas", "Pocitos", "Portones", "Parque Roosevelt / Géant", "Aeropuerto de Carrasco", "Zonamerica"],
    "222": ["Montevideo (Tres Cruces / Río Branco)", "Lagomar", "Solymar", "El Pinar", "Salinas", "Atlántida", "Las Toscas", "Parque del Plata"],
    "222D": ["Montevideo (Tres Cruces / Río Branco)", "Salinas", "Atlántida", "Las Toscas", "Parque del Plata"]
}

def parse_copsa_times(file_path):
    """Extrae horarios de salida HH:MM para ida y vuelta de un HTML de COPSA."""
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    ida_sec, vta_sec = "", ""
    if "➡️ IDA:" in html:
        parts = html.split("➡️ IDA:")
        if len(parts) > 1:
            sub = parts[1]
            if "⬅️ VUELTA:" in sub:
                ida_sec, vta_sec = sub.split("⬅️ VUELTA:")[0], sub.split("⬅️ VUELTA:")[1]
            else:
                ida_sec = sub

    def get_times(sec):
        times = []
        for tr in re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", sec):
            tds = re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr)
            if len(tds) >= 2:
                t = re.sub(r"<[^>]+>", "", tds[0]).replace("🕒", "").strip()
                m = re.search(r"\b(\d{1,2}:\d{2})\b", t)
                if m:
                    hhmm = m.group(1).zfill(5)
                    times.append(hhmm)
        return sorted(list(set(times)))

    return get_times(ida_sec), get_times(vta_sec)

def normalize_url(url):
    if not url:
        return ""
    return url.replace("http://www.servicioti.com.uy", "https://www.servicioti.com.uy")

# 2. Construir archivo histórico de Blogger y mapear por línea
archivo_blogger_map = {}

for pid, item in progreso_antiguos.items():
    u = normalize_url(item.get("url", ""))
    if not u:
        continue
    archivo_blogger_map[u] = {
        "id": str(pid),
        "titulo": item.get("title", "").strip(),
        "url": u,
        "lineas": item.get("lineas", []),
        "fecha": "2026-09-20",
        "categoria": "Archivo Actualizado 2026"
    }

for item in posts_antiguos:
    u = normalize_url(item.get("url", ""))
    if not u or "sandia" in u or "frutas" in u:
        continue
    if u not in archivo_blogger_map:
        archivo_blogger_map[u] = {
            "id": str(item.get("id", "")),
            "titulo": item.get("title", "").strip(),
            "url": u,
            "lineas": [l for l in item.get("labels", []) if len(l) <= 6 and any(c.isdigit() for c in l)],
            "fecha": item.get("published", "")[:10],
            "categoria": "Archivo Histórico / Especial"
        }

for item in cutcsa_hist:
    u = normalize_url(item.get("url", ""))
    if not u:
        continue
    if u not in archivo_blogger_map:
        archivo_blogger_map[u] = {
            "id": str(item.get("id", "")),
            "titulo": item.get("title", "").strip(),
            "url": u,
            "lineas": [],
            "fecha": item.get("published", "")[:10],
            "categoria": "Especial CUTCSA / Tarifas"
        }

# Registrar Página Guía Oficial de COETC
coetc_guia_url = "https://www.servicioti.com.uy/p/horarios-coetc-guia-lineas-suburbanas.html"
archivo_blogger_map[coetc_guia_url] = {
    "id": "8331816308880741215",
    "titulo": "Horarios COETC: Guía de Líneas Suburbanas 222 y 222D",
    "url": coetc_guia_url,
    "lineas": ["222", "222D"],
    "fecha": "2026-10-23",
    "categoria": "Página Oficial / Catálogo",
    "diaTipo": "general"
}

# Enriquecer detección de líneas en títulos de archivo_blogger_map
for u, post in archivo_blogger_map.items():
    t_up = post["titulo"].upper()
    detected = set(post["lineas"])
    for token in ["700", "701", "703", "704", "705", "706", "707", "708", "709", "710", "711", "712", "713", "714",
                  "724", "747", "748", "750", "751", "752", "757", "7A", "7H", "8A", "1A", "2A", "802", "803", "804",
                  "807", "808", "809", "810", "7E5", "7E7R", "7E8D", "7E8R", "8E7R", "8E8R", "P756", "P757", "P758",
                  "P759", "P760", "P761", "P768", "P7A", "P7H", "P802", "P804", "DM1", "XA1", "XA2",
                  "C1", "C2", "C3", "C4", "C5", "222", "222D"]:
        if re.search(r"\b" + re.escape(token) + r"\b", t_up):
            detected.add(token)
    if "LINEA ESTE" in t_up or "LÍNEA ESTE" in t_up or "PUNTA DEL ESTE" in t_up:
        detected.add("ESTE")
    post["lineas"] = sorted(list(detected))
    if "DOMINGO" in t_up:
        post["diaTipo"] = "domingos"
    elif "SABADO" in t_up or "SÁBADO" in t_up:
        post["diaTipo"] = "sabados"
    elif "HABIL" in t_up or "HÁBIL" in t_up:
        post["diaTipo"] = "habiles"
    elif "VERANO" in t_up:
        post["diaTipo"] = "verano"
    elif "PRECIO" in t_up or "BOLETO" in t_up:
        post["diaTipo"] = "tarifas"
    else:
        post["diaTipo"] = "general"

archivo_blogger_list = sorted(archivo_blogger_map.values(), key=lambda x: x["titulo"])

def extract_localidades(lid, text):
    locs = set(EXTRA_STOPS_BY_LINE.get(lid, []))
    t_up = text.upper()
    for k, canon in LOCALIDAD_CANONICAL.items():
        if k in t_up:
            locs.add(canon)
    return sorted(list(locs))

def get_related_posts_for_line(lid, empresa_filter=None):
    rel = []
    for p in archivo_blogger_list:
        if lid in p["lineas"]:
            if empresa_filter and empresa_filter.upper() == "CUTCSA" and lid == "DM1":
                pass
            rel.append({
                "titulo": p["titulo"],
                "url": p["url"],
                "diaTipo": p["diaTipo"]
            })
    return rel

# 3. Compilar las 90 líneas
lineas_master = []

# 3A. COPSA Suburbana / Local / Compartida (52 líneas)
for lid, pub in copsa_pub.items():
    rep = copsa_rep.get(lid, {})
    archivos = rep.get("archivos", [])
    lav_info = next((a for a in archivos if "lunes_a_viernes" in a.get("filename", "")), {})
    sab_info = next((a for a in archivos if "sabado" in a.get("filename", "")), {})
    dom_info = next((a for a in archivos if "domingo" in a.get("filename", "")), {})

    line_safe = lid.replace("/", "_")
    folder = os.path.join(copsa_lineas_dir, line_safe)
    lav_ida, lav_vta = parse_copsa_times(os.path.join(folder, f"{line_safe}_lunes_a_viernes.html"))
    sab_ida, sab_vta = parse_copsa_times(os.path.join(folder, f"{line_safe}_sabado.html"))
    dom_ida, dom_vta = parse_copsa_times(os.path.join(folder, f"{line_safe}_domingo.html"))

    nombre_raw = pub.get("nombre", f"{lid} - COPSA")
    ruta_clean = re.sub(r"^" + re.escape(lid) + r"\s*-\s*", "", nombre_raw).strip()
    partes = [p.strip() for p in ruta_clean.split("/") if p.strip()]
    origen_str = partes[0].title() if partes else "Montevideo"
    destino_str = partes[-1].title() if len(partes) > 1 else ruta_clean.title()

    corredor = pub.get("corredor", "Suburbano")
    depto = "Montevideo / Canelones" if corredor != "Local" else "Canelones (Local)"
    locs = extract_localidades(lid, nombre_raw + " " + rep.get("tituloIda", "") + " " + rep.get("tituloVuelta", ""))
    rel_posts = get_related_posts_for_line(lid, "COPSA")

    url_main = normalize_url(pub.get("url", ""))
    url_hab = next((r["url"] for r in rel_posts if r["diaTipo"] == "habiles" and len(r["titulo"]) < 95), url_main)
    url_sab = next((r["url"] for r in rel_posts if r["diaTipo"] == "sabados" and len(r["titulo"]) < 95), url_main)
    url_dom = next((r["url"] for r in rel_posts if r["diaTipo"] == "domingos" and len(r["titulo"]) < 95), url_main)

    lineas_master.append({
        "uid": f"COPSA-{lid}",
        "id": lid,
        "empresa": "COPSA",
        "nombre": ruta_clean,
        "nombreCompleto": nombre_raw,
        "corredor": f"Corredor {corredor}",
        "corredorCodigo": corredor,
        "tipo": "Línea Local Departamental" if corredor == "Local" else ("Línea Compartida" if corredor == "Compartidas" else "Suburbana"),
        "departamento": depto,
        "origen": origen_str,
        "destino": destino_str,
        "tituloIda": rep.get("tituloIda", f"{origen_str} → {destino_str}").strip(),
        "tituloVuelta": rep.get("tituloVuelta", f"{destino_str} → {origen_str}").strip(),
        "localidades": locs,
        "url": url_main,
        "urlsPorDia": {
            "habiles": url_main,
            "sabados": url_main,
            "domingos": url_main,
            "especiales": {"habiles": url_hab, "sabados": url_sab, "domingos": url_dom}
        },
        "frecuencias": {
            "habiles": lav_info.get("total", len(lav_ida) + len(lav_vta)),
            "sabados": sab_info.get("total", len(sab_ida) + len(sab_vta)),
            "domingos": dom_info.get("total", len(dom_ida) + len(dom_vta)),
            "total": sum(a.get("total", 0) for a in archivos)
        },
        "salidas": {
            "habiles": {"ida": lav_ida, "vuelta": lav_vta},
            "sabados": {"ida": sab_ida, "vuelta": sab_vta},
            "domingos": {"ida": dom_ida, "vuelta": dom_vta}
        },
        "postsRelacionados": rel_posts,
        "destacada": lid in ["710", "711", "712", "714", "7A", "1A", "2A", "809", "700", "709", "751", "757"]
    })

# 3B. COPSA Línea Este y Línea 713 (2 líneas interdepartamentales / Costa de Oro Este)
este_data = este_all["linea_este"]
este_ida_times = sorted(list(set(r[0] for r in este_data["hacia_pde"]["filas"] if r and ":" in r[0])))
este_vta_times = sorted(list(set(r[0] for r in este_data["hacia_mvd"]["filas"] if r and ":" in r[0])))
este_total = len(este_data["hacia_pde"]["filas"]) + len(este_data["hacia_mvd"]["filas"])
este_url = normalize_url(este_pub["linea_este"]["url"])

lineas_master.append({
    "uid": "COPSA-ESTE",
    "id": "Línea Este",
    "empresa": "COPSA Este",
    "nombre": "MONTEVIDEO ↔ PUNTA DEL ESTE / PIRIÁPOLIS / SAN FRANCISCO",
    "nombreCompleto": "Línea Este - Montevideo / Piriápolis / Balneario San Francisco / Maldonado / Punta del Este",
    "corredor": "Interdepartamental Este",
    "corredorCodigo": "Este",
    "tipo": "Interdepartamental",
    "departamento": "Montevideo / Maldonado",
    "origen": "Montevideo (Tres Cruces)",
    "destino": "Punta del Este / Piriápolis",
    "tituloIda": "Montevideo (Tres Cruces / Aeropuerto) → Piriápolis / San Francisco / Maldonado / Punta del Este",
    "tituloVuelta": "Punta del Este / Maldonado / Piriápolis / San Francisco → Montevideo (Tres Cruces)",
    "localidades": EXTRA_STOPS_BY_LINE["ESTE"],
    "url": este_url,
    "urlsPorDia": {
        "habiles": este_url,
        "sabados": este_url,
        "domingos": este_url
    },
    "frecuencias": {
        "habiles": este_total,
        "sabados": este_total,
        "domingos": este_total,
        "total": este_total * 3
    },
    "salidas": {
        "habiles": {"ida": este_ida_times, "vuelta": este_vta_times},
        "sabados": {"ida": este_ida_times, "vuelta": este_vta_times},
        "domingos": {"ida": este_ida_times, "vuelta": este_vta_times}
    },
    "postsRelacionados": get_related_posts_for_line("ESTE"),
    "destacada": True,
    "novedad": "Incluye nuevo servicio diario por Balneario San Francisco, Punta Colorada y Punta Negra"
})

l713_data = este_all["linea_713"]
l713_ida_times = sorted(list(set(r[0] for r in l713_data["hacia_jaureguiberry"]["filas"] if r and ":" in r[0])))
l713_vta_times = sorted(list(set(r[0] for r in l713_data["hacia_mvd"]["filas"] if r and ":" in r[0])))
l713_total = len(l713_data["hacia_jaureguiberry"]["filas"]) + len(l713_data["hacia_mvd"]["filas"])
l713_url = normalize_url(este_pub["linea_713"]["url"])

lineas_master.append({
    "uid": "COPSA-713",
    "id": "713",
    "empresa": "COPSA Este",
    "nombre": "MONTEVIDEO ↔ JAUREGUIBERRY (COSTA DE ORO ESTE)",
    "nombreCompleto": "713 - Montevideo / Araminda / Sta. Lucía del Este / Cuchilla Alta / Santa Ana / Jaureguiberry",
    "corredor": "Costa de Oro Este",
    "corredorCodigo": "Este",
    "tipo": "Suburbana / Interbalnearia",
    "departamento": "Montevideo / Canelones",
    "origen": "Montevideo (Tres Cruces)",
    "destino": "Jaureguiberry",
    "tituloIda": "Montevideo → Araminda / Sta. Lucía del Este / Cuchilla Alta / Santa Ana / Jaureguiberry",
    "tituloVuelta": "Jaureguiberry / Santa Ana / Cuchilla Alta / Sta. Lucía del Este / Araminda → Montevideo",
    "localidades": EXTRA_STOPS_BY_LINE["713"],
    "url": l713_url,
    "urlsPorDia": {
        "habiles": l713_url,
        "sabados": l713_url,
        "domingos": l713_url
    },
    "frecuencias": {
        "habiles": l713_total,
        "sabados": l713_total,
        "domingos": l713_total,
        "total": l713_total * 3
    },
    "salidas": {
        "habiles": {"ida": l713_ida_times, "vuelta": l713_vta_times},
        "sabados": {"ida": l713_ida_times, "vuelta": l713_vta_times},
        "domingos": {"ida": l713_ida_times, "vuelta": l713_vta_times}
    },
    "postsRelacionados": get_related_posts_for_line("713"),
    "destacada": True
})

# 3C. CUTCSA (34 líneas: Corredores C, D y L)
for lid, pub in cutcsa_pub.items():
    cdata = cutcsa_all.get(lid, {})
    dias_list = cdata.get("dias", [])
    hab_d = next((d for d in dias_list if d.get("tipo") == "habiles"), {})
    sab_d = next((d for d in dias_list if d.get("tipo") == "sabados"), {})
    dom_d = next((d for d in dias_list if d.get("tipo") == "domingos"), {})

    def extract_cutcsa_times(d_obj, key):
        arr = d_obj.get(key, [])
        times = []
        for item in arr:
            s = item.get("salida", "").strip()
            if re.match(r"^\d{1,2}:\d{2}$", s):
                times.append(s.zfill(5))
        return sorted(list(set(times)))

    hab_ida = extract_cutcsa_times(hab_d, "ida")
    hab_vta = extract_cutcsa_times(hab_d, "vuelta")
    sab_ida = extract_cutcsa_times(sab_d, "ida")
    sab_vta = extract_cutcsa_times(sab_d, "vuelta")
    dom_ida = extract_cutcsa_times(dom_d, "ida")
    dom_vta = extract_cutcsa_times(dom_d, "vuelta")

    cnt_hab = len(hab_d.get("ida", [])) + len(hab_d.get("vuelta", []))
    cnt_sab = len(sab_d.get("ida", [])) + len(sab_d.get("vuelta", []))
    cnt_dom = len(dom_d.get("ida", [])) + len(dom_d.get("vuelta", []))

    nombre_raw = pub.get("nombre", f"Línea {lid}")
    partes = [p.strip() for p in nombre_raw.split("-") if p.strip()]
    origen_str = partes[0] if partes else "Montevideo"
    destino_str = partes[-1] if len(partes) > 1 else nombre_raw

    cor = pub.get("corredor", "C")
    cor_label = {
        "C": "Corredor C (Costa de Oro)",
        "D": "Corredor D (Diferenciales)",
        "L": "Corredor L (Locales Montevideo)"
    }.get(cor, f"Corredor {cor}")

    locs = extract_localidades(lid, nombre_raw)
    url_main = normalize_url(pub.get("url", ""))
    rel_posts = get_related_posts_for_line(lid, "CUTCSA")

    lineas_master.append({
        "uid": f"CUTCSA-{lid}",
        "id": lid if lid != "DM1" else "DM1 (CUTCSA)",
        "codigoCorto": lid,
        "empresa": "CUTCSA",
        "nombre": nombre_raw,
        "nombreCompleto": f"{lid} - {nombre_raw}",
        "corredor": cor_label,
        "corredorCodigo": f"CUTCSA-{cor}",
        "tipo": pub.get("tipo", "Urbana / Suburbana"),
        "departamento": "Montevideo / Canelones" if cor in ["C", "D"] else "Montevideo",
        "origen": origen_str,
        "destino": destino_str,
        "tituloIda": f"{origen_str} → {destino_str}",
        "tituloVuelta": f"{destino_str} → {origen_str}",
        "localidades": locs,
        "url": url_main,
        "urlsPorDia": {
            "habiles": url_main,
            "sabados": url_main,
            "domingos": url_main
        },
        "frecuencias": {
            "habiles": cnt_hab,
            "sabados": cnt_sab,
            "domingos": cnt_dom,
            "total": cnt_hab + cnt_sab + cnt_dom
        },
        "salidas": {
            "habiles": {"ida": hab_ida, "vuelta": hab_vta},
            "sabados": {"ida": sab_ida, "vuelta": sab_vta},
            "domingos": {"ida": dom_ida, "vuelta": dom_vta}
        },
        "postsRelacionados": rel_posts,
        "destacada": lid in ["C1", "C2", "C3", "C4", "C5", "D1", "D5", "D8", "D10", "DM1"]
    })

# 3D. COETC Líneas 222 y 222D (Montevideo ↔ Parque del Plata)
coetc_guia_url = "https://www.servicioti.com.uy/p/horarios-coetc-guia-lineas-suburbanas.html"
coetc_hab_url = "https://www.servicioti.com.uy/2024/03/222-222d-horarios-dias-habiles-coetc.html"
coetc_sab_url = "https://www.servicioti.com.uy/2024/03/222-222d-horarios-sabados-coetc.html"
coetc_dom_url = "https://www.servicioti.com.uy/2024/03/222-222d-horarios-domingos-coetc.html"
coetc_2022_url = "https://www.servicioti.com.uy/2022/12/horarios-222-coetc-destino-montevideo.html"

for coetc_id, coetc_name, coetc_tipo in [
    ("222", "Montevideo ↔ Parque del Plata (por Interbalnearia / Giannattasio)", "Suburbana Cooperativa"),
    ("222D", "Montevideo ↔ Parque del Plata (Servicio Directo / Semidirecto)", "Suburbana Directo")
]:
    lineas_master.append({
        "uid": f"COETC-{coetc_id}",
        "id": coetc_id,
        "empresa": "COETC",
        "nombre": coetc_name,
        "nombreCompleto": f"{coetc_id} COETC - {coetc_name}",
        "corredor": "Corredor Interbalnearia (COETC)",
        "corredorCodigo": "COETC",
        "tipo": coetc_tipo,
        "departamento": "Montevideo / Canelones",
        "origen": "Montevideo (Terminal Baltasar Brum)",
        "destino": "Parque del Plata",
        "tituloIda": "Montevideo → El Pinar / Salinas / Atlántida / Parque del Plata",
        "tituloVuelta": "Parque del Plata / Atlántida / Salinas / El Pinar → Montevideo",
        "localidades": EXTRA_STOPS_BY_LINE["222"],
        "url": coetc_hab_url,
        "urlsPorDia": {
            "habiles": coetc_hab_url,
            "sabados": coetc_sab_url,
            "domingos": coetc_dom_url
        },
        "frecuencias": {
            "habiles": 48 if coetc_id == "222" else 14,
            "sabados": 38 if coetc_id == "222" else 8,
            "domingos": 32 if coetc_id == "222" else 6,
            "total": 118 if coetc_id == "222" else 28
        },
        "salidas": {
            "habiles": {
                "ida": ["05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:15", "09:00", "09:45", "10:30", "11:15", "12:00", "12:45", "13:30", "14:15", "15:00", "15:45", "16:30", "17:15", "18:00", "18:45", "19:30", "20:30", "21:30", "22:30"],
                "vuelta": ["04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:45", "08:30", "09:15", "10:00", "10:45", "11:30", "12:15", "13:00", "13:45", "14:30", "15:15", "16:00", "16:45", "17:30", "18:15", "19:00", "20:00", "21:00"]
            },
            "sabados": {
                "ida": ["05:30", "06:15", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:15"],
                "vuelta": ["05:00", "05:45", "06:30", "07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30", "17:30", "18:30", "19:30", "20:30", "21:30"]
            },
            "domingos": {
                "ida": ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:30"],
                "vuelta": ["05:30", "06:30", "07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30", "17:30", "18:30", "19:30", "20:45"]
            }
        },
        "postsRelacionados": [
            {"titulo": "Horarios COETC: Guía de Líneas Suburbanas 222 y 222D", "url": coetc_guia_url, "diaTipo": "general"},
            {"titulo": "222-222D Horarios Días Hábiles COETC Actualizado", "url": coetc_hab_url, "diaTipo": "habiles"},
            {"titulo": "222-222D Horarios Sábados COETC Actualizado", "url": coetc_sab_url, "diaTipo": "sabados"},
            {"titulo": "222-222D Horarios Domingos COETC Actualizado", "url": coetc_dom_url, "diaTipo": "domingos"},
            {"titulo": "Horarios 222 COETC Destino Montevideo - Parque del Plata", "url": coetc_2022_url, "diaTipo": "habiles"}
        ],
        "destacada": True
    })

# 4. Guías Maestras y Páginas Estáticas de Blogger
guias_maestras = [
    {
        "id": "guia-copsa-pagina",
        "titulo": "Catálogo Oficial COPSA (52 Líneas Suburbanas)",
        "subtitulo": "Página maestra con todas las líneas por corredor: Av. Italia, Ruta 5, Centro, Locales y Compartidas",
        "empresa": "COPSA",
        "badge": "Página Oficial",
        "icono": "🚌",
        "color": "#0056b3",
        "url": "https://www.servicioti.com.uy/p/horarios-copsa-guia-de-todas-las-lineas.html"
    },
    {
        "id": "guia-cutcsa-pagina",
        "titulo": "Catálogo Oficial CUTCSA (Líneas C, D y L)",
        "subtitulo": "Directorio completo de las 34 líneas Suburbanas de la Costa, Diferenciales y Locales de Montevideo",
        "empresa": "CUTCSA",
        "badge": "Página Oficial",
        "icono": "🚍",
        "color": "#d9232e",
        "url": "https://www.servicioti.com.uy/p/horarios-cutcsa-guia-de-lineas-c-d-l.html"
    },
    {
        "id": "guia-coetc-pagina",
        "titulo": "Catálogo Oficial COETC (Líneas 222 y 222D)",
        "subtitulo": "Guía completa suburbana: Montevideo ↔ Parque del Plata por Giannattasio e Interbalnearia",
        "empresa": "COETC",
        "badge": "Página Oficial",
        "icono": "🟪",
        "color": "#dc2626",
        "url": "https://www.servicioti.com.uy/p/horarios-coetc-guia-lineas-suburbanas.html"
    },
    {
        "id": "guia-este-pagina",
        "titulo": "Guía COPSA Línea Este y 713 (Maldonado / Rocha / Costa)",
        "subtitulo": "Punta del Este, Piriápolis, Balneario San Francisco, Punta Colorada, Punta Negra y Jaureguiberry",
        "empresa": "COPSA Este",
        "badge": "Interdepartamental",
        "icono": "🏖️",
        "color": "#047857",
        "url": "https://www.servicioti.com.uy/p/horarios-copsa-linea-este-y-linea-713.html"
    },
    {
        "id": "guia-tarifas-boletos",
        "titulo": "Precio de Boletos Suburbanos e Información Tarifaria",
        "subtitulo": "Tarifas vigentes para líneas suburbanas C1, C2, C3, C4, C5, 214, Directos y tramos metropolitanos",
        "empresa": "Tarifas MTOP",
        "badge": "Precios y Boletos",
        "icono": "🎫",
        "color": "#b45309",
        "url": "https://www.servicioti.com.uy/2024/03/c5-c4-c3-c2-c1-214-directo-precio.html"
    },
    {
        "id": "guia-portal-historico",
        "titulo": "Índice Canónico General de Horarios de Ómnibus",
        "subtitulo": "Publicación histórica central del blog con enlaces cruzados a todas las temporadas y corredores",
        "empresa": "ServicioTI",
        "badge": "Portal Central",
        "icono": "🏛️",
        "color": "#0f172a",
        "url": "https://www.servicioti.com.uy/2022/12/horarios-omnibus.html"
    }
]

# 5. Compilar Índice Geográfico de Localidades (A-Z)
localidades_map = {}
for l in lineas_master:
    for loc in l["localidades"]:
        if loc not in localidades_map:
            localidades_map[loc] = {
                "nombre": loc,
                "lineas": [],
                "empresas": set(),
                "urlPrincipal": l["url"]
            }
        localidades_map[loc]["lineas"].append({
            "uid": l["uid"],
            "id": l["id"],
            "empresa": l["empresa"],
            "url": l["url"]
        })
        localidades_map[loc]["empresas"].add(l["empresa"])

localidades_list = []
for loc_name in sorted(localidades_map.keys()):
    info = localidades_map[loc_name]
    localidades_list.append({
        "nombre": info["nombre"],
        "cantidadLineas": len(info["lineas"]),
        "empresas": sorted(list(info["empresas"])),
        "lineas": info["lineas"],
        "urlPrincipal": info["urlPrincipal"]
    })

# Estadísticas globales
total_frecuencias_sistema = sum(l["frecuencias"]["total"] for l in lineas_master)
urls_unicas_blogger = set()
for l in lineas_master:
    urls_unicas_blogger.add(l["url"])
    for k, v in l["urlsPorDia"].items():
        if isinstance(v, str):
            urls_unicas_blogger.add(v)
        elif isinstance(v, dict):
            for sv in v.values():
                urls_unicas_blogger.add(sv)
for p in archivo_blogger_list:
    urls_unicas_blogger.add(p["url"])
for g in guias_maestras:
    urls_unicas_blogger.add(g["url"])

dataset = {
    "meta": {
        "generado": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dominioIndice": "https://horarios.servicioti.com.uy",
        "dominioBlogger": "https://www.servicioti.com.uy",
        "totalLineas": len(lineas_master),
        "totalPostsArchivo": len(archivo_blogger_list),
        "totalGuiasMaestras": len(guias_maestras),
        "totalUrlsBloggerIndexadas": len(urls_unicas_blogger),
        "totalLocalidades": len(localidades_list),
        "totalFrecuencias": total_frecuencias_sistema
    },
    "guiasMaestras": guias_maestras,
    "lineas": lineas_master,
    "localidades": localidades_list,
    "archivoBlogger": archivo_blogger_list
}

with open(os.path.join(JS_DIR, "data.js"), "w", encoding="utf-8") as f:
    f.write("// Base de Datos Maestra de Horarios ServicioTI - Generada Automáticamente\n")
    f.write("window.HORARIOS_DATA = ")
    json.dump(dataset, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

print(f"✅ js/data.js compilado con éxito!")
print(f"   - Total Líneas Indexadas: {len(lineas_master)}")
print(f"   - Total Guías Maestras: {len(guias_maestras)}")
print(f"   - Total Posts Históricos/Especiales: {len(archivo_blogger_list)}")
print(f"   - Total URLs Únicas de Blogger: {len(urls_unicas_blogger)}")
print(f"   - Total Localidades A-Z: {len(localidades_list)}")
print(f"   - Total Frecuencias Registradas: {total_frecuencias_sistema}")
