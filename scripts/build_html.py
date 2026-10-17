# -*- coding: utf-8 -*-
"""
Generador de index.html con Pre-Renderizado Estático SEO Total + JSON-LD Multi-Entidad
Asegura que los rastreadores (Googlebot, Bingbot, Perplexity, ChatGPT) vean el 100% de los
159 enlaces directos a www.servicioti.com.uy directamente en el código fuente HTML.
"""

import os
import json
import html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JS_PATH = os.path.join(BASE_DIR, "js", "data.js")
INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")

with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
    raw = f.read()
    json_str = raw.split("window.HORARIOS_DATA = ", 1)[1].rstrip(";\n")
    dataset = json.loads(json_str)

meta = dataset["meta"]
guias = dataset["guiasMaestras"]
lineas = dataset["lineas"]
localidades = dataset["localidades"]
archivo = dataset["archivoBlogger"]

def esc(s):
    return html.escape(str(s or ""), quote=True)

# 1. Construir JSON-LD Schema.org (WebSite + CollectionPage + ItemList de 90 BusTrips + FAQPage)
item_list_elements = []
for idx, l in enumerate(lineas, start=1):
    item_list_elements.append({
        "@type": "ListItem",
        "position": idx,
        "item": {
            "@type": "BusTrip",
            "name": f"Horarios {l['empresa']} Línea {l['id']}: {l['nombre']}",
            "busNumber": l["id"],
            "busName": l["nombreCompleto"],
            "provider": {
                "@type": "Organization",
                "name": l["empresa"]
            },
            "departureBusStop": {
                "@type": "BusStop",
                "name": l["origen"]
            },
            "arrivalBusStop": {
                "@type": "BusStop",
                "name": l["destino"]
            },
            "url": l["url"],
            "mainEntityOfPage": l["url"]
        }
    })

schema_json_ld = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": "https://horarios.servicioti.com.uy/#website",
            "url": "https://horarios.servicioti.com.uy/",
            "name": "Horarios de Ómnibus Uruguay • Índice Oficial ServicioTI",
            "alternateName": "Horarios ServicioTI",
            "description": "El índice interactivo más completo de horarios de ómnibus suburbanos, interdepartamentales, diferenciales y locales de Uruguay (COPSA, CUTCSA, Línea Este y COETC). Fuente oficial de consulta: www.servicioti.com.uy",
            "inLanguage": "es-UY",
            "publisher": {
                "@type": "Organization",
                "name": "ServicioTI Uruguay",
                "url": "https://www.servicioti.com.uy/"
            }
        },
        {
            "@type": "CollectionPage",
            "@id": "https://horarios.servicioti.com.uy/#collection",
            "url": "https://horarios.servicioti.com.uy/",
            "name": "Directorio Maestro de Horarios de Ómnibus COPSA, CUTCSA, Línea Este y COETC (Actualizado 2026)",
            "isPartOf": {"@id": "https://horarios.servicioti.com.uy/#website"},
            "about": "Horarios de transporte colectivo urbano, suburbano e interdepartamental en Montevideo, Canelones y Maldonado, Uruguay.",
            "mainEntity": {
                "@type": "ItemList",
                "name": "Catálogo Oficial de 90 Líneas de Ómnibus en ServicioTI.com.uy",
                "numberOfItems": len(lineas),
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "itemListElement": item_list_elements
            }
        },
        {
            "@type": "FAQPage",
            "@id": "https://horarios.servicioti.com.uy/#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "¿Dónde se consultan las planillas completas de horarios de COPSA, CUTCSA, Línea Este y COETC?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Todas las planillas completas de horarios vigentes (Lunes a Viernes, Sábados y Domingos/Feriados, ida y vuelta) están alojadas y actualizadas en el portal principal www.servicioti.com.uy. Este índice en horarios.servicioti.com.uy permite buscar por línea, origen, destino o localidad y acceder en un clic a cada publicación oficial del blog."
                    }
                },
                {
                    "@type": "Question",
                    "name": "¿Qué líneas de ómnibus van desde Montevideo a Parque del Plata, Atlántida y Salinas?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Hacia Salinas, Atlántida, Las Toscas y Parque del Plata operan las líneas 710, 709 y 711 de COPSA, las líneas suburbanas C1, C1SD, C2, C2SD, C3, C4, C4D y C5 de CUTCSA, y las líneas 222 y 222D de COETC."
                    }
                },
                {
                    "@type": "Question",
                    "name": "¿Qué líneas cubren Montevideo a Punta del Este, Piriápolis, Balneario San Francisco y Jaureguiberry?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "La Línea Este de COPSA conecta Montevideo (Tres Cruces) y el Aeropuerto de Carrasco con Piriápolis, Balneario San Francisco, Punta Colorada, Punta Negra, Portezuelo, Maldonado, Punta del Este, La Barra, José Ignacio y Laguna Garzón. Para Araminda, Santa Lucía del Este, Cuchilla Alta, Santa Ana y Jaureguiberry operan las líneas 712 y 713 de COPSA."
                    }
                },
                {
                    "@type": "Question",
                    "name": "¿Cuáles son los teléfonos de atención al cliente de COPSA, CUTCSA y Tres Cruces?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Atención al cliente COPSA: 2902 1818 (WhatsApp 098 001 970). Atención al cliente CUTCSA: 19333 (WhatsApp 094 805 818). Atención al cliente COETC: 19272. Terminal Tres Cruces: 2408 8601. Terminal Baltasar Brum (Río Branco): 2908 6594."
                    }
                }
            ]
        }
    ]
}

# 2. Pre-renderizar Tarjetas de Guías Maestras
guias_html = []
for g in guias:
    guias_html.append(f"""
      <a href="{esc(g['url'])}" target="_blank" rel="noopener" class="guide-card" title="Abrir {esc(g['titulo'])} en ServicioTI.com.uy">
        <div>
          <div class="guide-top">
            <span style="font-size: 24px;">{g['icono']}</span>
            <span class="guide-badge" style="background: {esc(g['color'])};">{esc(g['badge'])}</span>
          </div>
          <h3 class="guide-title">{esc(g['titulo'])}</h3>
          <p class="guide-desc">{esc(g['subtitulo'])}</p>
        </div>
        <div class="guide-cta">
          <span>Abrir Guía Oficial en ServicioTI.com.uy</span>
          <span>↗</span>
        </div>
      </a>
    """)

# 3. Pre-renderizar las 90 Tarjetas de Líneas (para indexación instantánea por motores de búsqueda)
lineas_html = []
for l in lineas:
    stops_chips = "".join(
        f'<button type="button" class="stop-chip" data-loc="{esc(loc)}">📍 {esc(loc)}</button>'
        for loc in l["localidades"][:7]
    )
    rel_items = "".join(
        f'<li><a href="{esc(rp["url"])}" target="_blank" rel="noopener">📄 {esc(rp["titulo"])} ↗</a></li>'
        for rp in l.get("postsRelacionados", [])[:6]
    )
    rel_block = (
        f'<details class="lc-related"><summary>🔗 +{len(l["postsRelacionados"])} guías y planillas específicas en el Blog</summary>'
        f'<ul class="lc-related-list">{rel_items}</ul></details>'
        if l.get("postsRelacionados") else ""
    )
    novedad_block = f'<div class="lc-novedad">✨ {esc(l["novedad"])}</div>' if l.get("novedad") else ""

    url_hab = l["urlsPorDia"].get("habiles", l["url"])
    url_sab = l["urlsPorDia"].get("sabados", l["url"])
    url_dom = l["urlsPorDia"].get("domingos", l["url"])

    lineas_html.append(f"""
      <article class="line-card" data-empresa="{esc(l['empresa'])}" data-uid="{esc(l['uid'])}">
        <div class="lc-header">
          <div class="lc-id-group">
            <a href="{esc(l['url'])}" target="_blank" rel="noopener" class="lc-badge">{esc(l['id'])}</a>
            <div class="lc-title-wrap">
              <h3><a href="{esc(l['url'])}" target="_blank" rel="noopener">{esc(l['nombre'])}</a></h3>
              <div class="lc-meta-tags">
                <span class="lc-tag">{esc(l['empresa'])}</span>
                <span class="lc-tag">{esc(l['corredor'])}</span>
                <span class="lc-tag">{esc(l['departamento'])}</span>
              </div>
            </div>
          </div>
          <button type="button" class="btn-fav" data-fav="{esc(l['uid'])}" aria-label="Guardar línea {esc(l['id'])} en favoritos">☆</button>
        </div>
        <div class="lc-body">
          {novedad_block}
          <a href="{esc(l['url'])}" target="_blank" rel="noopener" class="lc-radar-box">
            <div class="radar-top">
              <span>📡 Frecuencias Oficiales Vigentes</span>
              <span>{l['frecuencias']['total']} salidas registradas</span>
            </div>
            <div class="radar-times-grid">
              <div class="radar-dir-item">
                <div class="radar-dir-label">➡️ Hacia {esc(l['destino'])}</div>
                <span class="radar-next-time">🟢 Consultar salidas</span>
              </div>
              <div class="radar-dir-item">
                <div class="radar-dir-label">⬅️ Hacia {esc(l['origen'])}</div>
                <span class="radar-next-time">🟢 Consultar regreso</span>
              </div>
            </div>
            <span class="radar-more-link">Ver todas las horas, paradas y ramales en el Blog ↗</span>
          </a>
          <div class="lc-stops">{stops_chips}</div>
          <div class="lc-days-grid">
            <a href="{esc(url_hab)}" target="_blank" rel="noopener" class="day-link-btn">
              <span class="day-lbl">Lun a Vie</span>
              <span class="day-cnt">{l['frecuencias']['habiles']} sal. ↗</span>
            </a>
            <a href="{esc(url_sab)}" target="_blank" rel="noopener" class="day-link-btn">
              <span class="day-lbl">Sábados</span>
              <span class="day-cnt">{l['frecuencias']['sabados']} sal. ↗</span>
            </a>
            <a href="{esc(url_dom)}" target="_blank" rel="noopener" class="day-link-btn">
              <span class="day-lbl">Domingos</span>
              <span class="day-cnt">{l['frecuencias']['domingos']} sal. ↗</span>
            </a>
          </div>
          <a href="{esc(l['url'])}" target="_blank" rel="noopener" class="lc-cta-main">
            <span>📖 Consultar Horarios Completos en ServicioTI.com.uy</span>
            <span>↗</span>
          </a>
          {rel_block}
        </div>
      </article>
    """)

# 4. Pre-renderizar Directorio Geográfico A-Z (89 Localidades)
localidades_html = []
for loc in localidades:
    empresas_str = ", ".join(loc["empresas"])
    localidades_html.append(f"""
      <div class="locality-card" data-loc="{esc(loc['nombre'])}" title="Filtrar las {loc['cantidadLineas']} líneas que pasan por {esc(loc['nombre'])} ({esc(empresas_str)})">
        <div>
          <div class="loc-name">📍 {esc(loc['nombre'])}</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">{esc(empresas_str)}</div>
        </div>
        <span class="loc-count">{loc['cantidadLineas']} lín.</span>
      </div>
    """)

# 5. Pre-renderizar Archivo Completo de las 68 Publicaciones Especiales e Históricas de Blogger
archivo_html = []
for p in archivo:
    lineas_badge = f"Líneas: {', '.join(p['lineas'][:6])}" if p.get("lineas") else p.get("categoria", "Especial")
    archivo_html.append(f"""
      <a href="{esc(p['url'])}" target="_blank" rel="noopener" class="archive-item" title="Abrir publicación original en ServicioTI.com.uy">
        <div class="archive-title">📄 {esc(p['titulo'])}</div>
        <div class="archive-meta">
          <span>{esc(lineas_badge)}</span>
          <span class="archive-cta">Leer en el Blog ↗</span>
        </div>
      </a>
    """)

html_doc = f"""<!DOCTYPE html>
<html lang="es-UY">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Horarios de Ómnibus Uruguay 2026: COPSA, CUTCSA, Línea Este y COETC | ServicioTI</title>
  <meta name="description" content="Índice oficial inteligente de horarios de ómnibus suburbanos, interdepartamentales, diferenciales y locales de Uruguay. Buscador en vivo de las 90 líneas de COPSA, CUTCSA, Línea Este y COETC por localidad, corredor y horario con acceso directo a ServicioTI.com.uy.">
  <meta name="keywords" content="horarios omnibus uruguay, horarios copsa, horarios cutcsa, horarios linea este copsa, horarios coetc 222, horarios 710, horarios 711, horarios 712, horarios 713, horarios 714, horarios c1 c2 c3 c4 c5, omnibus montevideo canelones, omnibus punta del este piriapolis, servicioti horarios">
  <meta name="author" content="Andrés Franchi Ugartemendía - ServicioTI.com.uy">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="https://horarios.servicioti.com.uy/">

  <!-- Open Graph / WhatsApp / Redes Sociales -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Horarios de Ómnibus ServicioTI">
  <meta property="og:url" content="https://horarios.servicioti.com.uy/">
  <meta property="og:title" content="🚌 Índice Oficial de Horarios de Ómnibus Uruguay 2026 (COPSA • CUTCSA • Línea Este • COETC)">
  <meta property="og:description" content="Buscador instantáneo de 90 líneas, 89 localidades y Radar de Próximo Coche en vivo. Consulta todas las planillas oficiales en ServicioTI.com.uy.">
  <meta property="og:image" content="https://horarios.servicioti.com.uy/assets/icons/og-banner.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="es_UY">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="🚌 Horarios de Ómnibus Uruguay 2026 | Índice Inteligente ServicioTI">
  <meta name="twitter:description" content="Encuentra tu próximo ómnibus de COPSA, CUTCSA, Línea Este y COETC en segundos. 90 líneas y 159 guías enlazadas a ServicioTI.com.uy.">
  <meta name="twitter:image" content="https://horarios.servicioti.com.uy/assets/icons/og-banner.png">

  <!-- PWA & Icons -->
  <meta name="theme-color" content="#0056b3">
  <link rel="icon" type="image/svg+xml" href="assets/icons/favicon.svg">
  <link rel="apple-touch-icon" href="assets/icons/icon-192.png">
  <link rel="manifest" href="manifest.json">

  <!-- Estilos Principales -->
  <link rel="stylesheet" href="css/styles.css">

  <!-- Schema.org JSON-LD Multi-Entidad (WebSite + CollectionPage + 90 BusTrips + FAQPage) -->
  <script type="application/ld+json">
{json.dumps(schema_json_ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body>

  <!-- BARRA SUPERIOR STICKY -->
  <header class="top-navbar">
    <div class="container navbar-inner">
      <a href="#top" class="brand-logo">
        <img src="assets/icons/favicon.svg" alt="Logo Horarios ServicioTI" width="36" height="36">
        <span>Horarios <span style="color: var(--brand-primary);">ServicioTI</span></span>
        <span class="brand-tag">Uruguay 2026</span>
      </a>

      <nav class="nav-links" aria-label="Navegación rápida del índice">
        <a href="#guias-oficiales" class="nav-pill">📚 Catálogos</a>
        <a href="#catalogo-lineas" class="nav-pill">🚌 90 Líneas</a>
        <a href="#directorio-localidades" class="nav-pill">📍 89 Localidades</a>
        <a href="#archivo-blogger" class="nav-pill">🗂️ Archivo Completo (68)</a>
        <a href="#preguntas-frecuentes" class="nav-pill">❓ Ayuda y Teléfonos</a>
      </nav>

      <div style="display: flex; align-items: center; gap: 8px;">
        <div class="live-clock-pill" title="Hora oficial en Montevideo, Uruguay (UTC-3)">
          <span class="pulse-dot"></span>
          <span id="liveClockText">Uruguay • En Vivo</span>
        </div>
        <button type="button" id="btnThemeToggle" class="btn-theme" title="Cambiar modo claro / oscuro" aria-label="Cambiar tema de color">🌗</button>
        <a href="https://www.servicioti.com.uy/" target="_blank" rel="noopener" class="btn-blog-top" title="Ir al Blog Principal www.servicioti.com.uy">
          <span>Ir a ServicioTI.com.uy</span>
          <span>↗</span>
        </a>
      </div>
    </div>
  </header>

  <!-- HERO PRINCIPAL Y BUSCADOR OMNICANAL -->
  <section id="top" class="hero-section">
    <div class="container">
      <div class="hero-badge-row">
        <span class="hero-pill">⚡ El Índice Maestro de Transporte del Uruguay</span>
        <span class="hero-pill">🏛️ Fuente Oficial: www.servicioti.com.uy</span>
      </div>

      <h1 class="hero-title">
        Todos los Horarios de Ómnibus de <span>COPSA, CUTCSA, Línea Este y COETC</span> en un Solo Lugar
      </h1>
      <p class="hero-subtitle">
        Buscá por número de línea, barrio, balneario o ruta, consultá el <strong>Radar de Próximo Coche en Vivo</strong> y abrí con un toque la planilla oficial completa en <strong>ServicioTI.com.uy</strong>.
      </p>

      <!-- CAJA DE BÚSQUEDA OMNICANAL -->
      <div class="Omnisearch-box" role="search">
        <span class="search-icon">🔍</span>
        <input
          type="search"
          id="searchInput"
          class="search-input-main"
          placeholder="Buscar línea o destino (ej: 710, C4, Piriápolis, Salinas, Pando, 222, San Francisco, Cerro)..."
          aria-label="Buscar línea de ómnibus, localidad o corredor"
          autocomplete="off"
        >
        <div class="search-actions">
          <span class="kbd-hint">Ctrl + K</span>
          <button type="button" id="btnVoiceSearch" class="btn-icon-search" title="Buscar por voz" aria-label="Buscar por voz">🎤</button>
          <button type="button" id="btnClearSearch" class="btn-icon-search" title="Limpiar búsqueda" aria-label="Limpiar búsqueda">✕</button>
        </div>
      </div>

      <!-- BÚSQUEDAS RÁPIDAS POPULARES -->
      <div class="quick-chips-row">
        <span class="quick-chip-label">🔥 Más buscados:</span>
        <button type="button" class="quick-chip" data-query="710">🚌 Línea 710</button>
        <button type="button" class="quick-chip" data-query="Línea Este">🏖️ Línea Este (Punta del Este / Piriápolis)</button>
        <button type="button" class="quick-chip" data-query="713">🌊 Línea 713 (Jaureguiberry)</button>
        <button type="button" class="quick-chip" data-query="San Francisco">🌴 Balneario San Francisco</button>
        <button type="button" class="quick-chip" data-query="C4">🚍 CUTCSA C4</button>
        <button type="button" class="quick-chip" data-query="222">🚐 COETC 222</button>
        <button type="button" class="quick-chip" data-query="7A">🛣️ Línea 7A Pando</button>
        <button type="button" class="quick-chip" data-query="DM1">🏢 Línea DM1 Zonamerica</button>
        <button type="button" class="quick-chip" data-query="2A">🌾 Línea 2A Santa Lucía</button>
      </div>

      <!-- MÉTRICAS DEL SISTEMA -->
      <div class="hero-stats-grid">
        <div class="hero-stat-card">
          <span class="stat-num">{meta['totalLineas']}</span>
          <span class="stat-desc">Líneas Indexadas</span>
        </div>
        <div class="hero-stat-card">
          <span class="stat-num">{meta['totalLocalidades']}</span>
          <span class="stat-desc">Localidades y Barrios</span>
        </div>
        <div class="hero-stat-card">
          <span class="stat-num">{meta['totalFrecuencias']:,}</span>
          <span class="stat-desc">Salidas Registradas</span>
        </div>
        <div class="hero-stat-card">
          <span class="stat-num">{meta['totalUrlsBloggerIndexadas']}</span>
          <span class="stat-desc">Páginas en ServicioTI.com.uy</span>
        </div>
      </div>
    </div>
  </section>

  <main class="container">

    <!-- PLANIFICADOR INTELIGENTE ORIGEN ↔ DESTINO -->
    <section class="planner-card" aria-label="Planificador de viaje entre localidades">
      <div class="planner-header">
        <div class="planner-title">
          <span>🧭 Planificador Inteligente Origen ↔ Destino</span>
          <span style="font-size: 12px; font-weight: 700; background: var(--copsa-bg); color: var(--brand-primary); padding: 2px 10px; border-radius: 999px;">Multi-Empresa</span>
        </div>
        <span style="font-size: 12.5px; color: var(--text-muted); font-weight: 600;">Elegí dos localidades para filtrar todas las líneas que las conectan</span>
      </div>
      <div class="planner-controls">
        <select id="plannerOrigen" class="planner-select" aria-label="Seleccionar localidad de origen">
          <option value="">📍 Desde cualquier origen (Ej: Montevideo, El Pinar...)</option>
        </select>
        <button type="button" id="btnSwapPlanner" class="btn-swap" title="Invertir Origen y Destino" aria-label="Invertir Origen y Destino">⇄</button>
        <select id="plannerDestino" class="planner-select" aria-label="Seleccionar localidad de destino">
          <option value="">🏁 Hacia cualquier destino (Ej: Parque del Plata, Pando...)</option>
        </select>
        <button type="button" id="btnClearPlanner" class="btn-planner-clear">Limpiar</button>
      </div>
    </section>

    <!-- GUÍAS OFICIALES Y CATÁLOGOS MAESTROS EN BLOGGER -->
    <section id="guias-oficiales" class="section-block">
      <div class="section-header">
        <div>
          <h2 class="section-title">📚 Catálogos Oficiales y Guías Maestras en ServicioTI.com.uy</h2>
          <p class="section-subtitle">Acceso directo a las páginas centrales alojadas en Blogger con directorios completos y cuadros tarifarios</p>
        </div>
      </div>
      <div class="guides-grid">
        {"".join(guias_html)}
      </div>
    </section>

    <!-- CATÁLOGO INTERACTIVO DE LAS 90 LÍNEAS -->
    <section id="catalogo-lineas" class="section-block">
      <div class="section-header">
        <div>
          <h2 class="section-title">🚌 Índice Maestro de Líneas y Radar de Próximas Salidas</h2>
          <p class="section-subtitle">Cada tarjeta calcula el próximo coche en tiempo real y enlaza directamente a la publicación oficial en <strong>www.servicioti.com.uy</strong></p>
        </div>
      </div>

      <!-- BARRA DE FILTROS -->
      <div class="controls-toolbar">
        <div class="filter-tabs-row">
          <div class="company-tabs" role="tablist" aria-label="Filtrar por empresa de transporte">
            <button type="button" class="tab-btn active" data-empresa="ALL">🌐 Todas ({len(lineas)})</button>
            <button type="button" class="tab-btn" data-empresa="COPSA">🟦 COPSA Suburbana (52)</button>
            <button type="button" class="tab-btn" data-empresa="CUTCSA">🟥 CUTCSA C • D • L (34)</button>
            <button type="button" class="tab-btn" data-empresa="COPSA Este">🟩 COPSA Línea Este y 713 (2)</button>
            <button type="button" class="tab-btn" data-empresa="COETC">🟪 COETC 222 / 222D (2)</button>
            <button type="button" class="tab-btn" data-empresa="FAVS">⭐ Mis Favoritas (<span id="favCountBadge">0</span>)</button>
          </div>
        </div>

        <div class="secondary-filters-row">
          <div class="filter-group">
            <select id="corredorSelect" class="filter-select" aria-label="Filtrar por corredor">
              <option value="ALL">🛣️ Todos los Corredores</option>
            </select>

            <select id="diaRadarSelect" class="filter-select" aria-label="Seleccionar tipo de día para el radar">
              <option value="AUTO">📡 Radar Día: Automático (Hoy en Uruguay)</option>
              <option value="habiles">💼 Simular Lunes a Viernes (Hábiles)</option>
              <option value="sabados">🛍️ Simular Sábados</option>
              <option value="domingos">☀️ Simular Domingos y Feriados</option>
            </select>

            <select id="ordenSelect" class="filter-select" aria-label="Ordenar listado de líneas">
              <option value="DESTACADAS">🔥 Ordenar: Líneas Más Consultadas</option>
              <option value="PROXIMO">⏱️ Ordenar: Próximo Coche en Salir</option>
              <option value="FRECUENCIA">📊 Ordenar: Mayor Cantidad de Frecuencias</option>
              <option value="CODIGO">🔤 Ordenar: Código de Línea (A–Z)</option>
            </select>
          </div>

          <div id="resultsCounter" class="results-counter">
            Mostrando {len(lineas)} de {len(lineas)} líneas indexadas • 100% enlazadas a ServicioTI.com.uy
          </div>
        </div>
      </div>

      <!-- GRILLA DE TARJETAS PRE-RENDERIZADAS -->
      <div id="linesGrid" class="lines-grid">
        {"".join(lineas_html)}
      </div>
    </section>

    <!-- DIRECTORIO GEOGRÁFICO A-Z (89 LOCALIDADES, BARRIOS Y BALNEARIOS) -->
    <section id="directorio-localidades" class="section-block">
      <div class="section-header">
        <div>
          <h2 class="section-title">📍 Índice Geográfico A–Z por Localidades, Balnearios y Barrios ({len(localidades)})</h2>
          <p class="section-subtitle">Tocá cualquier localidad de Montevideo, Canelones o Maldonado para ver todas las líneas que pasan por allí y abrir sus horarios en el Blog</p>
        </div>
      </div>
      <div id="localitiesCloud" class="localities-cloud">
        {"".join(localidades_html)}
      </div>
    </section>

    <!-- ARCHIVO COMPLETO DE LAS 68 PUBLICACIONES ESPECIALES E HISTÓRICAS EN BLOGGER -->
    <section id="archivo-blogger" class="section-block">
      <div class="section-header">
        <div>
          <h2 class="section-title">🗂️ Índice Completo de Publicaciones Especiales, Corredores y Archivo en Blogger ({len(archivo)})</h2>
          <p class="section-subtitle">Todas las publicaciones agrupadas por ruta (Ruta 5, Ruta 8, Ruta 84, Costa de Oro), por día (Hábiles, Sábados, Domingos), Verano/Invierno y Tarifas alojadas en <strong>www.servicioti.com.uy</strong></p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <input
            type="search"
            id="archiveSearchInput"
            class="filter-select"
            placeholder="🔍 Filtrar publicación (ej. Ruta 84, 710, Sábados)..."
            aria-label="Filtrar publicaciones del archivo del blog"
          >
          <select id="archiveDiaSelect" class="filter-select" aria-label="Filtrar archivo por tipo de día">
            <option value="ALL">Todas las categorías ({len(archivo)})</option>
            <option value="habiles">Días Hábiles</option>
            <option value="sabados">Sábados</option>
            <option value="domingos">Domingos</option>
            <option value="verano">Especiales Verano</option>
            <option value="tarifas">Precios y Boletos</option>
          </select>
          <span id="archiveCounter" class="results-counter" style="align-self: center;">{len(archivo)} publicaciones indexadas</span>
        </div>
      </div>

      <div id="archiveGrid" class="archive-grid">
        {"".join(archivo_html)}
      </div>
    </section>

    <!-- PREGUNTAS FRECUENTES (FAQ) Y TELÉFONOS DE EMPRESAS -->
    <section id="preguntas-frecuentes" class="section-block">
      <div class="section-header">
        <div>
          <h2 class="section-title">❓ Preguntas Frecuentes y Teléfonos Oficiales de Atención</h2>
          <p class="section-subtitle">Información útil sobre terminales, empresas suburbanas y funcionamiento del índice</p>
        </div>
      </div>

      <div class="faq-grid">
        <div class="faq-card">
          <h3>📖 ¿Dónde veo todas las horas de pasada y paradas intermedias?</h3>
          <p>
            Este portal (<strong>horarios.servicioti.com.uy</strong>) funciona como el índice inteligente y radar rápido. Al hacer clic en cualquier línea o día (Lunes a Viernes, Sábados o Domingos), se abre la <strong>publicación oficial completa en <a href="https://www.servicioti.com.uy/" target="_blank" rel="noopener" style="color: var(--brand-primary); font-weight: 700;">www.servicioti.com.uy</a></strong> con todas las grillas horarias detalladas.
          </p>
        </div>

        <div class="faq-card">
          <h3>📞 Teléfonos de Atención al Cliente y Terminales</h3>
          <p>
            • <strong>COPSA Suburbana y Este:</strong> Tel. 2902 1818 | WhatsApp 098 001 970<br>
            • <strong>CUTCSA:</strong> Tel. 19333 | WhatsApp 094 805 818<br>
            • <strong>COETC:</strong> Tel. 19272<br>
            • <strong>Terminal Baltasar Brum (Río Branco):</strong> Tel. 2908 6594<br>
            • <strong>Terminal Tres Cruces:</strong> Tel. 2408 8601
          </p>
        </div>

        <div class="faq-card">
          <h3>🏖️ ¿Qué líneas van a la Costa de Oro, Piriápolis y Punta del Este?</h3>
          <p>
            Hacia <strong>Ciudad de la Costa y Costa de Oro</strong> operan COPSA (700, 705, 707, 708, 709, 710, 711, 712, 713, 714, 7E5, 7E7R, 7E8D, 7E8R, 8E7R, 8E8R), CUTCSA (C1, C2, C3, C4, C5) y COETC (222 y 222D). Hacia <strong>Piriápolis, Balneario San Francisco, Maldonado y Punta del Este</strong> opera la <a href="https://www.servicioti.com.uy/2026/10/horarios-copsa-linea-este-montevideo.html" target="_blank" rel="noopener" style="color: var(--brand-primary); font-weight: 700;">Línea Este de COPSA</a>.
          </p>
        </div>
      </div>
    </section>

  </main>

  <!-- FOOTER CON ENLACES DIRECTOS AL ECOSISTEMA SERVICIOTI -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <h4>🚌 Horarios ServicioTI Uruguay</h4>
          <p style="color: #94a3b8; line-height: 1.5; margin-bottom: 10px;">
            Índice centralizado de transporte colectivo urbano, suburbano e interdepartamental. Todas las consultas horarias son servidas por nuestro portal principal en Blogger.
          </p>
          <p><a href="https://www.servicioti.com.uy/" target="_blank" rel="noopener">👉 Visitar www.servicioti.com.uy</a></p>
        </div>

        <div class="footer-col">
          <h4>📚 Catálogos Principales en el Blog</h4>
          <ul>
            <li><a href="https://www.servicioti.com.uy/p/horarios-copsa-guia-de-todas-las-lineas.html" target="_blank" rel="noopener">Guía Oficial COPSA (52 Líneas)</a></li>
            <li><a href="https://www.servicioti.com.uy/p/horarios-cutcsa-guia-de-lineas-c-d-l.html" target="_blank" rel="noopener">Guía Oficial CUTCSA (Líneas C, D y L)</a></li>
            <li><a href="https://www.servicioti.com.uy/p/horarios-copsa-linea-este-y-linea-713.html" target="_blank" rel="noopener">Guía COPSA Línea Este y 713</a></li>
            <li><a href="https://www.servicioti.com.uy/2024/03/222-222d-horarios-dias-habiles-coetc.html" target="_blank" rel="noopener">Horarios COETC 222 y 222D</a></li>
            <li><a href="https://www.servicioti.com.uy/2024/03/c5-c4-c3-c2-c1-214-directo-precio.html" target="_blank" rel="noopener">Precios de Boletos Suburbanos</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>🔥 Líneas Más Consultadas</h4>
          <ul>
            <li><a href="https://www.servicioti.com.uy/2026/09/horarios-copsa-linea-710-710-montevideo.html" target="_blank" rel="noopener">COPSA Línea 710 (Parque del Plata)</a></li>
            <li><a href="https://www.servicioti.com.uy/2026/10/horarios-copsa-linea-este-montevideo.html" target="_blank" rel="noopener">COPSA Línea Este (Punta del Este / Piriápolis)</a></li>
            <li><a href="https://www.servicioti.com.uy/2026/10/horarios-copsa-linea-713-montevideo.html" target="_blank" rel="noopener">COPSA Línea 713 (Jaureguiberry)</a></li>
            <li><a href="https://www.servicioti.com.uy/2026/09/horarios-cutcsa-linea-c4-montevideo.html" target="_blank" rel="noopener">CUTCSA Línea C4 (Parque del Plata)</a></li>
            <li><a href="https://www.servicioti.com.uy/2026/09/horarios-copsa-linea-7a-7a-montevideo.html" target="_blank" rel="noopener">COPSA Línea 7A (Montevideo / Pando)</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>🌐 Ecosistema ServicioTI.com.uy</h4>
          <ul>
            <li><a href="https://www.servicioti.com.uy/" target="_blank" rel="noopener">Portal Principal ServicioTI</a></li>
            <li><a href="https://truco-uruguayo.servicioti.com.uy/" target="_blank" rel="noopener">Truco Uruguayo Online</a></li>
            <li><a href="https://conga.servicioti.com.uy/" target="_blank" rel="noopener">Conga Uruguaya Premium</a></li>
            <li><a href="https://www.servicioti.com.uy/p/juegos-de-cartas-uruguayos-online-truco.html" target="_blank" rel="noopener">Portal de Juegos Criollos</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <p>© 2026 <strong>ServicioTI.com.uy</strong> • Desarrollado por Andrés Franchi Ugartemendía • Todos los enlaces de horarios dirigen a las publicaciones oficiales en Blogger.</p>
      </div>
    </div>
  </footer>

  <!-- SCRIPTS DE DATOS E INTERACTIVIDAD -->
  <script src="js/data.js"></script>
  <script src="js/app.js"></script>
</body>
</html>
"""

with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("OK: index.html generado con exito. Bytes:", os.path.getsize(INDEX_HTML_PATH))
