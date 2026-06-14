# macOS Settings

このディレクトリには、`scripts/setup.sh` が再適用する macOS 固有の設定スナップショットを置きます。

## Layout

- `defaults/*.plist`: `defaults import` で再適用する macOS defaults snapshot
- `displays/current.sh`: `displayplacer` で再適用する現在のディスプレイ配置
- `keybindings/DefaultKeyBinding.dict`: 存在する場合に `~/Library/KeyBindings/` へ配置する Cocoa key bindings

`defaults` snapshot は現在のマシンの基本設定を再現するためのものです。最近使った項目、履歴、analytics timestamp などの揮発情報は保存しません。`pmset` の電源設定と `displayplacer` のディスプレイ配置は `scripts/setup.sh` から別途適用します。
