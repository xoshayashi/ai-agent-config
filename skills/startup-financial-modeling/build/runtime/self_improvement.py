"""Deterministic checks for SFM self-improvement reflection records."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

REQUIRED_FIELDS = (
    "task_type",
    "artifact_type",
    "redacted_evidence",
    "observed_failure",
    "verification_evidence",
    "root_cause_category",
    "generalized_lesson",
    "proposed_change_layer",
    "privacy_classification",
    "regression_proof",
)

VALID_LAYERS = {
    "runtime",
    "test_eval",
    "quality_gate",
    "reference_protocol",
    "skill_trigger",
    "docs_progress",
    "artifact_only",
    "no_skill_change",
}

ALLOWED_PRIVACY = {"public", "sanitized", "internal", "confidential-redacted"}

SENSITIVE_PATTERNS = {
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "named_secret": re.compile(r"(?i)\b(api[_-]?key|password|secret|token)\s*[:=]\s*\S+"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}

X_HANDLE = re.compile(r"(?<![\w/])@[A-Za-z0-9_]{1,15}\b")
X_STATUS_URL = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/[^/\s]+/status/\d+", re.I)
LONG_NUMERIC_LITERAL = re.compile(r"(?<![\w.])\d{4,}(?![\w.])")


@dataclass(frozen=True)
class PanelLens:
    """One semantic-review lens for reflection-record acceptance."""

    id: str
    name: str
    max_points: int
    min_points: int


PANEL_LENSES = (
    PanelLens("R1", "correctness and doctrine compliance", 25, 18),
    PanelLens("R2", "verification depth and honesty", 35, 25),
    PanelLens("R3", "generality and design health", 20, 14),
    PanelLens("R4", "artifact quality and readability", 20, 14),
)
PANEL_ACCEPT_SCORE = 80

VERIFICATION_TERMS = (
    "pytest",
    "quality gate",
    "quality_gates.py",
    "strict audit",
    "eval",
    "recalc",
    "render",
    "validate_reflection_record",
    "closeout_consistency",
)
WEAK_PROOF_RE = re.compile(
    r"(?i)\b(self[- ]?review|manual review only|looks good|seems fine|n/a|none)\b"
)
GENERIC_LESSON_RE = re.compile(
    r"(?i)\b(always improve|make it better|be more careful|use better judgment|high quality)\b"
)
WEAKENING_RE = re.compile(
    r"(?i)\b(skip|relax|weaken|remove|bypass|disable)\b.*\b(strict audit|privacy|source discipline|regression|human review)\b"
)


def _iter_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        out: list[str] = []
        for item in value.values():
            out.extend(_iter_text(item))
        return out
    if isinstance(value, (list, tuple, set)):
        out = []
        for item in value:
            out.extend(_iter_text(item))
        return out
    return [str(value)]


def detect_sensitive_text(value: Any) -> list[str]:
    """Return privacy findings for text that must not enter durable records."""
    findings: list[str] = []
    for text in _iter_text(value):
        for name, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"sensitive:{name}")
        if text.count("\n") >= 20:
            findings.append("raw_transcript_or_log_block")
    return sorted(set(findings))


def _contains_company_specific_lesson(record: Mapping[str, Any]) -> bool:
    lesson_text = "\n".join(
        _iter_text({
            "generalized_lesson": record.get("generalized_lesson"),
            "proposed_change": record.get("proposed_change"),
            "regression_proof": record.get("regression_proof"),
        })
    ).lower()
    company_names = [str(name).lower() for name in record.get("company_names", []) if str(name).strip()]
    return any(name and name in lesson_text for name in company_names)


def _has_instance_shaped_lesson(record: Mapping[str, Any]) -> bool:
    lesson = " ".join(_iter_text(record.get("generalized_lesson")))
    if record.get("allow_numeric_in_lesson"):
        return False
    if "JPY" in lesson or "yen" in lesson.lower() or "円" in lesson or "¥" in lesson:
        return True
    return bool(LONG_NUMERIC_LITERAL.search(lesson))


def validate_reflection_record(record: Mapping[str, Any]) -> list[str]:
    """Validate a proposed durable self-improvement reflection record."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"missing:{field}")

    layer = record.get("proposed_change_layer")
    if layer and layer not in VALID_LAYERS:
        errors.append(f"invalid_layer:{layer}")

    privacy = record.get("privacy_classification")
    if privacy and privacy not in ALLOWED_PRIVACY:
        errors.append(f"invalid_privacy:{privacy}")

    reusable = record.get("is_reusable", True)
    if reusable and layer in {"artifact_only", "no_skill_change"}:
        errors.append("reusable_record_needs_skill_layer")
    if reusable and str(record.get("regression_proof", "")).strip().lower() in {"none", "n/a", "na"}:
        errors.append("missing:regression_proof")

    for finding in detect_sensitive_text(record):
        errors.append(finding)

    if _contains_company_specific_lesson(record):
        errors.append("overfit:company_specific_lesson")
    if reusable and _has_instance_shaped_lesson(record):
        errors.append("overfit:instance_numeric_lesson")

    x_signal = record.get("public_signal_type") == "x" or record.get("x_public_signal")
    if x_signal:
        durable_text = "\n".join(
            _iter_text({
                "generalized_lesson": record.get("generalized_lesson"),
                "proposed_change": record.get("proposed_change"),
                "regression_proof": record.get("regression_proof"),
            })
        )
        if X_HANDLE.search(durable_text):
            errors.append("x_signal:handle_not_stripped")
        if X_STATUS_URL.search(durable_text):
            errors.append("x_signal:status_url_not_stripped")
        if record.get("raw_public_post"):
            errors.append("x_signal:raw_post_not_allowed")

    if record.get("changes_audit_pass_criteria") and not record.get("milestone_review"):
        errors.append("review_required:audit_or_doctrine_change")
    if record.get("changes_privacy_policy") and not record.get("milestone_review"):
        errors.append("review_required:privacy_change")

    return sorted(set(errors))


def _text_blob(record: Mapping[str, Any], fields: tuple[str, ...]) -> str:
    return "\n".join(_iter_text({field: record.get(field) for field in fields}))


def _has_verification_term(text: str) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in VERIFICATION_TERMS)


def _evidence_count(record: Mapping[str, Any]) -> int:
    raw = record.get("evidence_count")
    if isinstance(raw, int):
        return raw
    evidence = record.get("evidence_instances") or record.get("repetition_evidence")
    if isinstance(evidence, (list, tuple, set)):
        return len([item for item in evidence if str(item).strip()])
    return 0


def score_reflection_panel(record: Mapping[str, Any]) -> dict[str, Any]:
    """Score a validator-clean Reflection Record for semantic acceptance.

    The structural validator remains the first gate. This panel is the second
    gate: it rejects records that are private-safe and schema-shaped but still
    fail to prove that the proposed durable change improves the skill.
    """
    scores = {lens.id: lens.max_points for lens in PANEL_LENSES}
    findings: list[str] = []
    blockers: list[str] = []

    validator_errors = validate_reflection_record(record)
    if validator_errors:
        scores["R1"] -= 15
        blockers.append("validator_failed")
        findings.append(f"R1: structural validator errors: {validator_errors}")

    author = str(record.get("record_author", "")).strip().lower()
    reviewer = str(record.get("panel_reviewer", "")).strip().lower()
    if not reviewer:
        scores["R1"] -= 5
        blockers.append("panel:reviewer_required")
        findings.append("R1: missing independent panel_reviewer")
    elif author and author == reviewer:
        scores["R1"] -= 10
        blockers.append("panel:self_review_not_independent")
        findings.append("R1: record author and panel reviewer are the same")

    doctrine_text = _text_blob(
        record,
        (
            "observed_failure",
            "generalized_lesson",
            "proposed_change",
            "regression_proof",
        ),
    )
    if WEAKENING_RE.search(doctrine_text) and not record.get("milestone_review"):
        scores["R1"] -= 12
        blockers.append("review_required:doctrine_weakening")
        findings.append("R1: possible audit/privacy/source/regression weakening without review")

    citations = record.get("panel_evidence_citations") or record.get("evidence_citations")
    if not isinstance(citations, (list, tuple)) or len([c for c in citations if str(c).strip()]) < 2:
        scores["R2"] -= 15
        findings.append("R2: panel score lacks at least two cited evidence anchors")

    verification_text = _text_blob(record, ("verification_evidence", "regression_proof"))
    if not _has_verification_term(verification_text):
        scores["R2"] -= 12
        findings.append("R2: verification evidence does not name a concrete command, eval, gate, recalc, or render check")
    if WEAK_PROOF_RE.search(str(record.get("regression_proof", ""))):
        scores["R2"] -= 18
        blockers.append("panel:weak_regression_proof")
        findings.append("R2: regression proof is subjective or absent")
    if not record.get("broader_gate_to_rerun"):
        scores["R2"] -= 4
        findings.append("R2: no broader gate named for closeout")

    generalized_lesson = " ".join(_iter_text(record.get("generalized_lesson")))
    if len(generalized_lesson.split()) < 10 or GENERIC_LESSON_RE.search(generalized_lesson):
        scores["R3"] -= 10
        blockers.append("panel:weak_generalized_lesson")
        findings.append("R3: generalized lesson is too generic to protect a reusable invariant")

    if record.get("is_reusable", True) and _evidence_count(record) < 2:
        scores["R3"] -= 8
        blockers.append("pruning:n1_requires_deferred_candidate")
        findings.append("R3: reusable change lacks n>=2 evidence or a deferred-candidate disposition")

    root_cause = str(record.get("root_cause_category", ""))
    layer = str(record.get("proposed_change_layer", ""))
    deterministic_roots = {"runtime_bug", "eval_gap", "quality_gate_gap", "tooling_gap"}
    if root_cause in deterministic_roots and layer in {"skill_trigger", "docs_progress"}:
        scores["R3"] -= 6
        findings.append("R3: deterministic defect is proposed too high in the stack")

    if not record.get("expected_quality_effect"):
        scores["R4"] -= 6
        findings.append("R4: missing expected quality effect on the artifact or workflow")
    if record.get("adds_always_loaded_text") and layer != "skill_trigger":
        scores["R4"] -= 8
        findings.append("R4: proposed change adds always-loaded text outside a trigger-only need")
    if str(record.get("proposed_change", "")).count("\n") > 12:
        scores["R4"] -= 4
        findings.append("R4: proposed change is too bulky for a durable reflection")

    clamped = {
        lens.id: max(0, min(lens.max_points, scores[lens.id]))
        for lens in PANEL_LENSES
    }
    total = sum(clamped.values())
    for lens in PANEL_LENSES:
        if clamped[lens.id] < lens.min_points:
            blockers.append(f"panel:{lens.id}_below_minimum")

    accepted = total >= PANEL_ACCEPT_SCORE and not blockers
    return {
        "accepted": accepted,
        "total": total,
        "max_total": sum(lens.max_points for lens in PANEL_LENSES),
        "scores": clamped,
        "findings": sorted(set(findings)),
        "blockers": sorted(set(blockers)),
    }


def validate_reflection_record_for_acceptance(record: Mapping[str, Any]) -> list[str]:
    """Return all errors that block durable reflection acceptance."""
    errors = [f"validator:{err}" for err in validate_reflection_record(record)]
    panel = score_reflection_panel(record)
    if not panel["accepted"]:
        errors.extend(panel["blockers"] or ["panel:score_below_threshold"])
    return sorted(set(errors))
