"""Anchor tasks meet Taiwan context and their graders work."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
CLAW = ROOT / "tasks_claw_eval_tw"


def load_yaml(orig):
    for d in CLAW.iterdir():
        if d.is_dir():
            data = yaml.safe_load((d / "task.yaml").read_text(encoding="utf-8"))
            if data["source"]["original_task_id"] == orig:
                return d.name, data
    return None, None


def load_grader(folder):
    spec = importlib.util.spec_from_file_location("g_" + folder, CLAW / folder / "grader.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TwAnchors(unittest.TestCase):
    def test_weather_is_taipei(self):
        folder, d = load_yaml("task_weather")
        self.assertRegex(d["prompt"]["text"], r"台北|臺北|Taipei")
        g = load_grader(folder)
        with tempfile.TemporaryDirectory() as t:
            Path(t, "weather.py").write_text(
                "import requests\ntry:\n    print(requests.get('https://wttr.in/Taipei').text)\nexcept Exception as e:\n    print(e)\n",
                encoding="utf-8")
            s = g.grade([], t)
        self.assertEqual(s["references_location"], 1.0)

    def test_calendar_is_taiwan_timezone(self):
        folder, d = load_yaml("task_calendar")
        blob = d["prompt"]["text"] + str(d.get("expected_behavior", ""))
        self.assertRegex(blob, r"Asia/Taipei|台灣|台北")

    def test_stock_trend_is_tsmc_with_real_values(self):
        folder, d = load_yaml("task_csv_stock_trend")
        self.assertRegex(d["prompt"]["text"], r"台積電|2330")
        g = load_grader(folder)
        report = ("台積電 2024 看漲。起始價 593.00，結束價 1,075.00，漲跌幅 +81.28%。\n"
                  "2024-09-18 至 2024-09-26 連續上漲 6 天；2024-05-27 至 2024-05-31 連續下跌 4 天。\n"
                  "全年最高 1,090，最低 576。\n" + "".join(f"{m}月 " for m in range(1, 13)))
        with tempfile.TemporaryDirectory() as t:
            Path(t, "stock_trend_report.md").write_text(report, encoding="utf-8")
            s = g.grade([], t)
        self.assertEqual(s["starting_price"], 1.0)
        self.assertEqual(s["ending_price"], 1.0)
        self.assertEqual(s["trend_direction"], 1.0)

    def test_sanity_is_chinese(self):
        folder, d = load_yaml("task_sanity")
        self.assertTrue(any("一" <= c <= "鿿" for c in d["prompt"]["text"]))

    def test_fixture_exists(self):
        self.assertTrue((ROOT / "assets" / "tw" / "csvs" / "tw_stock_2330_2024.csv").exists())


if __name__ == "__main__":
    unittest.main()
