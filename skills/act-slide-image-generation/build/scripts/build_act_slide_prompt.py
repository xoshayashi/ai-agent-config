#!/usr/bin/env python3
"""Build concise ACT slide planning and gpt-image-2 generation contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

IMAGE_MODEL = "gpt-image-2"
ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = json.loads((ROOT / "references" / "canonical-geometry.json").read_text(encoding="utf-8"))
DEFAULT_DESIGN_TOKENS_PATH = ROOT / "references" / "design-tokens.json"
ALLOWED_SIZES = {"2048x1152"}
MAX_GENERATION_CONTRACT_BYTES = 6144
UNRESOLVED_COMPOSITION = "UNRESOLVED - describe the content-led composition intent"
UNRESOLVED_ALIGNMENT = "UNRESOLVED - describe the composition-specific Grid/Flex nesting intent"


def validate_size(size: str) -> str:
    try:
        width, height = map(int, size.lower().split("x", 1))
    except ValueError as exc:
        raise SystemExit(f"Invalid --size '{size}'. Use 2048x1152.") from exc
    if width % 16 or height % 16:
        raise SystemExit(f"Invalid --size '{size}'. gpt-image-2 requires both edges to be multiples of 16.")
    normalized = f"{width}x{height}"
    if normalized not in ALLOWED_SIZES:
        raise SystemExit(f"Invalid --size '{normalized}'. This ACT slide skill only supports 16:9 gpt-image-2 sizes: 2048x1152.")
    return normalized


def read_brief(path: str | None) -> str:
    if not path:
        return "[paste or summarize the user brief here]"
    return Path(path).read_text(encoding="utf-8").strip()


def read_design_tokens(path: str | None) -> dict:
    token_path = Path(path) if path else DEFAULT_DESIGN_TOKENS_PATH
    try:
        tokens = json.loads(token_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid --design-tokens: {exc}") from exc
    required_roles = {
        "slide_background", "main_message", "sub_message", "body_primary", "body_secondary", "footer",
        "separator", "neutral_panel", "structural_panel", "primary_accent", "primary_accent_deep",
        "positive_state", "deemphasized_state", "single_focus_fill", "single_focus_stroke", "secondary_accent", "text_on_dark",
    }
    colors, roles = tokens.get("colors", {}), tokens.get("role_mapping", {})
    usage = tokens.get("usage", {})
    if tokens.get("schema_version") != 1 or not isinstance(colors, dict) or not colors or not required_roles.issubset(roles):
        raise SystemExit("Invalid --design-tokens; provide the complete ACT color palette and semantic role mapping.")
    if any(not isinstance(value, str) or not value.startswith("#") or len(value) != 7 for value in colors.values()):
        raise SystemExit("Invalid --design-tokens; every color is a six-digit hex value.")
    if any(role not in colors for role in roles.values()):
        raise SystemExit("Invalid --design-tokens; every semantic role maps to a registered color token.")
    if usage != {"single_focus_per_slide": True, "flat_fills": True, "gradient": "none", "shadow": "none"}:
        raise SystemExit("Invalid --design-tokens; usage keeps one focus, flat fills, and quiet depth treatment.")
    return tokens


def resolve_color_roles(design_tokens: dict) -> dict[str, str]:
    colors, roles = design_tokens["colors"], design_tokens["role_mapping"]
    return {role: colors[token_name] for role, token_name in roles.items()}


def rectangles_overlap(a: dict, b: dict) -> bool:
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


def rectangle_union_area(rectangles: list[dict]) -> int:
    xs = sorted({rect["x"] for rect in rectangles} | {rect["x"] + rect["w"] for rect in rectangles})
    area = 0
    for left, right in zip(xs, xs[1:]):
        intervals = sorted((rect["y"], rect["y"] + rect["h"]) for rect in rectangles if rect["x"] < right and rect["x"] + rect["w"] > left)
        covered = 0
        if intervals:
            start, end = intervals[0]
            for next_start, next_end in intervals[1:]:
                if next_start > end:
                    covered += end - start
                    start, end = next_start, next_end
                else:
                    end = max(end, next_end)
            covered += end - start
        area += (right - left) * covered
    return area


def read_layout_plan(path: str | None, mode: str, design_tokens: dict) -> dict | None:
    if mode not in {"single-slide-image", "repair"}:
        return None
    if not path:
        raise SystemExit("Provide --layout-plan with a validated Grid/Flex layout plan before generation or repair.")
    try:
        plan = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid --layout-plan: {exc}") from exc
    required = {
        "slide_argument_plan", "closure_matrix", "footer_mode", "source_plan", "message_box_plan", "header_furniture_plan", "content_atom_registry", "model_fit_plan", "clarity_plan", "surface_plan", "tone_plan", "layout_tree", "grid_plan", "flex_plan", "component_geometry_plan",
        "structural_rule_plan", "connector_plan", "rigidity_plan", "occupancy_plan", "quiet_region",
    }
    absent = sorted(required - set(plan))
    if absent:
        raise SystemExit("Invalid --layout-plan; required sections: " + ", ".join(sorted(required)))
    if plan["footer_mode"] not in {"absent", "present"}:
        raise SystemExit("Invalid --layout-plan; footer_mode is absent or present.")
    header_furniture = plan["header_furniture_plan"]
    if header_furniture != {
        "surface": "uninterrupted_canvas",
        "visible_component_ids": ["header_h1", "header_subtitle"],
        "visible_geometry_count": 0,
    }:
        raise SystemExit("Invalid --layout-plan; header_furniture_plan uses uninterrupted canvas with only header_h1 and header_subtitle visible.")
    model_fit = plan["model_fit_plan"]
    required_model_fit = {
        "governing_thought_count", "primary_topology_count", "visual_anchor_count", "major_region_count",
        "hierarchy_depth", "repeated_module_max", "reading_path_steps", "visible_string_count",
        "microtext_component_count", "reference_image_count", "generation_batch_size",
        "copy_capacity_status", "render_feasibility", "prompt_compilation_basis",
    }
    if not required_model_fit.issubset(model_fit):
        raise SystemExit("Invalid --layout-plan; model_fit_plan requires the complete image-model complexity and copy-capacity contract.")
    if (model_fit["governing_thought_count"], model_fit["primary_topology_count"], model_fit["visual_anchor_count"]) != (1, 1, 1):
        raise SystemExit("Invalid --layout-plan; use one governing thought, one primary topology, and one visual anchor.")
    if not 2 <= model_fit["major_region_count"] <= 4 or not 2 <= model_fit["hierarchy_depth"] <= 3:
        raise SystemExit("Invalid --layout-plan; model-fit composition uses 2-4 major regions and hierarchy depth 2-3.")
    if not 2 <= model_fit["repeated_module_max"] <= 5 or not 2 <= model_fit["reading_path_steps"] <= 6:
        raise SystemExit("Invalid --layout-plan; repeated modules and reading-path steps stay inside the approved production ranges.")
    if not 1 <= model_fit["visible_string_count"] <= 18 or model_fit["microtext_component_count"] != 0:
        raise SystemExit("Invalid --layout-plan; copy capacity uses 1-18 visible strings and zero microtext components.")
    if not 0 <= model_fit["reference_image_count"] <= 2 or model_fit["generation_batch_size"] != 1:
        raise SystemExit("Invalid --layout-plan; use a small labeled reference set and generate one slide per call.")
    if model_fit["copy_capacity_status"] != "approved" or model_fit["render_feasibility"] != "approved" or model_fit["prompt_compilation_basis"] != "2048x1152":
        raise SystemExit("Invalid --layout-plan; approve copy capacity and render feasibility, then compile on the 2048x1152 basis.")
    atoms = plan["content_atom_registry"].get("atoms", [])
    atom_required = {"id", "exact_text", "semantic_role", "component_id", "anchor_line", "baseline_step", "max_lines", "expected_occurrences"}
    if not atoms or any(not atom_required.issubset(atom) for atom in atoms):
        raise SystemExit("Invalid --layout-plan; content_atom_registry binds every visible string to one component and line budget.")
    if len(atoms) != model_fit["visible_string_count"] or len({atom["id"] for atom in atoms}) != len(atoms):
        raise SystemExit("Invalid --layout-plan; visible-string count matches unique content atoms.")
    if any(not atom["exact_text"].strip() or atom["expected_occurrences"] != 1 or atom["max_lines"] not in {1, 2} for atom in atoms):
        raise SystemExit("Invalid --layout-plan; each content atom has exact copy, one occurrence, and a one- or two-line budget.")
    argument = plan["slide_argument_plan"]
    required_argument = {
        "question", "claim", "evidence_atom_ids", "warrant", "implication", "action_or_transition",
        "inputs_from_prior", "new_contribution", "outputs_to_next", "decision_impact",
        "strongest_alternative", "boundary", "owner", "timing", "success_measure", "open_items",
    }
    if not isinstance(argument, dict) or set(argument) != required_argument:
        raise SystemExit("Invalid --layout-plan; slide_argument_plan contains the complete question, claim, evidence, warrant, implication, transition, dependency, alternative, boundary, and open-item contract.")
    text_fields = required_argument - {"evidence_atom_ids", "open_items"}
    if any(not isinstance(argument[field], str) or not argument[field].strip() for field in text_fields):
        raise SystemExit("Invalid --layout-plan; every slide argument field is explicit and non-empty.")
    atom_ids = {atom["id"] for atom in atoms}
    if not isinstance(argument["evidence_atom_ids"], list) or not argument["evidence_atom_ids"] or not set(argument["evidence_atom_ids"]).issubset(atom_ids):
        raise SystemExit("Invalid --layout-plan; evidence_atom_ids bind the slide claim to registered visible evidence atoms.")
    header_atoms = {component_id: [atom for atom in atoms if atom["component_id"] == component_id] for component_id in ("header_h1", "header_subtitle")}
    if any(len(bound_atoms) != 1 for bound_atoms in header_atoms.values()):
        raise SystemExit("Invalid --layout-plan; header inventory binds exactly one text atom to header_h1 and header_subtitle.")
    h1_text = header_atoms["header_h1"][0]["exact_text"]
    if argument["claim"] != h1_text or argument["new_contribution"] != argument["claim"]:
        raise SystemExit("Invalid --layout-plan; the action title, slide claim, and new contribution are one proposition.")
    if not isinstance(argument["open_items"], list) or any(
        not isinstance(item, dict)
        or set(item) != {"text", "owner", "due_date"}
        or any(not isinstance(item[key], str) or not item[key].strip() for key in item)
        for item in argument["open_items"]
    ):
        raise SystemExit("Invalid --layout-plan; every decision-critical open item has explicit text, owner, and due date.")
    closure = plan["closure_matrix"]
    required_closure = {
        "load_bearing_claim_coverage", "evidence_to_claim_binding", "adjacent_slide_transition_coverage",
        "final_action_coverage", "open_item_owner_due_coverage", "unstated_decision_critical_premise_count",
        "unused_load_bearing_conclusion_count", "unresolved_contradiction_count", "rows",
    }
    if not isinstance(closure, dict) or set(closure) != required_closure:
        raise SystemExit("Invalid --layout-plan; closure_matrix contains every coverage, contradiction, premise, conclusion, and row gate.")
    coverage_fields = {
        "load_bearing_claim_coverage", "evidence_to_claim_binding", "adjacent_slide_transition_coverage",
        "final_action_coverage", "open_item_owner_due_coverage",
    }
    zero_fields = {
        "unstated_decision_critical_premise_count", "unused_load_bearing_conclusion_count", "unresolved_contradiction_count",
    }
    if any(closure[field] != 1.0 for field in coverage_fields) or any(closure[field] != 0 for field in zero_fields):
        raise SystemExit("Invalid --layout-plan; argument closure coverage is 100% and premise, unused-conclusion, and contradiction counts are zero.")
    required_rows = {"claim", "evidence", "warrant", "implication", "alternative", "boundary", "owner", "timing", "success_measure"}
    allowed_statuses = {"resolved", "explicit_assumption", "open_with_owner_and_due_date"}
    rows = closure["rows"]
    if not isinstance(rows, list) or len(rows) != len(required_rows) or any(not isinstance(row, dict) for row in rows) or {row.get("field") for row in rows} != required_rows or any(
        set(row) != {"field", "status"} or row["status"] not in allowed_statuses for row in rows
    ):
        raise SystemExit("Invalid --layout-plan; closure_matrix rows resolve claim, evidence, warrant, implication, alternative, boundary, owner, timing, and success measure.")
    row_status = {row["field"]: row["status"] for row in rows}
    if any(row_status[field] == "resolved" and not argument[field].strip() for field in ("owner", "timing", "success_measure")):
        raise SystemExit("Invalid --layout-plan; resolved owner, timing, and success-measure rows bind to explicit argument values.")
    has_open_row = any(status == "open_with_owner_and_due_date" for status in row_status.values())
    if has_open_row != bool(argument["open_items"]):
        raise SystemExit("Invalid --layout-plan; open closure rows and owner/due-date open_items are present together.")
    if any(atom["anchor_line"] not in range(1, 18) or (atom["component_id"] != "footer_master" and atom["baseline_step"] % GEOMETRY["grid"]["unit_px"]) for atom in atoms):
        raise SystemExit("Invalid --layout-plan; every content atom has one grid anchor and one 8px body baseline; the footer atom uses its canonical centered baseline.")
    for component_id, geometry_key in (("header_h1", "h1"), ("header_subtitle", "subtitle")):
        atom = header_atoms[component_id][0]
        if atom["anchor_line"] != 1 or atom["baseline_step"] != GEOMETRY["header"][geometry_key]["baseline_y"] or atom["max_lines"] != 1:
            raise SystemExit("Invalid --layout-plan; header atoms use the canonical left anchor, baseline, and one-line budget.")
    source_plan = plan["source_plan"]
    required_source = {"visibility", "reference_class", "publication_title", "locator", "source_line", "annotations"}
    if not required_source.issubset(source_plan) or source_plan["visibility"] not in {"none", "visible"}:
        raise SystemExit("Invalid --layout-plan; source_plan declares visibility, reference class, publication title, locator, and source line.")
    annotations = source_plan.get("annotations")
    if not isinstance(annotations, list) or len(annotations) > 2 or any(not isinstance(item, str) or not item.startswith(("Assumption: ", "Note: ")) for item in annotations):
        raise SystemExit("Invalid --layout-plan; footer annotations use up to one Assumption and one Note entry with exact prefixes.")
    if len({item.split(":", 1)[0] for item in annotations}) != len(annotations) or [item.split(":", 1)[0] for item in annotations] != sorted([item.split(":", 1)[0] for item in annotations], key=lambda value: {"Assumption": 0, "Note": 1}[value]):
        raise SystemExit("Invalid --layout-plan; footer annotations appear once each in Assumption then Note order.")
    footer_atoms = [atom for atom in atoms if atom["semantic_role"] == "footer" or atom["component_id"] == "footer_master"]
    if source_plan["visibility"] == "none":
        if source_plan["reference_class"] != "none" or source_plan["publication_title"] or source_plan["locator"] or source_plan["source_line"] != "none":
            raise SystemExit("Invalid --layout-plan; source visibility none keeps external-reference fields empty and source_line none.")
    else:
        locator = source_plan["locator"].strip()
        traceable_prefixes = ("https://", "doi:", "statute:", "dataset:")
        if plan["footer_mode"] != "present" or source_plan["reference_class"] != "external_publication":
            raise SystemExit("Invalid --layout-plan; a visible source pairs with footer_mode present and reference_class external_publication.")
        if not source_plan["publication_title"].strip() or not locator.lower().startswith(traceable_prefixes):
            raise SystemExit("Invalid --layout-plan; a visible source requires a publication title and a traceable HTTPS, DOI, statute, or public-dataset locator.")
        if not source_plan["source_line"].startswith("Source: ") or source_plan["publication_title"] not in source_plan["source_line"]:
            raise SystemExit("Invalid --layout-plan; visible source text starts exactly with 'Source: ' and names the registered external publication.")
    footer_entries = ([] if source_plan["visibility"] == "none" else [source_plan["source_line"]]) + annotations
    if not footer_entries:
        if plan["footer_mode"] != "absent" or footer_atoms:
            raise SystemExit("Invalid --layout-plan; an empty provenance footer uses footer_mode absent and zero footer atoms.")
    else:
        expected_text = "   ".join(footer_entries)
        if plan["footer_mode"] != "present" or len(footer_atoms) != 1 or footer_atoms[0]["exact_text"] != expected_text:
            raise SystemExit("Invalid --layout-plan; one footer atom combines Source, Assumption, and Note entries in canonical order.")
        footer_atom = footer_atoms[0]
        if footer_atom["component_id"] != "footer_master" or not 1 <= footer_atom["max_lines"] <= GEOMETRY["footer"]["max_lines"]:
            raise SystemExit("Invalid --layout-plan; the footer atom binds to footer_master with a one- or two-line budget.")
        expected_baseline = GEOMETRY["footer"]["baseline_y_by_max_lines"][str(footer_atom["max_lines"])][0]
        if footer_atom["baseline_step"] != expected_baseline:
            raise SystemExit("Invalid --layout-plan; the footer atom uses the canonical centered baseline for its line budget.")
    message_box_plan = plan["message_box_plan"]
    if set(message_box_plan) != {"boxes"} or not isinstance(message_box_plan["boxes"], list):
        raise SystemExit("Invalid --layout-plan; message_box_plan uses the explicit shape {'boxes': []} when no message box is present.")
    if plan["footer_mode"] == "present" and message_box_plan["boxes"]:
        raise SystemExit("Invalid --layout-plan; footer-present layouts reserve the dedicated clear body envelope and use no canonical bottom message box.")
    clarity = plan["clarity_plan"]
    required_clarity = {"primary_relationship", "visual_grammar", "major_region_count", "region_roles", "start_region_id", "landing_region_id", "reading_path", "connector_count", "connector_set_count", "visual_anchor_count", "emphasis_system_count", "outer_frame_role", "redundant_encoding_count", "mark_language_consistency", "region_internal_distribution_consistency", "thumbnail_path_status"}
    if not required_clarity.issubset(clarity):
        raise SystemExit("Invalid --layout-plan; clarity_plan requires the complete one-relationship reading-path contract.")
    allowed_relationships = {"comparison", "sequence", "hierarchy", "transformation", "loop"}
    if clarity["primary_relationship"] not in allowed_relationships or clarity["visual_grammar"] not in allowed_relationships:
        raise SystemExit("Invalid --layout-plan; select one comparison, sequence, hierarchy, transformation, or loop grammar.")
    if clarity["primary_relationship"] != clarity["visual_grammar"] or clarity["major_region_count"] != model_fit["major_region_count"]:
        raise SystemExit("Invalid --layout-plan; one visual grammar matches the primary relationship and region count.")
    role_ids = [role.get("id") for role in clarity["region_roles"]]
    if len(role_ids) != clarity["major_region_count"] or len(role_ids) != len(set(role_ids)) or clarity["start_region_id"] not in role_ids or clarity["landing_region_id"] not in role_ids:
        raise SystemExit("Invalid --layout-plan; region roles are unique and include the explicit start and landing.")
    if not 2 <= len(clarity["reading_path"]) <= 6 or clarity["reading_path"][0] != clarity["start_region_id"] or clarity["reading_path"][-1] != clarity["landing_region_id"]:
        raise SystemExit("Invalid --layout-plan; reading_path preserves the declared start and landing.")
    if len(clarity["reading_path"]) != model_fit["reading_path_steps"]:
        raise SystemExit("Invalid --layout-plan; model-fit reading-path steps equal the registered clarity path length.")
    if clarity["connector_set_count"] != 1 or clarity["visual_anchor_count"] != 1 or clarity["emphasis_system_count"] != 1 or clarity["redundant_encoding_count"] != 0:
        raise SystemExit("Invalid --layout-plan; use one connector set, one anchor, one emphasis system, and zero redundant encodings.")
    if clarity["mark_language_consistency"] < 0.95 or clarity["region_internal_distribution_consistency"] < 0.90:
        raise SystemExit("Invalid --layout-plan; peer regions share one mark language and balanced internal distribution.")
    if clarity["primary_relationship"] != "loop" and clarity["connector_count"] > clarity["major_region_count"] - 1:
        raise SystemExit("Invalid --layout-plan; one-way compositions use at most region-count minus one connectors.")
    if clarity["outer_frame_role"] not in {"semantic_containment", "none"} or clarity["thumbnail_path_status"] != "approved":
        raise SystemExit("Invalid --layout-plan; outer frame has a semantic role or none, and the thumbnail path is approved.")
    surface = plan["surface_plan"]
    required_surface = {"top_level_surface_count", "major_radius_px", "peer_radius_px", "radius_consistency_score", "grouping_methods"}
    if not required_surface.issubset(surface) or not 2 <= surface["top_level_surface_count"] <= 4:
        raise SystemExit("Invalid --layout-plan; surface_plan uses 2-4 coordinated top-level surfaces.")
    if surface["major_radius_px"] not in {8, 12} or surface["peer_radius_px"] not in {4, 8} or surface["radius_consistency_score"] < 0.95:
        raise SystemExit("Invalid --layout-plan; surface radii use the ACT softness tokens with >=0.95 peer consistency.")
    if "shared_axes" not in surface["grouping_methods"] or not ({"repeated_spacing", "connectors"} & set(surface["grouping_methods"])):
        raise SystemExit("Invalid --layout-plan; coordinated surfaces group through shared axes plus spacing or connectors.")
    tone = plan["tone_plan"]
    required_tone = {"ambient_role", "region_role", "structural_role", "focus_role", "semantic_tone_count", "focal_tone_count", "tone_role_consistency", "flat_tonal_layers", "role_assignments"}
    expected_tones = {"ambient_role": "slide_background", "region_role": "neutral_panel", "structural_role": "structural_panel", "focus_role": "single_focus_fill"}
    if not required_tone.issubset(tone) or any(tone[key] != value for key, value in expected_tones.items()):
        raise SystemExit("Invalid --layout-plan; tone_plan uses stable semantic design-token roles.")
    if not 3 <= tone["semantic_tone_count"] <= 4 or tone["focal_tone_count"] != 1 or tone["tone_role_consistency"] < 0.95 or tone["flat_tonal_layers"] is not True:
        raise SystemExit("Invalid --layout-plan; luminous tones use 3-4 semantic roles, one focus, >=0.95 consistency, and flat layers.")
    assignments = tone["role_assignments"]
    expected_roles = {"ambient", "lifted", "structural", "focal"}
    if not isinstance(assignments, list) or {item.get("role") for item in assignments} != expected_roles or len(assignments) != 4:
        raise SystemExit("Invalid --layout-plan; luminous tone roles map ambient, lifted, structural, and focal exactly once.")
    if any(item.get("target_type") not in {"canvas", "region", "content_atom"} or not item.get("target_id") for item in assignments):
        raise SystemExit("Invalid --layout-plan; every luminous tone role binds to one canvas, region, or content atom target.")
    ambient = next(item for item in assignments if item["role"] == "ambient")
    if ambient != {"role": "ambient", "target_type": "canvas", "target_id": "canvas"}:
        raise SystemExit("Invalid --layout-plan; ambient light binds to the canvas target.")
    nodes = plan["layout_tree"].get("nodes", [])
    ids = [node.get("id") for node in nodes]
    if not nodes or any(not node_id for node_id in ids) or len(ids) != len(set(ids)):
        raise SystemExit("Invalid --layout-plan; layout_tree nodes require unique ids.")
    node_ids = set(ids)
    if any(role_id not in node_ids for role_id in role_ids):
        raise SystemExit("Invalid --layout-plan; clarity region roles reference registered layout-tree nodes.")
    atom_ids = {atom["id"] for atom in atoms}
    for assignment in assignments:
        target_type, target_id = assignment["target_type"], assignment["target_id"]
        if target_type == "region" and target_id not in node_ids:
            raise SystemExit("Invalid --layout-plan; luminous region targets reference registered layout-tree nodes.")
        if target_type == "content_atom" and target_id not in atom_ids:
            raise SystemExit("Invalid --layout-plan; luminous content targets reference registered content atoms.")
    node_by_id = {node["id"]: node for node in nodes}
    roots = [node for node in nodes if node.get("parent_id") is None]
    if len(roots) != 1 or roots[0].get("layout") != "grid":
        raise SystemExit("Invalid --layout-plan; use exactly one Grid root.")
    for node in nodes:
        if node.get("layout") not in {"grid", "flex", "item"}:
            raise SystemExit("Invalid --layout-plan; every node layout is grid, flex, or item.")
        if node.get("parent_id") is not None and node.get("parent_id") not in node_ids:
            raise SystemExit("Invalid --layout-plan; every non-root node references one declared parent.")
    for node in nodes:
        visited = {node["id"]}
        cursor = node
        while cursor.get("parent_id") is not None:
            parent_id = cursor["parent_id"]
            if parent_id in visited:
                raise SystemExit("Invalid --layout-plan; layout_tree uses an acyclic parent graph.")
            visited.add(parent_id)
            cursor = node_by_id[parent_id]
    grid = plan["grid_plan"]
    geometry_grid = GEOMETRY["grid"]
    if any(grid.get(key) != geometry_grid[key] for key in ("columns", "track_px", "gutter_px")):
        raise SystemExit("Invalid --layout-plan; parent grid must use 16 columns, 73px tracks, and 24px gutters.")
    regions = grid.get("regions", [])
    if not regions or any(region.get("id") not in node_ids for region in regions):
        raise SystemExit("Invalid --layout-plan; grid regions must reference registered nodes.")
    for region in regions:
        if not (1 <= region.get("column_start", 0) < region.get("column_end", 0) <= 17):
            raise SystemExit("Invalid --layout-plan; grid regions use integer line spans within 1..17.")
        if any(not isinstance(region.get(key), int) for key in ("column_start", "column_end", "row_start", "row_end")):
            raise SystemExit("Invalid --layout-plan; grid line and baseline positions use integers.")
        if region["row_start"] % geometry_grid["unit_px"] != 0 or region["row_end"] % geometry_grid["unit_px"] != 0:
            raise SystemExit("Invalid --layout-plan; planned row positions align exactly to the 8px baseline.")
    shell = GEOMETRY["outer_shell"]
    body = GEOMETRY["body"]
    envelope = body["target_envelope_without_footer"] if plan["footer_mode"] == "absent" else body["target_envelope_with_footer"]
    body_top, body_bottom = envelope["top"], envelope["bottom"]
    region_boxes: dict[str, dict[str, int]] = {}
    for region in regions:
        span = region["column_end"] - region["column_start"]
        x = shell["x"] + (region["column_start"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"])
        width = span * geometry_grid["track_px"] + (span - 1) * geometry_grid["gutter_px"]
        box = {"x": x, "y": region["row_start"], "w": width, "h": region["row_end"] - region["row_start"]}
        if box["y"] < body_top or box["y"] + box["h"] > body_bottom or box["h"] <= 0:
            raise SystemExit("Invalid --layout-plan; grid regions stay inside the selected footer-mode body band.")
        region_boxes[region["id"]] = box

    component_plan = plan["component_geometry_plan"]
    components = component_plan.get("components", [])
    component_required = {"id", "type", "parent_id", "bounds", "left_anchor_line", "right_anchor_line", "top_baseline_step", "bottom_baseline_step", "role", "peer_group"}
    if not components or any(not component_required.issubset(component) for component in components):
        raise SystemExit("Invalid --layout-plan; component_geometry_plan registers every meaningful component with bounds, anchors, baselines, role, and peer group.")
    component_ids = [component["id"] for component in components]
    if len(component_ids) != len(set(component_ids)) or any(component_id not in node_ids for component_id in component_ids):
        raise SystemExit("Invalid --layout-plan; component ids are unique registered layout-tree nodes.")
    component_by_id = {component["id"]: component for component in components}
    atom_by_id = {atom["id"]: atom for atom in atoms}
    box_tokens = GEOMETRY["message_box"]
    registered_box_ids: set[str] = set()
    for box in message_box_plan["boxes"]:
        required_box = {"component_id", "atom_id", "line_count", "line_height_px", "vertical_padding_px", "horizontal_padding_px", "height_px", "surface_role", "icon_children"}
        if not required_box.issubset(box):
            raise SystemExit("Invalid --layout-plan; every message box declares component, text atom, line metrics, padding tokens, height, surface role, and icon children.")
        component_id, atom_id = box["component_id"], box["atom_id"]
        if component_id != "message_box":
            raise SystemExit("Invalid --layout-plan; the canonical message-box component id is message_box.")
        if component_id in registered_box_ids or component_id not in component_by_id or atom_id not in atom_by_id:
            raise SystemExit("Invalid --layout-plan; message-box ids are unique and reference registered components and text atoms.")
        registered_box_ids.add(component_id)
        component, atom = component_by_id[component_id], atom_by_id[atom_id]
        if component["type"] != "message_box" or component["role"] != "message_box" or atom["component_id"] != component_id or atom["semantic_role"] not in {"message_box", "takeaway"}:
            raise SystemExit("Invalid --layout-plan; a message box is a dedicated text component bound to one message-box or takeaway atom.")
        if box["line_count"] not in box_tokens["allowed_line_counts"] or atom["max_lines"] != box["line_count"]:
            raise SystemExit("Invalid --layout-plan; message-box line count matches the registered one-line text atom.")
        if box["line_height_px"] != box_tokens["line_height_px"] or box["vertical_padding_px"] not in box_tokens["vertical_padding_tokens_px"] or box["horizontal_padding_px"] not in box_tokens["horizontal_padding_tokens_px"]:
            raise SystemExit("Invalid --layout-plan; message-box line height and padding use canonical ACT tokens.")
        expected_height = box["line_count"] * box["line_height_px"] + 2 * box["vertical_padding_px"]
        allowed_heights = box_tokens["height_by_line_count_px"][str(box["line_count"])]
        if box["height_px"] != expected_height or box["height_px"] not in allowed_heights or component["bounds"]["h"] != box["height_px"]:
            raise SystemExit(f"Invalid --layout-plan; message-box height is derived from line count, {box_tokens['line_height_px']}px line height, and vertical padding, then matches component geometry.")
        if box["surface_role"] not in box_tokens["allowed_surface_roles"]:
            raise SystemExit("Invalid --layout-plan; message-box surface uses the registered focal tone role.")
        expected_bounds = {"x": box_tokens["x"], "y": box_tokens["y"], "w": box_tokens["width"], "h": box["height_px"]}
        if component["bounds"] != expected_bounds:
            raise SystemExit("Invalid --layout-plan; message-box bounds match the canonical full-width master.")
        icon_atoms = [candidate for candidate in atoms if candidate["component_id"] == component_id and candidate["semantic_role"] == "icon"]
        icon_components = [candidate for candidate in components if candidate.get("parent_id") == component_id and candidate["type"] == "icon"]
        if box["icon_children"] != [] or icon_atoms or icon_components:
            raise SystemExit("Invalid --layout-plan; message boxes are text-only with zero icon children and zero icon atoms.")
    component_box_ids = {component["id"] for component in components if component["type"] == "message_box" or component["role"] == "message_box"}
    if component_box_ids != registered_box_ids:
        raise SystemExit("Invalid --layout-plan; every message-box component appears exactly once in message_box_plan.")
    allowed_copy_targets = set(component_by_id) | {"header_h1", "header_subtitle", "footer_master"}
    if any(atom["component_id"] not in allowed_copy_targets for atom in atoms):
        raise SystemExit("Invalid --layout-plan; every content atom binds to a registered body or header/footer master component.")
    for atom in atoms:
        if atom["component_id"] not in component_by_id:
            continue
        owner = component_by_id[atom["component_id"]]["bounds"]
        anchor_x = shell["x"] + (atom["anchor_line"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"])
        if not owner["x"] <= anchor_x <= owner["x"] + owner["w"] or not owner["y"] <= atom["baseline_step"] <= owner["y"] + owner["h"]:
            raise SystemExit("Invalid --layout-plan; body content-atom anchors stay inside their owning component.")
    for component in components:
        if component["parent_id"] not in node_ids or node_by_id[component["id"]].get("parent_id") != component["parent_id"]:
            raise SystemExit("Invalid --layout-plan; every component belongs to its declared layout parent.")
        bounds = component["bounds"]
        if not {"x", "y", "w", "h"}.issubset(bounds) or min(bounds.values()) < 0:
            raise SystemExit("Invalid --layout-plan; component bounds use non-negative x, y, w, and h.")
        if bounds["x"] < shell["x"] or bounds["x"] + bounds["w"] > shell["right"] or bounds["y"] < body_top or bounds["y"] + bounds["h"] > body_bottom:
            raise SystemExit("Invalid --layout-plan; every component stays inside the shell and footer-mode body band.")
        if not (1 <= component["left_anchor_line"] < component["right_anchor_line"] <= 17):
            raise SystemExit("Invalid --layout-plan; component horizontal anchors use grid lines 1..17.")
        expected_left = shell["x"] + (component["left_anchor_line"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"])
        expected_right = shell["x"] + (component["right_anchor_line"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"]) - geometry_grid["gutter_px"]
        if abs(bounds["x"] - expected_left) > geometry_grid["line_snap_tolerance_px"] or abs(bounds["x"] + bounds["w"] - expected_right) > geometry_grid["line_snap_tolerance_px"]:
            raise SystemExit("Invalid --layout-plan; component edges match their registered column anchors within 4px.")
        if component["type"] == "message_box":
            if min(component["top_baseline_step"] % geometry_grid["unit_px"], geometry_grid["unit_px"] - component["top_baseline_step"] % geometry_grid["unit_px"]) > geometry_grid["baseline_snap_tolerance_px"] or min(component["bottom_baseline_step"] % geometry_grid["unit_px"], geometry_grid["unit_px"] - component["bottom_baseline_step"] % geometry_grid["unit_px"]) > geometry_grid["baseline_snap_tolerance_px"]:
                raise SystemExit("Invalid --layout-plan; template-derived message-box edges stay within 4px of the 8px baseline.")
        elif component["top_baseline_step"] % geometry_grid["unit_px"] or component["bottom_baseline_step"] % geometry_grid["unit_px"]:
            raise SystemExit("Invalid --layout-plan; component top and bottom positions use the 8px baseline.")
        if abs(bounds["y"] - component["top_baseline_step"]) > geometry_grid["baseline_snap_tolerance_px"] or abs(bounds["y"] + bounds["h"] - component["bottom_baseline_step"]) > geometry_grid["baseline_snap_tolerance_px"]:
            raise SystemExit("Invalid --layout-plan; component bounds match their registered vertical baselines within 4px.")
        if "text" in component["type"]:
            if component.get("text_anchor_line") not in range(1, 18) or component.get("first_baseline_step", -1) % geometry_grid["unit_px"]:
                raise SystemExit("Invalid --layout-plan; text components declare a grid text anchor and 8px first baseline.")
        if component["type"] in {"icon", "number", "mark"} and component.get("center_anchor_line") not in range(1, 18):
            raise SystemExit("Invalid --layout-plan; centered marks declare a center grid line.")

    for index, component in enumerate(components):
        for peer in components[index + 1:]:
            if rectangles_overlap(component["bounds"], peer["bounds"]):
                raise SystemExit("Invalid --layout-plan; registered components occupy distinct non-overlapping regions.")

    peer_groups: dict[str, list[dict]] = {}
    for component in components:
        if component["peer_group"]:
            peer_groups.setdefault(component["peer_group"], []).append(component)
    tolerance = geometry_grid["line_snap_tolerance_px"]
    for peers in peer_groups.values():
        if len(peers) < 2:
            continue
        widths = [peer["bounds"]["w"] for peer in peers]
        heights = [peer["bounds"]["h"] for peer in peers]
        paddings = [peer.get("padding_px", 0) for peer in peers]
        if max(widths) - min(widths) > tolerance or max(heights) - min(heights) > tolerance or max(paddings) - min(paddings) > tolerance:
            raise SystemExit("Invalid --layout-plan; peer modules keep equal dimensions and padding within 4px.")

    rules = plan["structural_rule_plan"].get("rules", [])
    rule_required = {"id", "role", "parent_id", "orientation", "start_anchor", "end_anchor", "baseline_step", "start_point", "end_point", "stroke_px", "color_role"}
    if any(not rule_required.issubset(rule) for rule in rules):
        raise SystemExit("Invalid --layout-plan; structural_rule_plan registers every rule with role, anchors, baseline, stroke, and color.")
    for rule in rules:
        if rule["parent_id"] not in node_ids or rule["orientation"] not in {"horizontal", "vertical"}:
            raise SystemExit("Invalid --layout-plan; structural rules use registered parents and horizontal or vertical orientation.")
        if rule["start_anchor"] not in range(1, 18) or rule["end_anchor"] not in range(1, 18) or rule["baseline_step"] % geometry_grid["unit_px"]:
            raise SystemExit("Invalid --layout-plan; structural-rule endpoints and positions snap to the grid and 8px baseline.")
        if not 1 <= rule["stroke_px"] <= 3:
            raise SystemExit("Invalid --layout-plan; structural-rule stroke uses the 1-3px hierarchy.")
        start, end = rule["start_point"], rule["end_point"]
        if not {"x", "y"}.issubset(start) or not {"x", "y"}.issubset(end):
            raise SystemExit("Invalid --layout-plan; structural rules declare explicit start and end points.")
        if rule["orientation"] == "horizontal" and (start["y"] != end["y"] or start["y"] != rule["baseline_step"]):
            raise SystemExit("Invalid --layout-plan; horizontal structural-rule points share the declared baseline.")
        if rule["orientation"] == "vertical" and start["x"] != end["x"]:
            raise SystemExit("Invalid --layout-plan; vertical structural-rule points share one x coordinate.")
        expected_start_x = shell["x"] + (rule["start_anchor"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"])
        expected_end_x = shell["x"] + (rule["end_anchor"] - 1) * (geometry_grid["track_px"] + geometry_grid["gutter_px"])
        if rule["orientation"] == "horizontal":
            expected_end_x -= geometry_grid["gutter_px"]
            if abs(start["x"] - expected_start_x) > tolerance or abs(end["x"] - expected_end_x) > tolerance:
                raise SystemExit("Invalid --layout-plan; horizontal structural-rule points match their declared column anchors within 4px.")
        elif rule["start_anchor"] != rule["end_anchor"] or abs(start["x"] - expected_start_x) > tolerance:
            raise SystemExit("Invalid --layout-plan; vertical structural-rule points share their declared column anchor within 4px.")
        if any(point["x"] < shell["x"] or point["x"] > shell["right"] or point["y"] < body_top or point["y"] > body_bottom for point in (start, end)):
            raise SystemExit("Invalid --layout-plan; structural-rule points stay inside the selected body envelope.")

    connectors = plan["connector_plan"].get("connectors", [])
    connector_required = {"id", "from_id", "to_id", "source_port", "target_port", "route", "waypoints", "bend_count", "crossing_count", "line_token", "arrowhead_token"}
    allowed_ports = {"left_center", "right_center", "top_center", "bottom_center"}
    for connector in connectors:
        if not connector_required.issubset(connector) or connector["from_id"] not in component_by_id or connector["to_id"] not in component_by_id:
            raise SystemExit("Invalid --layout-plan; connectors register endpoints, ports, route, waypoints, bends, crossings, and line tokens.")
        if connector["route"] not in {"orthogonal", "declared_arc"}:
            raise SystemExit("Invalid --layout-plan; connector route is orthogonal or a declared arc.")
        if connector["source_port"] not in allowed_ports or connector["target_port"] not in allowed_ports:
            raise SystemExit("Invalid --layout-plan; connector ports use a registered component-edge center.")
        if connector["route"] == "orthogonal" and (connector["bend_count"] not in {0, 1, 2} or connector["crossing_count"] != 0):
            raise SystemExit("Invalid --layout-plan; orthogonal connectors use 0-2 bends and zero crossings.")
        if any(not {"x", "y"}.issubset(point) or point["y"] % geometry_grid["unit_px"] for point in connector["waypoints"]):
            raise SystemExit("Invalid --layout-plan; connector waypoints use explicit x/y coordinates on the 8px baseline.")
        if any(point["x"] < shell["x"] or point["x"] > shell["right"] or point["y"] < body_top or point["y"] > body_bottom for point in connector["waypoints"]):
            raise SystemExit("Invalid --layout-plan; connector waypoints stay inside the selected body envelope.")
    if clarity["connector_count"] != len(connectors):
        raise SystemExit("Invalid --layout-plan; clarity connector count matches the registered connector plan.")
    for connector in connectors:
        if not connector["waypoints"]:
            continue
        source = component_by_id[connector["from_id"]]["bounds"]
        target = component_by_id[connector["to_id"]]["bounds"]
        def port_point(bounds: dict, port: str) -> tuple[float, float]:
            return {
                "left_center": (bounds["x"], bounds["y"] + bounds["h"] / 2),
                "right_center": (bounds["x"] + bounds["w"], bounds["y"] + bounds["h"] / 2),
                "top_center": (bounds["x"] + bounds["w"] / 2, bounds["y"]),
                "bottom_center": (bounds["x"] + bounds["w"] / 2, bounds["y"] + bounds["h"]),
            }[port]
        source_point = port_point(source, connector["source_port"])
        target_point = port_point(target, connector["target_port"])
        first, last = connector["waypoints"][0], connector["waypoints"][-1]
        if max(abs(first["x"] - source_point[0]), abs(first["y"] - source_point[1]), abs(last["x"] - target_point[0]), abs(last["y"] - target_point[1])) > geometry_grid["line_snap_tolerance_px"]:
            raise SystemExit("Invalid --layout-plan; connector endpoints match registered component ports within 4px.")
    quiet_key = "quiet_clearance_range_without_footer" if plan["footer_mode"] == "absent" else "quiet_clearance_range_with_footer"
    quiet_lo, quiet_hi = body[quiet_key]
    first_region_y = min(box["y"] for box in region_boxes.values())
    canonical_header_bottom = GEOMETRY["header"]["clearance_datum_y"]
    if not quiet_lo <= first_region_y - canonical_header_bottom <= quiet_hi:
        raise SystemExit("Invalid --layout-plan; first body region matches the footer-mode canonical header/body clearance band.")
    containers = plan["flex_plan"].get("containers", [])
    if not containers:
        raise SystemExit("Invalid --layout-plan; declare at least one Flex container.")
    containers_by_id = {container.get("id"): container.get("bounds") for container in containers if container.get("id") and container.get("bounds")}
    required_container = {"id", "bounds", "main_axis", "wrap", "line_plan", "gap_px", "justify", "align", "children"}
    required_child = {"id", "basis_px", "grow", "shrink", "min_main_px", "min_cross_px", "allocation_bounds"}
    allowed_justify = {"start", "center", "end", "space-between", "space-around", "space-evenly"}
    allowed_align = {"start", "center", "end", "baseline", "stretch"}
    allocation_rectangles: list[dict] = []
    for container in containers:
        if not required_container.issubset(container) or container["id"] not in node_ids or container["main_axis"] not in {"row", "column"}:
            raise SystemExit("Invalid --layout-plan; each Flex container requires the complete container contract.")
        if container["wrap"] not in {"nowrap", "wrap"}:
            raise SystemExit("Invalid --layout-plan; Flex wrap is nowrap or wrap.")
        if container["gap_px"] not in GEOMETRY["flex"]["gap_tokens_px"]:
            raise SystemExit("Invalid --layout-plan; Flex gap uses 16, 24, 32, or 48px.")
        if container["justify"] not in allowed_justify or container["align"] not in allowed_align:
            raise SystemExit("Invalid --layout-plan; Flex justify and align use the documented value sets.")
        if not container["children"] or any(not required_child.issubset(child) or child["id"] not in node_ids for child in container["children"]):
            raise SystemExit("Invalid --layout-plan; every Flex child requires basis/grow/shrink/min sizes, allocation bounds, and a registered id.")
        if any(next(node for node in nodes if node["id"] == child["id"]).get("parent_id") != container["id"] for child in container["children"]):
            raise SystemExit("Invalid --layout-plan; every Flex child belongs to its declared Flex parent.")
        if sum(container["line_plan"]) != len(container["children"]):
            raise SystemExit("Invalid --layout-plan; Flex line_plan accounts for every child exactly once.")
        if container["wrap"] == "nowrap" and container["line_plan"] != [len(container["children"])]:
            raise SystemExit("Invalid --layout-plan; nowrap uses one planned line containing every child.")
        bounds = container["bounds"]
        if not {"x", "y", "w", "h"}.issubset(bounds) or min(bounds.values()) < 0:
            raise SystemExit("Invalid --layout-plan; Flex bounds use non-negative x, y, w, and h.")
        if bounds["x"] < shell["x"] or bounds["x"] + bounds["w"] > shell["right"] or bounds["y"] < body_top or bounds["y"] + bounds["h"] > body_bottom:
            raise SystemExit("Invalid --layout-plan; Flex bounds stay inside the shell and selected footer-mode body band.")
        if container["id"] in region_boxes and any(abs(bounds[key] - region_boxes[container["id"]][key]) > geometry_grid["line_snap_tolerance_px"] for key in ("x", "y", "w", "h")):
            raise SystemExit("Invalid --layout-plan; Flex container bounds match their declared grid region within 4px.")
        main_size = bounds["w"] if container["main_axis"] == "row" else bounds["h"]
        cross_size = bounds["h"] if container["main_axis"] == "row" else bounds["w"]
        for child in container["children"]:
            allocation = child["allocation_bounds"]
            if not {"x", "y", "w", "h"}.issubset(allocation) or min(allocation.values()) < 0:
                raise SystemExit("Invalid --layout-plan; child allocation bounds use non-negative x, y, w, and h.")
            if allocation["x"] < bounds["x"] or allocation["x"] + allocation["w"] > bounds["x"] + bounds["w"] or allocation["y"] < bounds["y"] or allocation["y"] + allocation["h"] > bounds["y"] + bounds["h"]:
                raise SystemExit("Invalid --layout-plan; every child allocation stays inside its Flex parent.")
            allocation_main = allocation["w"] if container["main_axis"] == "row" else allocation["h"]
            allocation_cross = allocation["h"] if container["main_axis"] == "row" else allocation["w"]
            if child["min_main_px"] > allocation_main or child["min_cross_px"] > allocation_cross or child["min_cross_px"] > cross_size:
                raise SystemExit("Invalid --layout-plan; every Flex child allocation satisfies its minimum sizes.")
            registered_bounds = component_by_id.get(child["id"], {}).get("bounds") or region_boxes.get(child["id"]) or containers_by_id.get(child["id"])
            if registered_bounds is None:
                raise SystemExit("Invalid --layout-plan; every Flex child allocation binds to registered component, grid-region, or nested Flex geometry.")
            if any(abs(allocation[key] - registered_bounds[key]) > tolerance for key in ("x", "y", "w", "h")):
                raise SystemExit("Invalid --layout-plan; every Flex child allocation matches its registered geometry within 4px.")
            allocation_rectangles.append(allocation)
        for child in container["children"]:
            allocation_main = child["allocation_bounds"]["w" if container["main_axis"] == "row" else "h"]
            if child["basis_px"] and abs(allocation_main - child["basis_px"]) / child["basis_px"] > GEOMETRY["flex"]["basis_deviation_limit"]:
                raise SystemExit("Invalid --layout-plan; Flex allocation remains within 20% of the declared basis.")
        child_offset = 0
        for line_index, line_count in enumerate(container["line_plan"]):
            line_children = container["children"][child_offset:child_offset + line_count]
            axis = "x" if container["main_axis"] == "row" else "y"
            size_key = "w" if container["main_axis"] == "row" else "h"
            cross_key = "h" if container["main_axis"] == "row" else "w"
            line_cross_size = cross_size if container["wrap"] == "nowrap" else cross_size / len(container["line_plan"])
            cross_lo, cross_hi = GEOMETRY["flex"]["cross_axis_fill_range"]
            if any(not cross_lo <= child["allocation_bounds"][cross_key] / line_cross_size <= cross_hi for child in line_children):
                raise SystemExit("Invalid --layout-plan; every Flex child fills 82-100% of its line cross axis.")
            ordered_line_children = sorted(line_children, key=lambda child: child["allocation_bounds"][axis])
            for previous, current in zip(ordered_line_children, ordered_line_children[1:]):
                if rectangles_overlap(previous["allocation_bounds"], current["allocation_bounds"]):
                    raise SystemExit("Invalid --layout-plan; same-line Flex sibling allocations remain non-overlapping.")
                actual_gap = current["allocation_bounds"][axis] - (previous["allocation_bounds"][axis] + previous["allocation_bounds"][size_key])
                if abs(actual_gap - container["gap_px"]) > tolerance:
                    raise SystemExit("Invalid --layout-plan; same-line Flex siblings preserve the declared gap within 4px.")
            basis_total = sum(child["basis_px"] for child in line_children) + max(0, line_count - 1) * container["gap_px"]
            if basis_total > main_size:
                raise SystemExit("Invalid --layout-plan; Flex basis and gaps fit within every planned line.")
            actual_total = sum(child["allocation_bounds"][size_key] for child in line_children) + max(0, line_count - 1) * container["gap_px"]
            fill_floor = (
                GEOMETRY["flex"]["last_line_fill_min"]
                if container["wrap"] == "wrap" and len(container["line_plan"]) > 1 and line_index == len(container["line_plan"]) - 1
                else GEOMETRY["flex"]["main_axis_fill_range"][0]
            )
            if not fill_floor <= actual_total / main_size <= GEOMETRY["flex"]["main_axis_fill_range"][1]:
                raise SystemExit("Invalid --layout-plan; each Flex line meets its actual main-axis fill range after grow/shrink allocation.")
            child_offset += line_count
    occupancy = plan["occupancy_plan"]
    required_occupancy = {"body_width_target", "body_height_target", "container_width_target", "container_height_target", "allocated_area_target", "foreground_area_target", "text_ink_area_share_target", "object_ink_area_share_target"}
    if not required_occupancy.issubset(occupancy):
        raise SystemExit("Invalid --layout-plan; occupancy_plan requires body, container, allocated, foreground, text, and object targets.")
    body_height_key = "height_utilization_range_without_footer" if plan["footer_mode"] == "absent" else "height_utilization_range_with_footer"
    container_height_key = "top_level_container_height_utilization_range_without_footer" if plan["footer_mode"] == "absent" else "top_level_container_height_utilization_range_with_footer"
    ranges = {
        "body_width_target": tuple(GEOMETRY["body"]["width_utilization_range"]),
        "body_height_target": tuple(GEOMETRY["body"][body_height_key]),
        "container_width_target": tuple(GEOMETRY["body"]["top_level_container_width_utilization_range"]),
        "container_height_target": tuple(GEOMETRY["body"][container_height_key]),
        "allocated_area_target": tuple(GEOMETRY["body"]["allocated_region_area_fill_range"]),
        "foreground_area_target": tuple(GEOMETRY["body"]["meaningful_foreground_area_fill_range"]),
        "text_ink_area_share_target": tuple(GEOMETRY["body"]["text_ink_area_share_range"]),
        "object_ink_area_share_target": tuple(GEOMETRY["body"]["object_ink_area_share_range"]),
    }
    if any(not lo <= occupancy[key] <= hi for key, (lo, hi) in ranges.items()):
        raise SystemExit("Invalid --layout-plan; occupancy targets stay inside the canonical ranges.")
    ink_targets = (occupancy["text_ink_area_share_target"], occupancy["object_ink_area_share_target"])
    if sum(ink_targets) < occupancy["foreground_area_target"] - 0.02 or sum(ink_targets) > 1.0:
        raise SystemExit("Invalid --layout-plan; text and object ink shares support the foreground-union target while allowing overlap.")
    container_x1 = min(box["x"] for box in region_boxes.values())
    container_y1 = min(box["y"] for box in region_boxes.values())
    container_x2 = max(box["x"] + box["w"] for box in region_boxes.values())
    container_y2 = max(box["y"] + box["h"] for box in region_boxes.values())
    derived_container_width = (container_x2 - container_x1) / body["available_width"]
    available_height = body["available_height_without_footer"] if plan["footer_mode"] == "absent" else body["available_height_with_footer"]
    derived_container_height = (container_y2 - container_y1) / available_height
    if abs(occupancy["container_width_target"] - derived_container_width) > 0.02 or abs(occupancy["container_height_target"] - derived_container_height) > 0.02:
        raise SystemExit("Invalid --layout-plan; container occupancy targets match derived grid geometry within 0.02.")
    painted_body_rectangles = [component["bounds"] for component in components]
    primary_body_rectangles = [component["bounds"] for component in components if component["type"] != "message_box"]
    body_x1 = min(box["x"] for box in primary_body_rectangles)
    body_x2 = max(box["x"] + box["w"] for box in primary_body_rectangles)
    body_y1 = min(box["y"] for box in painted_body_rectangles)
    body_y2 = max(box["y"] + box["h"] for box in painted_body_rectangles)
    derived_body_width = (body_x2 - body_x1) / body["available_width"]
    derived_body_height = (body_y2 - body_y1) / available_height
    if abs(occupancy["body_width_target"] - derived_body_width) > 0.02 or abs(occupancy["body_height_target"] - derived_body_height) > 0.02:
        raise SystemExit("Invalid --layout-plan; body envelope targets match the derived primary-body width and complete vertical envelope within 0.02.")
    body_band_area = body["available_width"] * available_height
    derived_allocated_area = rectangle_union_area(painted_body_rectangles) / body_band_area
    if abs(occupancy["allocated_area_target"] - derived_allocated_area) > 0.02:
        raise SystemExit("Invalid --layout-plan; allocated-area target matches the union of child allocation rectangles within 0.02.")
    total_mass = sum(rectangle["w"] * rectangle["h"] for rectangle in painted_body_rectangles)
    derived_centroid_y = sum(
        rectangle["w"] * rectangle["h"] * (rectangle["y"] + rectangle["h"] / 2)
        for rectangle in painted_body_rectangles
    ) / total_mass / GEOMETRY["basis"]["height"]
    centroid_key = "centroid_y_range_without_footer" if plan["footer_mode"] == "absent" else "centroid_y_range_with_footer"
    centroid_lo, centroid_hi = body[centroid_key]
    if not centroid_lo <= derived_centroid_y <= centroid_hi:
        raise SystemExit(f"Invalid --layout-plan; area-weighted body centroid {derived_centroid_y:.3f} stays inside the canonical {centroid_lo:.2f}-{centroid_hi:.2f} band.")
    if plan["footer_mode"] == "absent":
        meaningful_rectangles = painted_body_rectangles
        lowest_allocation_pixel = max(rectangle["y"] + rectangle["h"] for rectangle in meaningful_rectangles)
        closure_lo, closure_hi = body["bottom_closure_range_without_footer"]
        bottom_visible_margin = GEOMETRY["basis"]["height"] - lowest_allocation_pixel
        if not closure_lo <= lowest_allocation_pixel <= closure_hi:
            raise SystemExit("Invalid --layout-plan; footer-absent allocation reaches the canonical bottom-closure band.")
        if abs(GEOMETRY["header"]["h1"]["visible_top_y"] - bottom_visible_margin) > body["outer_visible_margin_difference_max_px"]:
            raise SystemExit("Invalid --layout-plan; footer-absent planned top and bottom visible margins differ by at most 12px.")

    rigidity = plan["rigidity_plan"]
    required_rigidity = {"edge_registration_score", "repeated_module_consistency", "gap_token_compliance", "structural_rule_pass_rate", "connector_endpoint_pass_rate", "structured_cell_fill", "orphan_region_count", "shared_vertical_anchors", "shared_horizontal_anchors", "grid_rigidity_score"}
    if not required_rigidity.issubset(rigidity):
        raise SystemExit("Invalid --layout-plan; rigidity_plan requires every consulting-grid score and shared-axis count.")
    if rigidity["edge_registration_score"] < 0.90 or rigidity["repeated_module_consistency"] < 0.95 or rigidity["gap_token_compliance"] < 0.95:
        raise SystemExit("Invalid --layout-plan; edge, peer-module, and gap scores meet the consulting-grid thresholds.")
    if rigidity["structural_rule_pass_rate"] != 1.0 or rigidity["connector_endpoint_pass_rate"] != 1.0:
        raise SystemExit("Invalid --layout-plan; structural-rule and connector endpoint pass rates equal 1.00.")
    if not 0.65 <= rigidity["structured_cell_fill"] <= 0.85 or rigidity["orphan_region_count"] != 0:
        raise SystemExit("Invalid --layout-plan; structured-cell fill is 0.65-0.85 and orphan region count is zero.")
    if rigidity["shared_vertical_anchors"] < 3 or rigidity["shared_horizontal_anchors"] < 3:
        raise SystemExit("Invalid --layout-plan; the body establishes at least three shared vertical and horizontal anchors.")
    calculated_rigidity = (
        0.35 * rigidity["edge_registration_score"]
        + 0.25 * rigidity["repeated_module_consistency"]
        + 0.20 * rigidity["gap_token_compliance"]
        + 0.10 * rigidity["structural_rule_pass_rate"]
        + 0.10 * rigidity["connector_endpoint_pass_rate"]
    )
    if abs(rigidity["grid_rigidity_score"] - calculated_rigidity) > 0.005 or rigidity["grid_rigidity_score"] < 0.93:
        raise SystemExit("Invalid --layout-plan; grid_rigidity_score matches the weighted formula and passes 0.93.")
    quiet = plan["quiet_region"]
    if not {"bounds", "role", "related_regions"}.issubset(quiet):
        raise SystemExit("Invalid --layout-plan; quiet_region requires bounds, role, and related_regions.")
    if not quiet["related_regions"] or any(region_id not in node_ids for region_id in quiet["related_regions"]):
        raise SystemExit("Invalid --layout-plan; quiet_region references registered regions.")
    quiet_bounds = quiet["bounds"]
    if not {"x", "y", "w", "h"}.issubset(quiet_bounds) or quiet_bounds["x"] < shell["x"] or quiet_bounds["x"] + quiet_bounds["w"] > shell["right"] or quiet_bounds["y"] < shell["y"] or quiet_bounds["y"] + quiet_bounds["h"] > shell["bottom"]:
        raise SystemExit("Invalid --layout-plan; quiet_region stays inside the canonical shell.")
    if any(rectangles_overlap(quiet_bounds, rectangle) for rectangle in painted_body_rectangles):
        raise SystemExit("Invalid --layout-plan; quiet_region remains clear of every painted body component.")
    return plan


def geometry_contract(design_tokens: dict) -> str:
    g = GEOMETRY
    shell, header, body, footer, grid, flex = g["outer_shell"], g["header"], g["body"], g["footer"], g["grid"], g["flex"]
    width_lo, width_hi = (round(value * 100) for value in body["width_utilization_range"])
    height_without_lo, height_without_hi = (round(value * 100) for value in body["height_utilization_range_without_footer"])
    height_with_lo, height_with_hi = (round(value * 100) for value in body["height_utilization_range_with_footer"])
    container_w_lo, container_w_hi = (round(value * 100) for value in body["top_level_container_width_utilization_range"])
    container_h_without_lo, container_h_without_hi = (round(value * 100) for value in body["top_level_container_height_utilization_range_without_footer"])
    container_h_with_lo, container_h_with_hi = (round(value * 100) for value in body["top_level_container_height_utilization_range_with_footer"])
    area_lo, area_hi = (round(value * 100) for value in body["allocated_region_area_fill_range"])
    foreground_lo, foreground_hi = (round(value * 100) for value in body["meaningful_foreground_area_fill_range"])
    text_lo, text_hi = (round(value * 100) for value in body["text_ink_area_share_range"])
    object_lo, object_hi = (round(value * 100) for value in body["object_ink_area_share_range"])
    flex_main_lo, flex_main_hi = (round(value * 100) for value in flex["main_axis_fill_range"])
    flex_cross_lo, flex_cross_hi = (round(value * 100) for value in flex["cross_axis_fill_range"])
    centroid_without_lo, centroid_without_hi = (round(value * 100) for value in body["centroid_y_range_without_footer"])
    centroid_with_lo, centroid_with_hi = (round(value * 100) for value in body["centroid_y_range_with_footer"])
    h1_height = header["h1"]["visible_height_px_range"]
    subtitle_height = header["subtitle"]["visible_height_px_range"]
    box = g["message_box"]
    insets = shell["insets_px"]
    resolved = resolve_color_roles(design_tokens)
    return f"""non_negotiable_canvas_contract:
  canonical_geometry: {g['basis']['width']}x{g['basis']['height']} basis
  outer_shell: profile={shell['profile']}; top={insets['top']}px right={insets['right']}px bottom={insets['bottom']}px left={insets['left']}px; x={shell['x']}..{shell['right']} y={shell['y']}..{shell['bottom']}
  header_master: H1 x={header['h1']['x']} y={header['h1']['y']} w={header['h1']['width']}, one uniform {header['h1']['point_size']}pt/{header['h1']['weight']} line, rendered visible height {h1_height[0]}-{h1_height[1]}px; subtitle x={header['subtitle']['x']} y={header['subtitle']['y']} w={header['subtitle']['width']}, one {header['subtitle']['point_size']}pt/{header['subtitle']['weight']} line, rendered visible height {subtitle_height[0]}-{subtitle_height[1]}px; pilot deviation <={header['pilot_visible_height_tolerance_px']}px
  footer_absent: envelope y={body['target_envelope_without_footer']['top']}..{body['target_envelope_without_footer']['bottom']}; centroid {centroid_without_lo}-{centroid_without_hi}%; lowest meaningful body pixel y={body['bottom_closure_range_without_footer'][0]}..{body['bottom_closure_range_without_footer'][1]}; top/bottom visible-margin difference <={body['outer_visible_margin_difference_max_px']}px
  footer_present: envelope y={body['target_envelope_with_footer']['top']}..{body['target_envelope_with_footer']['bottom']}; centroid {centroid_with_lo}-{centroid_with_hi}%; provenance box x={footer['x']} y={footer['y']} w={footer['width']} h={footer['height']}, {footer['point_size']}pt, one or two lines, centered vertically with {footer['line_height_px']}px line metric
  body_occupancy: visible envelope {width_lo}-{width_hi}% width; footer-absent height {height_without_lo}-{height_without_hi}% and container height {container_h_without_lo}-{container_h_without_hi}%; footer-present height {height_with_lo}-{height_with_hi}% and container height {container_h_with_lo}-{container_h_with_hi}%; container width {container_w_lo}-{container_w_hi}%; child allocation union {area_lo}-{area_hi}% of available body-band area; foreground union {foreground_lo}-{foreground_hi}%, text ink {text_lo}-{text_hi}%, and object ink {object_lo}-{object_hi}% of visible envelope
  grid_contract: explicit {grid['columns']}-column parent grid with {grid['track_px']}px tracks, {grid['gutter_px']}px gutters, integer line spans, {grid['unit_px']}px vertical baseline, and ±{grid['line_snap_tolerance_px']}px line/baseline tolerance; nested 2D regions inherit parent lines
  flex_contract: declare bounds/axis/wrap/gap/alignment and child basis/grow/shrink/min; main fill {flex_main_lo}-{flex_main_hi}%, cross fill {flex_cross_lo}-{flex_cross_hi}%, basis deviation <=20%, final line >=75%, overflow/clipping/overlap=0
  layout_tree_gate: one declared parent per body element; every field has an audit counterpart; variance is repair_required
  consulting_grid_rigidity: register component/text/rule/value/icon/connector anchors; edge >=90%, peers >=95%, gaps >=95%, rules/connectors 100%, cells 65-85%, orphans 0, weighted score >=0.93
  composition_clarity: express one primary relationship through one visual grammar, 2-4 independent regions, one start/path/landing, and the registered grid geometry
  source_contract: Source: is reserved for one traceable external publication; Assumption: and Note: are optional labeled annotations; active entries combine in one footer_master; an empty set keeps footer_mode absent
  message_box_contract: text-only; zero icon children and icon atoms; {box['point_size']}pt, one line, {box['height_by_line_count_px']['1'][0]}px high, centered text, {box['horizontal_padding_tokens_px'][0]}px horizontal inset
  color_contract: design_token={design_tokens['name']}; canvas={resolved['slide_background']}; ink={resolved['main_message']}; sub_message={resolved['sub_message']}; footer={resolved['footer']}; structural={resolved['structural_panel']}; focus={resolved['single_focus_fill']} with stroke {resolved['single_focus_stroke']}
"""


def compile_render_plan(plan: dict, design_tokens: dict) -> dict:
    """Reduce the validator plan to visible states on the 2048x1152 render basis."""
    sx = 2048 / GEOMETRY["basis"]["width"]
    sy = 1152 / GEOMETRY["basis"]["height"]

    def scaled(bounds: dict) -> dict:
        return {
            "x": round(bounds["x"] * sx),
            "y": round(bounds["y"] * sy),
            "w": round(bounds["w"] * sx),
            "h": round(bounds["h"] * sy),
        }

    grid = GEOMETRY["grid"]
    shell = GEOMETRY["outer_shell"]
    regions = []
    for region in plan["grid_plan"]["regions"]:
        span = region["column_end"] - region["column_start"]
        bounds = {
            "x": shell["x"] + (region["column_start"] - 1) * (grid["track_px"] + grid["gutter_px"]),
            "y": region["row_start"],
            "w": span * grid["track_px"] + (span - 1) * grid["gutter_px"],
            "h": region["row_end"] - region["row_start"],
        }
        regions.append({"id": region["id"], "span": [region["column_start"], region["column_end"]], "bounds": scaled(bounds)})
    components = [
        {
            "id": component["id"], "type": component["type"], "role": component["role"],
            "peer_group": component["peer_group"], "bounds": scaled(component["bounds"]),
        }
        for component in plan["component_geometry_plan"]["components"]
    ]
    rules = [
        {"role": rule["role"], "orientation": rule["orientation"], "start": {"x": round(rule["start_point"]["x"] * sx), "y": round(rule["start_point"]["y"] * sy)}, "end": {"x": round(rule["end_point"]["x"] * sx), "y": round(rule["end_point"]["y"] * sy)}, "stroke_px": max(1, round(rule["stroke_px"] * sx))}
        for rule in plan["structural_rule_plan"]["rules"]
    ]
    connectors = [
        {"from": connector["from_id"], "to": connector["to_id"], "source_port": connector["source_port"], "target_port": connector["target_port"], "route": connector["route"], "waypoints": [{"x": round(point["x"] * sx), "y": round(point["y"] * sy)} for point in connector["waypoints"]]}
        for connector in plan["connector_plan"]["connectors"]
    ]
    message_boxes = []
    for box in plan["message_box_plan"]["boxes"]:
        compiled_box = dict(box)
        compiled_box.update({
            "line_height_px": round(box["line_height_px"] * sy),
            "vertical_padding_px": round(box["vertical_padding_px"] * sy),
            "horizontal_padding_px": round(box["horizontal_padding_px"] * sx),
            "height_px": round(box["height_px"] * sy),
        })
        message_boxes.append(compiled_box)
    footer = GEOMETRY["footer"]
    compiled_footer = {"mode": plan["footer_mode"]}
    if plan["footer_mode"] == "present":
        source_atom = next(atom for atom in plan["content_atom_registry"]["atoms"] if atom["component_id"] == "footer_master")
        compiled_footer.update({
            "component_id": "footer_master",
            "bounds": scaled({"x": footer["x"], "y": footer["y"], "w": footer["width"], "h": footer["height"]}),
            "point_size": footer["point_size"],
            "max_lines": source_atom["max_lines"],
            "line_height_px": round(footer["line_height_px"] * sy),
            "baseline_y_by_line": [round(value * sy) for value in footer["baseline_y_by_max_lines"][str(source_atom["max_lines"])]],
            "surface": "transparent_text_frame",
            "painted_geometry_count": 0,
        })
    return {
        "output_basis": "2048x1152",
        "footer_mode": plan["footer_mode"],
        "source_plan": plan["source_plan"],
        "message_box_plan": {"basis": "2048x1152", "boxes": message_boxes},
        "design_tokens": {"name": design_tokens["name"], "resolved_roles": resolve_color_roles(design_tokens), "usage": design_tokens["usage"]},
        "exact_copy": [{"id": atom["id"], "text": atom["exact_text"], "role": atom["semantic_role"], "component": atom["component_id"], "anchor": {"x": round(((GEOMETRY["message_box"]["x"] + GEOMETRY["message_box"]["width"] / 2) if atom["component_id"] == "message_box" else (shell["x"] + (atom["anchor_line"] - 1) * (grid["track_px"] + grid["gutter_px"]))) * sx), "baseline_y": round(atom["baseline_step"] * sy)}, "alignment": GEOMETRY["message_box"]["text_alignment"] if atom["component_id"] == "message_box" else "left", "max_lines": atom["max_lines"], "occurrences": 1} for atom in plan["content_atom_registry"]["atoms"]],
        "clarity": {key: plan["clarity_plan"][key] for key in ("primary_relationship", "region_roles", "start_region_id", "landing_region_id", "reading_path")},
        "surfaces": {
            "major_radius_px": round(plan["surface_plan"]["major_radius_px"] * sx),
            "peer_radius_px": round(plan["surface_plan"]["peer_radius_px"] * sx),
            "grouping_methods": plan["surface_plan"]["grouping_methods"],
        },
        "footer": compiled_footer,
        "tones": {key: plan["tone_plan"][key] for key in ("ambient_role", "region_role", "structural_role", "focus_role", "role_assignments")},
        "regions": regions,
        "components": components,
        "rules": rules,
        "connectors": connectors,
    }


def common_header(brief: str, mode: str, language: str, size: str, quality: str, design_tokens: dict) -> str:
    return f"""ACT slide workflow contract
mode: {mode}
language: {language}
image_model: {IMAGE_MODEL}
image_size: {size}
image_quality: {quality}
brief:
{brief}

{geometry_contract(design_tokens)}"""


def planning_tail(mode: str) -> str:
    detail = "deck-level sequence and per-slide plans" if mode == "deck-plan" else "per-slide story and evidence structure"
    return f"""planning_scope: {detail}
planning_rules:
  - apply argument_closure_lock; freeze deck_argument_plan and closure_matrix before visual layout
  - register each slide question, claim, evidence, warrant, implication, action_or_transition, inputs_from_prior, new_contribution, outputs_to_next, and decision_impact
  - pass 100% load-bearing claim coverage, evidence-to-claim binding, adjacent-slide transition coverage, and final owner/timing/success-measure coverage
  - state the audience, decision, governing thought, evidence state, and exact visible text
  - describe composition through relationships, visual weight, reading experience, and intended quiet region
  - keep composition vocabulary open; select components and region count from the content
  - distinguish fact, estimate, assumption, anecdote, and open question
  - register source_plan; reserve `Source: <citation>` for a traceable external reference; add concise `Assumption: ` and `Note: ` annotations when decision-relevant; combine active entries in one footer_master
  - create speaker notes and an ordered generation handoff
generation_handoff:
  - deck_argument_plan
  - closure_matrix
  - argument_closure_status
  - composition_intent
  - alignment_system
  - layout_tree
  - grid_plan
  - flex_plan
  - occupancy_plan
  - component_geometry_plan
  - structural_rule_plan
  - connector_plan
  - rigidity_plan
  - exact_text
  - footer_mode
  - zonal_mass_plan
  - evidence_and_source_state
  - source_plan
  - message_box_plan
  - image_prompt_ready
"""


def audit_tail() -> str:
    return """audit_output:
  - canvas_contract: approved / repair_required
  - grid_flex_contract: approved / repair_required
  - occupancy_contract: approved / repair_required
  - consulting_grid_rigidity: approved / repair_required
  - composition_clarity: approved / repair_required
  - exact_text: approved / repair_required
  - evidence_and_source: approved / repair_required
  - required_repairs:
"""


def lean_contract(brief: str, mode: str, composition: str, alignment: str, layout_plan: dict, language: str, size: str, quality: str, design_tokens: dict) -> str:
    if composition.startswith("UNRESOLVED") or alignment.startswith("UNRESOLVED"):
        raise SystemExit("Describe the content-led composition intent and composition-specific Grid/Flex nesting intent before building the generation contract.")
    action = "Edit the first referenced target image" if mode == "repair" else "Draw one new 16:9 strategy slide"
    reference = "Image 1 is content_target; preserve approved elements outside the named repair region." if mode == "repair" else "Use at most one style_board for material tokens; exact_text controls visible content."
    if len(brief) > 4000:
        raise SystemExit("Brief exceeds 4000 characters; split or condense it while preserving exact_text before generation.")
    compiled = compile_render_plan(layout_plan, design_tokens)
    validated_claim = layout_plan["slide_argument_plan"]["claim"]
    sx = 2048 / GEOMETRY["basis"]["width"]
    sy = 1152 / GEOMETRY["basis"]["height"]
    shell = GEOMETRY["outer_shell"]
    body = GEOMETRY["body"]
    envelope = body["target_envelope_without_footer"] if layout_plan["footer_mode"] == "absent" else body["target_envelope_with_footer"]
    header = GEOMETRY["header"]
    h1_rendered = [round(value * sy) for value in header["h1"]["visible_height_px_range"]]
    subtitle_rendered = [round(value * sy) for value in header["subtitle"]["visible_height_px_range"]]
    copy_lines = "\n".join(
        f'- {atom["id"]}: "{atom["text"]}" | role={atom["role"]} | component={atom["component"]} | anchor=({atom["anchor"]["x"]},{atom["anchor"]["baseline_y"]})' + (f' | alignment={atom["alignment"]}' if atom["alignment"] != "left" else "") + f' | lines<={atom["max_lines"]} | occurrences=1'
        for atom in compiled["exact_copy"]
    )
    layout_map = {
        "composition_intent": composition,
        "alignment_system": alignment,
        "clarity": compiled["clarity"],
        "surfaces": compiled["surfaces"],
        "regions": compiled["regions"],
        "components": compiled["components"],
        "rules": compiled["rules"],
        "connectors": compiled["connectors"],
        "footer": compiled["footer"],
    }
    resolved = resolve_color_roles(design_tokens)
    return f"""ACT slide image generation contract

DELIVERABLE
{action}; model={IMAGE_MODEL}; size={size}; quality={quality}; opaque PNG; language={language}.

MESSAGE
{validated_claim}

CANVAS
output_basis=2048x1152; canvas {resolved['slide_background']}; shell profile {shell['profile']} x={round(shell['x'] * sx)}..{round(shell['right'] * sx)} y={round(shell['y'] * sy)}..{round(shell['bottom'] * sy)}. H1 x={round(header['h1']['x'] * sx)} y={round(header['h1']['y'] * sy)}, one {header['h1']['point_size']}pt/{header['h1']['weight']} line with visible glyph height {h1_rendered[0]}-{h1_rendered[1]}px; subtitle x={round(header['subtitle']['x'] * sx)} y={round(header['subtitle']['y'] * sy)}, one {header['subtitle']['point_size']}pt/{header['subtitle']['weight']} line with visible glyph height {subtitle_rendered[0]}-{subtitle_rendered[1]}px. footer_mode={layout_plan['footer_mode']}; body envelope y={round(envelope['top'] * sy)}..{round(envelope['bottom'] * sy)}.
Header surface=uninterrupted canvas; visible components=[header_h1,header_subtitle]; geometry=0.

LAYOUT MAP
compiled_render_plan={json.dumps(layout_map, ensure_ascii=False, separators=(',', ':'))}

EXACT COPY
Render only these quoted strings, each at its bound component and occurrence count:
{copy_lines}

VISUAL SYSTEM
Noto Sans JP / Geist; design_tokens={json.dumps(compiled['design_tokens'], ensure_ascii=False, separators=(',', ':'))}; tones={json.dumps(compiled['tones'], ensure_ascii=False, separators=(',', ':'))}; shared edges; equal peers; straight rules; orthogonal connectors.

PRESERVATION STATE
{reference} Preserve fixed left header, independent rounded regions, quiet outer bands, exact copy, one grammar and emphasis system. source_plan={json.dumps(compiled['source_plan'], ensure_ascii=False, separators=(',', ':'))}. message_box_plan={json.dumps(compiled['message_box_plan'], ensure_ascii=False, separators=(',', ':'))}.

ACCEPTANCE
Exact-copy OCR/count match; header inventory matches; body stays in its envelope and reaches closure; shared axes, peers, radii, tones and connector endpoints match; overflow/clipping/overlap=0; Source: appears only for one external reference; Assumption: and Note: stay labeled; empty provenance keeps the footer quiet; every message box is text-only with copy-derived height.
"""


def build_prompt(brief: str, mode: str, composition: str, alignment: str, layout_plan: dict | None, language: str, size: str, quality: str, design_tokens: dict) -> str:
    if mode in {"single-slide-image", "repair"}:
        assert layout_plan is not None
        prompt = lean_contract(brief, mode, composition, alignment, layout_plan, language, size, quality, design_tokens)
        prompt_bytes = len(prompt.encode("utf-8"))
        if prompt_bytes > MAX_GENERATION_CONTRACT_BYTES:
            raise SystemExit(
                f"Compiled generation contract is {prompt_bytes} bytes; condense the brief or exact copy to fit the {MAX_GENERATION_CONTRACT_BYTES}-byte budget."
            )
        return prompt
    header = common_header(brief, mode, language, size, quality, design_tokens)
    if mode in {"deck-plan", "text-structure"}:
        return f"{header}\n\n{planning_tail(mode)}"
    return f"{header}\n\n{audit_tail()}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", nargs="?")
    parser.add_argument("--mode", default="single-slide-image", choices=["single-slide-image", "text-structure", "deck-plan", "repair", "audit"])
    parser.add_argument("--archetype", default=UNRESOLVED_COMPOSITION, help="Free-text composition intent; not a catalog selection.")
    parser.add_argument("--grid-mode", default=UNRESOLVED_ALIGNMENT, help="Composition-specific Grid/Flex nesting intent; the mandatory 16-column and recursive layout contracts always apply.")
    parser.add_argument("--layout-plan", help="JSON layout plan required for single-slide-image and repair modes.")
    parser.add_argument("--language", default="Japanese")
    parser.add_argument("--size", default="2048x1152")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--primary-guideline", default="embedded ACT design system")
    parser.add_argument("--design-tokens", help="Optional path to a schema-version-1 color token JSON; defaults to references/design-tokens.json.")
    args = parser.parse_args()
    design_tokens = read_design_tokens(args.design_tokens)
    print(build_prompt(read_brief(args.brief), args.mode, args.archetype, args.grid_mode, read_layout_plan(args.layout_plan, args.mode, design_tokens), args.language, validate_size(args.size), args.quality, design_tokens))


if __name__ == "__main__":
    main()
