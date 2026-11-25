#!/bin/bash
# generate all cartoon frames, 4 in parallel; 'ref' rows use the smuggler reference for consistency
cd "$(dirname "$0")"
python3 -I -c "
import json
for r in json.load(open('toons.json')): print(r[4]+'\t'+(r[6] or '-')+'\t'+r[5])
" | while IFS=$'\t' read -r name ref prompt; do
  [ -f art/$name.png ] && continue
  if [ "$ref" = "ref" ]; then
    echo "python3 -I tools_img.py art/$name.png \"Keep the same character design as in @img1. $prompt\" 16:9 art/test_smuggler.png"
  else
    echo "python3 -I tools_img.py art/$name.png \"$prompt\" 16:9"
  fi
done > build_cmds.txt
xargs -P 4 -I{} bash -c '{} || echo FAIL: {}' < build_cmds.txt
echo GEN_DONE
