#!/usr/bin/env bash
# Regenerate body.tex from the canonical markdown.
#   ../S10-WRITEUP-DRAFT.md  --(sed: from "## Abstract")-->  _src_body.md
#     --(pandoc)-->  _body_pandoc.tex  --(reformat.py)-->  body.tex
set -euo pipefail
cd "$(dirname "$0")"
DRAFT=../S10-WRITEUP-DRAFT.md

# body = everything from the Abstract heading to EOF (title is set in main.tex)
sed -n '/^## Abstract/,$p' "$DRAFT" > _src_body.md

pandoc _src_body.md -f gfm -t latex --wrap=preserve --shift-heading-level-by=-1 \
  -o _body_pandoc.tex

python3 reformat.py
echo "body.tex rebuilt."
