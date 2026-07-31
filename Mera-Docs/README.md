# Mera-Docs — notebooks behind the Mera.jl documentation

These notebooks are the **source of truth** for the [Mera.jl](https://github.com/ManuelBehrendt/Mera.jl)
documentation. Each one is converted to Markdown and becomes a page on the
[docs site](https://manuelbehrendt.github.io/Mera.jl/), and every tutorial page links back here so
you can run it yourself.

| folder | status | use it for |
|---|---|---|
| **`version_1.1/`** | **current** — tracks Mera v1.8.0 and later | everything |
| `version_1/` | archived — kept so older links keep working | reading history only |

## Which one do I want?

`version_1.1/`. It is the set the live documentation is generated from, so what you read on the
docs site and what the notebook does are the same thing.

## Why `version_1/` is still here

Older links — in papers, talks, emails and bookmarks — point at `version_1/` URLs, and deleting the
folder would break all of them permanently. It costs 25 MB to keep, so it stays.

**Do not use it as a guide to current Mera.** The API has moved since, in ways that change results
without raising an error:

- `getvar(gas, :T)` now returns **code units** and honours its unit argument. It previously
  returned Kelvin regardless, so a `version_1` notebook asking for `:T` gets different numbers
  today. Two notebooks in that folder are affected.
- `cx` + `level` now yields the physical cell **centre**, `(cx-0.5)·Δ`, rather than `cx·Δ`.
- On AREPO/IllustrisTNG data, `getvar(:birth)` is refused in favour of `:aform` — the stored field
  is a formation *scale factor*, not a time. (RAMSES `:birth` is unchanged, so the 15 notebooks in
  `version_1/` that use it are still correct for RAMSES.)

The current behaviour is documented in the Mera.jl CHANGELOG.

## Running them

Each notebook is executed end to end against real simulation output before publication, so the
outputs you see are real. Reproducing them needs the corresponding snapshots; the paths at the top
of each notebook say which. Large inputs and export products are deliberately not committed here —
see `version_1.1/.gitignore` for what is excluded and why.
