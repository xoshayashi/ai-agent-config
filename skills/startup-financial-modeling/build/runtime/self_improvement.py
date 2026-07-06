"""Deterministic checks for SFM self-improvement reflection records."""

from __future__ import annotations

import re
from collections.abc import Mapping
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
