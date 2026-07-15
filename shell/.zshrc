# ==============================================================================
#  _   _   _   _   _   _   _  
# | \_/ | / \ / \_/ | / \_/ | 
# |  _  | | | |  _  | |  _  |   Zsh Configuration File
# |_| |_| \_/ |_| |_| |_| |_|   User: sh
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. 環境変数 & PATH 設定 (Environment Variables & PATH)
# ------------------------------------------------------------------------------
# パス関係を一括して整理（優先度の高い順）
export PATH="/Users/sh/.antigravity-ide/antigravity-ide/bin:$HOME/.antigravity/antigravity/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# 基本文字コード
export LANG=ja_JP.UTF-8

# Pythonキャッシュファイル（.pyc）の生成を抑制
export PYTHONDONTWRITEBYTECODE=1


# ------------------------------------------------------------------------------
# 2. 履歴設定 (History Settings)
# ------------------------------------------------------------------------------
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

setopt HIST_IGNORE_DUPS      # 重複コマンドを記録しない
setopt HIST_IGNORE_SPACE     # スペースで始まるコマンドを記録しない
setopt SHARE_HISTORY         # 複数ターミナル間で履歴を共有


# ------------------------------------------------------------------------------
# 3. 補完 & シェルオプション (Shell Options & Autocompletion)
# ------------------------------------------------------------------------------
autoload -Uz compinit && compinit

setopt AUTO_CD               # ディレクトリ名だけでcdできるようにする
setopt CORRECT               # コマンドのスペルミスを自動修正

zstyle ':completion:*' menu select                 # 補完候補をキー矢印でメニュー選択可能に
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' # 補完時に大文字小文字を区別しない


# ------------------------------------------------------------------------------
# 4. 便利なエイリアス設定 (Aliases)
# ------------------------------------------------------------------------------
# --- 基本操作 ---
alias c='clear'
alias ll='ls -lah'           # 詳細ファイルリスト
alias la='ls -la'            # 隠しファイル含むリスト
alias ..='cd ..'             # 1つ上の階層へ
alias ...='cd ../..'         # 2つ上の階層へ

# --- Git ショートカット ---
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'

# --- AIエージェント設定 (YOLOモード) ---
# 警告・承認およびサンドボックスをスキップして高速実行
alias codex-yolo='codex --dangerously-bypass-approvals-and-sandbox'
alias claude-yolo='claude --dangerously-skip-permissions'
alias agy-yolo='agy --dangerously-skip-permissions'
alias hermes-yolo='hermes --yolo'
alias copilot-yolo='copilot --allow-all'


# ------------------------------------------------------------------------------
# 5. 外部プラグイン & 統合ツール (Plugins & Integrations)
# ------------------------------------------------------------------------------

# --- zsh-autosuggestions（コマンド自動提案） ---
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  [ -r "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ] && source "$_brew_prefix/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
  unset _brew_prefix
fi
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=244" # 提案時のテキストカラー（薄いグレー）

# --- fzf（インタラクティブ検索） ---
# Ctrl+R: 履歴検索 / Ctrl+T: ファイル選択
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

# --- zoxide（スマートな cd コマンド） ---
# z <一部のディレクトリ名> で即座に移動
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

# --- Starship プロンプト ---
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi


# ------------------------------------------------------------------------------
# 6. シンタックスハイライト (Syntax Highlighting) - ★必ず最下部に配置すること
# ------------------------------------------------------------------------------
if [[ -o interactive && "${TERM:-}" != "dumb" ]] && command -v brew >/dev/null 2>&1; then
  _brew_prefix="$(brew --prefix)"
  [ -r "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ] && source "$_brew_prefix/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  unset _brew_prefix
fi
