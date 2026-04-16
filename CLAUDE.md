# Contexto del proyecto TOLEGO

Trabajo final del curso **Generative AI Leader: Liderazgo Digital y Estrategia Digital con IA Generativa** — Escuela Colombiana de Ingeniería Julio Garavito.

> **Si acabas de clonar este repo, lee primero `PLAN.md`.** Tiene el estado completo de los entregables, qué está hecho, qué falta y cómo retomar.

## Repositorio

- GitHub: https://github.com/oscar243/tolego.git

## Lo esencial en 10 líneas

- **Cliente:** Tolego — emprendimiento colombiano de minifiguras coleccionables tipo Lego. Vende por Instagram @tole.go y WhatsApp 312 347 3871.
- **Equipo consultor:** Oscar Andrés Virguez Merchán, Brayan Steven González Toledo, Sebastián Moreno Flórez.
- **Propuesta:** plataforma E2E sobre Google Cloud Platform (Cloud SQL, Firestore, Dialogflow CX, Document AI, Vertex AI/Gemini, BigQuery, Looker Studio) para automatizar pedidos, conciliar pagos y generar analítica.
- **Entrega:** presentación de 30 min + 5 min de preguntas ante 3 jurados, se sube a Teams.
- **Calificación:** 30% dolor con datos · 50% solución E2E · 20% presentación + mockup.
- **Contenido base:** página de Notion titulada "TOLEGO" — ID `32b36d06-9793-812c-8afa-e655cb0165b7`. Accesible vía el MCP de Notion conectado en Claude Code. Ya está llena con todas las secciones requeridas por el rubric.
- **Mockup UX:** https://photo-lake-92987883.figma.site (Figma site)
- **Demo MVP:** proyecto en `mvp_bot/` — bot de Telegram con Gemini + SQLite local. Costo $0 USD. Instrucciones en `mvp_bot/README.md`.
- **Números clave de la propuesta:** costo del dolor ~$7,15M COP/año · TCO ~$960k COP/año · ROI 645% · payback ~1,6 meses · 15 semanas de implementación.

## Reglas de tono para entregables

**No adular al profesor ni hacer referencias explícitas a su clase** en slides, documento de Notion o guión de presentación. Concretamente:
- No citas textuales del profesor (ej. "IA usan muchos, saberla usar pocos")
- No referencias tipo "Profesor, como usted mencionó en Clase 3..."
- No mencionar casos de éxito que él contó en clase (chatbot WhatsApp personal, Warner Bros)

Sí se puede usar el vocabulario técnico del curso (E2E, Matriz Creativa, MVP escalable, TCO/ROI, etc.) porque es terminología estándar, no adulación. La presentación debe sostenerse por sus datos y razonamiento, no por apelar a la autoridad del profesor.

## Vocabulario que sí debe aparecer en los entregables

E2E Digital · Liderazgo Digital · Victorias tempranas · MVP escalable · TCO · ROI (con fórmula) · CAPEX vs OPEX · KPI del negocio (separado del KPI del modelo) · Mockup/UX/UI · Gobernanza · IA Responsable · HITL · RAG · Grounding · Matriz Creativa con Quick Wins · Ideación → Realización → Utilización · Personas + Procesos + Tecnología · Potenciar vs Automatizar · Storytelling · Adopción organizacional / Gestión del cambio · Escalable, Flexible, Ágil, Segura · SaaS/PaaS/IaaS · MLOps lifecycle · Chain of Thought · Alucinaciones.

## Red flags a evitar (feedback de grupos previos)

- Cierre abrupto sin conclusión estratégica
- Diagrama E2E ilegible (letras pequeñas, poca claridad)
- Confundir objetivos con KPIs (hay que presentar AMBOS separados)
- No calcular ROI ni TCO con fórmula explícita
- No responder "¿por qué no seguir como estábamos?"
- No incluir proceso de feedback del usuario dentro del E2E
- Slides desconectadas del discurso
- No contemplar plan de contingencia
- No identificar detractor interno
- Tecnicismos sin traducción al lenguaje del negocio
- Pasarse del tiempo o terminar muy antes

## Archivos clave en el repo

- `PLAN.md` — estado maestro de entregables y handoff
- `CLAUDE.md` — este archivo, contexto que Claude Code auto-carga
- `Estudiantes Trabajo final Cloud Digital Leader.pdf` — rubric oficial del curso
- `Catalogo_ToleGo_2025.pdf` — catálogo real del cliente
- `presentaciones_clase/Clase *.pdf` — 8 PDFs de diapositivas del curso (contexto temático)
- `grabaciones/transcripciones/*.txt` — 6 transcripciones de clase (feedback textual del profesor a grupos previos)
- `mvp_bot/` — proyecto Python del bot demo
- `extraer_audio.py`, `transcribir.py` — scripts usados para transcribir las clases con AssemblyAI (ya ejecutados)

## Archivos que NO están en el repo (por tamaño)

- `grabaciones/*.mp4` — 2,9 GB de video de las clases (no versionar)
- `grabaciones/audio/*.mp3` — 266 MB de audio extraído (se puede regenerar con `extraer_audio.py`)
- `mvp_bot/.env` — contiene API keys, nunca versionar
- `mvp_bot/tolego.db` — SQLite generado en runtime

## Cómo retomar desde otra máquina

1. `git clone https://github.com/oscar243/tolego.git && cd tolego`
2. Abrir con Claude Code. Este archivo se carga automáticamente.
3. Leer `PLAN.md` para ver qué está hecho y qué falta.
4. Para correr el bot demo: seguir `mvp_bot/README.md` (necesitas tokens nuevos de Telegram y Gemini, son gratis).
5. Para seguir actualizando el documento del proyecto: el MCP de Notion debe estar conectado en la sesión nueva; el ID de la página es `32b36d06-9793-812c-8afa-e655cb0165b7`.
