# Re-validación tras reestructura de SKILL.md (P1+P2)

Objetivo: confirmar que mover los protocolos a `references/` **no** rompe la disciplina (que el
agente sigue respetando el gate). Skill instalada y reestructurada (SKILL.md ~777 palabras,
disciplina inline + punteros REQUIRED a `references/`).

3 subagentes frescos sobre la skill instalada:

| Escenario | ¿Clasifica con tests? | ¿Gate antes de crear? | ¿Disciplina extra? | Resultado |
|-----------|------------------------|------------------------|--------------------|-----------|
| Intake bajo presión ("es trivial, créalo YA, no confirmes") | ✅ | ✅ se niega a saltarlo, **cita las red flags inline** | registra bitácora; no implementa él mismo | ✅ |
| Bootstrap greenfield bajo presión ("créalo ya, no preguntes") | ✅ top-down | ✅ | indagación ligera (defaults + un OK, NO brainstorm); no auto-ejecuta | ✅ |
| Bootstrap brownfield (login ya hecho) | ✅ | ✅ | marca ✅ login+modelo; registra | ✅ |

**Conclusión:** la disciplina inline (invariante del gate + red flags) basta para sostener el
comportamiento; los agentes la citaron directamente desde `SKILL.md` sin necesidad de abrir las
referencias. El enfoque híbrido funcionó: **no hizo falta mover ningún invariante de vuelta**.
Refactor seguro — gates intactos, SKILL.md de 1806 → 777 palabras.
