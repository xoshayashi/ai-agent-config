from __future__ import annotations

import importlib.util
from pathlib import Path
from openpyxl import Workbook


def test_build_model_wrapper_points_to_runtime() -> None:
    wrapper = Path(__file__).resolve().parents[1] / "scripts" / "build_model.py"
    spec = importlib.util.spec_from_file_location("startup_build_model_wrapper", wrapper)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    runtime_dir = module._runtime_dir()
    assert runtime_dir.name == "runtime"
    assert (runtime_dir / "build_model.py").exists()


def test_quality_gate_points_to_domain_rubric_and_strict_audit() -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
    spec = importlib.util.spec_from_file_location("startup_quality_gate", gate)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    root = module.skill_root()
    assert module.rubric_command(root)[1].endswith("emit-startup-finance-rubric.js")

    commands = module.strict_audit_commands(root, Path("/tmp"))
    assert len(commands) == 2
    assert all("--strict-audit" in command for command in commands)
    assert {command[command.index("--mode") + 1] for command in commands} == {
        "pricing",
        "cap_table",
    }
    assert module.architecture_command(root)[1].endswith("architecture_gate.py")


def test_quality_gate_parses_domain_score() -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
    spec = importlib.util.spec_from_file_location("startup_quality_gate_score", gate)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.domain_score(
        '{"metrics":[{"id":"startup-finance-domain-rubric-score","value":100}]}'
    ) == 100.0


def test_architecture_gate_enforces_openpyxl_contract() -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "architecture_gate.py"
    spec = importlib.util.spec_from_file_location("startup_architecture_gate", gate)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    root = module.skill_root()
    assert module.architecture_issues(root) == []


def test_quality_gate_recalc_error_inspector_detects_cached_errors(tmp_path: Path) -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
    spec = importlib.util.spec_from_file_location("startup_quality_gate_recalc", gate)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    wb = Workbook()
    ws = wb.active
    ws.title = "Calc"
    ws["A1"] = "#DIV/0!"
    xlsx = tmp_path / "errors.xlsx"
    wb.save(xlsx)

    assert module.formula_error_cells(xlsx) == ["Calc!A1=#DIV/0!"]


def test_quality_gate_recalc_calls_financial_integrity_audit() -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
    text = gate.read_text(encoding="utf-8")
    assert "audit_recalculated_financial_model" in text
    assert "recalculated workbook passed financial integrity audit" in text


def test_quality_gate_runs_scenario_eval() -> None:
    gate = Path(__file__).resolve().parents[1] / "scripts" / "quality_gate.py"
    spec = importlib.util.spec_from_file_location("startup_quality_gate_scenario", gate)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    root = module.skill_root()
    quick = module.scenario_eval_command(root, full=False, min_score=95)
    full = module.scenario_eval_command(root, full=True, min_score=95)

    assert quick[1].endswith("scenario_eval.py")
    assert "--full" not in quick
    assert "--full" in full
