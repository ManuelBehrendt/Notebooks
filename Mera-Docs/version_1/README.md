# version_1 — archived

**This folder is kept only so that older links keep working. For current Mera, use
[`../version_1.1/`](../version_1.1/).**

The live documentation at <https://manuelbehrendt.github.io/Mera.jl/> is generated from
`version_1.1/`. Nothing here is regenerated or checked against current Mera.

## What changed since

These notebooks predate three changes that alter results **without raising an error**, so running
them against a current Mera and trusting the numbers would be a mistake:

- **`getvar(gas, :T)` returns code units now**, and honours its unit argument. It used to return
  Kelvin regardless. Ask for `getvar(gas, :T, :K)` if you want Kelvin. Two notebooks here call it.
- **`cx` + `level` gives the physical cell centre**, `(cx-0.5)·Δ`, not `cx·Δ` — a half-cell shift
  in any position derived that way.
- **On AREPO/IllustrisTNG, `getvar(:birth)` is refused** in favour of `:aform`, because the stored
  field is a formation scale factor rather than a time. RAMSES `:birth` is unchanged, so the
  notebooks here that use it remain correct for RAMSES data.

See the Mera.jl CHANGELOG for the full list and the migration notes.
