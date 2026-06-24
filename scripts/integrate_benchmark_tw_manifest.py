#!/usr/bin/env python3
"""Register the 38 integrated benchmark tasks in tasks_tw/manifest.yaml.

Data-driven: reads each new task file's frontmatter `category` and appends the
id under the matching category group (creating new groups as needed). Existing
groups and members are preserved; nothing is duplicated. Text-based insertion
keeps the file's comments and ordering intact.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TASKS_TW = ROOT / "tasks_tw"
MANIFEST = TASKS_TW / "manifest.yaml"

NEW_IDS = [
    # v1
    "task_cross_asset_dual_screen", "task_ecommerce_basic_kpi",
    "task_ecommerce_basket_association", "task_ecommerce_clv_rfm",
    "task_log_capacity_planning", "task_log_distributed_trace",
    "task_log_service_health_summary", "task_semiconductor_supply_chain_risk",
    "task_tw_stock_correlation_sector", "task_tw_stock_event_study",
    # new_benchmark_files
    "task_ecommerce_json_analytics", "task_ecommerce_json_anomaly_detection",
    "task_log_microservice_sla", "task_microservice_incident_analysis",
    "task_semiconductor_md_valuation", "task_tw_stock_buy_signal",
    "task_tw_stock_factor_backtest", "task_tw_stock_portfolio_optimization",
    # v3
    "task_dns_fault_diagnosis", "task_dhcp_config_audit",
    "task_wifi_password_reset_plan", "task_network_interface_state",
    "task_05_dns_rollback_decision", "task_06_firewall_rule_dry_run",
    "task_07_proxy_cert_expiry", "task_08_incident_report_root_cause",
    "task_09_network_recovery_checklist", "task_10_multi_fault_triage",
    # v2
    "task_pdf_financial_report_analysis", "task_pptx_strategy_evaluation",
    "task_ux_interview_thematic_analysis", "task_xlsx_hr_analytics",
    "task_cross_format_business_intelligence", "task_supply_chain_timeline_analysis",
    "task_web_search_market_research", "task_docx_contract_audit",
    "task_review_fake_detection", "task_review_sentiment_product_insights",
]


def category_of(task_id: str) -> str:
    text = (TASKS_TW / f"{task_id}.md").read_text(encoding="utf-8")
    fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL).group(1)
    meta = yaml.safe_load(fm)
    return str(meta.get("category") or "uncategorized")


def main() -> int:
    missing = [t for t in NEW_IDS if not (TASKS_TW / f"{t}.md").exists()]
    if missing:
        print(f"!! missing task files, aborting: {missing}")
        return 2

    raw = MANIFEST.read_text(encoding="utf-8")
    manifest = yaml.safe_load(raw)
    categories = manifest.get("categories", {}) or {}
    existing = {gid: list(members or []) for gid, members in categories.items()}

    # Group new ids by category, skipping any already present anywhere.
    already = set()
    for members in existing.values():
        already.update(members)
    to_add: dict[str, list[str]] = {}
    for tid in NEW_IDS:
        if tid in already:
            continue
        cat = category_of(tid)
        to_add.setdefault(cat, []).append(tid)

    lines = raw.splitlines()

    def group_span(gid: str):
        """Return (header_idx, last_member_idx) for an existing group."""
        hi = next(i for i, ln in enumerate(lines)
                  if re.match(rf"^  {re.escape(gid)}:\s*$", ln))
        last = hi
        for j in range(hi + 1, len(lines)):
            if re.match(r"^  -\s+\S", lines[j]):
                last = j
            elif re.match(r"^  \S", lines[j]) or re.match(r"^\S", lines[j]):
                break
        return hi, last

    # Insert into existing groups (do later groups first to keep indices valid).
    existing_targets = [(g, ids) for g, ids in to_add.items() if g in existing]
    existing_targets.sort(key=lambda gi: group_span(gi[0])[1], reverse=True)
    for gid, ids in existing_targets:
        _, last = group_span(gid)
        ins = [f"  - {t}" for t in ids]
        lines[last + 1:last + 1] = ins

    # Append brand-new groups at end of file (categories is the last block).
    new_groups = [(g, ids) for g, ids in to_add.items() if g not in existing]
    new_groups.sort()
    tail = []
    for gid, ids in new_groups:
        tail.append(f"  {gid}:")
        tail.extend(f"  - {t}" for t in ids)
    if tail:
        while lines and lines[-1].strip() == "":
            lines.pop()
        lines.extend(tail)

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Report
    print("Added per category:")
    for g, ids in sorted(to_add.items()):
        tag = "(existing)" if g in existing else "(NEW group)"
        print(f"  {g} {tag}: {len(ids)} -> {ids}")
    total = sum(len(v) for v in to_add.values())
    print(f"Total added: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
