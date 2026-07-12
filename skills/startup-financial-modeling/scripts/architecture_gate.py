"""Validate the Excel-generation architecture contract for this skill."""

from __future__ import annotations

import sys
import ast
from pathlib import Path


FORBIDDEN_IMPORTS = {
    "xlsxwriter": "XlsxWriter is write-only; keep it out of the core builder.",
    "xlwings": "xlwings requires a live Excel surface; keep core builds headless.",
    "win32com": "COM automation is not portable in agent/headless runs.",
    "pandas": "pandas is not the workbook composition layer for model sheets.",
}

REQUIRED_ARCHITECTURE_TOKENS = {
    "build/references/_excel_generation_architecture.md": [
        "Use `openpyxl` as the canonical workbook engine",
        "XlsxWriter",
        "Layering Contract",
        "Intermediate Representation",
        "Formula Discipline",
        "volatile functions",
    ],
    "build/runtime/source_plan_builder.py": [
        "class LayoutSpec",
        "SOURCE_PLAN_SHEETS",
        "def _write_period_header",
        "def _label",
        "def _write_values",
    ],
    "build/runtime/workbook_spec.py": [
        "class WorkbookSpec",
        "class SheetSpec",
        "class RowSpec",
        "class CellSpec",
        "class FormulaExpr",
        "class StyleRole",
        "def render_workbook_spec",
    ],
    "build/runtime/build_model.py": [
        "MODE_BUNDLE_SEEDS",
        "SHEET_DEPENDENCIES",
        "def resolve_bundle",
        "def audit_workbook",
        "def audit_recalculated_financial_model",
        "VOLATILE_FORMULA_RE",
    ],
    "build/runtime/ib_format.py": [
        "IB_HARD_INPUT",
        "apply_semantic_fill_span",
        "apply_semantic_border_span",
        "set_workbook_default_font",
    ],
    "scripts/requirements.txt": [
        "openpyxl>=3.1",
    ],
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _python_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for base in (root / "build" / "runtime", root / "scripts"):
        paths.extend(path for path in base.glob("*.py") if path.name != "architecture_gate.py")
    return sorted(paths)


def _import_violations(root: Path) -> list[str]:
    issues: list[str] = []
    for path in _python_files(root):
        try:
            tree = ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            issues.append(f"{path.relative_to(root)}: could not parse Python AST: {exc}")
            continue
        for node in ast.walk(tree):
            package = ""
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                package = name.split(".")[0].lower()
                if not package:
                    continue
                if package in FORBIDDEN_IMPORTS:
                    rel = path.relative_to(root)
                    issues.append(f"{rel}: forbidden import `{package}`. {FORBIDDEN_IMPORTS[package]}")
    return issues


def _required_token_violations(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, tokens in REQUIRED_ARCHITECTURE_TOKENS.items():
        path = root / rel_path
        if not path.exists():
            issues.append(f"{rel_path}: required architecture file is missing")
            continue
        text = _read(path)
        for token in tokens:
            if token not in text:
                issues.append(f"{rel_path}: missing architecture token {token!r}")
    return issues


def architecture_issues(root: Path | None = None) -> list[str]:
    root = root or skill_root()
    return [*_required_token_violations(root), *_import_violations(root)]


def main() -> int:
    root = skill_root()
    issues = architecture_issues(root)
    if issues:
        for issue in issues:
            print(f"[architecture] {issue}", file=sys.stderr)
        return 2
    print("[architecture] Excel-generation architecture gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
