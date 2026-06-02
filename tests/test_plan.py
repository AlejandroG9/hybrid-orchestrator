import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import plan as p  # noqa: E402


class TestRollupStatus(unittest.TestCase):
    def test_empty_is_pending(self):
        self.assertEqual(p.rollup_status([]), p.STATUS["pendiente"])

    def test_any_blocked_wins(self):
        self.assertEqual(
            p.rollup_status(["✅ hecho", "⛔ bloqueado", "🔄 en curso"]),
            p.STATUS["bloqueado"],
        )

    def test_all_done(self):
        self.assertEqual(p.rollup_status(["✅ hecho", "✅ hecho"]), p.STATUS["hecho"])

    def test_any_in_progress(self):
        self.assertEqual(p.rollup_status(["🔲 pendiente", "🔄 en curso"]), p.STATUS["en curso"])

    def test_mixed_done_and_pending_is_in_progress(self):
        self.assertEqual(p.rollup_status(["✅ hecho", "🔲 pendiente"]), p.STATUS["en curso"])

    def test_all_pending(self):
        self.assertEqual(p.rollup_status(["🔲 pendiente", "🔲 pendiente"]), p.STATUS["pendiente"])


class TestNextNumber(unittest.TestCase):
    def test_empty_starts_at_one(self):
        self.assertEqual(p.next_number([]), 1)

    def test_consecutive(self):
        self.assertEqual(p.next_number([1, 2, 3]), 4)

    def test_with_gaps_appends_after_max(self):
        self.assertEqual(p.next_number([1, 3]), 4)


class TestSetFrontmatterField(unittest.TestCase):
    def test_replaces_existing_key(self):
        text = "---\nid: F01\nstatus: 🔲 pendiente\n---\n\nObjetivo\n"
        out = p.set_frontmatter_field(text, "status", "✅ hecho")
        self.assertIn("status: ✅ hecho", out)
        self.assertNotIn("🔲 pendiente", out)
        self.assertIn("Objetivo", out)

    def test_inserts_missing_key(self):
        text = "---\nid: F01\n---\n\nObjetivo\n"
        out = p.set_frontmatter_field(text, "status", "🔄 en curso")
        self.assertIn("status: 🔄 en curso", out)
        self.assertIn("id: F01", out)


class TestReplaceAutoBlock(unittest.TestCase):
    def test_replaces_between_markers(self):
        text = (
            "# Fase\n\nObjetivo autorado\n\n"
            f"{p.BEGIN_AUTO}\nviejo\n{p.END_AUTO}\n"
        )
        out = p.replace_auto_block(text, "**Estado:** ✅ hecho")
        self.assertIn("**Estado:** ✅ hecho", out)
        self.assertNotIn("viejo", out)
        self.assertIn("Objetivo autorado", out)

    def test_appends_when_no_markers(self):
        text = "# Fase\n\nObjetivo autorado\n"
        out = p.replace_auto_block(text, "**Estado:** 🔲 pendiente")
        self.assertIn(p.BEGIN_AUTO, out)
        self.assertIn(p.END_AUTO, out)
        self.assertIn("**Estado:** 🔲 pendiente", out)
        self.assertIn("Objetivo autorado", out)

    def test_idempotent(self):
        text = "# Fase\n\nObjetivo\n"
        once = p.replace_auto_block(text, "X")
        twice = p.replace_auto_block(once, "X")
        self.assertEqual(once, twice)


class TestRender(unittest.TestCase):
    def _stage(self):
        return {
            "id": "F01_E01", "num": 1, "title": "Login",
            "status": p.STATUS["en curso"],
            "activities": [
                {"id": "F01_E01_001", "backend": "gemini", "status": p.STATUS["hecho"]},
                {"id": "F01_E01_002", "backend": "codex", "status": p.STATUS["pendiente"]},
            ],
        }

    def test_stage_block_has_status_count_and_rows(self):
        out = p.render_level_block(self._stage(), kind="stage")
        self.assertIn("Estado", out)
        self.assertIn("1/2", out)
        self.assertIn("F01_E01_001", out)
        self.assertIn("gemini", out)

    def test_phase_block_lists_stages(self):
        phase = {
            "id": "F01", "num": 1, "title": "Auth",
            "status": p.STATUS["en curso"],
            "stages": [self._stage()],
        }
        out = p.render_level_block(phase, kind="phase")
        self.assertIn("E01", out)
        self.assertIn("Login", out)

    def test_render_plan_lists_phases(self):
        tree = {
            "title": "Mi Proyecto",
            "phases": [{"id": "F01", "num": 1, "title": "Auth",
                        "status": p.STATUS["en curso"], "stages": []}],
        }
        out = p.render_plan(tree)
        self.assertIn("F01", out)
        self.assertIn("Auth", out)


class TestSyncIntegration(unittest.TestCase):
    def _write(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content), encoding="utf-8")

    def _build_plan(self, root: Path):
        plan = root / "plan"
        self._write(plan / "fase_01" / "_fase.md",
                    "---\nid: F01\ntitle: Auth\nstatus: 🔲 pendiente\n---\n\nObjetivo de la fase\n")
        self._write(plan / "fase_01" / "etapa_01" / "_etapa.md",
                    "---\nid: F01_E01\ntitle: Login\nstatus: 🔲 pendiente\n---\n\nObjetivo de la etapa\n")
        self._write(plan / "fase_01" / "etapa_01" / "act_F01_E01_001.md",
                    "---\nrun-agent: gemini\nstatus: ✅ hecho\nphase: F01\nstage: E01\n---\n\n# Actividad\n")
        self._write(plan / "fase_01" / "etapa_01" / "act_F01_E01_002.md",
                    "---\nrun-agent: codex\nstatus: 🔲 pendiente\nphase: F01\nstage: E01\n---\n\n# Actividad\n")
        return plan

    def test_sync_derives_status_and_regenerates(self):
        with tempfile.TemporaryDirectory() as d:
            plan = self._build_plan(Path(d))
            p.sync(plan)
            etapa = (plan / "fase_01" / "etapa_01" / "_etapa.md").read_text(encoding="utf-8")
            fase = (plan / "fase_01" / "_fase.md").read_text(encoding="utf-8")
            planmd = (plan / "PLAN.md").read_text(encoding="utf-8")
            self.assertIn("🔄 en curso", etapa)
            self.assertIn("status: 🔄 en curso", etapa)
            self.assertIn("🔄 en curso", fase)
            self.assertIn("Objetivo de la etapa", etapa)
            self.assertIn("F01", planmd)
            self.assertIn("Auth", planmd)

    def test_sync_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            plan = self._build_plan(Path(d))
            p.sync(plan)
            first = (plan / "fase_01" / "_fase.md").read_text(encoding="utf-8")
            p.sync(plan)
            second = (plan / "fase_01" / "_fase.md").read_text(encoding="utf-8")
            self.assertEqual(first, second)


class TestAddCommands(unittest.TestCase):
    def _templates(self, root: Path) -> Path:
        tpl = root / "templates"
        tpl.mkdir()
        (tpl / "fase.md").write_text(
            "---\nid: \ntitle: \nstatus: 🔲 pendiente\ncreated: \n---\n\n## Objetivo\n", encoding="utf-8")
        (tpl / "etapa.md").write_text(
            "---\nid: \ntitle: \nstatus: 🔲 pendiente\ncreated: \n---\n\n## Objetivo\n", encoding="utf-8")
        (tpl / "activity.md").write_text(
            "---\nrun-agent: \nstatus: 🔲 pendiente\nphase: \nstage: \ncreated: \n---\n\n# Actividad\n", encoding="utf-8")
        return tpl

    def test_add_phase_then_stage_then_activity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan = root / "plan"
            tpl = self._templates(root)

            f = p.add_phase(plan, tpl, "Auth")
            self.assertEqual(f, plan / "fase_01" / "_fase.md")

            e = p.add_stage(plan, tpl, phase=1, title="Login")
            self.assertEqual(e, plan / "fase_01" / "etapa_01" / "_etapa.md")

            a = p.add_activity(plan, tpl, phase=1, stage=1, title="Endpoint", run_agent="codex")
            self.assertEqual(a, plan / "fase_01" / "etapa_01" / "act_F01_E01_001.md")
            self.assertIn("run-agent: codex", a.read_text(encoding="utf-8"))

    def test_add_stage_missing_phase_errors(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            plan = root / "plan"
            self._templates(root)
            with self.assertRaises(FileNotFoundError):
                p.add_stage(plan, root / "templates", phase=9, title="X")


if __name__ == "__main__":
    unittest.main()
