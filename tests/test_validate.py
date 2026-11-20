"""tests/test_validate.py — validate.py 分镜校验器正反向自测（零依赖，unittest）。

本仓 validate.py 为 check(data) 变体接口（按 shot 产出 issues），自测走 CLI 退出码契约。

运行：
  python -m unittest discover -s tests -v
  python tests/test_validate.py
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts" / "validate.py"
GOOD = ROOT / "tests" / "sample_good.json"
BAD = ROOT / "tests" / "sample_bad.json"


class TestValidateCli(unittest.TestCase):
    def test_good_sample_passes(self):
        r = subprocess.run([sys.executable, str(VALIDATE), str(GOOD)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_bad_sample_fails_with_issues(self):
        r = subprocess.run([sys.executable, str(VALIDATE), str(BAD)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAIL", r.stdout)
        self.assertIn("处缺陷", r.stdout)

    def test_cli_usage_error(self):
        r = subprocess.run([sys.executable, str(VALIDATE)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("用法", r.stderr)


if __name__ == "__main__":
    unittest.main()