# Spec-driven Development con SpecKit: la IA al servicio del desarrollador

La Spec-driven Development (Desarrollo Guiado por Especificaciones) comienza por una especificación detallada y ejecutable que actúa como fuente de verdad para el equipo y para las herramientas de IA. En lugar de prompts vagos, la IA recibe una guía estructurada que elimina ambigüedades y conduce a implementaciones más precisas, seguras y fiables.

## ¿Qué es SpecKit?
SpecKit es un kit de herramientas de código abierto de GitHub para SDD con agentes de IA. Incluye un CLI, plantillas y “steering prompts” compatibles con GitHub Copilot, Claude Code y Gemini CLI. Su objetivo es transformar la comunicación ad‑hoc hacia un flujo estructurado y verificable, centrado en la intención como fuente de verdad. A diferencia de marcos previos (p. ej., Kira de Amazon), SpecKit aporta plantillas y comandos de ciclo de vida integrados (/specify, /plan, /tasks, implementación) y “guardrails” como la Constitución.

## Fases clave (con puertas de validación)
1. Specify: qué y por qué; historias de usuario, escenarios y áreas que requieren aclaración.
2. Plan: stack técnico, arquitectura y restricciones; modelo de datos, investigación y contratos.
3. Tasks: desglose en tareas pequeñas, ordenadas y paralelizables; TDD primero.
4. Implement: ejecución incremental y control granular; cambios revisables.

## Comunicación desarrollador‑IA
Deja de ser “motor de búsqueda” y pasa a “programador par”: la especificación es el artefacto autoritativo que la IA consulta continuamente para mantenerse alineada con la intención del desarrollador.

## Inicio de proyecto con SpecKit
- `specify init <proyecto> --ai <copilot|claude|gemini>` para bootstrap.
- Abres el trabajo en el editor; usas /specify → /plan → /tasks para generar los artefactos.
- Lanzar UI local del analizador: `make ui` o `./scripts/ui`

## Salidas detalladas por fase
- Specify: especificación con historia principal, criterios de aceptación y casos extremos.
- Plan: modelo de datos, investigación y contratos; registra decisiones y alternativas.
- Tasks: lista numerada y ejecutable; facilita el seguimiento y el control del flujo.

## Elección del modelo de IA
SpecKit guía el proceso, pero la calidad del modelo sigue importando: distintos modelos pueden producir distintos niveles de profundidad y refinamiento.
