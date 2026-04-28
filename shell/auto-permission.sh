# Managed auto-permission startup wrappers for the three LLM CLIs distributed by ai-agent-config.
#
# Sourcing this file makes Codex, Gemini CLI, and Claude Code start interactive
# sessions in their permissive / auto-approval mode by default, while leaving
# maintenance subcommands (auth, install, mcp, plugin, doctor, etc.) untouched.
#
# Installed by scripts/setup.sh as a stable symlink at:
#   ${AI_AGENT_SHELL_LINK:-$HOME/.llm-config/auto-permission.sh}
# and sourced from the user's shell rc through a managed marker block.
#
# Removed cleanly by scripts/uninstall.sh.

# Codex: bypass approvals and sandbox for interactive sessions.
alias codex='codex --dangerously-bypass-approvals-and-sandbox'

# Gemini CLI: yolo mode (auto-accept all tool calls).
alias gemini='gemini --yolo'

# Claude Code: auto permission mode for normal sessions, but pass maintenance
# subcommands and flag-only invocations through unchanged so they can still
# manage installation, auth, MCP, plugins, and explicit permission overrides.
claude() {
  case "$1" in
    agents|auth|auto-mode|doctor|install|mcp|plugin|plugins|setup-token|update|upgrade|--help|-h|--version|-v|--permission-mode|--dangerously-skip-permissions|--allow-dangerously-skip-permissions)
      command claude "$@"
      ;;
    *)
      command claude --permission-mode auto "$@"
      ;;
  esac
}
