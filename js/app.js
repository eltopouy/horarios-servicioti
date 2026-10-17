/**
 * Motor Interactivo Principal - horarios.servicioti.com.uy
 * 100% Enrutador de Tráfico hacia Blogger (www.servicioti.com.uy)
 * Incluye Radar en Vivo UTC-3, Planificador Origen ↔ Destino, Buscador por Voz y Favoritos.
 */
(function () {
  'use strict';

  const DATA = window.HORARIOS_DATA || { lineas: [], localidades: [], archivoBlogger: [], guiasMaestras: [] };
  const FAV_STORAGE_KEY = 'sti_horarios_favs_v1';
  const THEME_STORAGE_KEY = 'sti_horarios_theme_v1';

  let state = {
    query: '',
    empresa: 'ALL',
    corredor: 'ALL',
    origen: '',
    destino: '',
    diaRadar: 'AUTO', // AUTO | habiles | sabados | domingos
    orden: 'DESTACADAS', // DESTACADAS | PROXIMO | FRECUENCIA | CODIGO
    archiveQuery: '',
    archiveDia: 'ALL',
    favs: loadFavs()
  };

  function loadFavs() {
    try {
      const raw = localStorage.getItem(FAV_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveFavs(favs) {
    try {
      localStorage.setItem(FAV_STORAGE_KEY, JSON.stringify(favs));
    } catch (e) {}
  }

  function normalizeText(str) {
    if (!str) return '';
    return String(str)
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  }

  // Obtener hora y día actual en Montevideo (UTC-3)
  function getUruguayNow() {
    const now = new Date();
    try {
      const parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Montevideo',
        hour12: false,
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
      }).formatToParts(now);
      const map = {};
      parts.forEach((p) => { map[p.type] = p.value; });
      const h = parseInt(map.hour || '0', 10) % 24;
      const m = parseInt(map.minute || '0', 10);
      const wd = map.weekday || 'Mon';
      let diaTipo = 'habiles';
      let diaNombre = 'Lunes a Viernes';
      if (wd === 'Sat') {
        diaTipo = 'sabados';
        diaNombre = 'Sábado';
      } else if (wd === 'Sun') {
        diaTipo = 'domingos';
        diaNombre = 'Domingo';
      }
      return {
        hhmm: String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0'),
        minutesOfDay: h * 60 + m,
        diaTipo,
        diaNombre
      };
    } catch (e) {
      const h = now.getHours();
      const m = now.getMinutes();
      const d = now.getDay();
      const diaTipo = d === 0 ? 'domingos' : (d === 6 ? 'sabados' : 'habiles');
      const diaNombre = d === 0 ? 'Domingo' : (d === 6 ? 'Sábado' : 'Lunes a Viernes');
      return {
        hhmm: String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0'),
        minutesOfDay: h * 60 + m,
        diaTipo,
        diaNombre
      };
    }
  }

  function timeToMinutes(hhmm) {
    if (!hhmm || !hhmm.includes(':')) return -1;
    const [h, m] = hhmm.split(':').map(Number);
    return h * 60 + m;
  }

  function computeNextDeparture(timesArray, nowMinutes) {
    if (!timesArray || !timesArray.length) {
      return { next: null, diffMinutes: 99999, remaining: 0 };
    }
    let nextTime = null;
    let diff = 99999;
    let remaining = 0;

    for (let i = 0; i < timesArray.length; i++) {
      const t = timesArray[i];
      const mins = timeToMinutes(t);
      if (mins >= nowMinutes) {
        if (nextTime === null) {
          nextTime = t;
          diff = mins - nowMinutes;
        }
        remaining++;
      }
    }

    // Si ya pasaron todos hoy, mostrar el primero de mañana
    if (nextTime === null && timesArray.length > 0) {
      const firstTomorrow = timesArray[0];
      const minsFirst = timeToMinutes(firstTomorrow);
      return {
        next: firstTomorrow,
        diffMinutes: (24 * 60 - nowMinutes) + minsFirst,
        remaining: 0,
        isTomorrow: true
      };
    }

    return { next: nextTime, diffMinutes: diff, remaining, isTomorrow: false };
  }

  function formatCountdown(info) {
    if (!info || !info.next) return '<span class="radar-next-time ended">Sin servicio hoy</span>';
    if (info.isTomorrow) {
      return `<span class="radar-next-time ended">🕒 ${info.next} (1° salida mañana)</span>`;
    }
    if (info.diffMinutes === 0) {
      return `<span class="radar-next-time">🟢 ${info.next} (¡Saliendo ahora!)</span>`;
    }
    if (info.diffMinutes < 60) {
      return `<span class="radar-next-time">🟢 ${info.next} (en ${info.diffMinutes} min)</span>`;
    }
    const hrs = Math.floor(info.diffMinutes / 60);
    const mins = info.diffMinutes % 60;
    return `<span class="radar-next-time">🕒 ${info.next} (en ${hrs}h ${mins}m)</span>`;
  }

  // Actualizar reloj superior en vivo
  function updateClockUI() {
    const uNow = getUruguayNow();
    const clockEl = document.getElementById('liveClockText');
    if (clockEl) {
      clockEl.textContent = `Uruguay ${uNow.hhmm} hs • ${uNow.diaNombre}`;
    }
  }

  // Construir el HTML de una tarjeta de línea (100% enlaces directos a Blogger)
  function renderLineCardHTML(l, uNow, activeDia) {
    const isFav = state.favs.includes(l.uid);
    const salidasDia = (l.salidas && l.salidas[activeDia]) ? l.salidas[activeDia] : { ida: [], vuelta: [] };
    const nextIda = computeNextDeparture(salidasDia.ida, uNow.minutesOfDay);
    const nextVta = computeNextDeparture(salidasDia.vuelta, uNow.minutesOfDay);
    const totalRestantes = nextIda.remaining + nextVta.remaining;

    const diaLabelMap = {
      habiles: 'Lunes a Viernes',
      sabados: 'Sábados',
      domingos: 'Domingos y Feriados'
    };

    const stopsHtml = (l.localidades || []).slice(0, 7).map((loc) =>
      `<button type="button" class="stop-chip" data-loc="${loc}" title="Filtrar líneas que pasan por ${loc}">📍 ${loc}</button>`
    ).join('');

    const extraStopsCount = Math.max(0, (l.localidades || []).length - 7);
    const moreStopsBadge = extraStopsCount > 0
      ? `<span class="stop-chip" style="cursor:default;">+${extraStopsCount} zonas</span>`
      : '';

    const novedadHtml = l.novedad
      ? `<div class="lc-novedad">✨ ${l.novedad}</div>`
      : '';

    const relatedPosts = l.postsRelacionados || [];
    const relatedHtml = relatedPosts.length > 0
      ? `<details class="lc-related">
          <summary>🔗 +${relatedPosts.length} guías y planillas específicas en el Blog</summary>
          <ul class="lc-related-list">
            ${relatedPosts.slice(0, 6).map((rp) =>
              `<li><a href="${rp.url}" target="_blank" rel="noopener">📄 ${rp.titulo} ↗</a></li>`
            ).join('')}
          </ul>
        </details>`
      : '';

    const urlHab = (l.urlsPorDia && l.urlsPorDia.habiles) || l.url;
    const urlSab = (l.urlsPorDia && l.urlsPorDia.sabados) || l.url;
    const urlDom = (l.urlsPorDia && l.urlsPorDia.domingos) || l.url;

    return `
      <article class="line-card" data-empresa="${l.empresa}" data-uid="${l.uid}">
        <div class="lc-header">
          <div class="lc-id-group">
            <a href="${l.url}" target="_blank" rel="noopener" class="lc-badge" title="Abrir horarios oficiales de Línea ${l.id} en ServicioTI.com.uy">${l.id}</a>
            <div class="lc-title-wrap">
              <h3><a href="${l.url}" target="_blank" rel="noopener">${l.nombre}</a></h3>
              <div class="lc-meta-tags">
                <span class="lc-tag">${l.empresa}</span>
                <span class="lc-tag">${l.corredor}</span>
                <span class="lc-tag">${l.departamento}</span>
              </div>
            </div>
          </div>
          <button type="button" class="btn-fav ${isFav ? 'active' : ''}" data-fav="${l.uid}" aria-label="Guardar línea ${l.id} en favoritos" title="${isFav ? 'Quitar de favoritos' : 'Fijar en mis líneas favoritas'}">
            ${isFav ? '⭐' : '☆'}
          </button>
        </div>

        <div class="lc-body">
          ${novedadHtml}

          <!-- RADAR EN VIVO (TEASER QUE ENVÍA EL TRÁFICO A BLOGGER) -->
          <a href="${l.url}" target="_blank" rel="noopener" class="lc-radar-box" title="Clic para consultar la tabla completa de horarios en ServicioTI.com.uy">
            <div class="radar-top">
              <span>📡 Radar Próximo Coche (${diaLabelMap[activeDia]})</span>
              <span>${totalRestantes > 0 ? `+${totalRestantes} salidas hoy` : 'Ver grilla completa'}</span>
            </div>
            <div class="radar-times-grid">
              <div class="radar-dir-item">
                <div class="radar-dir-label">➡️ Hacia ${l.destino}</div>
                ${formatCountdown(nextIda)}
              </div>
              <div class="radar-dir-item">
                <div class="radar-dir-label">⬅️ Hacia ${l.origen}</div>
                ${formatCountdown(nextVta)}
              </div>
            </div>
            <span class="radar-more-link">Ver todas las horas, paradas y ramales en el Blog ↗</span>
          </a>

          <!-- LOCALIDADES Y BARRIOS QUE CONECTA -->
          <div class="lc-stops">
            ${stopsHtml}
            ${moreStopsBadge}
          </div>

          <!-- ENLACES DIRECTOS POR DÍA HACIA BLOGGER -->
          <div class="lc-days-grid">
            <a href="${urlHab}" target="_blank" rel="noopener" class="day-link-btn ${l.frecuencias.habiles === 0 ? 'zero' : ''}" title="Ver horarios Lunes a Viernes de Línea ${l.id} en ServicioTI.com.uy">
              <span class="day-lbl">Lun a Vie</span>
              <span class="day-cnt">${l.frecuencias.habiles} sal. ↗</span>
            </a>
            <a href="${urlSab}" target="_blank" rel="noopener" class="day-link-btn ${l.frecuencias.sabados === 0 ? 'zero' : ''}" title="Ver horarios Sábados de Línea ${l.id} en ServicioTI.com.uy">
              <span class="day-lbl">Sábados</span>
              <span class="day-cnt">${l.frecuencias.sabados} sal. ↗</span>
            </a>
            <a href="${urlDom}" target="_blank" rel="noopener" class="day-link-btn ${l.frecuencias.domingos === 0 ? 'zero' : ''}" title="Ver horarios Domingos y Feriados de Línea ${l.id} en ServicioTI.com.uy">
              <span class="day-lbl">Domingos</span>
              <span class="day-cnt">${l.frecuencias.domingos} sal. ↗</span>
            </a>
          </div>

          <!-- BOTÓN PRINCIPAL DE CONSULTA EN BLOGGER -->
          <a href="${l.url}" target="_blank" rel="noopener" class="lc-cta-main">
            <span>📖 Consultar Horarios Completos en ServicioTI.com.uy</span>
            <span>↗</span>
          </a>

          ${relatedHtml}
        </div>
      </article>
    `;
  }

  function filterAndRenderLines() {
    const grid = document.getElementById('linesGrid');
    const counter = document.getElementById('resultsCounter');
    if (!grid) return;

    const uNow = getUruguayNow();
    const activeDia = state.diaRadar === 'AUTO' ? uNow.diaTipo : state.diaRadar;
    const q = normalizeText(state.query);

    let filtered = DATA.lineas.filter((l) => {
      if (state.empresa === 'FAVS') {
        if (!state.favs.includes(l.uid)) return false;
      } else if (state.empresa !== 'ALL' && l.empresa !== state.empresa) {
        return false;
      }

      if (state.corredor !== 'ALL' && l.corredor !== state.corredor) {
        return false;
      }

      if (state.origen && !(l.localidades || []).includes(state.origen)) {
        return false;
      }
      if (state.destino && !(l.localidades || []).includes(state.destino)) {
        return false;
      }

      if (q) {
        const haystack = normalizeText(
          `${l.id} ${l.nombreCompleto} ${l.empresa} ${l.corredor} ${l.departamento} ${(l.localidades || []).join(' ')}`
        );
        const tokens = q.split(/\s+/).filter(Boolean);
        for (const tok of tokens) {
          if (!haystack.includes(tok)) return false;
        }
      }

      return true;
    });

    // Ordenamiento inteligente
    filtered.sort((a, b) => {
      // Primero favoritos fijados
      const aFav = state.favs.includes(a.uid) ? 1 : 0;
      const bFav = state.favs.includes(b.uid) ? 1 : 0;
      if (aFav !== bFav) return bFav - aFav;

      if (state.orden === 'PROXIMO') {
        const sa = (a.salidas && a.salidas[activeDia]) ? a.salidas[activeDia] : { ida: [], vuelta: [] };
        const sb = (b.salidas && b.salidas[activeDia]) ? b.salidas[activeDia] : { ida: [], vuelta: [] };
        const da = Math.min(
          computeNextDeparture(sa.ida, uNow.minutesOfDay).diffMinutes,
          computeNextDeparture(sa.vuelta, uNow.minutesOfDay).diffMinutes
        );
        const db = Math.min(
          computeNextDeparture(sb.ida, uNow.minutesOfDay).diffMinutes,
          computeNextDeparture(sb.vuelta, uNow.minutesOfDay).diffMinutes
        );
        return da - db;
      }

      if (state.orden === 'FRECUENCIA') {
        return (b.frecuencias.total || 0) - (a.frecuencias.total || 0);
      }

      if (state.orden === 'CODIGO') {
        return String(a.id).localeCompare(String(b.id), 'es', { numeric: true });
      }

      // DESTACADAS por defecto
      const aDest = a.destacada ? 1 : 0;
      const bDest = b.destacada ? 1 : 0;
      if (aDest !== bDest) return bDest - aDest;
      return (b.frecuencias.total || 0) - (a.frecuencias.total || 0);
    });

    if (counter) {
      counter.textContent = `Mostrando ${filtered.length} de ${DATA.lineas.length} líneas indexadas • 100% enlazadas a ServicioTI.com.uy`;
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 14px; padding: 36px 24px; text-align: center;">
          <div style="font-size: 40px; margin-bottom: 10px;">🚌</div>
          <h3 style="font-size: 18px; font-weight: 800; margin-bottom: 6px;">No encontramos líneas con ese filtro exacto</h3>
          <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 16px;">Prueba limpiar los filtros o consulta directamente los catálogos generales en nuestro blog oficial.</p>
          <button type="button" id="btnResetEmpty" style="background: var(--brand-primary); color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 800; cursor: pointer;">Restablecer todos los filtros</button>
        </div>
      `;
      const btnReset = document.getElementById('btnResetEmpty');
      if (btnReset) btnReset.addEventListener('click', resetAllFilters);
      return;
    }

    grid.innerHTML = filtered.map((l) => renderLineCardHTML(l, uNow, activeDia)).join('');
  }

  function filterArchiveList() {
    const archiveGrid = document.getElementById('archiveGrid');
    const archiveCount = document.getElementById('archiveCounter');
    if (!archiveGrid) return;

    const q = normalizeText(state.archiveQuery);
    const items = (DATA.archivoBlogger || []).filter((item) => {
      if (state.archiveDia !== 'ALL' && item.diaTipo !== state.archiveDia) return false;
      if (q) {
        const hay = normalizeText(`${item.titulo} ${(item.lineas || []).join(' ')} ${item.categoria}`);
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    if (archiveCount) {
      archiveCount.textContent = `${items.length} publicaciones indexadas`;
    }

    archiveGrid.innerHTML = items.map((p) => `
      <a href="${p.url}" target="_blank" rel="noopener" class="archive-item" title="Abrir artículo oficial en ServicioTI.com.uy">
        <div class="archive-title">📄 ${p.titulo}</div>
        <div class="archive-meta">
          <span>${(p.lineas && p.lineas.length) ? 'Líneas: ' + p.lineas.slice(0, 6).join(', ') : p.categoria}</span>
          <span class="archive-cta">Leer en el Blog ↗</span>
        </div>
      </a>
    `).join('');
  }

  function resetAllFilters() {
    state.query = '';
    state.empresa = 'ALL';
    state.corredor = 'ALL';
    state.origen = '';
    state.destino = '';

    const sInput = document.getElementById('searchInput');
    if (sInput) sInput.value = '';
    const corSel = document.getElementById('corredorSelect');
    if (corSel) corSel.value = 'ALL';
    const origSel = document.getElementById('plannerOrigen');
    if (origSel) origSel.value = '';
    const destSel = document.getElementById('plannerDestino');
    if (destSel) destSel.value = '';

    document.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.empresa === 'ALL');
    });

    filterAndRenderLines();
  }

  function initPlannerAndCorridors() {
    const origSel = document.getElementById('plannerOrigen');
    const destSel = document.getElementById('plannerDestino');
    const corSel = document.getElementById('corredorSelect');

    if (origSel && destSel && DATA.localidades) {
      const opts = DATA.localidades.map((loc) =>
        `<option value="${loc.nombre}">${loc.nombre} (${loc.cantidadLineas} lín.)</option>`
      ).join('');
      origSel.innerHTML = `<option value="">📍 Desde cualquier origen (Ej: Montevideo, El Pinar...)</option>` + opts;
      destSel.innerHTML = `<option value="">🏁 Hacia cualquier destino (Ej: Parque del Plata, Pando...)</option>` + opts;

      origSel.addEventListener('change', (e) => {
        state.origen = e.target.value;
        filterAndRenderLines();
      });
      destSel.addEventListener('change', (e) => {
        state.destino = e.target.value;
        filterAndRenderLines();
      });
    }

    const swapBtn = document.getElementById('btnSwapPlanner');
    if (swapBtn && origSel && destSel) {
      swapBtn.addEventListener('click', () => {
        const tmp = origSel.value;
        origSel.value = destSel.value;
        destSel.value = tmp;
        state.origen = origSel.value;
        state.destino = destSel.value;
        filterAndRenderLines();
      });
    }

    const clearPlannerBtn = document.getElementById('btnClearPlanner');
    if (clearPlannerBtn) {
      clearPlannerBtn.addEventListener('click', resetAllFilters);
    }

    if (corSel && DATA.lineas) {
      const corridors = Array.from(new Set(DATA.lineas.map((l) => l.corredor))).sort();
      corSel.innerHTML = `<option value="ALL">🛣️ Todos los Corredores (${corridors.length})</option>` +
        corridors.map((c) => `<option value="${c}">${c}</option>`).join('');
      corSel.addEventListener('change', (e) => {
        state.corredor = e.target.value;
        filterAndRenderLines();
      });
    }
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    if (saved === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
    const themeBtn = document.getElementById('btnThemeToggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        if (next === 'dark') {
          document.documentElement.setAttribute('data-theme', 'dark');
        } else {
          document.documentElement.removeAttribute('data-theme');
        }
        localStorage.setItem(THEME_STORAGE_KEY, next);
      });
    }
  }

  function initVoiceSearch() {
    const voiceBtn = document.getElementById('btnVoiceSearch');
    const sInput = document.getElementById('searchInput');
    if (!voiceBtn || !sInput) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      voiceBtn.style.display = 'none';
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'es-UY';
    recognition.interimResults = false;

    voiceBtn.addEventListener('click', () => {
      try {
        voiceBtn.textContent = '🎙️';
        recognition.start();
      } catch (e) {}
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      sInput.value = transcript;
      state.query = transcript;
      filterAndRenderLines();
    };
  }

  function initEvents() {
    const sInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('btnClearSearch');

    if (sInput) {
      sInput.addEventListener('input', (e) => {
        state.query = e.target.value;
        filterAndRenderLines();
      });
    }

    if (clearSearchBtn && sInput) {
      clearSearchBtn.addEventListener('click', () => {
        sInput.value = '';
        state.query = '';
        sInput.focus();
        filterAndRenderLines();
      });
    }

    // Atajo Ctrl+K o "/" para enfocar el buscador
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (sInput) {
          sInput.focus();
          sInput.select();
        }
      }
    });

    // Quick chips en Hero
    document.querySelectorAll('.quick-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        const q = chip.dataset.query || '';
        if (sInput) sInput.value = q;
        state.query = q;
        filterAndRenderLines();
        const catalogEl = document.getElementById('catalogo-lineas');
        if (catalogEl) catalogEl.scrollIntoView({ behavior: 'smooth' });
      });
    });

    // Tabs de empresa
    document.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.empresa = btn.dataset.empresa || 'ALL';
        filterAndRenderLines();
      });
    });

    // Selector de día del Radar y Ordenamiento
    const diaSel = document.getElementById('diaRadarSelect');
    if (diaSel) {
      diaSel.addEventListener('change', (e) => {
        state.diaRadar = e.target.value;
        filterAndRenderLines();
      });
    }

    const ordenSel = document.getElementById('ordenSelect');
    if (ordenSel) {
      ordenSel.addEventListener('change', (e) => {
        state.orden = e.target.value;
        filterAndRenderLines();
      });
    }

    // Delegación en grilla de líneas (Favoritos y chips de localidad)
    const linesGrid = document.getElementById('linesGrid');
    if (linesGrid) {
      linesGrid.addEventListener('click', (e) => {
        const favBtn = e.target.closest('.btn-fav');
        if (favBtn) {
          const uid = favBtn.dataset.fav;
          if (state.favs.includes(uid)) {
            state.favs = state.favs.filter((x) => x !== uid);
          } else {
            state.favs.push(uid);
          }
          saveFavs(state.favs);
          updateFavCountBadge();
          filterAndRenderLines();
          return;
        }

        const stopChip = e.target.closest('.stop-chip[data-loc]');
        if (stopChip) {
          const loc = stopChip.dataset.loc;
          if (sInput) sInput.value = loc;
          state.query = loc;
          filterAndRenderLines();
          const catalogEl = document.getElementById('catalogo-lineas');
          if (catalogEl) catalogEl.scrollIntoView({ behavior: 'smooth' });
        }
      });
    }

    // Delegación en Directorio Geográfico A-Z
    const locCloud = document.getElementById('localitiesCloud');
    if (locCloud) {
      locCloud.addEventListener('click', (e) => {
        const card = e.target.closest('.locality-card[data-loc]');
        if (card) {
          const loc = card.dataset.loc;
          if (sInput) sInput.value = loc;
          state.query = loc;
          filterAndRenderLines();
          const catalogEl = document.getElementById('catalogo-lineas');
          if (catalogEl) catalogEl.scrollIntoView({ behavior: 'smooth' });
        }
      });
    }

    // Buscador del archivo histórico de Blogger
    const archInput = document.getElementById('archiveSearchInput');
    if (archInput) {
      archInput.addEventListener('input', (e) => {
        state.archiveQuery = e.target.value;
        filterArchiveList();
      });
    }

    const archDiaSel = document.getElementById('archiveDiaSelect');
    if (archDiaSel) {
      archDiaSel.addEventListener('change', (e) => {
        state.archiveDia = e.target.value;
        filterArchiveList();
      });
    }
  }

  function updateFavCountBadge() {
    const badge = document.getElementById('favCountBadge');
    if (badge) {
      badge.textContent = state.favs.length;
    }
  }

  // Inicialización al cargar el DOM
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    updateClockUI();
    updateFavCountBadge();
    initPlannerAndCorridors();
    initVoiceSearch();
    initEvents();
    filterAndRenderLines();

    // Actualizar el radar en vivo cada 20 segundos
    setInterval(() => {
      updateClockUI();
      filterAndRenderLines();
    }, 20000);

    // Registrar Service Worker para PWA
    if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
      navigator.serviceWorker.register('./sw.js').catch(() => {});
    }
  });
})();
