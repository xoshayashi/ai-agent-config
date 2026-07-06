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
const selfImprove = read("build/references/_self_improvement_protocol.md");
const selfImprovePanel = read("build/references/_self_improvement_reviewer_panel.md");
const selfImproveFailureModes = read("build/references/_self_improvement_failure_modes.md");
const selfImprovePruning = read("build/references/_self_improvement_pruning.md");
const selfImproveRuntime = read("build/runtime/self_improvement.py");
const closeoutConsistency = read("build/runtime/closeout_consistency.py");
const ibFormat = read("build/runtime/ib_format.py");
const kernel = read("build/runtime/economic_kernel.py");
const sourcePlan = read("build/runtime/source_plan_builder.py");
const capTable = read("build/runtime/cap_table_builder.py");
const tests = read("build/tests/test_build_model.py") + "\n" + read("build/tests/test_economic_quality.py");
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
        "20px",
        "No-Wrap Rule",
        "Fill span rules",
        "Borders are sparse accents",
        "one width per role",
        "Side-by-side tables",
      ]) &&
      includesAll(layout, [
        "No merged cells",
        "No wrapped text",
        "2.14",
        "one uniform width",
        "side-by-side semantic tables",
      ]) &&
      includesAll(ibFormat, [
        "IB_HARD_INPUT",
        "IB_FORMULA",
        "IB_LINK_INTRA",
        "IB_LINK_EXTERNAL",
        "FONT_SIZE_ALLOWED_CELLS",
        "INDENT_COL_WIDTH",
        "FMT_JPY_MILLION",
        "apply_semantic_border_span",
        "role_column_width_for_content",
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
    "session-log-self-improvement",
    10,
    [
      "SKILL.md",
      "build/references/_skill_invocation_protocol.md",
      "build/references/_self_improvement_protocol.md",
      "build/runtime/self_improvement.py",
      "build/evals/evals.json",
      "build/tests/test_build_model.py",
    ],
    () =>
      exists("build/references/_self_improvement_protocol.md") &&
      skill.includes("post-output/session-log-driven improvements") &&
      protocol.includes("_self_improvement_protocol.md") &&
      protocol.includes("At every closeout and every improvement prompt") &&
      includesAll(selfReview, ["self-improvement gate", "sanitized session evidence", "lowest durable layer"]) &&
      includesAll(selfImprove, [
        "Trigger Signals",
        "Evidence To Inspect",
        "Improvement Loop",
        "Research Intake",
        "Stop Conditions",
        "sanitized evidence",
        "one-off artifact issue",
        "reusable skill gap",
        "lowest durable layer",
        "regression proof",
        "validate_reflection_record",
        "Reflection Record",
        "Capability evals",
        "regression evals",
        "holdout/adversarial examples",
        "cost/latency",
        "milestone/human review",
        "raw local logs",
        "secrets",
        "X/public social posts only as weak signals",
        "_self_improvement_reviewer_panel.md",
        "_self_improvement_failure_modes.md",
        "_self_improvement_pruning.md",
        "validate_reflection_record_for_acceptance",
        "closeout_consistency.py",
      ]) &&
      includesAll(selfImprovePanel, [
        "Four Lenses",
        "R1 correctness and doctrine compliance",
        "R2 verification depth and honesty",
        "R3 generality and design health",
        "R4 artifact quality and readability",
        "The writer of the Reflection Record does not score it",
        "impression scores without citations are not admissible",
      ]) &&
      includesAll(selfImproveFailureModes, [
        "Model Collapse",
        "Reward Hacking / Goodhart",
        "Sycophancy",
        "Eval Overfit",
        "Non-Convergence",
        "Linked gates",
      ]) &&
      includesAll(selfImprovePruning, [
        "do not reflect",
        "n=1 evidence",
        "lowest durable layer",
        "Rules fail at the prompt and succeed at the boundary",
        "Deferred Candidate Format",
      ]) &&
      includesAll(selfImproveRuntime, [
        "validate_reflection_record",
        "validate_reflection_record_for_acceptance",
        "score_reflection_panel",
        "detect_sensitive_text",
        "SENSITIVE_PATTERNS",
        "overfit:company_specific_lesson",
        "x_signal:handle_not_stripped",
        "review_required:audit_or_doctrine_change",
      ]) &&
      includesAll(closeoutConsistency, [
        "check_closeout_consistency",
        "dangling_ref",
        "count_drift",
      ]) &&
      evals.includes("SELF_IMPROVEMENT_PROTOCOL") &&
      evals.includes("self_improvement_from_failed_session_log") &&
      evals.includes("self_improvement_panel_rejects_schema_valid_degradation") &&
      evals.includes("self_improvement_closeout_consistency_drift") &&
      evals.includes("self_improvement_failure_modes_mitigated") &&
      evals.includes("self_improvement_pruning_deferred_candidate") &&
      evals.includes("Reflection Record") &&
      tests.includes("test_self_improvement_protocol_triggers_from_logs_and_feedback") &&
      tests.includes("test_self_improvement_protocol_requires_regression_proof_and_privacy") &&
      tests.includes("test_self_improvement_reflection_validator_rejects_privacy_and_overfit_records") &&
      tests.includes("test_self_improvement_panel_rejects_schema_valid_quality_degradation") &&
      tests.includes("test_self_improvement_closeout_consistency_catches_links_and_count_drift") &&
      tests.includes("test_self_improvement_failure_modes_and_pruning_are_linked_from_gates")
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
        "test_default_layout_role_widths_are_workbook_consistent",
        "test_detect_table_block_does_not_fuse_side_by_side_tables",
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
