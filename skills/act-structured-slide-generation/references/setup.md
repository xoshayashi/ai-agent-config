# Environment Setup

Run every script from the skill directory unless an output path is explicit. Check first: the
machine may already have everything, in which case use the system `python3` and do not create a
venv (a venv only adds an activation step to every command).

```bash
python3 -c "import pptx, PIL, lxml, fontTools, graphviz, vl_convert" && \
  command -v soffice dot >/dev/null && echo "ready — no venv needed"
python3 scripts/setup_fonts.py --check   # the six static fonts the renderer measures with
```

## Fonts

`deck_text` measures every line with the same font files it draws with (Geist and Noto Sans JP,
400 / 600 / 700). Run `setup_fonts.py` without `--check` once to install them into
`~/Library/Fonts`; without them the line breaks and header limits are computed on a fallback font
and drift from the render. The Vega-Lite charts register the same font directories.

## Installing What Is Missing (macOS / Homebrew)

```bash
brew install graphviz                   # the `dot` CLI (relationship graphs)
brew install --cask libreoffice         # `soffice`, used to render .pptx → PDF/PNG
python3 -m pip install --user --break-system-packages python-pptx Pillow lxml fonttools \
                                        graphviz vl-convert-python pytest
```

Homebrew's Python is PEP 668 "externally managed", so plain `pip install` is refused;
`--user --break-system-packages` installs these packages into the user site instead. The repo's
`scripts/setup.sh` does the same from `scripts/requirements.txt`. Only reach for a venv if you
cannot install into the system Python:

```bash
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install -r scripts/requirements.txt
```

## Optional Dependencies

The image-asset dependencies (vl-convert-python, Graphviz) are imported lazily: a native-only deck
runs without them, and they are needed only when a deck uses an image chart `kind` or the
`diagram` pattern. matplotlib is not used.
