# Integración BMAD con SpecKit (SDD)

BMAD-METHOD (MIT) provee un marco de agentes, plantillas y checklists para planificación y ejecución con IA. Aunque nuestro proyecto (Music Analyzer Pro) usa SpecKit y POML para un flujo SDD, BMAD puede aportar valor en las fases de Specify/Plan/Tasks como guías y listas de verificación.

## Qué aporta BMAD
- Agentes y equipos: roles (Analyst, PM, Architect, SM, Dev, QA) y orquestador.
- Plantillas de documentación: PRD, arquitectura (fullstack/front-end), investigación de mercado, competitor analysis, story templates.
- Workflows YAML (greenfield/brownfield) y checklists (PM, PO, Architect, DoD, QA gate).
- Datos de apoyo: matrices de niveles/prioridades de test.

## Dónde encaja en SpecKit
- Specify (spec.md): Usar plantillas BMAD de PRD y story para enriquecer historias/escenarios.
- Plan (plan.md): Apoyarse en plantillas de arquitectura/checklists de architect y QA gate; incorporar matrices de test niveles/prioridades al plan de pruebas.
- Tasks (tasks.md): Convertir checklists y matrices en tareas explícitas (p. ej., QA gate, trazabilidad, test-first por capas).

## Cómo usarlo aquí
- Referencia directa a plantillas de BMAD clonadas en `BMAD-METHOD/bmad-core/templates/*.yaml` y checklists en `bmad-core/checklists/*`.
- POML: incluir rol/estilo de agentes (Analyst/Architect/QA) en los prompts `templates/poml/*.poml` si se desea mayor formalidad en la salida.
- No hay código de audio en BMAD; su aporte es metodológico (proceso, artefactos, QA/checklists).

## Recomendaciones prácticas
- Añadir secciones de QA Gate del template BMAD en `plan.md` (Constitution Check + QA Gate combinados).
- Incluir matriz de niveles/prioridades de tests en `research.md` o como anexo del plan.
- Usar “story-tmpl” para desglosar features grandes en historias refinadas antes de generar `tasks.md`.

> Nota: Mantener a SpecKit como fuente de verdad del flujo (Specify → Plan → Tasks) y usar BMAD como referencia de calidad y completitud en artefactos.
