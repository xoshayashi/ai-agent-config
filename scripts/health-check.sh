#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1


format=${AI_AGENT_HEALTH_FORMAT:-text}
strict=${AI_AGENT_HEALTH_STRICT:-0}
redact_output=${AI_AGENT_HEALTH_REDACT:-1}

case "${1:-}" in
  --json) format=json ;;
  --text) format=text ;;
  '') ;;
  *) printf 'error: usage: %s [--text|--json]\n' "$0" >&2; exit 2 ;;
esac

case "$format" in
  text|json) ;;
  *) printf 'error: AI_AGENT_HEALTH_FORMAT must be text or json\n' >&2; exit 2 ;;
esac
case "$strict" in
  0|1) ;;
  *) printf 'error: AI_AGENT_HEALTH_STRICT must be 0 or 1\n' >&2; exit 2 ;;
esac
case "$redact_output" in
  0|1) ;;
  *) printf 'error: AI_AGENT_HEALTH_REDACT must be 0 or 1\n' >&2; exit 2 ;;
esac

script_path=$0
case "$script_path" in
  */*) script_dir=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P) ;;
  *) script_dir=$(CDPATH= cd "$(dirname "$(command -v "$script_path")")" && pwd -P) ;;
esac

expand_home() {
  case "$1" in
    '~') printf '%s\n' "$HOME" ;;
    '~/'*) printf '%s/%s\n' "$HOME" "${1#~/}" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

json_escape() {
  printf '%s' "$1" | awk '
    BEGIN { ORS = "" }
    {
      gsub(/\\/, "\\\\")
      gsub(/"/, "\\\"")
      gsub(/\t/, "\\t")
      gsub(/\r/, "\\r")
      if (NR > 1) { printf "\\n" }
      printf "%s", $0
    }
  '
}

json_nullable_bool() {
  case "$1" in
    true) printf true ;;
    false) printf false ;;
    *) printf null ;;
  esac
}

status_rank=0
mark_status() {
  case "$1" in
    fail) status_rank=2 ;;
    warn) [ "$status_rank" -lt 1 ] && status_rank=1 ;;
  esac
  return 0
}

overall_status() {
  case "$status_rank" in
    0) printf ok ;;
    1) printf warn ;;
    *) printf fail ;;
  esac
}

display_path() {
  path=$1
  if [ "$redact_output" = "0" ]; then
    printf '%s' "$path"
    return 0
  fi
  case "$path" in
    '') printf '' ;;
    */*) printf '.../%s' "$(basename "$path")" ;;
    *) printf '%s' "$path" ;;
  esac
}

command_status() {
  if command -v "$1" >/dev/null 2>&1; then
    printf ok
  else
    printf missing
  fi
}

link_status_for() {
  dst=$1
  expected=$2
  parent=$(dirname "$dst")
  if [ ! -d "$parent" ]; then
    printf missing-parent
  elif [ ! -L "$dst" ]; then
    printf missing
  else
    current=$(readlink "$dst" 2>/dev/null || true)
    if [ "$current" = "$expected" ]; then
      printf ok
    else
      printf mismatch
    fi
  fi
}

skills_status_for() {
  home=$1
  target_root="$home/skills"
  if [ ! -d "$target_root" ]; then
    printf missing-parent
    return 0
  fi

  status=ok
  for skill_dir in "$skill_source_root"/*; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    link_status=$(link_status_for "$target_root/$skill_name" "$skill_dir")
    case "$link_status" in
      ok) ;;
      *)
        status=$link_status
        break
        ;;
    esac
  done
  printf '%s' "$status"
}

notify_status_for() {
  config_file=$1
  if [ ! -f "$config_file" ]; then
    printf missing
  elif grep -Fq "/notifications/notify.sh" "$config_file" 2>/dev/null; then
    printf ok
  else
    printf missing
  fi
}

default_config_home=$(CDPATH= cd "$script_dir/.." && pwd -P)
config_home=$(expand_home "${AI_AGENT_CONFIG_HOME:-$default_config_home}")
codex_home=$(expand_home "${AI_AGENT_CODEX_HOME:-$HOME/.codex}")
claude_home=$(expand_home "${AI_AGENT_CLAUDE_HOME:-$HOME/.claude}")
home_dir=$(expand_home "${AI_AGENT_HOME:-$HOME}")
skill_source_root="$config_home/skills"

git_status=$(command_status git)
claude_status=$(command_status claude)
codex_status=$(command_status codex)
agy_status=$(command_status agy)

repo_status=fail
repo_branch=unknown
repo_dirty=unknown
if command -v git >/dev/null 2>&1 && [ -d "$config_home/.git" ]; then
  if git -C "$config_home" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    repo_status=ok
    repo_branch=$(git -C "$config_home" rev-parse --abbrev-ref HEAD 2>/dev/null || printf unknown)
    if [ -n "$(git -C "$config_home" status --porcelain 2>/dev/null)" ]; then
      repo_dirty=true
      repo_status=warn
      mark_status warn
    else
      repo_dirty=false
    fi
  else
    mark_status fail
  fi
else
  mark_status fail
fi

if [ "$git_status" != "ok" ]; then
  mark_status warn
fi

codex_agents_status=$(link_status_for "$codex_home/AGENTS.md" "$config_home/instructions/AGENTS.md")
codex_shared_status=$(link_status_for "$codex_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
codex_design_status=$(link_status_for "$codex_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
codex_skills_status=$(skills_status_for "$codex_home")
claude_entry_status=$(link_status_for "$claude_home/CLAUDE.md" "$config_home/instructions/CLAUDE.md")
claude_shared_status=$(link_status_for "$claude_home/AI_AGENT_INSTRUCTIONS.md" "$config_home/instructions/AI_AGENT_INSTRUCTIONS.md")
claude_design_status=$(link_status_for "$claude_home/DESIGN.md" "$config_home/instructions/DESIGN.md")
claude_skills_status=$(skills_status_for "$claude_home")

shell_zshrc_status=$(link_status_for "$home_dir/.zshrc" "$config_home/shell/.zshrc")

codex_notify_status=$(notify_status_for "$codex_home/hooks.json")
claude_notify_status=$(notify_status_for "$claude_home/settings.json")

python3_status=$(command_status python3)
pip_status=$(command_status pip)
pip3_status=$(command_status pip3)
openpyxl_status=missing
if command -v python3 >/dev/null 2>&1 && python3 -c 'import openpyxl' >/dev/null 2>&1; then
  openpyxl_status=ok
fi
pptx_deps_status=missing
# graphviz は python パッケージだけでは動かない(CLI の dot が必要) — 実行ファイルまで
# 揃って初めて ok にする(org_tree/node_graph がビルド時に落ちる欠落を検知する)
if command -v python3 >/dev/null 2>&1 && python3 -c 'import pptx, PIL, lxml, fontTools, matplotlib, matplotlib_venn, graphviz' >/dev/null 2>&1 && command -v dot >/dev/null 2>&1; then
  pptx_deps_status=ok
fi
libreoffice_status=$(command_status libreoffice)
pdftoppm_status=$(command_status pdftoppm)
# スライド skill が採寸に使う Geist / Noto Sans JP。無いと描画が警告なく崩れるので必ず見る。
fonts_status=missing
fonts_script="$skill_source_root/act-structured-slide-generation/scripts/setup_fonts.py"
if command -v python3 >/dev/null 2>&1 && [ -f "$fonts_script" ] \
  && python3 "$fonts_script" --check >/dev/null 2>&1; then
  fonts_status=ok
fi

# 総合判定には、このリポジトリが設定する主役 CLI(claude / codex / agy)の存在と、
# スライド用フォントも入れる — これらが欠けていても ok と出す嘘の合格を防ぐ。
for status in \
  "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$codex_skills_status" \
  "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$claude_skills_status" \
  "$shell_zshrc_status" \
  "$codex_notify_status" "$claude_notify_status" \
  "$claude_status" "$codex_status" "$agy_status" \
  "$python3_status" "$openpyxl_status" "$pptx_deps_status" "$fonts_status"; do
  [ "$status" = "ok" ] || mark_status warn
done

if [ "$format" = "json" ]; then
  printf '{\n'
  printf '  "overall": "%s",\n' "$(overall_status)"
  printf '  "redacted": %s,\n' "$([ "$redact_output" = "1" ] && printf true || printf false)"
  printf '  "config_home": "%s",\n' "$(json_escape "$(display_path "$config_home")")"
  printf '  "codex_home": "%s",\n' "$(json_escape "$(display_path "$codex_home")")"
  printf '  "claude_home": "%s",\n' "$(json_escape "$(display_path "$claude_home")")"
  printf '  "repository": {"status": "%s", "branch": "%s", "dirty": %s},\n' "$repo_status" "$(json_escape "$repo_branch")" "$(json_nullable_bool "$repo_dirty")"
  printf '  "commands": {"git": "%s", "claude": "%s", "codex": "%s", "agy": "%s"},\n' "$git_status" "$claude_status" "$codex_status" "$agy_status"
  printf '  "links": {\n'
  printf '    "codex_AGENTS.md": "%s", "codex_AI_AGENT_INSTRUCTIONS.md": "%s", "codex_DESIGN.md": "%s", "codex_skills": "%s",\n' "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$codex_skills_status"
  printf '    "claude_CLAUDE.md": "%s", "claude_AI_AGENT_INSTRUCTIONS.md": "%s", "claude_DESIGN.md": "%s", "claude_skills": "%s",\n' "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$claude_skills_status"
  printf '    "shell_.zshrc": "%s"\n' "$shell_zshrc_status"
  printf '  },\n'
  printf '  "notifications": {"codex": "%s", "claude": "%s"},\n' "$codex_notify_status" "$claude_notify_status"
  printf '  "skill_dependencies": {"python3": "%s", "pip": "%s", "pip3": "%s", "openpyxl": "%s", "pptx_deps": "%s", "fonts": "%s", "libreoffice": "%s", "pdftoppm": "%s"}\n' "$python3_status" "$pip_status" "$pip3_status" "$openpyxl_status" "$pptx_deps_status" "$fonts_status" "$libreoffice_status" "$pdftoppm_status"
  printf '}\n'
else
  printf 'AI Agent Config health: %s\n' "$(overall_status)"
  printf 'redacted: %s\n' "$([ "$redact_output" = "1" ] && printf yes || printf no)"
  printf 'config: %s\n' "$(display_path "$config_home")"
  printf 'repository: %s branch=%s dirty=%s\n' "$repo_status" "$repo_branch" "$repo_dirty"
  printf 'commands: git=%s claude=%s codex=%s agy=%s\n' "$git_status" "$claude_status" "$codex_status" "$agy_status"
  printf 'links: codex(AGENTS=%s shared=%s design=%s skills=%s) claude(CLAUDE=%s shared=%s design=%s skills=%s)\n' \
    "$codex_agents_status" "$codex_shared_status" "$codex_design_status" "$codex_skills_status" \
    "$claude_entry_status" "$claude_shared_status" "$claude_design_status" "$claude_skills_status"
  printf 'shell: zshrc=%s\n' "$shell_zshrc_status"
  printf 'notifications: codex=%s claude=%s\n' \
    "$codex_notify_status" "$claude_notify_status"
  printf 'skill dependencies: python3=%s pip=%s pip3=%s openpyxl=%s pptx_deps=%s fonts=%s libreoffice=%s pdftoppm=%s\n' \
    "$python3_status" "$pip_status" "$pip3_status" "$openpyxl_status" "$pptx_deps_status" "$fonts_status" "$libreoffice_status" "$pdftoppm_status"
fi

if [ "$strict" = "1" ] && [ "$(overall_status)" != "ok" ]; then
  exit 1
fi
