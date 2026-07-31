# The 03 Sub-Regions Notebooks — What Was Built and Why (Record)

> Maintainer record, 2026-07-03 … 2026-07-09. Lives next to the notebooks in
> `version_2/` so it travels with them. Two notebooks share the topic:
> the PUBLIC fixture tutorial and the RESEARCH-side AVALON edition.

## 1. `03_hydro_Get_Subregions.ipynb` — public fixture tutorial (docs page)

REWRITTEN 2026-07-09 after a 3-expert panel review (pedagogy / narrative / visualization)
of the earlier restructure (896e00d97; that version preserved as
`03_hydro_Get_Subregions.pre-panel-rewrite.ipynb.bak`; the old 93-cell PyPlot catalog is in
`version_1/`). Runs on `RAMSES/manu_sim_sf_L14` output 400 (48 kpc box,
`gethydro(:rho, lmax=12, smallr=1e-11)`), kernel `mera-docs-1.12-_4t_-1.12` (dev Mera).
Title: "One Galaxy, One Mass Budget". 54 cells (22 code), 14 figures.

- Chapter arc: §1 galaxy + dissection-plan overlay (all coming cuts marked, only figure
  with ticks) → §2 hello-sub-region (one cut end to end; return type; defaults) →
  §3 one-sphere-three-masses (data-free split-cell CARTOON grid+circle first; all three
  treatments derived from ONE value-type extraction — whole cells = drop the :fraction
  column via `construct_datatype(select(...))`, centre test = `split=false`; nsub
  convergence demo vs analytic volume; triptych + coarse-west-rim zoom row; fraction
  scatter at TRUE cell centres, marker ∝ cellsize) → §4 budget piece by piece (disc
  edge-on split-vs-centre; nucleus + inverse partition; ring, no-sign-guarantee beat;
  envelope + fired shared-surface partition check) → §5 region algebra (lens bite in a
  ±3 kpc slab; annotated sculpture holes; inclusion–exclusion) → §6 THE LEDGER: four
  cylindrical zones (nucleus/inner/ring/rim) TILE the disc, table with total row,
  residual ~1e-16 — the panel's headline fix (old budget summed overlapping components
  to 140% of the box) → §7 how exact is exact (fringe bound + refine=2 on a slab) →
  §8 tilted regions (Axis3 schematic; volume vs analytic πR²·2h; z + y views) →
  §9 classic API reference → §10 guidance → summary echoing the checks.
- Figure grammar: ONE shared colour scale `SDLIM=(-3,3)` log10 Σ + one labelled colorbar
  per figure (`sd_bar!`), black axis backgrounds, pinned limits on every comparison,
  analytic surfaces dashed white/black, cyan = region being cut, orange = auxiliary,
  viridis reserved for :fraction, depth-restricted projections wherever a cavity is the
  subject (title states the slab), scale bars on tick-less anchor panels.
- Honesty: whole-cell = strict upper bound; centre test = near-cancelling estimate with
  NO guaranteed sign (measured: sphere +0.001%, disc −0.02%, ring −0.05%); fractions
  nsub-sampled for ALL curved regions (analytic only for axis-aligned Cuboid).

## MERGE (2026-07-12, commit db5fd2705, user request)

The public tutorial now carries EVERY example from both editions, all ported to
the fixture sim — 13 chapters, 74 cells, 21 figures: coarse-sphere bracket coda
(+93%/+19%), ring+inverse, operator-typing tip (\cup TAB / ASCII | & union()),
display-clip, tilted shell in 3 views (incl. along its own axis via los=),
in-plane bar, composites chapter (capstone w/ inclusion–exclusion, chimneys,
crescent, star-cluster Swiss cheese — 3% of disc volume holds 30% of its mass,
bows, filament tube), gas+stars budget (508,939 star particles; zones tile both
columns exactly), working-at-scale savedata/loaddata round-trip. Builder:
scratchpad/build_03_hydro.py (session-local). The AVALON edition remains
research-side and unpublished (its added value now: real-galaxy scale + RAM
discipline on 154M cells).

## refine_to (2026-07-12, feat 3bd6baf57, docs ddbbab4a1, user idea)

`subregion(obj, region; refine_to=[length, unit])` — target-size variant of
refine=k: per-cell depth ceil(log2(cellsize/target)), cap 10; mutually
exclusive with refine. Match to a projection's pxsize → pixel-sharp split
edges at any AMR level. Tutorial §7 demo: straddlers 0.375→0.047 kpc, fringe
0.265→0.024 kpc (≈1 px), mass invariant 0.99944. Suite 55: 86/86.

## @region macro + ~30x selection speedup (2026-07-13, 5beecf3a3 + 3cd694db2)

User asked for "macro pipelines for composites, readability + optimization" — split
into: (a) `@region [unit=..] [center=..] begin .. end` exported macro (injects shared
range_unit/center into region constructors unless explicit; named parts; returns plain
AbstractRegion); (b) evaluator speedup = analytic AABB per region (composes over
∩∪\!; oriented cylinders via support function; prune is bit-identical incl. inverse)
+ FUNCTION BARRIERS `_fracloop!`/`_keeploop!` (the closures from `_prepare` are
non-concrete; the barrier is the bulk of the win). Benchmark 16.7M cells: small sphere
4.58→0.124 s, 3-part composite 5.38→0.203 s. Suite 55: 95/95. Tutorial: §9 sculpture
as @region block (identical-region print), §13 pruning cost note. LESSON (hit 3x):
never inline python heredocs that write Julia triple-quoted/backslash source — use a
patch FILE with assembled quotes.

## 2. `03_hydro_Get_Subregions_avalon.ipynb` — AVALON research edition

Runs on AVALON `AV05CDhr` output 390 (MW-like; bulge/stellar-disc/DM halo are a STATIC
POTENTIAL; live matter = gas + 906,380 newly formed star particles; t ≈ 579 Myr,
box 48 kpc, levels 6–13, 167.0M cells full snapshot).

### Working set (RAM pattern — the file's own recipe cell regenerates it)
- Source `mera_v2/output_00390.jld2` is 25 GB (hydro table alone 13.7 GB;
  **`loaddata` reads a WHOLE datatype before windowing** — the key constraint).
- Working set at `AV05CDhr/mera_tutorial/output_00390.jld2`: **1.32 GB file,
  154,547,813 cells ≈ 5.8 GB RAM** — column cut FIRST (keep `:level,:cx,:cy,:cz,:rho`
  via `Mera.select` + `construct_datatype` + `selected_hydrovars=[1]`), THEN window
  `±16/±16/±6 kpc` about box centre (tall on purpose: keeps coarse above-plane cells).
- Spatial cuts alone DON'T work on AVALON: 88M level-13 cells concentrate in the inner
  disc (r<8 kpc alone holds 9.1 GB). The column cut is the lever.

### Final structure (2026-07-09, post fact-check; 77 cells, 22 figures)
1. Working set & RAM discipline (one object per section + `GC.gc()` releases)
2. The Galaxy in Five Components — the Dissection Plan (labeled overlay figure:
   circles r=3/7/13, thin-disc + fountain boxes, dotted test sphere) → components:
   inner disc `Cylinder(3,1.5)`, ring zone `CylShell(3,7,1.5)`, outer disc
   `CylShell(7,13,1.5)`, full disc `Cylinder(13,1.5)`, extraplanar
   `Cyl(13,4.5)\Cyl(13,1.5)`; ring additivity exact to −1.1e-16
3. One Sphere, Three Masses — measurement problem UNIFIED: coarse test sphere at
   (24,24,28) r=1.5 → bracket **+11.5% / −0.115%** vs split; triptych; fraction scatter;
   fringe bound (≤ one cell + one pixel: 0.103 vs 0.094+0.02 kpc); display-clip demo;
   `refine=2` demo on a slab (fringe 0.103→0.023 kpc ≈ ÷4, mass invariant 1.001)
4. Inverse selections (disc + ring; msum(region)+msum(inverse)=msum(gas) exactly)
5. Oriented regions: 3-D Axis3 schematic of the inclined ring FIRST, then the 30°
   `CylindricalShell(5,9,1; axis=[0.5,0,0.866])` in four views (volume orientation-
   invariant 351.85 vs 351.86 kpc³), in-plane bar (25°, vol 36.21 vs 36.19), 30° column
6. Composite constructions: capstone `(disc ∪ blister) \ chimney` face-on+edge-on,
   inclusion–exclusion; chimneys/crescent/Swiss-cheese each face-on+edge-on
   (cheese holes = spheres at young-star cluster sites FOUND FROM PARTICLES, search
   restricted to the 3–7 kpc annulus); bows plate `Cuboid \ 4 Spheres`; filament tube
   (3 stitched tilted cylinders along a polyline)
7. Payoff: gas + newly-formed-star budget per component (same region objects cut both
   datatypes), star overlay figure
8. Summary

### Honesty upgrades from the 2026-07-09 fact-check (16 findings)
[SUPERSEDED IN PART — see "The half-cell discovery" below. Corrections:]
- Fractions of CURVED regions are **nsub-sampled** (default 8/axis); analytic ONLY for
  axis-aligned Cuboid overlaps (the earlier note claiming analytic convex
  Sphere/Cylinder fractions was WRONG — `_prepare` samples them).
- The ~1% volume deviations (−1.0% AVALON halo sphere, +1.3% fixture sphere) were NOT
  sampling accuracy — they were the half-cell convention bug (fixed 21fbec5d5). With
  the fix, split volumes close on analytic truth to genuine nsub accuracy
  (fixture sphere: |dev| ≲ 0.05% at nsub=8, shrinking with nsub).
- Centre test (`split=false`) is NOT a guaranteed lower bound for ANY region — kept
  straddlers over-count, discarded ones under-count, the residual's sign is
  unguaranteed even for convex shapes (fixture sphere measured +0.001% ABOVE split).
- `refine=k` re-measures children → integrals move at the sampling level (1.00108).
- Projection fringe: split renders MORE beyond-surface map mass (0.03%) than the
  centre test (0.01%) because the centre test DELETES straddling cells (that's why it
  under-counts); split renders the correct mass feathered at cell scale.
- Classic symbol API: cylinder `direction` is **:z-only** (dispatcher errors on :x/:y);
  the old src docstring claiming :x/:y was stale → fixed in repo.

### Features/fixes BORN from this notebook (in the Mera repo)
- **`refine::Int=0` on `subregion(obj, region)`** (commit 09fa07c99): geometric octree
  subdivision of boundary cells to depth k; boundary localised to cellsize/2^k;
  raises result `lmax` so getvar/projection take the per-row level path (works on
  uniform grids too). 8 data-free tests in test 55. WARNING: refining a huge boundary
  (the whole 13-kpc disc surface at 154M cells) OOMs 32 GB — slab-scope refine demos.
- `subregioncylinder` docstring fix (direction :z-only).

### Infrastructure traps discovered (also in project memory)
- Jupyter kernel `julia-1.12-_4-threads_-1.12` points at
  `--project=…/Mingyu/mingyu_notebooks` whose Mera is a FROZEN snapshot copy
  (`~/.julia/packages/Mera/qPIBl`) — new src features are invisible there.
  Use the `mera-docs-1.12-*` kernels (drive `version_2` env, dev-tracked Mera,
  CairoMakie added) for anything needing current Mera.
- The AVALON notebook is NOT in `pages.manifest` (research-side; one manifest line +
  nav entry publishes it). Standalone HTML rendered next to it.
- Pre-restructure backup: `03_hydro_Get_Subregions_avalon.pre-restructure.ipynb.bak`.

### Open ideas
- Same restructure treatment for the particles/clumps sibling notebooks.
- Off-axis vs axis-aligned pixel-count discrepancy at equal pxsize — investigated
  2026-07-09 (see the answer in the session notes / below if appended).

## The half-cell discovery (2026-07-09, fix commit 21fbec5d5)

Found while fact-checking the rewritten public tutorial: its sphere-volume check
deviated +1.3% from (4/3)πR³ **independent of nsub** — impossible for correct
fractions on a tiling mesh (box closure Σvol==48³ is exact, no duplicate rows).

**Root cause:** Mera has TWO cell-position conventions. The RAMSES reader stores
`cx = floor(centre·2^l)+1`, so the physical cell centre is **(cx−0.5)·Δ** — and the
projection kernels use exactly that ("RAMSES-consistent", projection_hydro ~2199).
But `getvar(:x)` returns `cx·Δ` (the upper cell edge), and the value-type region
algebra AND the classic symbol subregion both tested cells at `cx·Δ` — half a LOCAL
cell off, a different physical offset per AMR level. Single-level data → harmless
translation (why the uniform-grid tests never caught it); mixed levels → biased
integrals and the **"franzig" split edges** (region machinery and renderer disagreed
about where coarse cells sit — the original user observation that led to refine=k).

**Fixed (21fbec5d5):** value-type region algebra now evaluates at (cx−0.5)·Δ (main
loop + refine children). Mixed-level regression test added (refined-half fixture;
axis-aligned cuboid = sampling-free, rtol 1e-10). Three tests retired that had
encoded "centre test always over-counts" — its sign is not guaranteed.

**Still on the OLD cx·Δ convention (pending decision — behaviour-visible):**
`getvar(:x/:y/:z)` (and derived positions/radii), classic symbol
`subregion`/`shellregion` (their cuts are half-a-local-cell off), external readers'
load-time window (`_external_select`), and the multicode contract test that
enshrines `getvar(:x)==cx·Δ`. Aligning all of these with the projection convention
is option "B" — needs the user's call (changes every position output by half a cell).

**Option B EXECUTED (2026-07-10, commit 1411af8a3, user decision):** getvar(:x/:y/:z),
classic subregion/shellregion (hydro/gravity/RT), _external_keep, immersive
lookup/interpolation ALL moved to (cx−0.5)·Δ; contract test 59 updated; off-axis
projections now agree with axis-aligned. Validated: data-free tier 1790/1790,
focused data-backed 1395/1395. RAMSES's own source confirms the convention
(amr2map.f90: xc=(dble(ix)-0.5D0)*dx; init_amr.f90: (ix+0.5) for 0-based).

**AVALON notebook RE-RUN on the fixed code (2026-07-10) + text pass:** 0 errors,
22 figures. The fix transformed its numbers: halo-sphere volume deviation
−1.0% → **+0.0047%** (true nsub sampling), centre test +0.133% (sign flipped —
no-guarantee framing now in text), tilted ring volume == analytic to 5 digits,
rendered fringe 0.103 → **0.003 kpc ≈ one map pixel** (the old "cell-sized
fringe" was mostly the half-cell misalignment), split-vs-centre beyond-surface
map mass now both ~0.01%, refine mass-invariance exactly 1.0. Text cells
24/26/28/36/41/43/76 rewritten accordingly (refine's payoff reframed as
sub-cell selection geometry, not fringe removal). Standalone HTML re-rendered.
Pre-rerun backup: scratchpad nbbak/avalon.pre-convention-rerun.ipynb.bak (local,
drive full). The public fixture tutorial was rebuilt on the fixed code and its
docs page regenerated (commits 33ccafa47, ee257ed3a).

**Masking/Filtering DONE (2026-07-10, commit be6b540a7):** the three by-hand
filter variants in 05_multi_Masking_Filtering now teach (cx−0.5)·Δ; notebook
re-executed (0 errors, all three variants agree at 2.81234e9 Msol), docs page
regenerated. No stale cx·Δ formula remains in any notebook or docs page.

## Answer: off-axis vs axis-aligned pixel counts at equal pxsize (2026-07-09)

Verified in source + empirically (spiral_clumps, 20-kpc sphere, pxsize=[0.3,:kpc]):
axis-aligned 334×334, off-axis 143×143, tilted 144×143 — ALL with pixel = 0.2994 kpc.

- **Pixel SIZE is always identical** between the two paths: both compute
  `res = ceil(boxlen/pxsize)` and use `boxlen/res` — i.e. the effective pixel equals the
  requested pxsize only when it divides boxlen (0.3 on a 100-kpc box → 0.2994).
- **Pixel COUNTS differ by design (the frame, not the pixel):**
  - axis-aligned frames the requested window on the box-anchored lattice; with no
    window it spans the object's stored ranges — for region-algebra subregions that is
    the FULL BOX;
  - off-axis ALWAYS auto-fits the AABB of the rotated selected cells, padded by
    1 pixel + half the coarsest selected cell's projected shadow per side, snapped to
    whole pixels (projection_hydro.jl ~1601-1620). Rotation stretches the AABB (≤√2)
    and the coarse-cell padding varies with the selection → counts vary between views.
- Practice: treat pixel size as the invariant; to compare maps, pin the frame
  (explicit xrange/yrange on the axis map, or fixed axis limits when plotting).
