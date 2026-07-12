#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const targetPath = process.argv[2] || process.env.PLUGIN_EVAL_TARGET || ".";
const root = path.resolve(targetPath);

function read(relPath) {
  try {
    return fs.readFileSync(path.join(root, relPath), "utf8");
  } catch {
    return "";
  }
}

function exists(relPath) {
  return fs.existsSync(path.join(root, relPath));
}

function includesAll(text, needles) {
  return needles.every((needle) => text.includes(needle));
}

function criterion(id, points, evidence, test) {
  return { id, points, evidence, passed: Boolean(test()) };
}

const skill = read("SKILL.md");
const protocol = read("build/references/_skill_invocation_protocol.md");
const design = read("build/references/_ib_workbook_design_system.md");
const layout = read("build/references/_layout_canonical.md");
const assumptions = read("build/references/_assumption_decomposition_patterns.md");
const valuation = read("build/references/_valuation_and_return_logic.md");
const sheetRubric = read("build/references/_sheet_quality_rubric.md");
const promptResearch = read("build/references/_ai_prompt_research_patterns.md");
const selfReview = read("build/references/_self_review_protocol.md");
const architecture = read("build/references/_excel_generation_architecture.md");
const ibFormat = read("build/runtime/ib_format.py");
const kernel = read("build/runtime/economic_kernel.py");
const sourcePlan = read("build/runtime/source_plan_builder.py");
const capTable = read("build/runtime/cap_table_builder.py");
const buildModel = read("build/runtime/build_model.py");
const workbookSpec = read("build/runtime/workbook_spec.py");
const qualityGate = read("scripts/quality_gate.py");
const architectureGate = read("scripts/architecture_gate.py");
const scenarioEval = read("scripts/scenario_eval.py");
const tests =
  read("build/tests/test_build_model.py") +
  "\n" +
  read("build/tests/test_economic_quality.py") +
  "\n" +
  read("tests/test_build_model_wrapper.py");
const evals = read("build/evals/evals.json");

const criteria = [
  criterion(
    "progressive-disclosure-and-stance",
    10,
    ["SKILL.md", "build/references/_skill_invocation_protocol.md"],
    () =>
      skill.split(/\r?\n/).length <= 80 &&
      skill.includes("former investment-banker / startup-CFO stance") &&
      skill.includes("_skill_invocation_protocol.md") &&
      protocol.includes("load the smallest set")
  ),
  criterion(
    "ib-workbook-design-system",
    20,
    ["build/references/_ib_workbook_design_system.md", "build/runtime/ib_format.py"],
    () =>
      includesAll(design, [
        "Input font",
        "Formula font",
        "Internal link font",
        "External link font",
        "Arial 10pt",
        "Money formats",
        "Terminal Comment",
        "20px",
        "No-Wrap Rule",
        "Fill span rules",
        "Borders are sparse accents",
      ]) &&
      includesAll(layout, ["No-Merge Rule", "No-Wrap Rule", "INDENT_COL_WIDTH", "terminal `Comment` column"]) &&
      includesAll(ibFormat, [
        "IB_HARD_INPUT",
        "IB_FORMULA",
        "IB_LINK_INTRA",
        "IB_LINK_EXTERNAL",
        "FONT_SIZE_ALLOWED_CELLS",
        "INDENT_COL_WIDTH",
        "FMT_JPY_MILLION",
        "apply_semantic_border_span",
      ])
  ),
  criterion(
    "assumption-depth-and-economic-kernel",
    20,
    [
      "build/references/_assumption_decomposition_patterns.md",
      "build/runtime/economic_kernel.py",
      "build/tests/test_economic_quality.py",
    ],
    () =>
      includesAll(assumptions, [
        "Selected driver",
        "Explanation drivers",
        "Implied value",
        "Support ratio / variance",
        "Evidence status",
      ]) &&
      includesAll(kernel, [
        "assumption_decomposition_for",
        "audit_economic_coherence",
        "churn_rate",
        "nol_balance",
      ]) &&
      includesAll(tests, ["K1", "K2", "K4", "K5"])
  ),
  criterion(
    "fd-valuation-and-return-logic",
    15,
    ["build/references/_valuation_and_return_logic.md", "build/tests/test_build_model.py"],
    () =>
      includesAll(valuation, [
        "Venture return",
        "MOIC",
        "IRR",
        "option pool",
        "liquidation preference",
        "dilution",
        "founder proceeds",
      ]) &&
      includesAll(sourcePlan + "\n" + capTable + "\n" + tests, [
        "FDSO",
        "compute_exit_waterfall",
        "Exit Waterfall",
        "New investor ownership",
        "MOIC",
        "Founder proceeds",
        "Ownership check",
      ])
  ),
  criterion(
    "sheet-quality-and-focused-scope",
    15,
    ["build/references/_sheet_quality_rubric.md", "build/evals/evals.json"],
    () =>
      includesAll(sheetRubric, [
        "Purpose",
        "Source boundary",
        "Dependency flow",
        "Checks",
        "Interpretation",
        "Include a sheet only if it owns a distinct decision surface",
      ]) &&
      evals.includes("XLSX_SHEET_QUALITY")
  ),
  criterion(
    "ai-x-prompt-research-synthesis",
    10,
    ["build/references/_ai_prompt_research_patterns.md", "build/evals/evals.json"],
    () =>
      exists("build/references/_ai_prompt_research_patterns.md") &&
      includesAll(promptResearch, [
        "X API recent search",
        "Prompt Contract",
        "Convert A Prompt Claim Into A Finance Model Gate",
        "Do not treat X posts",
      ]) &&
      protocol.includes("_ai_prompt_research_patterns.md") &&
      evals.includes("AI_PROMPT_RESEARCH_SYNTHESIS")
  ),
  criterion(
    "excel-generation-architecture",
    10,
    [
      "build/references/_excel_generation_architecture.md",
      "scripts/architecture_gate.py",
      "build/runtime/build_model.py",
    ],
    () =>
      includesAll(architecture, [
        "Use `openpyxl` as the canonical workbook engine",
        "XlsxWriter",
        "Layering Contract",
        "Intermediate Representation",
        "Formula Discipline",
        "volatile functions",
      ]) &&
      includesAll(workbookSpec, ["WorkbookSpec", "SheetSpec", "RowSpec", "CellSpec", "FormulaExpr", "StyleRole", "render_workbook_spec"]) &&
      includesAll(architectureGate, ["FORBIDDEN_IMPORTS", "ast.parse", "architecture_issues", "openpyxl>=3.1"]) &&
      includesAll(qualityGate, ["architecture_command", "architecture_gate.py", "scenario_eval_command", "scenario_eval.py", "recalc_and_inspect", "data_only=True", "audit_recalculated_financial_model"]) &&
      includesAll(scenarioEval, ["SCENARIOS", "recurring-software", "marketplace", "hardware-asset-heavy", "pre-revenue-milestone", "fintech-balance-sheet", "startup-finance-scenario-eval-score"]) &&
      includesAll(buildModel, ["VOLATILE_FORMULA_RE", "_audit_formula_engine", "audit_recalculated_financial_model"]) &&
      includesAll(tests, ["test_excel_generation_architecture_contract_is_documented_and_gated", "test_workbook_spec_renders_typed_ir_to_openpyxl_styles", "test_strict_audit_blocks_volatile_formula_functions", "test_saved_workbook_default_font_is_persisted_in_styles_xml", "test_recalculated_financial_audit_detects_broken_pnl_identity", "test_recalculated_financial_audit_passes_representative_full_workbook", "test_pre_revenue_valuation_uses_financing_implied_value_when_dcf_is_not_meaningful", "test_quality_gate_runs_scenario_eval"])
  ),
  criterion(
    "validation-and-closeout-discipline",
    10,
    ["build/references/_self_review_protocol.md", "build/tests/test_build_model.py"],
    () =>
      includesAll(selfReview, ["--strict-audit", "data_only=True", "rendered", "source"]) &&
      includesAll(tests, [
        "test_strict_audit_blocks_workbook_design_regressions",
        "test_generated_workbook_has_sheet_specific_quality_markers",
        "test_source_plan_has_no_excel_indent_or_clipped_role_columns",
      ])
  ),
];

const maxScore = criteria.reduce((sum, item) => sum + item.points, 0);
const score = criteria.reduce((sum, item) => sum + (item.passed ? item.points : 0), 0);
const percent = Math.round((score / maxScore) * 1000) / 10;

const checks = criteria.map((item) => ({
  id: `startup-finance-${item.id}`,
  category: "domain-rubric",
  severity: item.passed ? "info" : "error",
  status: item.passed ? "pass" : "fail",
  message: item.passed
    ? `${item.id} passed (${item.points} pts)`
    : `${item.id} missing required evidence (${item.points} pts)`,
  evidence: item.evidence,
  remediation: item.passed
    ? []
    : ["Update the cited reference/runtime/test/eval files until this criterion is evidenced."],
}));

checks.push({
  id: "startup-finance-domain-score-threshold",
  category: "domain-rubric",
  severity: percent >= 95 ? "info" : "error",
  status: percent >= 95 ? "pass" : "fail",
  message: `Startup finance domain rubric score is ${percent}/100`,
  evidence: [`earned ${score} of ${maxScore} weighted points`],
  remediation: percent >= 95 ? [] : ["Iterate until the domain rubric score is at least 95/100."],
});

console.log(
  JSON.stringify(
    {
      checks,
      metrics: [
        {
          id: "startup-finance-domain-rubric-score",
          category: "domain-rubric",
          value: percent,
          unit: "points",
          band: percent >= 95 ? "good" : percent >= 85 ? "moderate" : "poor",
        },
        {
          id: "startup-finance-domain-rubric-max",
          category: "domain-rubric",
          value: 100,
          unit: "points",
          band: "info",
        },
      ],
      artifacts: [
        {
          id: "startup-finance-domain-rubric-criteria",
          type: "json",
          label: "Startup finance domain rubric criteria",
          description: "Weighted deterministic rubric used for startup-financial-modeling skill quality.",
          data: criteria.map(({ id, points, passed, evidence }) => ({ id, points, passed, evidence })),
        },
      ],
    },
    null,
    2
  )
);
