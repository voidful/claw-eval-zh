"""All generated graders import; smoke-grade sanity/weather/csv_stock_trend.

Also verifies the bilingual normalization wrapper: a Traditional-Chinese report
scores the same as the equivalent English report (Chinese is scorable).
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

CLAW = ROOT / "tasks_claw_eval_zh"


def load(cid: str):
    p = CLAW / cid / "grader.py"
    spec = importlib.util.spec_from_file_location(f"grader_{cid}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def assistant(text: str) -> dict:
    return {"type": "message", "message": {"role": "assistant",
            "content": [{"type": "text", "text": text}]}}


class AllImportTests(unittest.TestCase):
    def test_all_graders_import(self) -> None:
        n = 0
        for d in sorted(p for p in CLAW.iterdir() if p.is_dir()):
            m = load(d.name)
            self.assertTrue(callable(getattr(m, "grade", None)), d.name)
            n += 1
        self.assertGreaterEqual(n, 143)


class SanityTests(unittest.TestCase):
    def test_sanity(self) -> None:
        g = load("P001zh_sanity")
        self.assertEqual(g.grade([assistant("你好")], "/none")["agent_responded"], 1.0)
        self.assertEqual(g.grade([], "/none")["agent_responded"], 0.0)


class WeatherTests(unittest.TestCase):
    def test_weather(self) -> None:
        g = load("P027zh_weather")
        with tempfile.TemporaryDirectory() as d:
            Path(d, "weather.py").write_text(
                "import requests\n"
                "def main():\n"
                "    try:\n"
                "        r = requests.get('https://wttr.in/San_Francisco?format=j1')\n"
                "        print(r.json())\n"
                "    except Exception as e:\n"
                "        print('error', e)\n",
                encoding="utf-8")
            s = g.grade([], d)
        self.assertEqual(s["file_created"], 1.0)
        self.assertEqual(s["has_http_request"], 1.0)
        self.assertEqual(s["references_location"], 1.0)


class CsvStockTrendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.g = load("P053zh_csv_stock_trend")

    def test_traditional_report(self) -> None:
        report = (
            "整體趨勢：看漲。起始價 77.45，結束價 110.03，漲跌幅 42.07%。\n"
            "8月 出現連續上漲 9 天；1月 出現連續下跌 5 天。\n"
            "1月 回落，4月 突破，夏季持續攀升，11月 創新高。\n"
        )
        with tempfile.TemporaryDirectory() as d:
            Path(d, "stock_trend_report.md").write_text(report, encoding="utf-8")
            s = self.g.grade([], d)
        self.assertEqual(s["trend_direction"], 1.0)
        self.assertEqual(s["starting_price"], 1.0)
        self.assertEqual(s["up_streak"], 1.0)
        self.assertEqual(s["down_streak"], 1.0)


class WrapperParityTests(unittest.TestCase):
    """A Chinese report should score the same as the English equivalent."""

    def test_gdp_ranking_zh_equals_en(self) -> None:
        g = load("P063zh_csv_gdp_ranking")
        zh = ("# GDP 報告\n## 摘要\nUnited States 17,420；Niue 0.01。共 15 個國家。\n"
              "總和 78,285；平均 352.6；中位數 21.52。\n"
              "前 5 大 50.1%，前 10 大 64.5%，前 20 大 79.1%。\n")
        en = ("# GDP Ranking\n## Summary\nUnited States 17,420; Niue 0.01. 15 countries.\n"
              "Total 78,285; mean 352.6; median 21.52.\n"
              "Top 5 ~50.1%, top 10 ~64.5%, top 20 ~79.1%.\n")
        with tempfile.TemporaryDirectory() as d:
            Path(d, "gdp_ranking_report.md").write_text(zh, encoding="utf-8")
            zh_mean = sum(g.grade([], d).values()) / 8
        with tempfile.TemporaryDirectory() as d:
            Path(d, "gdp_ranking_report.md").write_text(en, encoding="utf-8")
            en_mean = sum(g.grade([], d).values()) / 8
        self.assertGreater(zh_mean, 0.3)
        self.assertAlmostEqual(zh_mean, en_mean, places=2)


if __name__ == "__main__":
    unittest.main()
