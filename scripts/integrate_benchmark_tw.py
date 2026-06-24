#!/usr/bin/env python3
"""Integrate the v1/v2/v3/new benchmark task .md files into the tasks_tw suite.

This handles the *mechanically convertible* tasks: those that already use the
standard PinchBench markdown schema (YAML frontmatter + the canonical body
sections ``## Prompt / ## Expected Behavior / ## Grading Criteria /
## Automated Checks / ## LLM Judge Rubric``).

For each source task it:
  1. Injects the Taiwan locale frontmatter (language/locale/region) plus light
     provenance fields, and ensures grading_type/timeout are present.
  2. Rewrites every ``workspace_files[].source`` to live under ``tw/`` (the
     assets were copied to ``assets/tw/<type>/`` by the integration step).
  3. Renames a ``## Automated Checks (Python)`` header to ``## Automated Checks``
     (the loader matches the section name exactly).
  4. Demotes any non-canonical ``##`` body header to ``###`` so report-structure
     sub-sections fold into the Prompt the agent actually receives.
  5. Appends the standard bilingual grader-normalization wrapper inside the
     ``## Automated Checks`` python block (verbatim from an existing tw task).

Tasks needing real authoring judgement (missing Expected Behavior / Grading
Criteria, or a custom Chinese-section layout) are handled separately by agents
and are intentionally NOT in MECHANICAL below.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lib_zh  # noqa: E402

TASKS_TW = ROOT / "tasks_tw"
CANON = {
    "Prompt", "Expected Behavior", "Grading Criteria",
    "Automated Checks", "LLM Judge Rubric", "Additional Notes",
}

# (source_dir, filename) for the 29 mechanically-convertible tasks.
MECHANICAL = []
for fn in [
    "task_cross_asset_dual_screen", "task_ecommerce_basic_kpi",
    "task_ecommerce_basket_association", "task_ecommerce_clv_rfm",
    "task_log_capacity_planning", "task_log_distributed_trace",
    "task_log_service_health_summary", "task_semiconductor_supply_chain_risk",
    "task_tw_stock_correlation_sector", "task_tw_stock_event_study",
]:
    MECHANICAL.append(("benchmark_v1", fn))
for fn in [
    "task_ecommerce_json_analytics", "task_ecommerce_json_anomaly_detection",
    "task_log_microservice_sla", "task_microservice_incident_analysis",
    "task_semiconductor_md_valuation", "task_tw_stock_buy_signal",
    "task_tw_stock_factor_backtest", "task_tw_stock_portfolio_optimization",
]:
    MECHANICAL.append(("new_benchmark_files.tar 1", fn))
for fn in [
    "task_01_dns_fault_diagnosis", "task_02_dhcp_config_audit",
    "task_03_wifi_password_reset_plan", "task_04_network_interface_state",
    "task_08_incident_report_root_cause", "task_09_network_recovery_checklist",
    "task_10_multi_fault_triage",
]:
    MECHANICAL.append(("benchmark_v3.tar 1", fn))
for fn in [
    "task_pdf_financial_report_analysis", "task_pptx_strategy_evaluation",
    "task_ux_interview_thematic_analysis", "task_xlsx_hr_analytics",
]:
    MECHANICAL.append(("benchmark_v2", fn))

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def extract_wrapper() -> str:
    """Pull the canonical bilingual wrapper text from an existing tw grader."""
    sample = (TASKS_TW / "task_csv_cities_density.md").read_text(encoding="utf-8")
    m = re.search(r"```python\s*(.*?)\s*```", sample, re.DOTALL)
    code = m.group(1)
    idx = code.index("# --- Bilingual report normalization")
    return code[idx:].rstrip()


WRAPPER = extract_wrapper()


def split_id(fm_text: str) -> str:
    m = re.search(r"^id:\s*(\S+)\s*$", fm_text, re.MULTILINE)
    return m.group(1)


def has_key(fm_text: str, key: str) -> bool:
    return re.search(rf"^{re.escape(key)}\s*:", fm_text, re.MULTILINE) is not None


def transform_frontmatter(fm_text: str, source_benchmark: str) -> str:
    lines = fm_text.splitlines()
    out = []
    for ln in lines:
        m = re.match(r"^(\s*-\s*source:\s*)(\S.*?)\s*$", ln)
        if m and not m.group(2).startswith("tw/"):
            ln = f"{m.group(1)}tw/{m.group(2)}"
        out.append(ln)
    fm = "\n".join(out)
    add = []
    if not has_key(fm, "grading_type"):
        add.append("grading_type: hybrid")
    if not has_key(fm, "timeout_seconds"):
        add.append("timeout_seconds: 300")
    for k, v in [
        ("language", "zh"), ("locale", "zh-TW"), ("region", "TW"),
        ("localization", "taiwan"), ("localization_strategy", "native"),
        ("source_benchmark", source_benchmark),
    ]:
        if not has_key(fm, k):
            add.append(f"{k}: {v}")
    if add:
        fm = fm.rstrip() + "\n" + "\n".join(add)
    return fm


def transform_body(body: str) -> str:
    """Normalise body headers.

    The loader (lib_tasks._parse_sections) and the validator are *not*
    code-fence aware: any line starting with ``## `` begins a new section, even
    inside a ```markdown example block. So a non-canonical ``## `` header in an
    example report template would truncate the Prompt the agent receives.
    We therefore demote every non-canonical ``## `` header to ``### `` — except
    inside the ```python grader block, which we leave byte-for-byte intact.
    """
    lines = body.split("\n")
    in_fence = False
    fence_lang = ""
    out = []
    for ln in lines:
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
            else:
                in_fence = False
                fence_lang = ""
            out.append(ln)
            continue
        if in_fence and fence_lang == "python":
            out.append(ln)
            continue
        if re.match(r"^##\s+Automated Checks \(Python\)\s*$", ln):
            out.append("## Automated Checks")
            continue
        hm = re.match(r"^##\s+(.+?)\s*$", ln)
        if hm and hm.group(1).strip() not in CANON:
            out.append("### " + hm.group(1).strip())
            continue
        out.append(ln)
    body = "\n".join(out)
    body = ensure_grading_checklist(body)
    return insert_wrapper(body)


def ensure_grading_checklist(body: str) -> str:
    """If '## Grading Criteria' has a table but no ``- [ ]`` checklist, derive
    checklist items from the table so the loader can extract criteria (matching
    the rest of the tw suite). The original table is kept as reference.
    """
    lines = body.split("\n")
    # find section span
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^##\s+Grading Criteria\s*$", ln):
            start = i
            break
    if start is None:
        return body
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^##\s+\S", lines[j]):
            end = j
            break
    section = lines[start + 1:end]
    if any(re.match(r"^\s*-\s+\[[ x]\]\s+", s) for s in section):
        return body  # already has a checklist
    items = []
    for s in section:
        s = s.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        # skip header row and separator row (---)
        if not cells or all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if cells[0].lower() in {"key", "項目", "檢查項", "說明", "criterion"}:
            continue
        desc = cells[-1].replace("`", "").strip()
        if desc:
            items.append(f"- [ ] {desc}")
    if not items:
        return body
    new_section = section + [""] + items
    return "\n".join(lines[:start + 1] + new_section + lines[end:])


def insert_wrapper(body: str) -> str:
    # Locate the python block inside the '## Automated Checks' section.
    ac = body.index("## Automated Checks")
    open_fence = body.index("```python", ac)
    code_start = body.index("\n", open_fence) + 1
    close_fence = body.index("```", code_start)
    code = body[code_start:close_fence].rstrip("\n")
    new_code = code + "\n\n\n" + WRAPPER + "\n"
    return body[:code_start] + new_code + body[close_fence:]


def main() -> int:
    written = []
    for sd, fn in MECHANICAL:
        src = ROOT / sd / "tasks" / f"{fn}.md"
        text = src.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            print(f"!! NO FRONTMATTER: {src}")
            return 2
        fm_text, body = m.group(1), m.group(2)
        task_id = split_id(fm_text)
        fm_new = transform_frontmatter(fm_text, sd.replace(".tar 1", ""))
        body_new = transform_body(body)
        result = f"---\n{fm_new}\n---\n{body_new}"
        # Sanity: required sections present, grade() defined, no simplified chars.
        h2 = set(re.findall(r"^##\s+(.+)$", body_new, re.MULTILINE))
        missing = {"Prompt", "Expected Behavior", "Grading Criteria",
                   "Automated Checks", "LLM Judge Rubric"} - h2
        assert not missing, f"{task_id}: missing sections {missing}"
        code = re.search(r"```python\s*(.*?)\s*```", body_new, re.DOTALL).group(1)
        compile(code, f"{task_id}:grader", "exec")
        assert "def grade(" in code and "_GRADE_IMPL = grade" in code
        simp = lib_zh.find_simplified(body_new)
        assert not simp, f"{task_id}: simplified chars {simp}"
        dest = TASKS_TW / f"{task_id}.md"
        dest.write_text(result, encoding="utf-8")
        written.append(task_id)
        print(f"  OK  {sd}/{fn}.md -> tasks_tw/{task_id}.md")
    print(f"\nWrote {len(written)} task files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
