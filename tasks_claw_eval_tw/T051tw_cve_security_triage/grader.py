"""Grader for T051tw_cve_security_triage (Taiwan-localized from PinchBench `task_cve_security_triage`).

Phase 2 source: tasks_zh/task_cve_security_triage.md
Original file: tasks/task_cve_security_triage.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """CVE／資安分流（Triage）grader（繁中台灣化：鼎峰電商平台 dingfeng-shop）。

    檢查兩份交付物（triage_report.md、remediation_plan.md）的結構完整性與關鍵
    優先級指派正確性。CVE-ID、CVSS、套件名、PCI DSS 等國際技術名詞保留英文比對；
    場景敘述（部署時段、執行摘要、主版號）改為中英雙語比對，以容納繁體中文報告。
    僅用標準函式庫。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    triage_file = workspace / "triage_report.md"
    remediation_file = workspace / "remediation_plan.md"

    # --- Check 1：triage_report.md 已建立 ---
    scores["triage_report_created"] = 1.0 if triage_file.exists() else 0.0

    # --- Check 2：remediation_plan.md 已建立 ---
    scores["remediation_plan_created"] = 1.0 if remediation_file.exists() else 0.0

    # 兩份檔案皆不存在則提早返回
    if not triage_file.exists() and not remediation_file.exists():
        return {
            "triage_report_created": 0.0,
            "remediation_plan_created": 0.0,
            "all_cves_covered": 0.0,
            "priorities_assigned": 0.0,
            "express_rce_is_p0": 0.0,
            "jwt_bypass_is_p0": 0.0,
            "build_only_lower_priority": 0.0,
            "pci_scope_mentioned": 0.0,
            "deploy_windows_in_plan": 0.0,
            "major_version_flagged": 0.0,
            "executive_summary_exists": 0.0,
        }

    # 讀取可用內容
    triage_content = triage_file.read_text(encoding="utf-8", errors="ignore") if triage_file.exists() else ""
    remediation_content = remediation_file.read_text(encoding="utf-8", errors="ignore") if remediation_file.exists() else ""
    all_content = triage_content + "\n" + remediation_content
    all_lower = all_content.lower()
    triage_lower = triage_content.lower()

    # --- Check 3：分流報告涵蓋全部 10 個 CVE ---
    cve_ids = [
        "CVE-2026-29112", "CVE-2026-31845", "CVE-2026-28003",
        "CVE-2026-30291", "CVE-2026-27519", "CVE-2026-33010",
        "CVE-2026-34201", "CVE-2026-25877", "CVE-2026-36500",
        "CVE-2026-37188",
    ]
    found_cves = sum(1 for cve in cve_ids if cve.lower() in triage_lower)
    scores["all_cves_covered"] = found_cves / 10.0

    # --- Check 4：已指派優先級（P0-P3 標籤存在）---
    priority_matches = re.findall(r"\bP[0-3]\b", triage_content, re.IGNORECASE)
    if len(priority_matches) >= 10:
        scores["priorities_assigned"] = 1.0
    elif len(priority_matches) >= 7:
        scores["priorities_assigned"] = 0.75
    elif len(priority_matches) >= 4:
        scores["priorities_assigned"] = 0.5
    elif len(priority_matches) >= 1:
        scores["priorities_assigned"] = 0.25
    else:
        scores["priorities_assigned"] = 0.0

    # 輔助：在某 CVE 提及處附近尋找 P0-P3
    def find_priority_near_cve(cve_id, content):
        """在 CVE 提及位置前後尋找 P0-P3（前 150、後 300 字元）。"""
        matches = list(re.finditer(re.escape(cve_id.lower()), content.lower()))
        if not matches:
            return None
        for m in matches:
            start = max(0, m.start() - 150)
            end = min(len(content), m.end() + 300)
            section = content[start:end]
            p_match = re.search(r"\bP([0-3])\b", section, re.IGNORECASE)
            if p_match:
                return int(p_match.group(1))
        return None

    # --- Check 5：Express RCE 為 P0 ---
    express_p = find_priority_near_cve("CVE-2026-29112", triage_content)
    if express_p == 0:
        scores["express_rce_is_p0"] = 1.0
    elif express_p == 1:
        scores["express_rce_is_p0"] = 0.5
    else:
        scores["express_rce_is_p0"] = 0.0

    # --- Check 6：JWT 繞過為 P0 ---
    jwt_p = find_priority_near_cve("CVE-2026-31845", triage_content)
    if jwt_p == 0:
        scores["jwt_bypass_is_p0"] = 1.0
    elif jwt_p == 1:
        scores["jwt_bypass_is_p0"] = 0.5
    else:
        scores["jwt_bypass_is_p0"] = 0.0

    # --- Check 7：僅限建置的 CVE 優先級低於 runtime CVE ---
    minimatch_p = find_priority_near_cve("CVE-2026-33010", triage_content)
    semver_p = find_priority_near_cve("CVE-2026-34201", triage_content)
    if minimatch_p is not None and semver_p is not None and express_p is not None:
        if minimatch_p > express_p and semver_p > express_p:
            scores["build_only_lower_priority"] = 1.0
        elif minimatch_p > express_p or semver_p > express_p:
            scores["build_only_lower_priority"] = 0.5
        else:
            scores["build_only_lower_priority"] = 0.0
    elif minimatch_p is not None or semver_p is not None:
        build_p = minimatch_p if minimatch_p is not None else semver_p
        if build_p is not None and build_p >= 2:
            scores["build_only_lower_priority"] = 0.75
        else:
            scores["build_only_lower_priority"] = 0.25
    else:
        scores["build_only_lower_priority"] = 0.0

    # --- Check 8：提及 PCI DSS 範圍（國際合規名詞，英文＋中文）---
    pci_patterns = [r"pci", r"payment card", r"pci.?dss", r"cardholder",
                    r"付款", r"持卡人"]
    pci_found = any(re.search(p, all_lower) for p in pci_patterns)
    scores["pci_scope_mentioned"] = 1.0 if pci_found else 0.0

    # --- Check 9：修補計畫含部署時段（中英雙語：April 14/17、4/14、4 月 14 日）---
    remediation_lower = remediation_content.lower()
    deploy_patterns = [
        r"april\s*14", r"april\s*17", r"4/14", r"4/17", r"04-14", r"04-17",
        r"4\s*月\s*14", r"4\s*月\s*17", r"四月\s*14", r"四月\s*17",
    ]
    deploy_found = sum(1 for p in deploy_patterns if re.search(p, remediation_lower))
    if deploy_found >= 2:
        scores["deploy_windows_in_plan"] = 1.0
    elif deploy_found >= 1:
        scores["deploy_windows_in_plan"] = 0.5
    else:
        scores["deploy_windows_in_plan"] = 0.0

    # --- Check 10：主版號升級被標記（中英雙語）---
    major_version_keywords = [
        r"major version", r"breaking change", r"major upgrade", r"major bump",
        r"8\s*(?:to|→|->)\s*9", r"4\s*(?:to|→|->)\s*7",
        r"2\s*(?:to|→|->)\s*4",
        r"主版號", r"主版本", r"破壞性變更", r"跨主版", r"重大版本",
    ]
    major_found = any(re.search(p, all_lower) for p in major_version_keywords)
    if not major_found:
        # 後援：在相關套件附近出現測試／test 語彙
        risk_keywords = [
            r"test.*(?:jsonwebtoken|helmet|debug)",
            r"(?:jsonwebtoken|helmet|debug).*test",
            r"(?:jsonwebtoken|helmet|debug).{0,40}測試",
            r"測試.{0,40}(?:jsonwebtoken|helmet|debug)",
        ]
        major_found = any(re.search(p, all_lower) for p in risk_keywords)
    scores["major_version_flagged"] = 1.0 if major_found else 0.0

    # --- Check 11：修補計畫含執行摘要（中英雙語）---
    first_chunk = remediation_lower[:max(len(remediation_lower) // 5, 300)]
    head_pat = r"(executive summary|summary|overview|tldr|tl;dr|執行摘要|摘要|總覽|重點摘要)"
    full_pat = r"(executive summary|summary|overview|執行摘要|摘要|總覽)"
    if re.search(head_pat, first_chunk):
        scores["executive_summary_exists"] = 1.0
    elif re.search(full_pat, remediation_lower):
        scores["executive_summary_exists"] = 0.5
    else:
        scores["executive_summary_exists"] = 0.0

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
PRIMARY_DIMENSIONS = ['completion']


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
