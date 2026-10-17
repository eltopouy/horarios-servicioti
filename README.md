# 🚌 Horarios de Ómnibus Uruguay • Índice Oficial ServicioTI (`horarios.servicioti.com.uy`)

Aplicación web progresiva (PWA) e índice maestro inteligente para todas las líneas de ómnibus suburbanas, interdepartamentales, diferenciales y locales publicadas en **[www.servicioti.com.uy](https://www.servicioti.com.uy/)**.

---

## 🎯 Arquitectura "100% Tráfico hacia Blogger" (Hub & Spoke)

Este proyecto fue diseñado bajo una regla de oro:
- **`horarios.servicioti.com.uy`** actúa como el **Hub de Descubrimiento Ultra-Rápido, Buscador Omnicanal, Planificador Origen ↔ Destino y Radar de Próximo Coche en Vivo**.
- **`www.servicioti.com.uy` (Blogger)** es la **única fuente de consulta de las grillas horarias completas**. Cada tarjeta de línea, botón de día (`Lunes a Viernes`, `Sábados`, `Domingos`), chip de localidad y acceso de archivo dirige el 100% de los clics y páginas vistas directamente a los artículos originales alojados en Blogger.

---

## 📊 Cobertura del Índice (Actualización 2026)

* **90 Líneas Indexadas Individualmente:**
  * **52 Líneas de COPSA Suburbana, Local y Compartida:** Corredores Av. Italia (`700`–`8E8R`), Ruta 5 (`1A`, `2A`, `802`–`810`), Centro / Ruta 8 / Ruta 84 (`701`–`752`, `7A`, `7H`, `8A`), Locales de Canelones (`P756`–`P804`), Transversal (`757`) y Compartidas (`DM1`, `XA1`, `XA2`).
  * **34 Líneas de CUTCSA:** Corredor C Suburbanas (`C1`, `C1SD`, `C2`, `C2SD`, `C3`, `C4`, `C4D`, `C5`, `CE1`), Corredor D Diferenciales (`D1`, `D5`, `D8`, `D10`, `DM1`) y Corredor L Locales de Montevideo (`L1`–`L46`).
  * **2 Líneas de COPSA Línea Este y Costa de Oro Este:** `Línea Este` (Montevideo ↔ Piriápolis, Balneario San Francisco, Punta Colorada, Punta Negra, Maldonado, Punta del Este, La Barra, José Ignacio, Laguna Garzón) y `Línea 713` (Montevideo ↔ Araminda, Sta. Lucía del Este, Cuchilla Alta, Santa Ana, Jaureguiberry).
  * **2 Líneas de COETC Suburbana:** `222` y `222D` (Montevideo ↔ Parque del Plata).
* **6 Catálogos y Guías Maestras (`/p/...`)** + **Cuadro Tarifario de Boletos Suburbanos**.
* **68 Publicaciones Históricas y Especiales por Corredor y Día** actualizadas en Blogger.
* **89 Localidades, Barrios, Balnearios y Terminales** indexadas de la A a la Z.
* **159 URLs únicas de `www.servicioti.com.uy`** pre-renderizadas en el DOM HTML5 + Schema.org JSON-LD (`WebSite`, `CollectionPage`, `ItemList` con 90 `BusTrip`, `FAQPage`).

---

## ⚡ Funcionalidades Destacadas

1. **Radar en Vivo de Próximo Coche (Hora Oficial Uruguay `UTC-3`):** Calcula cada 20 segundos cuál es el próximo ómnibus en salir de Ida y de Vuelta según el día actual (o simulando Hábiles, Sábados o Domingos) como *teaser* dinámico para abrir la tabla completa en Blogger.
2. **Planificador Inteligente `Origen ↔ Destino`:** Compara todas las empresas que unen dos puntos (ej. *Montevideo* ↔ *Parque del Plata* o *El Pinar* ↔ *Pando*).
3. **Buscador Instantáneo (`Ctrl+K`) + Búsqueda por Voz (`Web Speech API`):** Tolerante a acentos, busca por línea, barrio, balneario, ruta o empresa.
4. **Sistema de Líneas Favoritas (`⭐`):** Fija las líneas frecuentes del pasajero en la parte superior usando `localStorage`.
5. **Pre-Renderizado Estático SEO + PWA Instalable:** Funciona al instante en móviles y escritorio con Modo Claro/Oscuro.

---

## 🛠️ Compilación y Verificación

```bash
# Recompilar base de datos desde las fuentes locales de Blogger y regenerar index.html
npm run build

# Ejecutar suite de auditoría y verificación de enlaces e integridad SEO
npm test
```

---

## 🌐 Dominio y Despliegue

* **Dominio Personalizado (`CNAME`):** [https://horarios.servicioti.com.uy](https://horarios.servicioti.com.uy)
* **Portal Fuente de Consulta:** [https://www.servicioti.com.uy](https://www.servicioti.com.uy)
* **Autor:** Andrés Franchi Ugartemendía
