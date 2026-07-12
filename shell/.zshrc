# ===================================================
# zsh 設定ファイル
# ===================================================

# --- 基本設定 ---
export LANG=ja_JP.UTF-8
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

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
alias codex-yolo='codex --dangerously-bypass-approvals-and-sandbox'
alias claude-yolo='claude --dangerously-skip-permissions'
alias agy-yolo='agy --dangerously-skip-permissions'
alias hermes-yolo='hermes --yolo'
alias copilot-yolo='copilot --allow-all'



# --- zsh-syntax-highlighting（コマンド色分け、必ず最後に読み込む）---
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  [ -r "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && source "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  unset _brew_prefix
fi
export PATH="$HOME/.local/bin:$PATH"

# Added by Antigravity
export PATH="$HOME/.antigravity/antigravity/bin:$PATH"

# Added by Antigravity IDE
export PATH="/Users/sh/.antigravity-ide/antigravity-ide/bin:$PATH"

