"""Grader for P051zh_cve_security_triage (adapted from PinchBench task `task_cve_security_triage`).

Original file: tasks/task_cve_security_triage.md
grading_type: hybrid

Contract (see docs/claw_eval_zh_schema.md §8):
  * grade(transcript, workspace_path) -> dict[str, float]
      Deterministic check, stdlib-only, importable without claw_eval.
  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval
      is importable; adapts grade() into DimensionScores.
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """
    Grade the CVE/Security Triage task.

    Checks for structural completeness of both deliverables and
    correctness of key priority assignments.
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    triage_file = workspace / "triage_report.md"
    remediation_file = workspace / "remediation_plan.md"

    # --- Check 1: triage_report.md created ---
    if not triage_file.exists():
        scores["triage_report_created"] = 0.0
    else:
        scores["triage_report_created"] = 1.0

    # --- Check 2: remediation_plan.md created ---
    if not remediation_file.exists():
        scores["remediation_plan_created"] = 0.0
    else:
        scores["remediation_plan_created"] = 1.0

    # Early return if neither file exists
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

    # Read available content
    triage_content = triage_file.read_text() if triage_file.exists() else ""
    remediation_content = remediation_file.read_text() if remediation_file.exists() else ""
    all_content = triage_content + "\n" + remediation_content
    all_lower = all_content.lower()
    triage_lower = triage_content.lower()

    # --- Check 3: All 10 CVEs covered in triage report ---
    cve_ids = [
        "CVE-2026-29112", "CVE-2026-31845", "CVE-2026-28003",
        "CVE-2026-30291", "CVE-2026-27519", "CVE-2026-33010",
        "CVE-2026-34201", "CVE-2026-25877", "CVE-2026-36500",
        "CVE-2026-37188",
    ]
    found_cves = sum(1 for cve in cve_ids if cve.lower() in triage_lower)
    scores["all_cves_covered"] = found_cves / 10.0

    # --- Check 4: Priorities assigned (P0-P3 labels present) ---
    priority_matches = re.findall(r'\bP[0-3]\b', triage_content, re.IGNORECASE)
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

    # Helper: find priority near a CVE reference
    def find_priority_near_cve(cve_id, content):
        """Look for P0-P3 within 300 chars of a CVE mention."""
        matches = list(re.finditer(re.escape(cve_id.lower()), content.lower()))
        if not matches:
            # Try package name as fallback
            return None
        for m in matches:
            start = max(0, m.start() - 150)
            end = min(len(content), m.end() + 300)
            section = content[start:end]
            p_match = re.search(r'\bP([0-3])\b', section, re.IGNORECASE)
            if p_match:
                return int(p_match.group(1))
        return None

    # --- Check 5: Express RCE is P0 ---
    express_p = find_priority_near_cve("CVE-2026-29112", triage_content)
    if express_p == 0:
        scores["express_rce_is_p0"] = 1.0
    elif express_p == 1:
        scores["express_rce_is_p0"] = 0.5
    else:
        scores["express_rce_is_p0"] = 0.0

    # --- Check 6: JWT bypass is P0 ---
    jwt_p = find_priority_near_cve("CVE-2026-31845", triage_content)
    if jwt_p == 0:
        scores["jwt_bypass_is_p0"] = 1.0
    elif jwt_p == 1:
        scores["jwt_bypass_is_p0"] = 0.5
    else:
        scores["jwt_bypass_is_p0"] = 0.0

    # --- Check 7: Build-only CVEs lower priority than runtime CVEs ---
    minimatch_p = find_priority_near_cve("CVE-2026-33010", triage_content)
    semver_p = find_priority_near_cve("CVE-2026-34201", triage_content)
    # Compare against express RCE priority
    if minimatch_p is not None and semver_p is not None and express_p is not None:
        if minimatch_p > express_p and semver_p > express_p:
            scores["build_only_lower_priority"] = 1.0
        elif minimatch_p > express_p or semver_p > express_p:
            scores["build_only_lower_priority"] = 0.5
        else:
            scores["build_only_lower_priority"] = 0.0
    elif minimatch_p is not None or semver_p is not None:
        # Partial credit: at least one build CVE is present and classified
        build_p = minimatch_p if minimatch_p is not None else semver_p
        if build_p is not None and build_p >= 2:
            scores["build_only_lower_priority"] = 0.75
        else:
            scores["build_only_lower_priority"] = 0.25
    else:
        scores["build_only_lower_priority"] = 0.0

    # --- Check 8: PCI DSS scope mentioned ---
    pci_patterns = [r"pci", r"payment card", r"pci.?dss", r"cardholder"]
    pci_found = any(re.search(p, all_lower) for p in pci_patterns)
    scores["pci_scope_mentioned"] = 1.0 if pci_found else 0.0

    # --- Check 9: Deploy windows in remediation plan ---
    remediation_lower = remediation_content.lower()
    deploy_patterns = [r"april\s*14", r"april\s*17", r"4/14", r"4/17", r"04-14", r"04-17"]
    deploy_found = sum(1 for p in deploy_patterns if re.search(p, remediation_lower))
    if deploy_found >= 2:
        scores["deploy_windows_in_plan"] = 1.0
    elif deploy_found >= 1:
        scores["deploy_windows_in_plan"] = 0.5
    else:
        scores["deploy_windows_in_plan"] = 0.0

    # --- Check 10: Major version upgrades flagged ---
    major_version_keywords = [
        r"major version", r"breaking change", r"major upgrade",
        r"8\s*(?:to|→|->)\s*9", r"4\s*(?:to|→|->)\s*7",
        r"2\s*(?:to|→|->)\s*4", r"major bump",
    ]
    major_found = any(re.search(p, all_lower) for p in major_version_keywords)
    # Also check for general upgrade risk language near relevant packages
    if not major_found:
        risk_keywords = [r"test.*(?:jsonwebtoken|helmet|debug)", r"(?:jsonwebtoken|helmet|debug).*test"]
        major_found = any(re.search(p, all_lower) for p in risk_keywords)
    scores["major_version_flagged"] = 1.0 if major_found else 0.0

    # --- Check 11: Executive summary in remediation plan ---
    first_chunk = remediation_lower[:max(len(remediation_lower) // 5, 300)]
    if re.search(r"(executive summary|summary|overview|tldr|tl;dr)", first_chunk):
        scores["executive_summary_exists"] = 1.0
    elif re.search(r"(executive summary|summary|overview)", remediation_lower):
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
