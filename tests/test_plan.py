import sys
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


if __name__ == "__main__":
    unittest.main()
