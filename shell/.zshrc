# ===================================================
# zsh 設定ファイル
# ===================================================

# --- 基本設定 ---
export LANG=ja_JP.UTF-8
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  export PATH="$_brew_prefix/opt/python/libexec/bin:$_brew_prefix/share/google-cloud-sdk/bin:$PATH"
  unset _brew_prefix
fi

# --- 履歴設定 ---
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS      # 重複コマンドを記録しない
setopt HIST_IGNORE_SPACE     # スペースで始まるコマンドを記録しない
setopt SHARE_HISTORY         # 複数ターミナル間で履歴を共有

# --- 補完設定 ---
autoload -Uz compinit && compinit
setopt AUTO_CD               # ディレクトリ名だけでcdできる
setopt CORRECT               # コマンドのスペルを自動修正
zstyle ':completion:*' menu select   # 補完候補をメニュー表示
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'  # 大文字小文字を区別しない

# --- zsh-autosuggestions（コマンド自動提案）---
# 過去の履歴からコマンドを薄いグレーで提案 → → キーで確定
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  [ -r "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && source "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
  unset _brew_prefix
fi
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=244"

# --- fzf（インタラクティブ検索）---
# Ctrl+R で履歴をインタラクティブ検索
# Ctrl+T でファイルをインタラクティブ選択
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v fzf >/dev/null 2>&1; then
  eval "$(fzf --zsh)"
fi
export FZF_DEFAULT_OPTS="
  --height 40%
  --border rounded
  --info inline
  --prompt '🔍 '
  --pointer '▶'
  --color 'hl:yellow,hl+:yellow'
"

# --- zoxide（スマートな cd コマンド）---
# z <ディレクトリ名の一部> で素早く移動できる
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

# --- 便利なエイリアス ---
alias ll='ls -lah'           # 詳細なファイル一覧
alias la='ls -la'
alias ..='cd ..'             # 一つ上のディレクトリへ
alias ...='cd ../..'         # 二つ上のディレクトリへ
alias gs='git status'        # Gitの状態確認
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'

# --- Starship プロンプト（最後に読み込む）---
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi

alias c='clear'
# Keep permissive CLI launches explicit so base commands retain their defaults.
alias gemini-yolo='gemini --yolo'
alias codex-yolo='codex --dangerously-bypass-approvals-and-sandbox'
alias claude-yolo='claude --dangerously-skip-permissions'
alias agy-yolo='agy --dangerously-skip-permissions'
alias hermes-yolo='hermes --yolo'
alias copilot-yolo='copilot --allow-all'

# --- Ollama BYOK for Copilot CLI ---
export OLLAMA_CONTEXT_LENGTH=16384
export COPILOT_PROVIDER_MAX_PROMPT_TOKENS=8192
export COPILOT_PROVIDER_MAX_OUTPUT_TOKENS=8192

# --- zsh-syntax-highlighting（コマンド色分け、必ず最後に読み込む）---
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  [ -r "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && source "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  unset _brew_prefix
fi
export PATH="$HOME/.local/bin:$PATH"

# --- Slack MCP bearer token (macOS Keychain) ---
if [[ -z "${SLACK_MCP_USER_TOKEN:-}" ]]; then
  _slack_mcp_user_token=$(security find-generic-password -a "$USER" -s "codex_slack_mcp_user_token" -w 2>/dev/null)
  if [[ -n "$_slack_mcp_user_token" ]]; then
    export SLACK_MCP_USER_TOKEN="$_slack_mcp_user_token"
  fi
  unset _slack_mcp_user_token
fi

# --- APIキー: GCP Secret Manager → macOS Keychain にキャッシュ ---
# 編集方法:
#   - 鍵を追加:    gcloud secrets create <name> --data-file=- --project=$GSECRETS_PROJECT
#                  下の GSECRETS_LIST に "<name>:<ENV_VAR>" を追加
#   - 鍵を更新:    echo -n "新値" | gcloud secrets versions add <name> --data-file=- --project=$GSECRETS_PROJECT
#                  その後 `secrets-sync` を実行してKeychainを更新
#   - 値を確認:    secrets-list
GSECRETS_PROJECT="sh-secrets-mgr-2026"
GSECRETS_LIST=("jina-api-key:JINA_API_KEY")

_gsecret_get() {
  local name="$1" val
  val=$(security find-generic-password -a "$USER" -s "gsecret_${name}" -w 2>/dev/null)
  if [[ -z "$val" ]]; then
    val=$(gcloud secrets versions access latest --secret="$name" --project="$GSECRETS_PROJECT" 2>/dev/null) || return 1
    security add-generic-password -a "$USER" -s "gsecret_${name}" -w "$val" -U >/dev/null 2>&1
  fi
  print -r -- "$val"
}

secrets-sync() {
  local entry name val
  for entry in "${GSECRETS_LIST[@]}"; do
    name="${entry%%:*}"
    if val=$(gcloud secrets versions access latest --secret="$name" --project="$GSECRETS_PROJECT" 2>/dev/null); then
      security add-generic-password -a "$USER" -s "gsecret_${name}" -w "$val" -U >/dev/null 2>&1
      echo "✓ $name"
    else
      echo "✗ $name (fetch failed — gcloud auth login が必要かも)"
    fi
  done
}

secrets-list() {
  local entry name var val
  for entry in "${GSECRETS_LIST[@]}"; do
    name="${entry%%:*}"; var="${entry##*:}"
    val=$(security find-generic-password -a "$USER" -s "gsecret_${name}" -w 2>/dev/null)
    if [[ -n "$val" ]]; then
      printf '  %-20s → %s (cached, %d chars)\n' "$var" "$name" "${#val}"
    else
      printf '  %-20s → %s (NOT CACHED)\n' "$var" "$name"
    fi
  done
}

for _gs_entry in "${GSECRETS_LIST[@]}"; do
  _gs_name="${_gs_entry%%:*}"
  _gs_var="${_gs_entry##*:}"
  if _gs_val=$(_gsecret_get "$_gs_name"); then
    export "${_gs_var}=${_gs_val}"
  fi
done
unset _gs_entry _gs_name _gs_var _gs_val

# Added by Antigravity
export PATH="$HOME/.antigravity/antigravity/bin:$PATH"

# Added by Antigravity IDE
export PATH="/Users/sh/.antigravity-ide/antigravity-ide/bin:$PATH"

# Google Cloud SDK installed outside Homebrew on this machine.
if [ -f '/Users/sh/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/sh/Downloads/google-cloud-sdk/path.zsh.inc'; fi
if [ -f '/Users/sh/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/sh/Downloads/google-cloud-sdk/completion.zsh.inc'; fi
