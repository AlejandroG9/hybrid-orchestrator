import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

# Permitir importar el script (no es un paquete instalable)
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_subagent as r  # noqa: E402


class TestResolveBackend(unittest.TestCase):
    def setUp(self):
        # Orden por defecto, claude al final
        self.order = ["gemini", "codex", "cursor-agent", "claude"]

    def test_declared_available_returns_itself(self):
        chosen, fell_back, _ = r.resolve_backend(
            "gemini", available={"gemini", "claude"}, order=self.order
        )
        self.assertEqual(chosen, "gemini")
        self.assertFalse(fell_back)

    def test_declared_missing_falls_to_next_installed(self):
        chosen, fell_back, motivo = r.resolve_backend(
            "gemini", available={"codex", "claude"}, order=self.order
        )
        self.assertEqual(chosen, "codex")
        self.assertTrue(fell_back)
        self.assertIn("gemini", motivo)
        self.assertIn("codex", motivo)

    def test_falls_through_to_claude_when_only_claude(self):
        chosen, fell_back, _ = r.resolve_backend(
            "gemini", available={"claude"}, order=self.order
        )
        self.assertEqual(chosen, "claude")
        self.assertTrue(fell_back)

    def test_raises_when_nothing_available(self):
        with self.assertRaises(RuntimeError):
            r.resolve_backend("gemini", available=set(), order=self.order)


class TestEffectiveFallbackOrder(unittest.TestCase):
    def test_default_when_no_env(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["gemini", "codex", "cursor-agent", "claude"])

    def test_env_override_respected_claude_last(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "codex,gemini,claude"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["codex", "gemini", "claude"])
        self.assertEqual(order[-1], "claude")

    def test_env_override_without_claude_appends_it(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "codex,gemini"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order[-1], "claude")
        self.assertIn("codex", order)

    def test_env_override_ignores_unknown_names(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "foo,codex,bar"}, clear=True):
            order = r.effective_fallback_order()
        self.assertNotIn("foo", order)
        self.assertNotIn("bar", order)
        self.assertIn("codex", order)
        self.assertEqual(order[-1], "claude")

    def test_env_override_all_invalid_falls_to_default(self):
        with mock.patch.dict("os.environ", {"HYBRID_FALLBACK_ORDER": "foo,bar"}, clear=True):
            order = r.effective_fallback_order()
        self.assertEqual(order, ["gemini", "codex", "cursor-agent", "claude"])


class TestAvailability(unittest.TestCase):
    def test_is_available_true_when_which_finds_it(self):
        with mock.patch("run_subagent.shutil.which", return_value="/usr/bin/gemini"):
            self.assertTrue(r.is_available("gemini"))

    def test_is_available_false_when_which_returns_none(self):
        with mock.patch("run_subagent.shutil.which", return_value=None):
            self.assertFalse(r.is_available("gemini"))

    def test_available_backends_collects_only_installed(self):
        def fake_which(exe):
            return "/path" if exe in ("gemini", "claude") else None
        with mock.patch("run_subagent.shutil.which", side_effect=fake_which):
            avail = r.available_backends()
        self.assertEqual(avail, {"gemini", "claude"})


class TestCheck(unittest.TestCase):
    def test_print_check_lists_installed_and_missing(self):
        def fake_which(exe):
            return "/usr/bin/" + exe if exe in ("gemini", "claude") else None
        buf = io.StringIO()
        with mock.patch("run_subagent.shutil.which", side_effect=fake_which):
            with mock.patch.dict("os.environ", {}, clear=True):
                with redirect_stdout(buf):
                    r.print_check()
        out = buf.getvalue()
        self.assertIn("gemini", out)
        self.assertIn("✅", out)
        self.assertIn("❌", out)
        self.assertIn("Cadena efectiva", out)


if __name__ == "__main__":
    unittest.main()
