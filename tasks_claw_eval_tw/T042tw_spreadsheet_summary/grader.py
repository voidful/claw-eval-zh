"""Grader for T042tw_spreadsheet_summary (Taiwan-localized from PinchBench `task_spreadsheet_summary`).

Phase 2 source: tasks_zh/task_spreadsheet_summary.md
Original file: tasks/task_spreadsheet_summary.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """台灣版 CSV 與 Excel 資料摘要 grader。

    應有事實「從佈署的台灣 fixtures 動態實算」——
      - quarterly_sales.csv：總營收／總利潤／總數量／最佳地區／最佳產品
      - company_expenses.xlsx：Q1 總費用／最高費用部門／最高費用員工／各部門 Q1 預算
    再比對 agent 產生的中文報告 data_summary.md。僅用標準函式庫，金額為新臺幣（NT$），
    不沿用任何美國 $ 數值。.xlsx 以 zipfile + xml.etree 自行解析（不依賴 openpyxl）。
    """
    from pathlib import Path
    import csv
    import re
    import zipfile
    import xml.etree.ElementTree as ET
    from collections import defaultdict

    keys = [
        "report_created", "total_revenue", "total_profit", "top_region",
        "top_product", "total_expenses", "top_department", "top_employee",
        "budget_comparison",
    ]
    workspace = Path(workspace_path)

    # --- 找報告檔 ---
    report_path = workspace / "data_summary.md"
    if not report_path.exists():
        for alt in ["summary.md", "report.md", "data_report.md", "analysis.md",
                    "資料摘要.md", "摘要報告.md", "摘要.md"]:
            if (workspace / alt).exists():
                report_path = workspace / alt
                break
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    # --- 從 CSV 動態實算正解 ---
    csv_path = workspace / "quarterly_sales.csv"
    total_revenue = total_cost = total_units = 0
    rev_by_region = defaultdict(int)
    rev_by_product = defaultdict(int)
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                def num(k):
                    return int(round(float(re.sub(r"[^\d.\-]", "", row.get(k) or "0") or 0)))
                rev = num("Revenue")
                cost = num("Cost")
                units = num("Units_Sold")
                total_revenue += rev
                total_cost += cost
                total_units += units
                rev_by_region[(row.get("Region") or "").strip()] += rev
                rev_by_product[(row.get("Product") or "").strip()] += rev
    total_profit = total_revenue - total_cost
    top_region = max(rev_by_region.items(), key=lambda kv: kv[1]) if rev_by_region else ("", 0)
    top_product = max(rev_by_product.items(), key=lambda kv: kv[1]) if rev_by_product else ("", 0)

    # --- 從 XLSX 動態實算正解（標準函式庫解析 .xlsx）---
    xlsx_path = workspace / "company_expenses.xlsx"
    exp_total = 0
    exp_by_dept = defaultdict(int)
    exp_by_emp = defaultdict(int)
    q1_budget = {}

    def read_xlsx(path):
        """回傳 {sheet_name: [ [cell, ...], ... ]}，cell 為字串或數字。"""
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
              "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
        out = {}
        with zipfile.ZipFile(path) as z:
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in sroot.findall("m:si", ns):
                    shared.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
            wbroot = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = []
            for sh in wbroot.find("m:sheets", ns).findall("m:sheet", ns):
                rid = sh.get("{%s}id" % ns["r"])
                sheets.append((sh.get("name"), rid))
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            rid2target = {}
            for rel in rels:
                rid2target[rel.get("Id")] = rel.get("Target")

            def col_idx(ref):
                m = re.match(r"([A-Z]+)", ref or "")
                if not m:
                    return 0
                s = m.group(1)
                n = 0
                for ch in s:
                    n = n * 26 + (ord(ch) - ord("A") + 1)
                return n - 1

            for name, rid in sheets:
                target = rid2target.get(rid, "")
                part = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
                if part not in z.namelist():
                    part = "xl/worksheets/" + target.split("/")[-1]
                root = ET.fromstring(z.read(part))
                rows = []
                for r in root.iter("{%s}row" % ns["m"]):
                    cells = {}
                    maxc = -1
                    for cc in r.findall("m:c", ns):
                        ref = cc.get("r", "")
                        ci = col_idx(ref)
                        t = cc.get("t")
                        v = cc.find("m:v", ns)
                        if t == "s" and v is not None:
                            val = shared[int(v.text)]
                        elif t == "inlineStr":
                            isn = cc.find("m:is", ns)
                            val = "".join(x.text or "" for x in isn.iter("{%s}t" % ns["m"])) if isn is not None else ""
                        elif v is not None:
                            try:
                                f = float(v.text)
                                val = int(f) if f.is_integer() else f
                            except ValueError:
                                val = v.text
                        else:
                            val = ""
                        cells[ci] = val
                        maxc = max(maxc, ci)
                    rows.append([cells.get(i, "") for i in range(maxc + 1)])
                out[name] = rows
        return out

    if xlsx_path.exists():
        try:
            data = read_xlsx(xlsx_path)
            exp_rows = data.get("Q1_Expenses") or []
            for row in exp_rows[1:]:
                if len(row) < 4:
                    continue
                emp = str(row[0]).strip()
                dept = str(row[1]).strip()
                try:
                    amt = int(round(float(row[3])))
                except (ValueError, TypeError):
                    continue
                if not emp:
                    continue
                exp_total += amt
                exp_by_dept[dept] += amt
                exp_by_emp[emp] += amt
            bud_rows = data.get("Budgets") or []
            for row in bud_rows[1:]:
                if len(row) < 2:
                    continue
                dept = str(row[0]).strip()
                try:
                    q1_budget[dept] = int(round(float(row[1])))
                except (ValueError, TypeError):
                    pass
        except Exception:  # noqa: BLE001
            pass

    top_dept = max(exp_by_dept.items(), key=lambda kv: kv[1]) if exp_by_dept else ("", 0)
    top_emp = max(exp_by_emp.items(), key=lambda kv: kv[1]) if exp_by_emp else ("", 0)

    # --- 讀報告，準備比對（去千分位逗號與空白，方便數字匹配）---
    c = report_path.read_text(encoding="utf-8", errors="ignore")
    nospace = re.sub(r"[\s,]", "", c)

    def has_num(n):
        return n > 0 and str(int(n)) in nospace

    def has_name(name):
        return bool(name) and name in c

    scores = {"report_created": 1.0}

    scores["total_revenue"] = 1.0 if has_num(total_revenue) else 0.0
    scores["total_profit"] = 1.0 if has_num(total_profit) else 0.0

    region_ok = has_name(top_region[0]) and (
        has_num(top_region[1])
        or re.search(re.escape(top_region[0]) + r".{0,30}(最高|最佳|最大|第一|冠軍|居首|領先)", c)
        or re.search(r"(最高|最佳|最大|第一|冠軍|居首|領先).{0,30}" + re.escape(top_region[0]), c)
    )
    scores["top_region"] = 1.0 if region_ok else 0.0

    product_ok = has_name(top_product[0]) and (
        has_num(top_product[1])
        or re.search(re.escape(top_product[0]) + r".{0,30}(最高|最佳|最暢銷|最大|第一|冠軍|居首|領先)", c)
        or re.search(r"(最高|最佳|最暢銷|最大|第一|冠軍|居首|領先).{0,30}" + re.escape(top_product[0]), c)
    )
    scores["top_product"] = 1.0 if product_ok else 0.0

    scores["total_expenses"] = 1.0 if has_num(exp_total) else 0.0

    dept_ok = has_name(top_dept[0]) and (
        has_num(top_dept[1])
        or re.search(re.escape(top_dept[0]) + r".{0,30}(最高|最多|最大|第一|居首|領先)", c)
        or re.search(r"(最高|最多|最大|第一|居首|領先).{0,30}" + re.escape(top_dept[0]), c)
    )
    scores["top_department"] = 1.0 if dept_ok else 0.0

    emp_ok = has_name(top_emp[0]) and (
        has_num(top_emp[1])
        or re.search(re.escape(top_emp[0]) + r".{0,30}(最高|最多|最大|第一|居首|領先)", c)
        or re.search(r"(最高|最多|最大|第一|居首|領先).{0,30}" + re.escape(top_emp[0]), c)
    )
    scores["top_employee"] = 1.0 if emp_ok else 0.0

    budget_terms = re.search(r"(預算|實際|超支|在預算內|結餘|差額|對比|比較)", c)
    budget_num = any(has_num(v) for v in q1_budget.values())
    scores["budget_comparison"] = 1.0 if (
        budget_terms and (budget_num or re.search(r"(預算.{0,40}(實際|費用)|(實際|費用).{0,40}預算)", c))
    ) else 0.0

    return scores


# --- Bilingual report normalization (中文 report -> English keywords) ---
# See docs/claw_eval_zh_schema.md §8 and scripts/lib_zh.py. The English-only
# path is unchanged (no CJK in reports -> direct passthrough, no shadow copy).
try:
    from lib_zh import normalize_zh_to_en as _zh_normalize
except Exception:  # noqa: BLE001
    def _zh_normalize(_text):
        return _text

_GRADE_IMPL = grade


def grade(transcript, workspace_path):  # noqa: F811
    """Shadow-normalize Chinese report text, then run the original grade()."""
    import shutil
    import tempfile
    from pathlib import Path as _P

    text_exts = (".md", ".txt", ".rst", ".markdown")
    ws = workspace_path
    try:
        src = _P(workspace_path)
        if src.exists() and src.is_dir():
            needs = False
            for f in src.rglob("*"):
                if f.is_file() and f.suffix.lower() in text_exts:
                    try:
                        if any("一" <= c <= "鿿" for c in f.read_text(encoding="utf-8")):
                            needs = True
                            break
                    except (OSError, UnicodeDecodeError):
                        pass
            if needs:
                shadow = _P(tempfile.mkdtemp(prefix="cez_ws_")) / "ws"
                shutil.copytree(src, shadow, dirs_exist_ok=True)
                for f in shadow.rglob("*"):
                    if f.is_file() and f.suffix.lower() in text_exts:
                        try:
                            f.write_text(
                                _zh_normalize(f.read_text(encoding="utf-8")),
                                encoding="utf-8",
                            )
                        except (OSError, UnicodeDecodeError):
                            pass
                ws = str(shadow)
    except Exception:  # noqa: BLE001
        ws = workspace_path
    return _GRADE_IMPL(transcript, ws)


# --- Optional Claw-Eval adapter (only active when `claw_eval` is importable) ---
# Keeps grader.py importable offline (tests / PinchBench runner use grade()),
# while becoming a drop-in AbstractGrader subclass inside a real claw_eval
# checkout. See docs/claw_eval_zh_schema.md section 8.
PRIMARY_DIMENSIONS = ['completion', 'safety']


def to_dimension_scores(component_scores: dict) -> dict:
    """Map flat component scores into completion/safety/robustness (plain dict)."""
    vals = [float(v) for v in component_scores.values() if isinstance(v, (int, float))]
    completion = round(sum(vals) / len(vals), 4) if vals else 0.0
    return {"completion": completion, "safety": 1.0, "robustness": 1.0}


try:  # pragma: no cover - exercised only with claw_eval installed
    from claw_eval.graders.base import AbstractGrader
    from claw_eval.models.trace import DimensionScores

    _CLAW_EVAL_AVAILABLE = True
except Exception:  # noqa: BLE001
    _CLAW_EVAL_AVAILABLE = False


if _CLAW_EVAL_AVAILABLE:  # pragma: no cover

    def _messages_to_transcript(messages):
        """Best-effort conversion of Claw-Eval TraceMessages to PinchBench events."""
        transcript = []
        for m in messages:
            role = m.message.role
            content = []
            text = getattr(m.message, "text", "") or ""
            if text:
                content.append({"type": "text", "text": text})
            transcript.append(
                {"type": "message", "message": {"role": role, "content": content}}
            )
        return transcript

    def _reconstruct_workspace(env_snapshot):
        """Write env_snapshot files to a temp dir and return its path (or '')."""
        if not env_snapshot:
            return ""
        import tempfile
        from pathlib import Path as _Path

        root = _Path(tempfile.mkdtemp(prefix="claw_eval_zh_ws_"))
        files = env_snapshot.get("files", env_snapshot) if isinstance(env_snapshot, dict) else {}
        if isinstance(files, dict):
            for rel, body in files.items():
                try:
                    dest = root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if isinstance(body, bytes):
                        dest.write_bytes(body)
                    else:
                        dest.write_text(str(body), encoding="utf-8")
                except OSError:
                    pass
        return str(root)

    class ClawEvalZhGrader(AbstractGrader):
        """Adapter that wraps the module-level grade() into DimensionScores."""

        def grade(self, messages, dispatches, task, audit_data=None, judge=None,
                  media_events=None, env_snapshot=None):
            transcript = _messages_to_transcript(messages)
            workspace = _reconstruct_workspace(env_snapshot)
            component_scores = grade(transcript, workspace)
            scores = DimensionScores()
            dims = to_dimension_scores(component_scores)
            scores.completion = dims["completion"]
            scores.safety = dims["safety"]
            scores.robustness = self.compute_robustness(dispatches)
            scores.efficiency_turns = len(
                [m for m in messages if m.message.role == "assistant"]
            )
            return scores
