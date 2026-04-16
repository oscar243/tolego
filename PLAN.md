# Plan de trabajo — Presentación Final TOLEGO

> **Si acabas de clonar el repo desde otra máquina, lee primero la sección "Handoff" al final de este archivo.** Luego vuelve aquí para ver estado y próximos pasos.

---

## 0. Contexto rápido (30 segundos)

- **Curso:** Generative AI Leader — Escuela Colombiana de Ingeniería Julio Garavito
- **Profesor:** Nicolás Fernández
- **Cliente:** Tolego — emprendimiento de minifiguras tipo Lego (Bogotá), vende por Instagram @tole.go + WhatsApp 312 347 3871
- **Equipo:** Oscar Virguez, Brayan González, Sebastián Moreno
- **Entrega:** presentación 30 min + 5 min preguntas ante 3 jurados, sube a Teams
- **Calificación:** 30% dolor con datos · 50% solución E2E · 20% presentación + mockup
- **Propuesta técnica:** plataforma E2E sobre GCP (Cloud SQL, Firestore, Dialogflow CX, Document AI, Vertex AI/Gemini, BigQuery, Looker Studio)

### Archivos clave
- **Notion (contenido base):** página "TOLEGO", ID `32b36d06-9793-812c-8afa-e655cb0165b7`
- **Rubric oficial:** `Estudiantes Trabajo final Cloud Digital Leader.pdf`
- **Diapositivas del profe:** `presentaciones_clase/Clase 1–11.pdf` (la **Clase 4 = caso Schneider = plantilla de oro**)
- **Transcripciones de clase:** `grabaciones/transcripciones/*.txt` (en Clase 1 hay feedback textual a grupos previos)
- **Mockup actual:** https://photo-lake-92987883.figma.site (versión Figma, luego haremos variante en GCP)

---

## 1. Gaps pendientes (lo que falta vs. rubric + feedback del profe)

Orden por prioridad de impacto:

| # | Entregable | Pesa | Estado |
|---|---|---|---|
| 1 | **Tabla de dolor con datos cuantificados** | 30% | ✅ (2026-04-15, actualizado en Notion con magnitud $7,15M COP/año) |
| 2 | **ROI con fórmula explícita** `(Beneficio − TCO) / TCO` | Alto | ✅ (2026-04-15, ROI 645%, payback 1,6 meses en Notion) |
| 3 | **Cronograma detallado** por fases Ideación→Realización→Utilización con roles y costos | Alto | ✅ (2026-04-15, 15 semanas + fase continua, 8 roles, 2 escenarios de costo) |
| 4 | **Conclusión estratégica + llamado a la acción** | Alto | ✅ (2026-04-15, recap dolor + 3 números + 3 dimensiones + liderazgo digital + CTA con 3 decisiones) |
| 5 | **Mockup** integrado a la presentación | 20% | ✅ Figma listo, falta embeber |
| 6 | **Demo en vivo** (Telegram Bot + Gemini + SQLite local) | Mandatorio | ✅ (2026-04-15, proyecto `mvp_bot/` listo — pendiente: pegar API keys en .env y correr) |
| 7 | **Plan de contingencia** si fallan APIs/GCP/WhatsApp | Medio | ✅ (2026-04-15, 8 escenarios + observabilidad + RPO/RTO en Notion) |
| 8 | **KPIs duplicados**: KPI del negocio ≠ KPI del modelo | Medio | ✅ (2026-04-15, 7 KPIs de negocio + 10 KPIs de solución con baseline/meta/fuente) |
| 9 | **Liderazgo digital transversal** (gestión del cambio, detractor interno) | Medio | ✅ (2026-04-15, sección dedicada en Notion: perfil sponsor + detractor + filosofía + intervenciones por etapa + comunicación + capacitación + 5 riesgos de adopción) |
| 10 | **"¿Por qué IA Gen y no algo simple?"** respondido explícitamente | Medio | ✅ (2026-04-15, sección dedicada en Notion: comparación vs status quo + alternativas descartadas + fit presupuesto/prioridad) |
| 11 | **Habeas Data (Ley 1581 Colombia)** en gobernanza | Bajo | ✅ (2026-04-15, fila en tabla de gobernanza + subsección Habeas Data con 9 componentes: autorización, ARCO, RNBD, responsable/encargado, etc.) |

---

## 2. Orden de ejecución (cronograma de trabajo)

### Paso 1 — Tabla de dolor con datos [2 h]
Responder este cuestionario (con Oscar, que tiene relación con Tolego) o estimar con benchmarks:

- [ ] ¿Pedidos promedio al mes? (rango realista: 30–80)
- [ ] ¿Minutos por pedido manual? (leer DM + verificar stock + confirmar + facturar)
- [ ] ¿Errores de precio o stock al mes? (≥3 típico en ops manuales)
- [ ] ¿Ventas perdidas por no responder a tiempo o por quiebre de stock?
- [ ] ¿Horas/semana en actualizar Excel de inventario?
- [ ] Seguidores en IG (verificable vía @tole.go)
- [ ] Tasa de conversión DM→venta efectiva (benchmark e-commerce Colombia: 2–4%)
- [ ] Ticket promedio en COP
- [ ] % ventas por franquicia (¿Marvel domina? ¿Anime?)

Si no hay datos reales, usar benchmarks de industria y anotar "estimación basada en X" (el profe acepta esto).

**Salida:** llenar la tabla de Notion en sección "Necesidad del Negocio" + calcular **costo total del dolor en COP/año** para mostrar magnitud (como Schneider: 40 M€/año).

### Paso 2 — Bloque financiero TCO + ROI [1 h]
Fórmula: `ROI = (Beneficio anual − TCO anual) / TCO anual × 100`

- **TCO estimado:** Cloud SQL ~$7 + Dialogflow 300 sesiones gratis + Document AI 1.000 páginas gratis + BigQuery ~$5 + Looker gratuito ≈ **$20 USD/mes = $240 USD/año ≈ $960.000 COP/año**
- **Beneficio estimado:** horas ahorradas × valor/hora + ventas recuperadas por respuesta rápida + reducción de merma por mejor stock
- **ROI esperado:** apuntar a un número alto justificado (>500%) — Schneider llegó a 18.947%

**Salida:** slide con tabla TCO (desglosado) + tabla Beneficios (desglosado) + fórmula aplicada.

### Paso 3 — Cronograma por fases [1 h]
Tabla o Gantt simple en 3 bloques:

| Fase | Semanas | Actividades | Rol responsable | Costo |
|---|---|---|---|---|
| Ideación | 1–3 | Levantamiento, diseño arquitectura, mockups | Consultor + dueño | $X |
| Realización | 4–10 | Implementación Cloud SQL, Dialogflow, Looker, Document AI | Desarrollador + evaluador | $Y |
| Utilización | 11+ | Puesta en producción, monitoreo, feedback, mejora continua | Operador + soporte | $Z |

**Salida:** slide de cronograma + tabla de roles (mínimo 3: desarrollador, evaluador, consumidor).

### Paso 4 — Conclusión estratégica [30 min]
Estructura obligatoria:
1. Recap del dolor cuantificado
2. La solución en una frase
3. 3 beneficios concretos con números
4. "¿Por qué ahora?" (urgencia)
5. **Llamado a la acción** — qué aprobamos/firmamos hoy

Evitar: cerrar con "gracias" a secas (feedback textual del profe: *"cierre repentino, no me lo esperaba"*).

### Paso 5 — Demo [2 h]
Opciones ordenadas por realismo:
- **A:** flujo conversacional real en Dialogflow CX (sandbox gratuito) — el mejor
- **B:** video grabado (OBS + navegador) mostrando el flujo end-to-end — plan B seguro
- **C:** click-through en Figma simulando conversación — plan C

**Salida:** URL del flujo o archivo .mp4 de 60–90 segundos.

### Paso 6 — Plan de contingencia [30 min]
Slide de una línea por escenario:
- ¿WhatsApp Business API down? → fallback a formulario web
- ¿Dialogflow no entiende? → escalamiento a humano (HITL)
- ¿GCP caído en región? → failover a otra región / modo degradado
- ¿Costo se dispara? → alertas en Cloud Billing + cap de gasto

### Paso 7 — KPIs duplicados [30 min]
Separar explícitamente en 2 tablas:
- **KPI del negocio:** ventas, ticket promedio, tasa de conversión, retención, NPS
- **KPI del modelo/solución:** latencia del bot, precisión del OCR, tasa de conciliación automática, adopción in-app, uptime

### Paso 8 — Liderazgo Digital [1 h]
Una sección por cada etapa del E2E respondiendo *"¿cómo aseguramos adopción?"*:
- Sesión de kickoff con el dueño (sponsor)
- Capacitación en modo "sin tecnicismos"
- Detractor interno: **el dueño mismo acostumbrado al Excel** → estrategia: piloto de 2 semanas con inventario en Cloud SQL paralelo al Excel, comparar tiempos
- Celebrar victorias tempranas públicamente

### Paso 9 — Gobernanza con Habeas Data [30 min]
Mencionar explícitamente:
- **Ley 1581 de 2012 (Habeas Data Colombia)** para datos de clientes
- Autorización de tratamiento de datos en chatbot
- Cifrado en reposo por defecto en Cloud SQL
- Borrado de imágenes de comprobantes a 30 días

### Paso 10 — "¿Por qué IA Gen y no algo simple?" [20 min]
Una slide comparando 3 opciones:
| Opción | Costo | Tiempo impl. | Escalabilidad | Defecto |
|---|---|---|---|---|
| Seguir en Excel | $0 | 0 | Ninguna | Status quo insostenible |
| CRM genérico (Shopify/Alegra) | ~$50/mes | 2 sem | Media | No integra IG/WA ni OCR |
| **Nuestra solución GCP** | ~$20/mes | 3 meses | Alta | Inversión inicial |

---

## 3. Vocabulario obligatorio (checklist del profe)

Si alguna de estas palabras NO aparece en la presentación, penaliza. Marcar ✅ al incluirlas:

- [ ] E2E Digital
- [ ] Liderazgo Digital / Líder digital
- [ ] Victorias tempranas
- [ ] MVP escalable y dinámico
- [ ] TCO (Total Cost of Ownership)
- [ ] ROI (fórmula aplicada explícitamente)
- [ ] CAPEX vs OPEX
- [ ] KPI del negocio + KPI del modelo (separados)
- [ ] Mockup / UX / UI
- [ ] Gobernanza de datos
- [ ] IA Responsable / Uso responsable
- [ ] HITL (Human in the Loop)
- [ ] RAG (Retrieval-Augmented Generation)
- [ ] Grounding / Fundamentación
- [ ] Matriz Creativa con Quick Wins
- [ ] Ideación → Realización → Utilización (ciclo de vida)
- [ ] Personas + Procesos + Tecnología
- [ ] Potenciar vs Automatizar (decir cuál de los dos hace Tolego)
- [ ] Storytelling / Narrativa de datos
- [ ] Adopción organizacional / Gestión del cambio
- [ ] Escalable, Flexible, Ágil, Segura (los 4 atributos de la nube)
- [ ] SaaS / PaaS / IaaS
- [ ] MLOps lifecycle
- [ ] Chain of Thought
- [ ] Alucinaciones (nombradas como reto de IA Gen)

---

## 4. Red flags — errores que el profe castigó en grupos previos

Tomados de feedback textual en Clase 1 (20-feb-2026). **Releer antes de ensayar.**

- ❌ **Cierre abrupto** sin conclusión estratégica
- ❌ **Diagrama E2E ilegible** (*"me tocó hacer mega zoom con los ojos"*)
- ❌ **Objetivos confundidos con KPIs**
- ❌ **Sin ROI ni TCO calculados**
- ❌ **No responder "¿por qué no seguir como estábamos?"**
- ❌ **No incluir proceso de feedback del usuario** dentro del E2E
- ❌ **Slides desconectadas del discurso** (*"buen podcast, mala película"*)
- ❌ **No contemplar plan de contingencia**
- ❌ **No identificar detractor interno** y cómo gestionar su resistencia
- ❌ **Confundir "calidad" con "precisión"** (calidad es más integral)
- ❌ **Tecnicismos sin traducción** al lenguaje del negocio
- ❌ **Pasarse del tiempo o terminar muy antes** (un grupo terminó 1 min antes, penalizado)

---

## 5. Armas secretas del contexto del profesor

Referencias que **le encantan** y que debemos citar (suman puntos visibles):

1. **Su caso personal:** *chatbot en WhatsApp con integraciones CRM/ERP/PIM + IA generativa*. **Esto es literalmente Tolego.** Citar en la intro: *"Profesor, en Clase 3 usted compartió este patrón arquitectónico — nuestra propuesta lo lleva al segmento de coleccionables colombianos"*.
2. **Caso Warner Bros + Vertex AI** (-50% costos, -80% tiempo) — usar como benchmark del ROI posible.
3. **Plantilla Schneider Electric (Clase 4)** — mirror estructural. Schneider llegó a ROI = 18.947%.
4. **Ejemplo Oxxo / Bogotá local** (Clase 1) — podemos usar paralelismo geográfico.

---

## 6. Estructura final propuesta (30 min, 18 slides)

| # | Slide | Min | Presenta |
|---|---|---|---|
| 1 | Portada + hook | 1 | Oscar |
| 2 | Consultores + expertise | 1 | Oscar |
| 3 | Tolego (cliente) | 2 | Brayan |
| 4-5 | Dolor cuantificado (datos) | 3 | Brayan |
| 6 | Matriz Creativa + Quick Wins | 2 | Sebastián |
| 7 | Arquitectura E2E (diagrama legible) | 3 | Sebastián |
| 8 | Consumo Digital / Modelo estrella | 2 | Oscar |
| 9 | ETL | 1 | Oscar |
| 10 | Gobernanza + IA Responsable + Habeas Data | 1 | Brayan |
| 11 | Mockup (Figma + Looker Studio) | 3 | Brayan |
| 12 | Demo en vivo | 2 | Sebastián |
| 13 | Mantención + Feedback loop | 1 | Sebastián |
| 14 | TCO + ROI con fórmula | 2 | Oscar |
| 15 | Cronograma por fases | 1 | Oscar |
| 16 | Adopción + Liderazgo Digital | 1 | Brayan |
| 17 | Riesgos vs Beneficios + Contingencia | 1 | Sebastián |
| 18 | Conclusión + Llamado a la acción | 2 | Oscar |

**Total: 29 min + 1 min de colchón**

---

## 7. Checklist del día de la presentación

- [ ] Subir PPT a Teams antes de las 4:00 PM
- [ ] Llegar a la sesión mandatoria
- [ ] Presentación descargada localmente (por si falla internet)
- [ ] Demo grabada en video como plan B (por si Dialogflow falla)
- [ ] Cronómetro visible para cumplir 30 min exactos
- [ ] Repartir quién habla en cada slide (sin pausas incómodas)
- [ ] Laptop con cargador + adaptador HDMI
- [ ] Un integrante preparado para las 5 min de preguntas con respuestas a:
  - "¿Cómo miden adopción?"
  - "¿Qué pasa si falla X?"
  - "¿Por qué esta tecnología y no otra?"
  - "¿Cuándo recuperan la inversión?"

---

## 8. Handoff — retomar desde otra máquina (snapshot 2026-04-15)

### Estado general
Todos los entregables de contenido están cerrados en la sección 1 de este archivo. Lo que queda es **producir la presentación visual (slides) a partir del contenido ya estructurado en Notion** y hacer ensayos de la defensa.

### Qué ya está hecho (cerrado, no hay que rehacer)
- **Notion "TOLEGO"** (ID `32b36d06-9793-812c-8afa-e655cb0165b7`) con todas las secciones del rubric completas: dolor cuantificado, solución E2E, gobernanza + Habeas Data, KPIs separados (negocio/modelo), ETL, mantención, contingencia, comparativa vs alternativas, liderazgo digital, cronograma, TCO+ROI con fórmula, conclusión con llamado a la acción.
- **Mockup Figma:** https://photo-lake-92987883.figma.site
- **MVP del bot demo:** carpeta `mvp_bot/` con código Python listo. Solo falta pegar tokens y correrlo (instrucciones en `mvp_bot/README.md`).
- **Transcripciones de clase:** `grabaciones/transcripciones/*.txt` — ya procesadas, sirven como contexto adicional si hace falta.

### Pasos para retomar en una máquina nueva
1. **Clonar:** `git clone https://github.com/oscar243/tolego.git && cd tolego`
2. **Abrir con Claude Code.** El archivo `CLAUDE.md` se carga automáticamente y da contexto base.
3. **Leer este `PLAN.md`** (especialmente la tabla de la sección 1 para ver estado).
4. **Verificar que el MCP de Notion esté conectado** — necesario para editar la página TOLEGO desde la nueva sesión.
5. **Correr el bot demo** siguiendo `mvp_bot/README.md` (crear bot en @BotFather, key en aistudio.google.com/apikey, pegar en `.env`, `python -m src.bot`).

### Qué hacer a continuación (siguiente sesión)
Propuesta en orden de impacto:
1. **Producir la PPT** — convertir las secciones de Notion en diapositivas siguiendo la estructura de la sección 2 de este archivo (18 slides / 30 min / 3 presentadores). Usar PowerPoint, Google Slides o Canva. Exportar el mockup de Figma como imágenes para incrustar.
2. **Probar y pulir el bot demo** — correrlo localmente, hacer 2-3 pruebas del guión, grabar un video de respaldo de 60-90s por si falla la demo en vivo.
3. **Guión de presentación por persona** — escribir qué dice cada integrante en cada slide, con tiempos.
4. **Ensayos cronometrados** — mínimo 2 ensayos completos para ajustar tiempos y transiciones.
5. **Cumplir el checklist del día** (sección 7 de este archivo).

### Lo que NO está en el repo y hay que regenerar si se necesita
- `grabaciones/*.mp4` — videos originales de 2,9 GB (no versionados). No son necesarios para lo que viene.
- `grabaciones/audio/*.mp3` — audios extraídos (~266 MB). Regenerables con `python extraer_audio.py` si se necesitan.
- `mvp_bot/.env` — nunca se versiona. Crearlo desde `.env.example` con tokens nuevos.
- `mvp_bot/tolego.db` — se regenera solo al primer arranque del bot.
- **Memoria de Claude Code** (carpeta `.claude/projects/.../memory/`) — es local de cada máquina y no transfiere por git. Todo el contexto crítico ya está consolidado en `CLAUDE.md` y en este `PLAN.md`.

### API keys necesarias (todas gratuitas)
- **Telegram Bot Token:** hablar con @BotFather en Telegram → `/newbot`
- **Gemini API Key:** https://aistudio.google.com/apikey → "Create API key"
- Pegar ambas en `mvp_bot/.env` (copiar desde `.env.example`)
