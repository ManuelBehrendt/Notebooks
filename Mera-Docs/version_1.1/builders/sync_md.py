#!/usr/bin/env python3
"""Copy markdown-cell sources from a freshly built notebook into an executed one.

Text-only edits do not change any output, so re-executing for them is waste. This
refuses to touch anything if the CODE cells differ in any way — that case needs a
real re-execution.

    python3 sync_md.py <built.ipynb> <executed.ipynb>
"""
import json, sys

built_p, exec_p = sys.argv[1], sys.argv[2]
built = json.load(open(built_p))
ex = json.load(open(exec_p))

b, e = built["cells"], ex["cells"]
if len(b) != len(e):
    sys.exit("REFUSED: cell counts differ (%d vs %d) — re-execute" % (len(b), len(e)))

for i, (cb, ce) in enumerate(zip(b, e)):
    if cb["cell_type"] != ce["cell_type"]:
        sys.exit("REFUSED: cell %d type differs — re-execute" % i)
    if cb["cell_type"] == "code" and cb["source"] != ce["source"]:
        sys.exit("REFUSED: code cell %d differs — re-execute" % i)

changed = 0
for cb, ce in zip(b, e):
    if cb["cell_type"] == "markdown" and cb["source"] != ce["source"]:
        ce["source"] = cb["source"]
        changed += 1

json.dump(ex, open(exec_p, "w"), indent=1)
open(exec_p, "a").write("\n")
print("synced %d markdown cell(s) into %s" % (changed, exec_p))
