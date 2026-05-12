from __future__ import annotations

import importlib.util
from pathlib import Path


def test_build_model_wrapper_points_to_runtime() -> None:
    wrapper = Path(__file__).resolve().parents[1] / "scripts" / "build_model.py"
    spec = importlib.util.spec_from_file_location("startup_build_model_wrapper", wrapper)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    runtime_dir = module._runtime_dir()
    assert runtime_dir.name == "runtime"
    assert (runtime_dir / "build_model.py").exists()
