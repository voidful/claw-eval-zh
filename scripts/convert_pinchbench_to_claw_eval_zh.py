#!/usr/bin/env python3
"""Convert PinchBench markdown tasks into claw-eval-zh outputs.

Produces, for each selected PinchBench task:
  * tasks_zh/<original_task_id>.md                (PinchBench markdown, Chinese)
  * tasks_claw_eval_zh/<P###zh_slug>/task.yaml    (Claw-Eval-style)
  * tasks_claw_eval_zh/<P###zh_slug>/grader.py
and a suite-wide reports/translation_coverage.json.

Translation is deterministic — NO external translation API. Human translations
live in scripts/translation_overrides.yaml; tasks without an override get a
clearly-marked scaffold (translation_status: scaffold) and are flagged in the
coverage report. See docs/task_translation_policy.md and
docs/claw_eval_zh_schema.md.

Modes:
  --dry-run            Show what would be written (default if --write absent).
  --write              Actually write files.
  --limit N            Only process the first N selected tasks.
  --tasks a,b,c        Only these task IDs (comma-separated).
  --variant zh-CN|zh-TW  Prompt variant (default zh-CN).
  --overwrite          Overwrite existing output files.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib_tasks import Task, TaskLoader  # noqa: E402
import lib_zh  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("convert")

TODO_MARKER = "<!-- TODO(zh): 待人工翻譯 -->"


class _BlockDumper(yaml.SafeDumper):
    """YAML dumper that renders multi-line strings as literal `|` blocks."""


def _str_representer(dumper: yaml.SafeDumper, data: str):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_BlockDumper.add_representer(str, _str_representer)


def dump_yaml(data: Any) -> str:
    return yaml.dump(
        data, Dumper=_BlockDumper, allow_unicode=True, sort_keys=False,
        default_flow_style=False, width=100,
    )

# --- Category mapping: PinchBench category -> (claw_category, base_tag) -------
# base_tag is overridden to "multimodal"/"multi_turn" by helpers below.
CATEGORY_MAP: Dict[str, str] = {
    "productivity": "productivity",
    "research": "research",
    "writing": "writing",
    "coding": "coding",
    "analysis": "analysis",
    "csv_analysis": "data_analysis",
    "log_analysis": "log_analysis",
    "meeting_analysis": "meeting_analysis",
    "memory": "memory",
    "skills": "skills",
    "integrations": "integrations",
}

# Heuristic keyword sets ------------------------------------------------------
# SAFETY_KEYWORDS are matched as whole words (\b…\b) to avoid substring false
# positives (e.g. "contract" inside "contractions").
SAFETY_KEYWORDS = [
    "email", "e-mail", "inbox", "gmail", "draft", "drafts", "reply",
    "finance", "financial", "stock", "stocks", "pension", "mortgage", "loan",
    "invoice", "expense", "expenses", "salary", "earnings", "valuation",
    "medical", "clinical", "pharmacy", "medication", "patient", "patients",
    "legal", "lawsuit", "contract", "contracts", "regulation", "regulations",
    "compliance", "credential", "credentials", "password", "api key",
    "api_key", "secret", "delete", "destructive",
]
# Multi-token / phrase safety markers matched as plain substrings.
SAFETY_PHRASES = ["rm -rf", "drop table", "git reset --hard"]
# Concrete live-web markers only (generic words like "today"/"latest" caused
# false positives on static blog assets).
LIVE_WEB_MARKERS = [
    "http://", "https://", "web search", "web_search", "search the web",
    "search online", "wttr.in", "polymarket", "browse the web",
]
ENGLISH_NL_TOKENS = [
    "bullish", "bearish", "upward", "downward", "increase", "decrease",
    "consecutive", "summary", "positive", "negative", "uptrend", "downtrend",
    "handling", "failed", "success", "anomal", "outlier",
]


def _word_match(blob: str, keywords: List[str]) -> bool:
    """Whole-word match for alphanumeric keywords (case-insensitive)."""
    for kw in keywords:
        if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", blob, re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def slugify_task_id(task_id: str) -> str:
    """task_csv_stock_trend -> csv_stock_trend (snake_case, no task_ prefix)."""
    slug = task_id
    if slug.startswith("task_"):
        slug = slug[len("task_"):]
    slug = re.sub(r"[^a-z0-9]+", "_", slug.lower()).strip("_")
    return slug


def claw_id_for(index: int, task_id: str) -> str:
    """Build P###zh_slug from a 0-based manifest index."""
    return f"P{index + 1:03d}zh_{slugify_task_id(task_id)}"


def extract_grading_code(task: Task) -> str:
    """Extract the python code from a task's ## Automated Checks block."""
    if not task.automated_checks:
        return ""
    match = re.search(r"```python\s*(.*?)\s*```", task.automated_checks, re.DOTALL)
    return match.group(1) if match else ""


def has_sessions(task: Task) -> bool:
    return bool(task.frontmatter.get("sessions"))


def map_category(task: Task) -> str:
    return CATEGORY_MAP.get(task.category, task.category or "general")


def is_multimodal(task: Task) -> bool:
    tid = task.task_id.lower()
    blob = (task.prompt + " " + task.expected_behavior).lower()
    return any(
        kw in tid or kw in blob
        for kw in ("image", "video", "_img", "screenshot", "multimodal", "vision")
    )


def base_tag(task: Task) -> str:
    if is_multimodal(task):
        return "multimodal"
    if has_sessions(task) or task.category == "memory":
        return "multi_turn"
    return "general"


def map_difficulty(task: Task, override: Optional[Dict[str, Any]]) -> str:
    if override and override.get("difficulty"):
        return str(override["difficulty"])
    t = task.timeout_seconds or 120
    if t <= 90:
        return "easy"
    if t <= 180:
        return "medium"
    return "hard"


def is_external_service(task: Task) -> bool:
    if task.category in ("integrations", "gws", "github"):
        return True
    prereqs = task.frontmatter.get("prerequisites", []) or []
    return any("fws" in str(p) or "gws" in str(p) for p in prereqs)


def is_safety_sensitive(task: Task) -> bool:
    if is_external_service(task):
        return True
    blob = task.task_id + " " + task.prompt + " " + task.expected_behavior
    if _word_match(blob, SAFETY_KEYWORDS):
        return True
    low = blob.lower()
    return any(p in low for p in SAFETY_PHRASES)


def needs_robustness(task: Task) -> bool:
    if has_sessions(task) or is_external_service(task) or task.category == "research":
        return True
    blob = (task.prompt + " " + task.expected_behavior).lower()
    return any(m in blob for m in LIVE_WEB_MARKERS)


def is_live_web(task: Task) -> bool:
    if task.category == "research":
        return True
    blob = (task.prompt + " " + task.expected_behavior).lower()
    return any(m in blob for m in LIVE_WEB_MARKERS)


def grader_has_english_assumption(task: Task, code: str) -> bool:
    if task.grading_type == "llm_judge":
        return False
    text = code.lower()
    return any(tok in text for tok in ENGLISH_NL_TOKENS)


def compute_primary_dimensions(task: Task) -> List[str]:
    dims = ["completion"]
    if is_safety_sensitive(task):
        dims.append("safety")
    if needs_robustness(task):
        dims.append("robustness")
    return dims


# ---------------------------------------------------------------------------
# Translation resolution
# ---------------------------------------------------------------------------
class Translation:
    """Resolved (possibly scaffolded) Chinese content for a task."""

    def __init__(self, task: Task, override: Optional[Dict[str, Any]]):
        self.task = task
        self.override = override or {}
        self.is_complete = bool(override)

    @property
    def task_name(self) -> str:
        return self.override.get("task_name") or self.task.name

    @property
    def prompt(self) -> str:
        if "prompt" in self.override:
            return str(self.override["prompt"]).strip()
        if self.task.frontmatter.get("sessions"):
            # Multi-session: the top-level prompt is a pointer, not user-facing
            # content (the real prompts live in sessions). For a translated
            # task this is complete; only scaffold if no override at all.
            if self.is_complete:
                return "本任務為多輪任務，完整對話腳本見 user_agent.sessions（task.yaml）／ frontmatter 的 sessions（markdown）。"
            return f"{TODO_MARKER}\n{self.task.prompt}"
        # scaffold: keep original prompt + TODO marker
        return f"{TODO_MARKER}\n{self.task.prompt}"

    @property
    def expected_behavior(self) -> str:
        if "expected_behavior" in self.override:
            return str(self.override["expected_behavior"]).strip()
        return f"{TODO_MARKER}\n{self.task.expected_behavior}"

    @property
    def grading_criteria(self) -> List[str]:
        if "grading_criteria" in self.override:
            return [str(c) for c in self.override["grading_criteria"]]
        return list(self.task.grading_criteria)

    @property
    def llm_judge_rubric(self) -> Optional[str]:
        if "llm_judge_rubric" in self.override:
            return str(self.override["llm_judge_rubric"]).strip()
        return self.task.llm_judge_rubric

    @property
    def grader_code(self) -> str:
        """Grader body: explicit override wins, else original extracted code."""
        if "grader_py" in self.override:
            return str(self.override["grader_py"]).strip("\n")
        return extract_grading_code(self.task)

    @property
    def prompt_untranslated(self) -> bool:
        if "prompt" in self.override:
            return False
        # Multi-session complete tasks carry their user-facing text in the
        # (translated) sessions, not the top-level prompt.
        if self.is_complete and self.task.frontmatter.get("sessions"):
            return False
        return True


# ---------------------------------------------------------------------------
# tasks_zh markdown generation
# ---------------------------------------------------------------------------
def build_zh_markdown(task: Task, tr: Translation) -> str:
    fm: Dict[str, Any] = {
        "id": task.task_id,  # keep original id for PinchBench-compatible runner
        "name": tr.task_name,
        "category": task.category,
        "grading_type": task.grading_type,
        "timeout_seconds": task.timeout_seconds,
        "language": "zh",
        "locale": "zh-TW",
        "source_task_id": task.task_id,
        "source_benchmark": "pinchbench",
        "claw_eval_id": None,  # filled by caller
        "workspace_files": task.workspace_files or [],
    }
    if task.grading_weights:
        fm["grading_weights"] = task.grading_weights
    sessions = task.frontmatter.get("sessions")
    if sessions:
        fm["multi_session"] = True
        fm["sessions"] = _translate_sessions(sessions, tr)
    return fm  # caller assembles


def _translate_sessions(sessions: List[Any], tr: Translation) -> List[Any]:
    """Translate multi-session prompts if an override provides them."""
    ov_sessions = tr.override.get("sessions")
    out: List[Any] = []
    for i, s in enumerate(sessions):
        if isinstance(s, dict):
            new = dict(s)
            if ov_sessions and i < len(ov_sessions) and ov_sessions[i].get("prompt"):
                new["prompt"] = ov_sessions[i]["prompt"]
            elif not tr.is_complete:
                new["prompt"] = f"{TODO_MARKER}\n{s.get('prompt', '')}"
            out.append(new)
        else:
            out.append(s)
    return out


def render_zh_markdown(task: Task, tr: Translation, claw_id: str) -> str:
    fm = build_zh_markdown(task, tr)
    fm["claw_eval_id"] = claw_id
    frontmatter = dump_yaml(fm).strip()

    parts: List[str] = [f"---\n{frontmatter}\n---", ""]
    parts.append(f"# {tr.task_name}")
    parts.append("")
    parts.append("## Prompt")
    parts.append("")
    if task.frontmatter.get("sessions"):
        parts.append("本任務為多輪任務，請見 frontmatter 的 `sessions` 欄位。")
    else:
        parts.append(tr.prompt)
    parts.append("")
    parts.append("## Expected Behavior")
    parts.append("")
    parts.append(tr.expected_behavior)
    parts.append("")
    parts.append("## Grading Criteria")
    parts.append("")
    for c in tr.grading_criteria:
        parts.append(f"- [ ] {c}")
    parts.append("")
    if task.grading_type in ("automated", "hybrid"):
        parts.append("## Automated Checks")
        parts.append("")
        parts.append("```python")
        parts.append(grader_body(task, tr))
        parts.append("```")
        parts.append("")
    if task.grading_type in ("llm_judge", "hybrid"):
        parts.append("## LLM Judge Rubric")
        parts.append("")
        parts.append(resolve_rubric(task, tr) or "依任務的評分標準（Grading Criteria）評估。")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Claw-Eval task.yaml generation
# ---------------------------------------------------------------------------
def _automated_component(weight: float) -> Dict[str, Any]:
    # Phase 2 schema: check.entrypoint points at grader.py. This is a
    # claw-eval-zh extension (upstream DeterministicCheck(extra="forbid") would
    # reject `entrypoint`); documented in docs/claw_eval_zh_schema.md.
    return {
        "name": "automated",
        "weight": weight,
        "check": {
            "type": "python",
            "entrypoint": "grader.py",
            "description": "確定性檢查，見 grader.py",
        },
    }


def _llm_judge_component(weight: float) -> Dict[str, Any]:
    return {
        "name": "llm_judge",
        "weight": weight,
        "check": {"type": "llm_judge", "description": "語意評分，依 judge_rubric"},
    }


def build_scoring_components(task: Task) -> List[Dict[str, Any]]:
    gt = task.grading_type
    weights = task.grading_weights or {}
    if gt == "automated":
        return [_automated_component(1.0)]
    if gt == "llm_judge":
        return [_llm_judge_component(1.0)]
    if gt == "hybrid":
        aw = float(weights.get("automated", 0.5))
        lw = float(weights.get("llm_judge", 0.5))
        return [_automated_component(aw), _llm_judge_component(lw)]
    return []


def build_fixtures(task: Task) -> List[Dict[str, str]]:
    fixtures: List[Dict[str, str]] = []
    for f in task.workspace_files or []:
        if "source" in f and "dest" in f:
            fixtures.append({"source": f["source"], "dest": f["dest"]})
    return fixtures


def _services_for(task: Task) -> List[Dict[str, Any]]:
    """Note mock services for fws/gws/github tasks (best-effort)."""
    if is_external_service(task):
        return [{"name": "fws", "note": "Google Workspace / GitHub mock (fws)"}]
    return []


def build_task_yaml(task: Task, tr: Translation, claw_id: str) -> Dict[str, Any]:
    claw_category = map_category(task)
    tag_kind = base_tag(task)
    tags = ["pinchbench", "claw-eval-zh", "zh-TW", task.category, tag_kind]
    # de-dup while preserving order
    seen = set()
    tags = [t for t in tags if t and not (t in seen or seen.add(t))]

    data: Dict[str, Any] = {}
    data["task_id"] = claw_id
    data["task_name"] = tr.task_name
    data["version"] = "0.2.0"
    data["category"] = claw_category
    data["difficulty"] = map_difficulty(task, tr.override)
    data["tags"] = tags
    data["source"] = {
        "benchmark": "pinchbench",
        "original_task_id": task.task_id,
        "original_file": f"tasks/{task.task_id}.md",
    }
    data["prompt"] = {"text": tr.prompt, "language": "zh"}
    data["tools"] = tr.override.get("tools", []) or []
    data["tool_endpoints"] = []
    data["services"] = _services_for(task)
    data["fixtures"] = build_fixtures(task)
    data["environment"] = {
        "timeout_seconds": task.timeout_seconds,
        "max_turns": len(task.frontmatter.get("sessions", [])) or 1,
    }
    data["scoring_components"] = build_scoring_components(task)
    data["safety_checks"] = []
    # expected_actions = the translated grading criteria (what the agent should do).
    data["expected_actions"] = list(tr.grading_criteria)

    sessions = task.frontmatter.get("sessions")
    if sessions:
        ua: Dict[str, Any] = {"enabled": True, "mode": "scripted", "sessions": []}
        translated = _translate_sessions(sessions, tr)
        for s in translated:
            if isinstance(s, dict):
                ua["sessions"].append({
                    "prompt": s.get("prompt", ""),
                    "new_session": bool(s.get("new_session", False)),
                })
        data["user_agent"] = ua
    else:
        data["user_agent"] = {"enabled": False}

    data["judge_rubric"] = resolve_rubric(task, tr)
    data["reference_solution"] = tr.expected_behavior
    data["primary_dimensions"] = compute_primary_dimensions(task)

    data["metadata"] = {
        "locale": "zh-TW",
        "grading_type": task.grading_type,
        "grading_weights": task.grading_weights or {},
        "workspace_files": task.workspace_files or [],
        "source_benchmark": "pinchbench",
        "translation_status": "complete" if tr.is_complete else "scaffold",
        "conversion_stage": "phase2_full_traditional_chinese",
        "notes": "Generated from PinchBench by convert_pinchbench_to_claw_eval_zh.py",
    }
    return data


# ---------------------------------------------------------------------------
# grader.py generation
# ---------------------------------------------------------------------------
GRADER_ADAPTER = '''

# --- Optional Claw-Eval adapter (only active when `claw_eval` is importable) ---
# Keeps grader.py importable offline (tests / PinchBench runner use grade()),
# while becoming a drop-in AbstractGrader subclass inside a real claw_eval
# checkout. See docs/claw_eval_zh_schema.md section 8.
PRIMARY_DIMENSIONS = __PRIMARY_DIMENSIONS__


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
'''

LLM_JUDGE_GRADE = '''def grade(transcript: list, workspace_path: str) -> dict:
    """LLM-judge-only task: no deterministic automated score.

    Semantic grading is delegated to task.yaml `judge_rubric`. Returning an
    empty dict signals "no automated component" to the runner.
    """
    return {}
'''


# Bilingual report normalization wrapper. Appended after the deterministic grade
# body so a Traditional/Simplified-Chinese report can satisfy the original
# English keyword checks. English path is byte-identical: when no report text
# file contains CJK, it passes through to the original grade() with no copy.
GRADER_NORMALIZE_WRAPPER = '''

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
'''


def resolve_rubric(task: Task, tr: Translation) -> str:
    """Judge rubric for llm_judge/hybrid tasks.

    Mirrors PinchBench behaviour: when a task has no explicit rubric (many
    hybrid log tasks), fall back to its (translated) grading criteria.
    """
    if task.grading_type not in ("llm_judge", "hybrid"):
        return ""
    if tr.llm_judge_rubric:
        return tr.llm_judge_rubric
    crit = tr.grading_criteria
    if crit:
        return (
            "依下列評分標準逐項評估（每項 0.0–1.0，最後取平均）：\n"
            + "\n".join(f"- {c}" for c in crit)
        )
    return ""


def grader_body(task: Task, tr: Translation) -> str:
    """The embeddable grade() body (used by both grader.py and markdown)."""
    if task.grading_type == "llm_judge":
        return LLM_JUDGE_GRADE
    code = tr.grader_code
    if not code:
        return LLM_JUDGE_GRADE
    return code.rstrip() + "\n" + GRADER_NORMALIZE_WRAPPER


def render_grader_py(task: Task, tr: Translation, claw_id: str) -> str:
    header = (
        f'"""Grader for {claw_id} (adapted from PinchBench task `{task.task_id}`).\n\n'
        f"Original file: tasks/{task.task_id}.md\n"
        f"grading_type: {task.grading_type}\n\n"
        "Contract (see docs/claw_eval_zh_schema.md §8):\n"
        "  * grade(transcript, workspace_path) -> dict[str, float]\n"
        "      Deterministic check, stdlib-only, importable without claw_eval.\n"
        "  * ClawEvalZhGrader (AbstractGrader subclass) — only when claw_eval\n"
        "      is importable; adapts grade() into DimensionScores.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n\n"
    )

    body = grader_body(task, tr)
    adapter = GRADER_ADAPTER.replace(
        "__PRIMARY_DIMENSIONS__", repr(compute_primary_dimensions(task))
    )
    return header + body + adapter


# ---------------------------------------------------------------------------
# Coverage report
# ---------------------------------------------------------------------------
def _translated_blob(tr: Translation) -> str:
    """User-facing translated text used for simplified/leakage scanning."""
    parts = [tr.task_name, tr.prompt, tr.expected_behavior]
    parts += list(tr.grading_criteria)
    if tr.llm_judge_rubric:
        parts.append(tr.llm_judge_rubric)
    ov_sessions = tr.override.get("sessions") or []
    for s in ov_sessions:
        if isinstance(s, dict) and s.get("prompt"):
            parts.append(str(s["prompt"]))
    return "\n".join(p for p in parts if p)


def build_coverage(
    all_tasks: List[Task],
    overrides: Dict[str, Any],
    id_map: Dict[str, str],
) -> Dict[str, Any]:
    translated, todo, untranslated_prompt = [], [], []
    english_grader, live_web, safety_sensitive = [], [], []
    multi_turn, multimodal, integration = [], [], []
    simplified_findings, english_leakage_findings = [], []
    grader_modified = []

    for task in all_tasks:
        ov = overrides.get(task.task_id)
        tr = Translation(task, ov)
        cid = id_map.get(task.task_id, "")
        entry = {"task_id": task.task_id, "claw_eval_id": cid}
        if tr.is_complete:
            translated.append(entry)
        else:
            todo.append(entry)
        if tr.prompt_untranslated:
            untranslated_prompt.append(entry)
        if grader_has_english_assumption(task, tr.grader_code):
            english_grader.append(entry)
        if is_live_web(task):
            live_web.append(entry)
        if is_safety_sensitive(task):
            safety_sensitive.append(entry)
        if has_sessions(task) or task.category == "memory":
            multi_turn.append(entry)
        if is_multimodal(task):
            multimodal.append(entry)
        if is_external_service(task):
            integration.append(entry)
        if "grader_py" in tr.override:
            grader_modified.append(entry)

        # Quality scans on the translated content (only meaningful when complete)
        if tr.is_complete:
            blob = _translated_blob(tr)
            simp = lib_zh.find_simplified(blob)
            if simp:
                simplified_findings.append({**entry, "chars": simp[:30]})
            ratio = lib_zh.english_leakage_ratio(blob)
            if ratio > 0.5:
                english_leakage_findings.append({**entry, "latin_ratio": round(ratio, 3)})

    return {
        "generated_by": "convert_pinchbench_to_claw_eval_zh.py",
        "conversion_stage": "phase2_full_traditional_chinese",
        "total_source_tasks": len(all_tasks),
        "total_tasks_zh": len(all_tasks),
        "total_claw_eval_zh": len(all_tasks),
        "fully_translated_count": len(translated),
        "manual_review_required_count": None,  # filled by caller after build_manual_review
        "tasks_with_todo": len(todo),
        "tasks_with_untranslated_english_prompt": len(untranslated_prompt),
        "tasks_with_english_output_grader_assumption": len(english_grader),
        "tasks_with_live_web_dependency": len(live_web),
        "tasks_with_safety_sensitive_domain": len(safety_sensitive),
        "simplified_char_findings": len(simplified_findings),
        "english_leakage_findings": len(english_leakage_findings),
        "grader_modified_count": len(grader_modified),
        "safety_sensitive_count": len(safety_sensitive),
        "multi_turn_count": len(multi_turn),
        "multimodal_count": len(multimodal),
        "integration_count": len(integration),
        "failed_tasks": [],
        "details": {
            "translated": translated,
            "todo": todo,
            "untranslated_english_prompt": untranslated_prompt,
            "english_output_grader_assumption": english_grader,
            "live_web_dependency": live_web,
            "safety_sensitive_domain": safety_sensitive,
            "multi_turn": multi_turn,
            "multimodal": multimodal,
            "integration": integration,
            "grader_modified": grader_modified,
            "simplified_char_findings": simplified_findings,
            "english_leakage_findings": english_leakage_findings,
        },
    }


def build_manual_review(
    all_tasks: List[Task],
    overrides: Dict[str, Any],
    id_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Build reports/manual_review_required.json entries with severities."""
    items: List[Dict[str, Any]] = []
    for task in all_tasks:
        ov = overrides.get(task.task_id)
        tr = Translation(task, ov)
        cid = id_map.get(task.task_id, "")
        reasons: List[str] = []
        severity = "low"

        if not tr.is_complete:
            reasons.append("尚未提供人工翻譯 override（scaffold）")
            severity = "high"
        if is_safety_sensitive(task):
            reasons.append("安全敏感領域（finance/medical/legal/security/email/external/credential）")
            severity = "high"
        if "grader_py" in tr.override:
            reasons.append("grader 已被修改（雙語化），需確認評分邏輯與原始一致")
            severity = "high"
        if is_live_web(task):
            reasons.append("依賴 live web / 當前事實，重跑結果可能變動")
            severity = _max_sev(severity, "high")
        if grader_has_english_assumption(task, tr.grader_code) and "grader_py" not in tr.override:
            reasons.append("grader 仰賴英文自然語言關鍵字；中文報告靠 normalize wrapper 對應，建議人工驗證")
            severity = _max_sev(severity, "medium")
        if task.grading_type in ("llm_judge", "hybrid"):
            reasons.append("含 LLM judge rubric，翻譯後主觀評分可能受影響")
            severity = _max_sev(severity, "medium")
        if has_sessions(task):
            reasons.append("多輪任務，需確認 sessions 翻譯與流程一致")
            severity = _max_sev(severity, "medium")

        if not reasons:
            continue
        items.append({
            "task_id": task.task_id,
            "claw_eval_id": cid,
            "severity": severity,
            "reasons": reasons,
            "files": [
                f"tasks_zh/{task.task_id}.md",
                f"tasks_claw_eval_zh/{cid}/task.yaml",
                f"tasks_claw_eval_zh/{cid}/grader.py",
            ],
            "suggested_action": "人工逐欄檢查翻譯語意、確認 grader 與 reference solution 一致、必要時補充 safety rubric。",
        })
    return items


_SEV_ORDER = {"low": 0, "medium": 1, "high": 2}


def _max_sev(a: str, b: str) -> str:
    return a if _SEV_ORDER.get(a, 0) >= _SEV_ORDER.get(b, 0) else b


# ---------------------------------------------------------------------------
# tasks_zh manifest (filtered mirror of tasks/manifest.yaml)
# ---------------------------------------------------------------------------
def regenerate_zh_manifest(src_manifest: Path, tasks_zh_dir: Path) -> Dict[str, Any]:
    """Build a manifest for whatever zh task md files currently exist."""
    existing = {p.stem for p in tasks_zh_dir.glob("*.md")}
    raw = yaml.safe_load(src_manifest.read_text(encoding="utf-8"))
    out: Dict[str, Any] = {}
    if "run_first" in raw:
        out["run_first"] = [t for t in raw["run_first"] if t in existing]
    if "core" in raw:
        out["core"] = [t for t in raw["core"] if t in existing]
    if "categories" in raw:
        out["categories"] = {}
        for cat, ids in raw["categories"].items():
            kept = [t for t in (ids or []) if t in existing]
            if kept:
                out["categories"][cat] = kept
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert PinchBench tasks to claw-eval-zh.")
    p.add_argument("--dry-run", action="store_true", help="Show actions, write nothing")
    p.add_argument("--write", action="store_true", help="Actually write output files")
    p.add_argument("--limit", type=int, default=None, help="Process first N selected tasks")
    p.add_argument("--tasks", type=str, default=None, help="Comma-separated task IDs")
    p.add_argument("--variant", choices=["zh-CN", "zh-TW"], default="zh-TW")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any selected task lacks a complete override")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    p.add_argument("--tasks-dir", type=Path, default=SKILL_ROOT / "tasks")
    p.add_argument("--out-zh", type=Path, default=SKILL_ROOT / "tasks_zh")
    p.add_argument("--out-claw", type=Path, default=SKILL_ROOT / "tasks_claw_eval_zh")
    p.add_argument("--overrides", type=Path, default=SCRIPT_DIR / "translation_overrides.yaml")
    p.add_argument("--overrides-dir", type=Path, default=SCRIPT_DIR / "translation_overrides",
                   help="Directory of per-batch override YAMLs (merged after --overrides)")
    p.add_argument("--coverage-out", "--report", dest="coverage_out", type=Path,
                   default=SKILL_ROOT / "reports" / "translation_coverage.json")
    p.add_argument("--manual-review-out", type=Path,
                   default=SKILL_ROOT / "reports" / "manual_review_required.json")
    return p.parse_args(argv)


def _merge_override_file(path: Path, into: Dict[str, Any]) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return
    tasks = data.get("tasks", data)
    if isinstance(tasks, dict):
        into.update(tasks)


def load_overrides(path: Path, overrides_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load overrides from a single YAML, then merge a directory of YAMLs.

    Directory entries take precedence over the single-file entries, so newly
    translated batches override the legacy smoke file.
    """
    merged: Dict[str, Any] = {}
    if path and path.exists():
        _merge_override_file(path, merged)
    if overrides_dir and overrides_dir.exists():
        for f in sorted(overrides_dir.glob("*.yaml")) + sorted(overrides_dir.glob("*.yml")):
            _merge_override_file(f, merged)
    return merged


def convert(argv: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run the conversion. Returns a summary dict (used by tests)."""
    args = parse_args(argv)
    write = args.write and not args.dry_run

    loader = TaskLoader(args.tasks_dir)
    all_tasks = loader.load_all_tasks()
    id_map = {t.task_id: claw_id_for(i, t.task_id) for i, t in enumerate(all_tasks)}
    overrides = load_overrides(args.overrides, args.overrides_dir)

    # Select subset
    selected = all_tasks
    if args.tasks:
        wanted = {s.strip() for s in args.tasks.split(",") if s.strip()}
        selected = [t for t in all_tasks if t.task_id in wanted]
    if args.limit is not None:
        selected = selected[: args.limit]

    written: List[str] = []
    skipped: List[str] = []

    for task in selected:
        claw_id = id_map[task.task_id]
        tr = Translation(task, overrides.get(task.task_id))

        zh_md_path = args.out_zh / f"{task.task_id}.md"
        claw_dir = args.out_claw / claw_id
        task_yaml_path = claw_dir / "task.yaml"
        grader_path = claw_dir / "grader.py"

        zh_md = render_zh_markdown(task, tr, claw_id)
        task_yaml = dump_yaml(build_task_yaml(task, tr, claw_id))
        grader_py = render_grader_py(task, tr, claw_id)

        status = "complete" if tr.is_complete else "scaffold"
        logger.info("• %-30s -> %s  [%s]", task.task_id, claw_id, status)

        if not write:
            continue

        for path, content in (
            (zh_md_path, zh_md),
            (task_yaml_path, task_yaml),
            (grader_path, grader_py),
        ):
            if path.exists() and not args.overwrite:
                skipped.append(str(path))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(str(path))

    # Regenerate zh manifest from whatever exists now
    if write:
        args.out_zh.mkdir(parents=True, exist_ok=True)
        manifest = regenerate_zh_manifest(args.tasks_dir / "manifest.yaml", args.out_zh)
        manifest_header = (
            "# Auto-generated by convert_pinchbench_to_claw_eval_zh.py\n"
            "# Mirrors tasks/manifest.yaml, filtered to tasks present in tasks_zh/.\n"
        )
        (args.out_zh / "manifest.yaml").write_text(
            manifest_header + dump_yaml(manifest),
            encoding="utf-8",
        )
        written.append(str(args.out_zh / "manifest.yaml"))

    coverage = build_coverage(all_tasks, overrides, id_map)
    manual_review = build_manual_review(all_tasks, overrides, id_map)
    coverage["manual_review_required_count"] = len(manual_review)
    if write:
        args.coverage_out.parent.mkdir(parents=True, exist_ok=True)
        args.coverage_out.write_text(
            json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(str(args.coverage_out))
        args.manual_review_out.parent.mkdir(parents=True, exist_ok=True)
        args.manual_review_out.write_text(
            json.dumps(
                {"generated_by": "convert_pinchbench_to_claw_eval_zh.py",
                 "count": len(manual_review), "items": manual_review},
                ensure_ascii=False, indent=2),
            encoding="utf-8")
        written.append(str(args.manual_review_out))

    logger.info(
        "\n%s: %d task(s) selected, %d file(s) written, %d skipped.",
        "WROTE" if write else "DRY-RUN",
        len(selected), len(written), len(skipped),
    )
    logger.info(
        "Coverage: %d/%d translated, %d TODO, %d simplified-findings, %d leakage.",
        coverage["fully_translated_count"], coverage["total_source_tasks"],
        coverage["tasks_with_todo"], coverage["simplified_char_findings"],
        coverage["english_leakage_findings"],
    )

    # --strict: fail if any SELECTED task is not a complete translation.
    incomplete = [t.task_id for t in selected if not Translation(t, overrides.get(t.task_id)).is_complete]
    if args.strict and incomplete:
        logger.error("STRICT: %d selected task(s) lack a complete override: %s",
                     len(incomplete), ", ".join(incomplete[:10]))
        sys.exit(1)

    return {
        "selected": [t.task_id for t in selected],
        "id_map": id_map,
        "written": written,
        "skipped": skipped,
        "coverage": coverage,
        "manual_review": manual_review,
        "incomplete": incomplete,
        "wrote": write,
    }


def main() -> None:
    convert()


if __name__ == "__main__":
    main()
