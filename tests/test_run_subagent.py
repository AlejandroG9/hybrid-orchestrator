import sys
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
