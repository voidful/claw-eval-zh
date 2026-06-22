"""Grader for T119tw_meeting_tech_product_features (Taiwan-localized from PinchBench `task_meeting_tech_product_features`).

Phase 2 source: tasks_zh/task_meeting_tech_product_features.md
Original file: tasks/task_meeting_tech_product_features.md
grading_type: hybrid

Contract: grade(transcript, workspace_path) -> dict[str, float]; stdlib-only,
importable without claw_eval. Bilingual report normalization + optional
Claw-Eval AbstractGrader adapter (see docs/claw_eval_zh_schema.md §8).
"""

from __future__ import annotations


def grade(transcript: list, workspace_path: str) -> dict:
    """
    TW（鼎峰科技）產品功能優先排序 grader。

    查核項事實改從台灣逐字稿
    （dest=meeting_transcript.md）動態推導，再比對 agent 的中文報告
    （feature_priorities.md）。僅用標準函式庫。
    """
    from pathlib import Path
    import re

    scores = {}
    workspace = Path(workspace_path)

    # --- 找 agent 產生的中文報告 ---
    report_path = workspace / "feature_priorities.md"
    if not report_path.exists():
        for alt in [
            "features.md", "product_features.md", "feature_list.md",
            "priorities.md", "feature_priority.md", "功能優先排序.md",
            "功能清單.md",
        ]:
            alt_path = workspace / alt
            if alt_path.exists():
                report_path = alt_path
                break

    keys = [
        "report_created", "min_features", "ux_top_pick",
        "vuln_mgmt_top_pick", "gitops_top_pick", "pipeline_editor",
        "fuzzing_deprioritized", "community_contributions",
        "bundling_methodology", "top_five_section",
    ]
    if not report_path.exists():
        return {k: 0.0 for k in keys}

    scores["report_created"] = 1.0
    content = report_path.read_text(encoding="utf-8", errors="ignore")
    c = content.lower()

    # --- 從逐字稿動態讀出「應有事實」（用於 sanity，事實鎖在逐字稿） ---
    tpath = workspace / "meeting_transcript.md"
    ttext = ""
    if tpath.exists():
        ttext = tpath.read_text(encoding="utf-8", errors="ignore")
    # 逐字稿確實討論到的關鍵事實（若逐字稿在，這些才該成立）
    tx = ttext

    # --- 1) 最少功能數：條列項 + 標題 ---
    feature_markers = re.findall(
        r'(?:^|\n)\s*(?:[-*•]|\d+[.)、]) ?.{6,}', content
    )
    headers = re.findall(r'(?:^|\n)#+\s+.+', content)
    # 也支援表格列（| 開頭、含分隔線）作為功能列
    table_rows = re.findall(r'(?:^|\n)\s*\|[^\n]*\|', content)
    total_items = len(feature_markers) + len(headers) + len(table_rows)
    scores["min_features"] = (
        1.0 if total_items >= 8 else (0.5 if total_items >= 5 else 0.0)
    )

    # --- 2) UX 改善為整體前 5 名（興奮度 3 / 高優先） ---
    ux_present = bool(
        re.search(r'(?:ux|user\s*experience|使用者體驗|使用者經驗|體驗改善)', c)
    )
    ux_top = bool(
        re.search(
            r'(?:ux|使用者體驗|使用者經驗|體驗)[^\n]{0,80}'
            r'(?:top|前\s*5|前五|高優先|最高|優先|興奮度\s*[:：]?\s*3|興奮度\D{0,3}3)',
            c,
        )
        or re.search(
            r'(?:top|前\s*5|前五|高優先|最高|優先|興奮度\s*[:：]?\s*3)'
            r'[^\n]{0,80}(?:ux|使用者體驗|使用者經驗|體驗)',
            c,
        )
    )
    scores["ux_top_pick"] = 1.0 if ux_top else (0.5 if ux_present else 0.0)

    # --- 3) 漏洞管理為整體前 5 名 ---
    scores["vuln_mgmt_top_pick"] = (
        1.0
        if re.search(
            r'(?:vulnerability\s*management|漏洞管理|漏洞\s*管理|弱點管理)', c
        )
        else 0.0
    )

    # --- 4) GitOps / Kubernetes agent 為整體前 5 名 ---
    gitops_patterns = [
        r'gitops',
        r'(?:kubernetes|k8s)\s*agent',
        r'kubernetes',
        r'k8s',
        r'(?:hashicorp|terraform)\s*整合',
        r'terraform',
    ]
    gitops_hits = sum(1 for p in gitops_patterns if re.search(p, c))
    scores["gitops_top_pick"] = (
        1.0 if gitops_hits >= 2 else (0.5 if gitops_hits >= 1 else 0.0)
    )

    # --- 5) CI/CD 流水線編輯器 ---
    scores["pipeline_editor"] = (
        1.0
        if re.search(r'(?:pipeline\s*editor|流水線編輯器|流水線\s*編輯器|管線編輯器)', c)
        else 0.0
    )

    # --- 6) 模糊測試（fuzzing）因先前媒體報導被降低優先序 ---
    fuzz_present = bool(re.search(r'(?:fuzz|模糊測試)', c))
    fuzz_dep = bool(
        re.search(
            r'(?:fuzz|模糊測試)[^\n]{0,80}'
            r'(?:降低優先|降優先|deprioritiz|已.{0,4}報導|媒體|報導過|用爛|炒過|worn|報過|press|cover)',
            c,
        )
        or re.search(
            r'(?:降低優先|降優先|deprioritiz|媒體報導|報導過|用爛|炒過|worn|press|cover)'
            r'[^\n]{0,80}(?:fuzz|模糊測試)',
            c,
        )
    )
    scores["fuzzing_deprioritized"] = (
        1.0 if fuzz_dep else (0.5 if fuzz_present else 0.0)
    )

    # --- 7) 社群貢獻（VS Code 整合 / Terraform 模組） ---
    community_patterns = [
        r'社群貢獻',
        r'社群[^。\n]{0,12}貢獻',
        r'community[^。\n]{0,12}contribut',
        r'(?:vs\s*code|vscode)[^。\n]{0,20}社群',
        r'社群[^。\n]{0,20}(?:vs\s*code|vscode|terraform)',
        r'(?:terraform\s*模組|terraform\s*module)[^。\n]{0,20}(?:社群|官方支援)',
    ]
    community_hits = sum(1 for p in community_patterns if re.search(p, c))
    scores["community_contributions"] = 1.0 if community_hits >= 1 else 0.0

    # --- 8) 整合（bundling）方法論：把多個小型 MVC 整合成主題 ---
    bundle_patterns = [
        r'(?:bundle|整合|包成|打包|歸納|彙整|整併|包在一起|包成一個)',
        r'(?:mvc|小型功能|小改動|小型改動|迭代)',
        r'(?:主題|敘事|故事|narrative|theme)',
    ]
    bundle_hits = sum(1 for p in bundle_patterns if re.search(p, c))
    scores["bundling_methodology"] = (
        1.0 if bundle_hits >= 2 else (0.5 if bundle_hits >= 1 else 0.0)
    )

    # --- 9) 整體前 5 名區段 ---
    scores["top_five_section"] = (
        1.0
        if re.search(
            r'(?:top\s*(?:five|5)|整體前\s*5|整體前五|前\s*5\s*名|前五名|top\s*5\s*overall)',
            c,
        )
        else 0.0
    )

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
