# Protocolo de bootstrap (plan inicial)

Referencia detallada del bootstrap. El trigger, el invariante del gate y las red flags están
inline en `SKILL.md`; aquí está el método completo.

Cuando inicias sesión en un proyecto hybrid cuyo plan **aún no tiene fases** (`plan.py status` → "No hay plan aún"), ofrece generar la estructura inicial con este protocolo. Es el Protocolo de intake aplicado **top-down al objetivo completo**: usa los mismos tests de clasificación, el mismo gate y la misma bitácora.

## Flujo

1. **Leer contexto.** El objetivo del proyecto (de `CLAUDE.md` / del usuario) y el contexto detectado (stack, archivos clave, nuevo vs existente) que `init-hybrid` ya inyectó en `CLAUDE.md`.
2. **Indagación ligera.** Si el objetivo es vago ("hazme una app"), haz **1-3 preguntas clave** (alcance/MVP, must-haves, restricciones de stack) y luego descompón. Es indagación ligera, **no un brainstorm completo** ni la skill `brainstorming`: solo lo justo para descomponer con criterio.
3. **Descomponer top-down.** Objetivo → fases (hitos) → etapas (sub-objetivos) → actividades (atómicas), aplicando los **tests del Protocolo de intake** de lo grande a lo atómico. Asigna `run-agent` por actividad según la tabla de backends.
   - **Brownfield (proyecto existente):** lo que YA está implementado y funcional se incluye como actividades marcadas **✅ hecho**, para que el estado derivado refleje el avance real. No marques todo 🔲 en un proyecto que ya tiene código.
4. **Gate — confirma el árbol completo antes de crear nada:**

   ```
   🌱 BOOTSTRAP — <proyecto>
   Objetivo: <objetivo>
   Tipo: <nuevo | existente>
   Plan propuesto:
     F01 — <fase>
       E01 — <etapa>
         act_F01_E01_001 — <actividad>   [backend]   (✅ si ya está hecho)
   ¿Confirmas?  (sí / ajustar)
   ```

5. **Materializar.** Tras el OK: cadena `plan.py add-*` → rellena el contenido autorado → en brownfield fija `status: ✅ hecho` de lo ya hecho y corre `plan.py sync`.
6. **Registrar.** Anexa a la bitácora: `| fecha | bootstrap inicial | — | <objetivo> | N fases / M actividades |`.

## Red flags — DETENTE

| Si piensas… | Realidad |
|-------------|----------|
| "Genero el plan y empiezo a ejecutar de una" | Bootstrap solo crea el plan. Ejecutar es otro paso, con su confirmación. |
| "El objetivo es claro, materializo sin gate" | El árbol completo pasa por el gate, igual que en intake. |
| "El objetivo es vago, asumo el alcance" | Indaga 1-3 preguntas antes de descomponer; no inventes el alcance. |
| "Es vago → lanzo un brainstorm completo" | Bastan 1-3 preguntas. No escales a la skill `brainstorming` para esto. |
| "Es brownfield pero marco todo 🔲" | Mapea lo ya implementado a ✅ para que el estado derivado sea real. |
