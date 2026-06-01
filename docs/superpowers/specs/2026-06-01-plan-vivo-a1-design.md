# Feature A1 — Mecánica del plan vivo

**Fecha:** 2026-06-01
**Estado:** Diseño aprobado, pendiente de implementación
**Skill:** hybrid-orchestrator
**Contexto:** Primera de tres piezas de Feature A ("plan vivo"). A1 = mecánica determinista.
A2 (intake + clasificación + gobierno) y A3 (bootstrap en init) se apoyan sobre A1 y se
diseñarán después, cada una con su propio spec.

---

## Problema

Hoy el estado del proyecto vive en `plan/PLAN.md`, mantenido a mano por el orquestador, y
las fases/etapas son solo directorios sin resumen propio. Para revisar el proyecto hay que
abrir todas las actividades, y PLAN.md se desincroniza con facilidad. No existe forma
determinista de crear niveles con IDs correctos ni de regenerar el estado.

## Objetivo

Una mecánica en código (testeable) que:
1. Cree fases / etapas / actividades con IDs y scaffolding correctos desde plantilla.
2. Mantenga el estado **siempre sincronizado**: `PLAN.md` y los resúmenes por nivel se
   **generan** a partir de la fuente de verdad (status de las actividades hoja + contenido
   autorado).
3. Ofrezca un dashboard de estado en terminal.

Fuera de alcance (YAGNI, para después): renumeración/reordenamiento, borrado de niveles,
métricas de tiempo, e **intake automático** (eso es A2).

---

## Modelo de datos y layout

```
proyecto/
└── plan/
    ├── PLAN.md                      ← 100% vista, generada (con encabezado autorado)
    ├── fase_01/
    │   ├── _fase.md                 ← resumen de la fase
    │   ├── etapa_01/
    │   │   ├── _etapa.md            ← resumen de la etapa
    │   │   ├── act_F01_E01_001.md   ← detalle (formato actual, sin cambios)
    │   │   └── act_F01_E01_002.md
    │   └── etapa_02/
    │       └── _etapa.md
    └── fase_02/
        └── _fase.md
```

**Convención de nombres:** `_fase.md` y `_etapa.md`. El guion bajo los ordena primero
dentro de su carpeta (encima de las actividades). Actividades: `act_FXX_EXX_NNN.md` (sin
cambios). Padding: fase/etapa 2 dígitos, actividad 3 dígitos.

**Dos zonas en cada archivo de nivel (`_fase.md`, `_etapa.md`, `PLAN.md`):**
- **Autorada:** la escribe el orquestador y se **preserva** siempre (objetivo, notas,
  criterios de alto nivel; en PLAN.md: nombre y objetivo del proyecto).
- **Generada:** la reescribe `plan.py sync`, **nunca se edita a mano**, delimitada por
  marcadores HTML:

  ```markdown
  <!-- BEGIN:auto — generado por plan.py, no editar -->
  **Estado:** 🔄 en curso (2/5 ✅)

  | Actividad | Backend | Estado |
  | --- | --- | --- |
  | act_F01_E01_001 | gemini | ✅ |
  <!-- END:auto -->
  ```

  `replace_auto_block` reemplaza lo que haya entre marcadores; si no existen, agrega el
  bloque (al final de la zona autorada).

**Frontmatter por nivel:**
- Fase (`_fase.md`): `id: F01`, `title:`, `status:` *(derivado, lo escribe sync)*, `created:`
- Etapa (`_etapa.md`): `id: F01_E01`, `title:`, `status:` *(derivado)*, `created:`
- Actividad: el actual (`run-agent`, `status`, `created`, `phase`, `stage`) — sin cambios.

**Fuente de verdad:** `status` de las actividades (hoja) + todo el contenido autorado. El
resto (status de fase/etapa, índices, PLAN.md) se deriva/regenera.

---

## Reglas de derivación de estado (rollup)

Estados de actividad (hoja): `🔲 pendiente`, `🔄 en curso`, `✅ hecho`, `⛔ bloqueado`.

`rollup_status(estados_hijos)` — misma función para etapa (sobre actividades) y fase (sobre
etapas), evaluada en este orden de precedencia:

| Condición sobre los hijos | Resultado |
|---|---|
| Sin hijos (vacío) | 🔲 pendiente |
| Algún hijo ⛔ | ⛔ bloqueado |
| Todos ✅ | ✅ hecho |
| Algún 🔄, **o** mezcla de ✅ y 🔲 | 🔄 en curso |
| Todos 🔲 | 🔲 pendiente |

`⛔` se propaga hacia arriba (visible en PLAN.md). Las zonas generadas muestran conteo de
contexto: `🔄 en curso (2/5 ✅)`.

> Nota de implementación: la precedencia importa. Evaluar primero ⛔, luego "todos ✅",
> luego la condición de 🔄, y por último "todos 🔲".

---

## Interfaz: `scripts/plan.py`

```bash
python3 plan.py add-phase    --title "Autenticación"
python3 plan.py add-stage    --phase 1 --title "Login con email"
python3 plan.py add-activity --phase 1 --stage 1 --title "Endpoint /login" --run-agent gemini
python3 plan.py sync     # regenera estados, índices y PLAN.md
python3 plan.py status   # dashboard en terminal (solo lectura, no escribe)
```

Comportamiento:
- `add-phase` → crea `plan/fase_NN/_fase.md` con el siguiente `NN`, desde `templates/fase.md`,
  frontmatter (`id`, `title`, `created`) lleno. Imprime la ruta. **Auto-sync al final.**
- `add-stage --phase N` → crea `plan/fase_0N/etapa_MM/_etapa.md` con el siguiente `MM`
  dentro de esa fase. **Auto-sync.**
- `add-activity --phase N --stage M` → crea `act_F0N_E0M_KKK.md` con el siguiente `KKK`,
  desde `templates/activity.md`, frontmatter (`run-agent` [default `gemini`], `status: 🔲`,
  `phase`, `stage`, `created`) lleno. **Auto-sync.**
- `sync` → recorre `plan/`, deriva estados bottom-up, reescribe zonas `BEGIN:auto` de cada
  `_fase.md`/`_etapa.md` y regenera `PLAN.md`. Idempotente.
- `status` → misma derivación que `sync` pero sin escribir; imprime el árbol con estados.

**IDs:** siempre se agrega el siguiente número en ese nivel (`next_number = max(existentes)+1`,
respetando huecos como append). Reordenar/insertar en medio con renumeración: fuera de A1.

**Errores:**
- `add-stage`/`add-activity` con una fase/etapa padre inexistente → error claro, salida 1.
- `--phase`/`--stage` faltantes donde se requieren → error de argumentos.
- `sync`/`status` sin `plan/` → mensaje "no hay plan aún", salida 0.

Flujo típico del orquestador: `add-activity` (esqueleto) → rellenar contenido autorado →
al cambiar un `status` de actividad, correr `sync` para propagar.

---

## DRY / dependencias

- `plan.py` importa `parse_frontmatter` de `run_subagent` (su `main()` está protegido por
  `if __name__ == "__main__"`, importar es seguro) en vez de duplicar el parser.
- Sin dependencias externas: stdlib (`argparse`, `pathlib`, `re`, `datetime`).

---

## Pruebas (TDD, `unittest` stdlib)

Funciones puras (sin E/S) testeadas directamente:
- `rollup_status(estados)` — todos los casos de la tabla: vacío→🔲, algún ⛔→⛔, todos ✅→✅,
  algún 🔄→🔄, mezcla ✅+🔲→🔄, todos 🔲→🔲.
- `next_number(existentes)` — lista vacía→1, consecutivos→max+1, con huecos→max+1, padding.
- `set_frontmatter_field(texto, clave, valor)` — actualiza campo existente; round-trip.
- `replace_auto_block(texto, bloque)` — reemplaza entre marcadores; agrega si faltan;
  preserva la zona autorada.
- `render_plan(arbol)` / `render_level_block(nodo)` — render determinista desde un árbol
  en memoria (sin tocar disco).

La capa de E/S (recorrer `plan/`, leer/escribir) es fina sobre esas funciones y se valida
con un smoke test de integración sobre un `plan/` temporal (`tempfile`): crear fase→etapa→
actividad, marcar una actividad ✅, `sync`, y comprobar que el `_etapa.md`, `_fase.md` y
`PLAN.md` reflejan el rollup esperado e idempotencia (un segundo `sync` no cambia nada).

---

## Archivos afectados

- **Nuevo** `scripts/plan.py` — subcomandos + funciones puras.
- **Nuevo** `templates/fase.md`, `templates/etapa.md` — moldes de nivel.
- **Nuevo** `tests/test_plan.py` — unitarios + smoke de integración.
- `templates/PLAN.md` — pasa a encabezado autorado + cuerpo generado entre marcadores.
- `install.sh` — añadir `scripts/plan.py` a la instalación del skill (hoy copia scripts
  uno por uno).
- `SKILL.md` y `templates/CLAUDE.md` — documentar el flujo con `plan.py`.

---

## Entregable de A1

Crear niveles con IDs correctos desde plantilla + plan siempre sincronizado (estados e
índices derivados) + dashboard `status`. Base sobre la que A2 (intake/clasificación) y A3
(bootstrap) se montarán después.
