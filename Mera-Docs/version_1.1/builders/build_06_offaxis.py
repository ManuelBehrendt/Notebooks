#!/usr/bin/env python3
"""Build 06_offaxis_Projection.ipynb from the expert-panel blueprint.

The blueprint is the panel's structured output; this script applies the corrections that only
running the code could reveal, then emits the notebook (+ a preflight .jl).
"""
import json, sys, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BLUEPRINT = os.path.join(HERE, "06_offaxis_blueprint.json")
NB_DIR = "/Volumes/FASTStorage/Simulations/Mera-Docs/version_1.1"
OUT_NB = os.path.join(NB_DIR, "06_offaxis_Projection.ipynb")
OUT_JL = os.path.join(HERE, "preflight_06_offaxis.jl")

b = json.load(open(BLUEPRINT))["result"]["blueprint"]

# ─────────────────────────────────────────────────────────────────────────────
# Corrections. Each is something the panel asserted but could not check, or a
# house-keeping fix. Keyed by (chapter, cell index).
# ─────────────────────────────────────────────────────────────────────────────

# 1. data path: match the sibling notebooks, with an ENV override
PATH_OLD = 'joinpath(ENV["MERA_TEST_DATA"], "RAMSES/spiral_clumps")'
PATH_NEW = ('joinpath(get(ENV, "MERA_TEST_DATA", "/Volumes/FASTStorage/Simulations/Mera-Tests"),\n'
            '                "RAMSES/spiral_clumps")')

# 2. savemap/loadmap must not litter the notebook directory
SAVE_OLD, SAVE_NEW = 'savemap(fo, "faceon_sd.jld2"', 'savemap(fo, joinpath(tempdir(), "faceon_sd.jld2")'
LOAD_OLD, LOAD_NEW = 'loadmap("faceon_sd.jld2"', 'loadmap(joinpath(tempdir(), "faceon_sd.jld2")'

# 3. MEASURED: the runtime Chapter 0 must state (blueprint's own "measure first" rule)
RUNTIME = "**≈ 90 s** end-to-end at `julia -t 8` (19 code cells, ~30 hydro `projection` calls)"

# 4. MEASURED: the sigma_LOS claim does NOT reproduce — rewrite the cell and its prose
SIGMA_CODE_OLD_HEAD = "# σ_LOS is a width measured INSIDE a pixel, so it depends on the pixel."
SIGMA_CODE = '''# Does σ_LOS depend on how finely you pixelate? Measure it rather than assume.
# (cells here are 0.78 / 1.56 / 3.12 kpc, so this sweep straddles the cell size)
med(A) = median(filter(x -> isfinite(x) && x > 0, vec(Float64.(A))))
println(rpad("pxsize [kpc]", 15), rpad("median σ_LOS", 16), "mean σ_LOS")
for px in (0.15, 0.6, 2.4)
    p = projection(gas, :σlos, :km_s; direction=:edgeon, center=[:bc], fov=15, fov_unit=:kpc,
                   aperture=:square, pxsize=[px, :kpc], verbose=false, show_progress=false)
    v = filter(x -> isfinite(x) && x > 0, vec(Float64.(p.maps[:σlos])))
    println(rpad(px, 15), rpad(round(median(v), digits=1), 16), round(mean(v), digits=1))
end'''

SIGMA_PROSE = '''Now the result that matters for trusting a σ map, and it is not the one you might expect.

A 16× change in pixel size moves the median σ_LOS by a few km/s, and the mean hardly at all. σ_LOS
is **not** dominated by how much sky one pixel covers — it is dominated by the spread of velocities
**along the ray**, and a sight line through a disc collects that spread no matter how finely you
sample the image plane. Only when the pixels grow past the local cell size (the last row: 2.4 kpc
pixels on 0.78–3.12 kpc cells) does transverse mixing start to add to the width.

That is a useful licence: choose `pxsize` for the *image* you want, and σ_LOS will not move under
you. It is also a warning about the opposite habit — refining the pixels will **not** resolve a
dispersion that is set by the depth of the structure you are looking through.'''

# 5. MEASURED: the epot map's "0.0" maximum is empty pixels, not physics
EPOT_OLD = '''println("gravity : maps ", collect(keys(pe.maps)), "   epot extrema ",
        round.(extrema(pe.maps[:epot]), sigdigits=3))'''
EPOT_NEW = '''# NB the raw extrema read (-0.53, 0.0) — that 0.0 is EMPTY pixels, not a physical potential.
# Report the filled pixels, and say how many were empty.
epot = pe.maps[:epot]; filled = filter(<(0), epot)
println("gravity : maps ", collect(keys(pe.maps)))
println("          epot over filled pixels ", round.(extrema(filled), sigdigits=4),
        "   (", count(iszero, epot), " of ", length(epot), " pixels empty)")'''

REWRITES = {}
LADDER = '# Same window as Chapter 1 — only `inclination` changes.\nlad0  = projection(gas, :sd, :Msol_pc2; inclination=0,  axis=:angmom, win...)\nlad30 = projection(gas, :sd, :Msol_pc2; inclination=30, axis=:angmom, win...)\nlad60 = projection(gas, :sd, :Msol_pc2; inclination=60, axis=:angmom, win...)\n\n# Is `direction=:faceon` the same as `inclination=0, axis=:angmom`? Separate the two halves of\n# that question — the LINE OF SIGHT and the ROLL — because the answer differs for each.\nprintln("max |ŵ_faceon − ŵ_inc0|     = ", maximum(abs, fo.los .- lad0.los))\nprintln("angle(û_faceon, û_inc0)     = ",\n        round(rad2deg(acos(clamp(sum(fo.up .* lad0.up), -1, 1))), digits=2), "°")\nprintln("max |Σ_faceon − Σ_inc0|     = ", round(maximum(abs, lad0.maps[:sd] .- fo.maps[:sd]), digits=1))\n# ... and the roll is recoverable exactly:\nlad0_pa = projection(gas, :sd, :Msol_pc2; inclination=0, axis=:angmom, position_angle=-90, win...)\nprintln("max |Σ_faceon − Σ_inc0,PA=-90| = ", maximum(abs, lad0_pa.maps[:sd] .- fo.maps[:sd]))\n\n# "Exactly one view specifier" and "direction implies :angmom" are promises about behaviour:\nfor (lbl, kw) in (("inclination + los", (inclination=35, los=[1,1,1])),\n                  ("direction=:faceon + axis", (direction=:faceon, axis=:angmom)))\n    e = try (projection(gas, :sd; kw..., win...); "NO ERROR") catch e; typeof(e).name.name end\n    println(rpad(lbl, 26), "→ ", e)\nend\n\nladder = [lad0, lad30, lad60, eo]      # i = 90 is the edge-on map from Chapter 1\ncr = sharedrange(ladder, :sd)\nmaprow(ladder, :sd, ["i = 0°", "i = 30°", "i = 60°", "i = 90°"]; crange=cr)'
LADDER_NOTE = '`direction=:faceon` and `inclination=0, axis=:angmom` are the **same line of sight** — the two `ŵ`\nvectors agree to the last bit — but they are *not* the same image. A face-on view leaves the roll\nabout `ŵ` undetermined, and the two code paths break that tie differently: the `û` vectors come out\nexactly **90° apart**, which is why the naive map-to-map difference above is large rather than zero.\n`position_angle=-90` recovers `:faceon` to floating-point round-off (the residual printed\nabove is ~4e-11 M⊙/pc² — summation order across threads, not a real difference).\n\nThe lesson generalises past this one preset: whenever a view leaves a degree of freedom free,\ncompare the **camera vectors**, not the pixels. Two correct maps of the same scene can differ by a\nroll.'
EXCL = '\n# "Exactly one view specifier" and "direction implies :angmom" are both checkable:\nfor (lbl, kw) in (("inclination + los", (inclination=35, los=[1,1,1])),\n                  ("direction=:faceon + axis", (direction=:faceon, axis=:angmom)))\n    e = try (projection(gas, :sd; kw..., center=[:bc], xrange=[-15,15], yrange=[-15,15],\n                        range_unit=:kpc, pxsize=[1.0,:kpc], verbose=false,\n                        show_progress=false); "NO ERROR") catch e; typeof(e).name.name end\n    println(rpad(lbl, 26), "→ ", e)\nend'
REJECT = '\n# "Rejected with a clear error" is a promise about behaviour — check it rather than trust it.\nfor v in (:σx, :σy, :σz, :σ, :r_cylinder, :r_sphere, :ϕ)\n    msg = try\n        projection(gas, v; inclination=35, axis=:angmom, center=[:bc], xrange=[-15,15],\n                   yrange=[-15,15], zrange=[-15,15], range_unit=:kpc, pxsize=[1.0,:kpc],\n                   verbose=false, show_progress=false)\n        "NO ERROR — the page is wrong"\n    catch e\n        first(replace(sprint(showerror, e), "\\n" => " "), 62) * "…"\n    end\n    println(rpad(v, 14), msg)\nend'
COMPAT = '# The table above is a set of claims. Run them — a compatibility table that is never executed\n# is exactly the kind of thing that goes stale when the code moves on.\nW = (center=[:bc], xrange=[-15,15], yrange=[-15,15], zrange=[-15,15], range_unit=:kpc,\n     pxsize=[1.0,:kpc], verbose=false, show_progress=false)\nsame(a, b) = maximum(abs, a.maps[:sd] .- b.maps[:sd]) == 0\nraises(f)  = try (f(); "NO ERROR") catch e; string(typeof(e).name.name) end\n\npc = projection(part, :sd, :Msol_pc2; direction=:edgeon, binning=:cic, W...)\nprintln("particle binning=:overlap falls back to :cic : ",\n        same(projection(part, :sd, :Msol_pc2; direction=:edgeon, binning=:overlap, W...), pc))\nprintln("particle binning=:exact   falls back to :cic : ",\n        same(projection(part, :sd, :Msol_pc2; direction=:edgeon, binning=:exact, W...), pc))\n# :sph/:voronoi now work off-axis too: both are rotation-invariant, so the same samplers run\n# on camera-frame coordinates. (They need a :volume column, which star particles lack.)\nfor w in (:sph, :voronoi)\n    println(rpad("weighting=:$w off-axis (needs :volume)", 45), ": ",\n            raises(() -> projection(part, :sd, :Msol_pc2; direction=:edgeon, weighting=w, W...)))\nend\nprintln("fov works on particles                       : ",\n        size(projection(part, :sd, :Msol_pc2; direction=:edgeon, center=[:bc], fov=15,\n                        fov_unit=:kpc, aperture=:square, pxsize=[1.0,:kpc],\n                        verbose=false, show_progress=false).maps[:sd]))\nprintln("slice(part, …)                               : ",\n        raises(() -> slice(part, :sd; direction=:edgeon, center=[:bc], xrange=[-15,15],\n                           yrange=[-15,15], range_unit=:kpc, pxsize=[1.0,:kpc], verbose=false)))\nfor kw in (:nmax, :max_threads)\n    println(rpad(string("particle ", kw), 45), ": ",\n            raises(() -> projection(part, :sd, :Msol_pc2; direction=:edgeon, (; kw => 8)..., W...)))\nend\nprintln("data_center ignored on off-axis hydro        : ",\n        same(projection(gas, :sd, :Msol_pc2; inclination=35, axis=:angmom, W...),\n             projection(gas, :sd, :Msol_pc2; inclination=35, axis=:angmom,\n                        data_center=[0.4,0.4,0.4], data_center_unit=:standard, W...)))'
BIN_PROSE2 = 'The totals agree and the pictures do not — which is the point, and the reason "is it\nconservative?" is the wrong question to stop at.\n\nRead the panels as one statement: **it is the pixel-to-cell ratio that decides, not the kernel.**\nAt 0.8 kpc pixels — about one pixel per cell here — `:cic` is a perfectly good preview and leaves\n**0 %** of pixels empty. Push to 0.1 kpc, eight pixels across every cell, and the point-deposit\nkernels fall apart: `:cic` leaves **27.8 %** of pixels empty and `:ngp` **64.4 %**. Each puts a\ncell\'s whole contribution at a single point, so the gaps between cell centres receive nothing and\nthe map acquires a texture that belongs to the grid rather than to the galaxy. `:overlap` spreads\neach cell over the area its shadow actually covers and leaves **no** pixel empty at any pixel size.\n\n**And the number that justifies the default.** Against `:exact`, the analytic footprint integral,\n`:overlap` agrees to a **median 0.0005 dex** per pixel (99th percentile 0.005, worst pixel 0.033;\nmass-weighted mean 0.0009 dex) — a 0.1 % effect, for roughly a third of the cost. The point-deposit\nkernels differ from the same reference by a **median 1.3 dex**, a factor of 20, on the pixels they\ndo fill. That is the whole case for the default in two numbers, and it is why `:exact` gets no\npanel above: it would be indistinguishable from `:overlap` by eye.\n\nThe level table tells you which regime you are in: divide the local cell size by your `pxsize`.\nBelow about one pixel per cell, any kernel will do; well above it, only the footprint methods are\nhonest.\n\nPractical rule: the default `:overlap` is already the accurate one — reach for `:cic`/`:ngp` when\nyou want a fast look at a sensible pixel size, and `:exact` when you want the analytic reference\nrather than a sampled approximation to it.'
BIN_FIG = '# ── figure code from here: panels, overlays, colorbars — no new Mera concepts ──\n# Show the REGIME, not one strawman: :cic where you would actually use it, then the three\n# sampled kernels at pixels 8x finer than the cell. :exact gets no panel on purpose — it is\n# visually indistinguishable from :overlap, and the cell above gives the number instead.\npc_ok = projection(gas, :sd, :Msol_pc2; inclination=60, axis=:angmom, binning=:cic,\n                   center=[:bc], fov=8, fov_unit=:kpc, aperture=:square,\n                   pxsize=[0.8,:kpc], verbose=false, show_progress=false)\nallv = reduce(vcat, [log10.(filter(>(0), vec(Float64.(p.maps[:sd]))))\n                     for p in (pc_ok, k_ngp, k_cic, k_ovl)])\ncr = (quantile(allv, 0.02), maximum(allv))\nmaprow([pc_ok, k_ngp, k_cic, k_ovl], :sd,\n       [":cic @ 0.8 kpc pixels\n1 pixel per cell — a fine preview",\n        ":ngp @ 0.1 kpc pixels\nall weight at cell centres",\n        ":cic @ 0.1 kpc pixels\n2x2 split — still no footprint",\n        ":overlap @ 0.1 kpc pixels\nsame pixels, footprint deposit"]; crange=cr)'
BIN_MEASURE = '# Which regime are you in? Binning only matters when PIXELS ARE FINER THAN CELLS.\nfor l in sort(unique(getvar(gas, :level)))\n    cs = info.boxlen / 2^l\n    println("level ", l, ":  cell ", rpad(round(cs, digits=2), 5), " kpc",\n            "  →  ", round(cs / 0.1, digits=1), " pixels per cell at pxsize = 0.1 kpc")\nend\n\nzoom = (center=[:bc], fov=8, fov_unit=:kpc, aperture=:square,\n        pxsize=[0.1,:kpc], verbose=false, show_progress=false)\n\nkern = Dict{Symbol,Any}(); secs = Dict{Symbol,Float64}()\nfor k in (:ngp, :cic, :overlap, :exact)\n    projection(gas, :sd, :Msol_pc2; inclination=60, axis=:angmom, binning=k, zoom...)   # warm-up\n    secs[k] = @elapsed kern[k] = projection(gas, :sd, :Msol_pc2; inclination=60,\n                                            axis=:angmom, binning=k, zoom...)\nend\nk_ngp, k_cic, k_ovl = kern[:ngp], kern[:cic], kern[:overlap]\n\n# :exact is the analytic reference — measure the others against it rather than asserting.\nE = Float64.(kern[:exact].maps[:sd])\nprintln()\nprintln(rpad("binning", 10), rpad("empty px", 11), rpad("time [s]", 10), "median |Δ| vs :exact [dex]")\nfor k in (:ngp, :cic, :overlap, :exact)\n    A = Float64.(kern[k].maps[:sd]); both = (A .> 0) .& (E .> 0)\n    d = k === :exact ? 0.0 : median(abs.(log10.(A[both]) .- log10.(E[both])))\n    println(rpad(k, 10), rpad(string(round(100*count(iszero, A)/length(A), digits=1), " %"), 11),\n            rpad(round(secs[k], digits=3), 10), round(d, digits=4))\nend'
BIN_INTRO = 'Chapter 5 settled the total. This chapter is about the **other** question: *where* the mass lands.\n\n**Why the shadow is a hexagon.** Look at a cube from a general direction and you see three of its\nsix faces — the three meeting at the corner nearest you. The outline of those three faces is a\nclosed circuit of **six** cube edges, so the silhouette cast on the image plane has six sides. It\ncollapses to a rectangle in exactly one situation: when the line of sight lies in a coordinate\nplane, i.e. when any component of `ŵ` is zero. Then only two faces front-face, and you get the\nfamiliar square — `direction=:x/:y/:z`, face-on and edge-on are all that case. Off-axis you are\ngenerically in the hexagonal regime.\n\nOne more thing follows, and it is why a single footprint rule can serve a whole AMR hierarchy:\nevery cell is an **axis-aligned** cube, so for a given camera every cell casts the *same* hexagon,\ndiffering only in scale.\n\nThat hexagon generally straddles several pixels. The four `binning` kernels are four answers to\n"how is it shared out" — they all share it out completely (hence one total), but they place it\ndifferently.\n\n![Four kernels, one footprint](assets/offaxis/offaxis_cell_treatment.svg)\n\n| `binning` | what it does | use it for |\n|---|---|---|\n| `:ngp` | all weight into the pixel containing the cell centre | fastest preview; holes and moiré when pixels are finer than cells |\n| `:cic` | bilinear split over the 2×2 neighbouring pixels | fast preview; smoother, still no footprint |\n| `:overlap` **(default)** | the cube is supersampled over its true footprint — `n³` sub-points with `n = ⌈cellsize/pixel⌉`, capped at `nmax=64`; cells past the cap deposit a footprint-sized top-hat, which is what keeps coarse cells hole-free | **everything you publish** |\n| `:exact` | the analytic footprint integral (a box-spline chord field over the hexagon) | the reference the others are checked against; no cap, slower |\n\n`:overlap` and `:exact` are threaded; `:ngp` and `:cic` run serially. `:exact` follows from the\nbox-spline representation of a projected cube (de Boor, *Box Splines*); nothing about choosing a\n`binning` depends on that derivation, so it is not reproduced here.\n\nThe table is a claim. The cell below measures it — all four kernels on the same data, against\n`:exact` as the reference.'
SLICE_CODE = 'view = (inclination=60, azimuth=30, axis=:angmom, center=[:bc])\n\n# pxsize is 0.25 kpc, not finer: cells here are 0.78 kpc (1.56 kpc further out), and a column\n# integral sampled well below the local cell size resolves the SHADOW OF EACH CELL — flat,\n# straight-edged plateaus that overlap and read as stacked slabs. That is the AMR grid being\n# displayed, not structure. Chapter 6 is where pixel-vs-cell size is treated properly.\nsl = slice(gas, :rho, :nH; view..., xrange=[-15,15], yrange=[-15,15],\n           range_unit=:kpc, pxsize=[0.25,:kpc], verbose=false)\n\n# projection: same view, and `fov` is how you get the SAME ±15 kpc camera frame\npr = projection(gas, :rho, :nH; view..., fov=15, fov_unit=:kpc, aperture=:square,\n                pxsize=[0.25,:kpc], verbose=false, show_progress=false)\n\nprintln("slice frame      ", size(sl.map), "   ", round(100*count(isnan, sl.map)/length(sl.map), digits=1), " % NaN")\nprintln("projection frame ", size(pr.maps[:rho]))\nprintln("slice extent [kpc] = ", round.(sl.extent .* gas.scale.kpc, digits=1))'
SLICE_NOTE = 'Two things in the left panel are the *selection* rather than the gas, and both are worth\nrecognising because they show up in every `fov` projection:\n\n- the soft darkening into the **corners** is the selection sphere — at `fov=15, aperture=:square`\n  the corners sit on the sphere and integrate zero depth (see "Choosing `fov`" in Chapter 4);\n- any **flat, straight-edged plateau** in the outskirts is a single AMR cell\'s projected shadow.\n  Sample a column integral much finer than the local cell and you resolve individual cell\n  footprints, which tile the map and read as overlapping slabs. At 0.25 kpc pixels against\n  0.78 kpc cells that is mostly gone; at 0.12 kpc it dominates the outer frame.\n\nNeither is a projection error — mass is conserved either way (Chapter 5). They are what you get\nfor asking the map a question finer than the data can answer.'
FOV_SEC = '### Choosing `fov`\n\n`fov` is a **half-width**: the frame spans ±`fov`, so `fov=15, fov_unit=:kpc` gives a 30 kpc image.\n\nIt is worth being explicit about what `fov` does *not* do, because the name invites the wrong\npicture. The camera is orthographic at every setting (Chapter 2) — there is no perspective to\ntune, no camera distance, no vanishing point. Changing `fov` does not move a camera nearer or\nfurther; it widens or narrows the frame, and with it the sphere of data that is selected.\n\n**What a given `fov` costs you in depth.** The selection is a sphere of radius `R` — `fov` for\n`aperture=:circle`, `√2·fov` for `:square`. A ray at in-plane distance `d` from the centre\ntherefore integrates a **chord**, not a slab:\n\n`depth(d) = 2·√(R² − d²)`\n\nFor `fov=15, aperture=:square` on this fixture (`R` = 21.2 kpc):\n\n| where in the frame | offset from centre | column depth |\n|---|---|---|\n| centre | 0 kpc | 42.4 kpc |\n| middle of an edge | 15 kpc | 30.0 kpc |\n| **corner** | 21.2 kpc | **0 kpc** |\n\nThe corners of a `:square` frame sit exactly on the selection sphere, so they integrate nothing.\nThat is the soft darkening you can see creeping into the corners of any `fov` projection of a\ndiffuse field — it is the selection boundary, not the gas. `:circle` tapers the same way, just at\nits own frame edge instead of in the corners.\n\nThe practical rule is the one Chapter 5 already gave for edge pixels: **make `fov` comfortably\nlarger than the structure you are measuring.** For a galaxy centred in frame this costs nothing —\nthe disc sits where the depth is flattest — but never read a diffuse column, a profile, or a scale\nheight out to the frame boundary.\n\n**So what is a natural `fov`?** One that (a) puts the object inside the flat-depth part of the\nframe and (b) keeps the selection sphere inside the box. Here the gas disc is ~10 kpc across, so\n15–25 kpc is the natural range: at `fov=15` the disc lives in the innermost third of the frame\nwhere depth varies by under 10 %. The upper bound is enforced for you — `fov` is capped at\n0.49·boxlen for `:circle` and 0.49/√2·boxlen for `:square` (≈ 34.6 kpc here), which is what keeps\nthe sphere from reaching outside the box and dragging the box faces back into the image.\n\n**Why you would deliberately change it.** A *smaller* `fov` is not just a tighter crop: it is a\n**shallower column**, so it removes foreground and background that a wider frame would integrate\ninto your disc — the closest thing `projection` has to a depth cut, since there is no line-of-sight\nslab. It also buys resolution, since the same pixel budget covers less sky. A *larger* `fov` buys\ncontext and a deeper column, at the price of more unrelated material along every ray. And whatever\nvalue you pick, `fov` is the only framing control that is rotation-invariant, so any set of frames\nmeant to be compared — angles, snapshots, movie frames — has to be framed this way.'

# CH2 cell0 — the panel left an outline ("Six sentences + the schematic"); write it
REWRITES[(2, 0)] = '''## 2. What a pixel contains

Before turning more knobs, it is worth being precise about what the numbers in a map *are*.

The camera is **orthographic**: every ray is parallel and the observer sits at infinity. There is
no vanishing point and no perspective, so nothing in the image gets larger by being nearer.

Mera reduces whatever view you specified to a single unit vector **ŵ**, the line of sight, and
completes it to a right-handed orthonormal camera basis **(r̂, û, ŵ)** — image x, image y, and the
viewing direction. Those are the three vectors you read back as `m.cam_right`, `m.up`, `m.los`.
`ŵ` points *into* the image, away from you; Chapter 7 turns that convention into a sign you can
check.

A pixel value is then the integral of the requested quantity along the parallel ray through that
pixel, over the whole depth of the selected data. That single sentence explains most of what
follows: it is why a projection conserves mass, why `zrange` matters as much as `xrange`, and why
a slice — which samples one plane instead of integrating through the volume (Chapter 8) — answers
a different question.

`position_angle` is a **roll**: it rotates `(r̂, û)` together about `ŵ`. The line of sight does
not move, so the *scene* is unchanged — but whether the **frame** sees the same gas depends on
the aperture, and it is worth measuring rather than assuming. Rolling by 30° here leaves
`Σ` identical to the last digit with `aperture=:circle` (a disc is roll-invariant) and changes it
by **2.3 %** with `aperture=:square`, because the square crop rotates inside the selection sphere
and its corners sweep across different material.

One consequence deserves to be stated on its own, because the next chapter is built on it: since
the projection is orthographic, **moving the camera away from the galaxy changes nothing**. There
is no camera distance to set. The only control over what lands in frame is the *width of the
frame* — a field of view.

The step-by-step basis construction (the deterministic choice of "up", the Gram–Schmidt
completion, the roll matrix) lives in `?projection`; you do not need it to use any of this.'''

REWRITES[(8, 1)] = SLICE_CODE

# CH4 cell4 — thin; this is the chapter's payoff and needs to land
REWRITES[(4, 4)] = '''Read the frame sizes above, not just the pictures.

The world-space window was asked for ±22 kpc and came back far taller, because `xrange`/`yrange`/
`zrange` bound a box **in simulation coordinates** and the camera frame is the bounding box of
that box *after rotation*. Leave `zrange` out, as is natural when you are thinking about an image,
and the full depth of the run folds into the image height as you tilt. The dashed cyan rectangle
on the first panel is what was requested; everything outside it is the rotated box's own footprint.

Worse, the window's **faces become features**. A sight line just inside the slab crosses its full
depth; a sight line just outside clips only a corner. The column density therefore drops along a
straight line — a hard edge across your map that looks like a rendering artefact but is the
selection box seen from an angle.

`fov` avoids all of this by framing the **camera plane** instead. The selection is a sphere, which
projects to the same disc at every orientation, so the frame cannot breathe:

* `aperture=:square` — a slightly larger sphere cropped to the ±`fov` square, giving a full
  rectangular frame that is **pixel-identical at every angle**. This is what a comparison figure,
  a ladder, or an orbit sequence needs.
* `aperture=:circle` (the default) — the sphere itself, so the frame's corners are empty.

Mera prints a one-off note when it sees an off-axis view with a windowed `xrange`/`yrange` and no
`zrange`, because the result is easy to mistake for a bug in the data.'''

# CH6 cell3 — thin; the binning chapter's conclusion
REWRITES[(6, 3)] = '''The totals agree and the pictures do not — which is the whole point of this chapter, and the
reason "is it conservative?" is the wrong question to stop at.

`:cic` left **27.8 %** of the pixels empty; `:overlap` left none. Both deposited the same mass. A
point deposit puts each cell's entire contribution at its centre, so where pixels are finer than
cells the gaps between centres simply receive nothing, and the map acquires a texture that belongs
to the grid rather than to the galaxy. The footprint methods spread each cell over the area its
shadow actually covers, so the map stays continuous.

The table above tells you when you are in that regime: divide the local cell size by your `pxsize`.
At 0.1 kpc pixels the coarsest cells here span **31 pixels**, and no point deposit can fill that
honestly.

Practical rule: the default `:overlap` is already the accurate one — reach for `:cic`/`:ngp` only
for a quick look, and use `:exact` when you want the analytic reference rather than a sampled
approximation to it.'''

# CH11 cell2 — thin
REWRITES[(11, 2)] = '''Nothing above is hydro-specific. The camera keywords, the framing keywords and the binning
keywords mean the same thing for every projectable data type:

* **particles** — point masses, deposited with the same kernels; `:sd` is a stellar surface
  density here rather than a gas one;
* **gravity** — projected through the two-object form `projection(hydro, gravity, var)`, where the
  hydro object supplies the weights and the gravity object the field. Both must describe the same
  cells, so load them from the same `info` at the same `lmax`.

The empty-pixel count printed above is worth carrying with you: an off-axis frame that is *not*
completely filled is normal, and the zeros are absence of data, not zero potential. Aggregate the
filled pixels, not the whole array.'''

# CH13 (Appendix B) — the panel left FILL-IN slots for test paths
REWRITES[(13, 0)] = '''## Appendix B — Where the guarantees are measured

Two claims on this page are load-bearing, so neither rests on prose.

**Mass is conserved at any angle and any pixel size.** Every binning mode is a partition-of-unity
deposit: each cell distributes its full weight across the pixels of the camera plane with shares
that sum to exactly 1, so the total deposited weight is `Σ m_cell` regardless of *where* the cells
land. Rotating the camera or changing the pixel grid only moves weight between pixels; it never
creates or destroys any. Cells whose stencil reaches past the border fold the outside share back
onto the edge pixel, so the sum is preserved rather than leaking. For `:overlap` the same argument
holds per sub-point, and for `:exact` the per-pixel footprint integrals are renormalised to the
cell volume — so the conserved total is exact by construction in both.

Chapter 5 measures it once on this dataset: `Σ(map) / msum(gas) − 1 = 0.0`.

**The kinematics recover the right axis.** `:vlos` is antisymmetric about the minor axis edge-on
and near-zero face-on — the check in Chapter 7, which is also how you detect a mis-centred
`center` before it silently tilts every map you make.

Both are pinned by the test suite rather than by this page, over a grid of viewing angles, pixel
sizes (including non-power-of-two) and binning kernels — see `test/34_offaxis_invariance_tests.jl`
and `test/68_offaxis_api_tests.jl` in the repository. If a change ever broke one of them, the
suite would fail before the documentation did.'''


BIN_CODE = '''# ── figure code from here: panels, overlays, colorbars — no new Mera concepts ──
# Show the REGIME, not one strawman: :cic where you would actually use it, :cic pushed past
# the cell size, and :overlap at those same fine pixels.
pc_ok  = projection(gas, :sd, :Msol_pc2; inclination=60, axis=:angmom, binning=:cic,
                    center=[:bc], fov=8, fov_unit=:kpc, aperture=:square,
                    pxsize=[0.8,:kpc], verbose=false, show_progress=false)
allv = reduce(vcat, [log10.(filter(>(0), vec(Float64.(p.maps[:sd]))))
                     for p in (pc_ok, p_cic, p_ovl)])
cr = (quantile(allv, 0.02), maximum(allv))
maprow([pc_ok, p_cic, p_ovl], :sd,
       [":cic @ 0.8 kpc pixels\n1 pixel per cell — a fine preview",
        ":cic @ 0.1 kpc pixels\n8 pixels per cell — falls apart",
        ":overlap @ 0.1 kpc pixels\nsame pixels, footprint deposit"]; crange=cr)'''

BIN_PROSE = '''The totals agree and the pictures do not — which is the point, and the reason "is it
conservative?" is the wrong question to stop at.

Read the three panels as one statement: **it is the pixel-to-cell ratio that decides, not the
kernel.** At 0.8 kpc pixels — about one pixel per cell here — `:cic` is a perfectly good preview
and leaves **0 %** of pixels empty. Push to 0.1 kpc, eight pixels across every cell, and the same
kernel leaves **27.8 %** of them empty: a point deposit puts each cell's whole contribution at its
centre, so the gaps between centres receive nothing and the map acquires a texture that belongs to
the grid rather than to the galaxy. `:overlap` spreads each cell over the area its shadow actually
covers, so it stays continuous at any pixel size.

The table above tells you which regime you are in: divide the local cell size by your `pxsize`.
Below about one pixel per cell, any kernel will do; well above it, only the footprint methods are
honest.

Practical rule: the default `:overlap` is already the accurate one — reach for `:cic`/`:ngp` when
you want a fast look at a sensible pixel size, and `:exact` when you want the analytic reference
rather than a sampled approximation to it.'''

KIN_CODE = '''kin = (center=[:bc], fov=15, fov_unit=:kpc, aperture=:square,
       pxsize=[0.8, :kpc], verbose=false, show_progress=false)

# ask for :sd alongside — used below only to SET THE COLOUR RANGE from where the mass is;
# every pixel is still plotted
keo = projection(gas, [:vlos, :σlos, :sd], [:km_s, :km_s, :Msol_pc2]; direction=:edgeon, kin...)
kfo = projection(gas, [:vlos, :σlos, :sd], [:km_s, :km_s, :Msol_pc2]; direction=:faceon, kin...)

finite(A) = filter(isfinite, vec(Float64.(A)))
println("edge-on   max |v_LOS| = ", round(maximum(abs, finite(keo.maps[:vlos])), digits=1), " km/s")
println("face-on   max |v_LOS| = ", round(maximum(abs, finite(kfo.maps[:vlos])), digits=1), " km/s")
println("median σ_LOS edge-on  = ", round(median(finite(keo.maps[:σlos])), digits=1), " km/s")'''

KIN_FIG = '''# ── figure code from here: panels, overlays, colorbars — no new Mera concepts ──
# Every pixel is shown. The colour range is set from the bright pixels (98th percentile), so the
# disc's rotation is legible and the faint outskirts SATURATE rather than being hidden — a reader
# can see there is signal there and that it is off the end of the scale, which a black mask would
# have concealed.
kinvals(m, key) = Float64.(m.maps[key])

function kinpanel!(ax, m, key, cmap, crange; logscale=false)
    A = kinvals(m, key); A = logscale ? log10.(replace(A, 0.0 => NaN)) : A
    e = getextent(m, :kpc)
    hm = heatmap!(ax, range(e[1],e[2],length=size(A,1)), range(e[3],e[4],length=size(A,2)), A;
                  colormap=cmap, nan_color=:black, interpolate=false, colorrange=crange)
    ax.aspect = DataAspect(); hm
end

# Colour range from the 2nd–98th percentile of ALL pixels, not just the bright ones. Scaling to
# the disc alone drives the halo off the end of the scale, and a saturated slab hides structure
# just as effectively as a mask does. σ_LOS here runs 15 → 1071 km/s (the disc is only 27–145),
# so it needs a log scale to show both at once.
pix(m, key) = filter(isfinite, vec(Float64.(m.maps[key])))
vmax = quantile(abs.(pix(keo, :vlos)), 0.98)
sl   = filter(>(0), vcat(pix(keo, :σlos), pix(kfo, :σlos)))
srng = (log10(quantile(sl, 0.02)), log10(quantile(sl, 0.98)))

fig = Figure(size=(1180, 400))
ax1 = Axis(fig[1,1], title="edge-on  v_LOS", xlabel="x' [kpc]", ylabel="y' [kpc]")
h1  = kinpanel!(ax1, keo, :vlos, :balance, (-vmax, vmax))
Colorbar(fig[1,2], h1, label="v_LOS [km/s]")
ax2 = Axis(fig[1,4], title="edge-on  σ_LOS", xlabel="x' [kpc]")
h2  = kinpanel!(ax2, keo, :σlos, :viridis, srng; logscale=true)
ax3 = Axis(fig[1,5], title="face-on  σ_LOS", xlabel="x' [kpc]")
kinpanel!(ax3, kfo, :σlos, :viridis, srng; logscale=true)
hideydecorations!(ax2, grid=false); hideydecorations!(ax3, grid=false)
Colorbar(fig[1,6], h2, label="log10 σ_LOS [km/s]")
colsize!(fig.layout, 3, Fixed(14))    # spacer: keeps the v colorbar from reading as panel 2's ylabel
fig'''

# ── QA fixes after LOOKING at the rendered figures (reported: "misaligned grids overlapping",
#    "the preview looks awful and not usable"). Both had one root cause: pixel sizes far finer
#    than the local cell, which makes the AMR structure dominate the picture.
REWRITES[(3, 1)] = LADDER      # EXCL folded in ABOVE the maprow, or the figure is lost
_APPEND = {(5, 1): REJECT}    # (5,1) ends in println, so appending is safe there

REWRITES[(6, 0)] = BIN_INTRO
REWRITES[(6, 1)] = BIN_MEASURE
REWRITES[(6, 2)] = BIN_FIG
# (BIN_CODE/BIN_PROSE from the first QA pass are superseded by the four-kernel versions)
_OLD_BIN = BIN_CODE
REWRITES[(6, 3)] = BIN_PROSE2
KIN_INTRO = """`:vlos` is `v·ŵ`, the component of the velocity along the line of sight — defined for **any**
camera. That is what makes it different from `:σx`/`:σy`/`:σz`, which only exist along the box axes
and are rejected off-axis.

`:σlos` is `√(⟨v_LOS²⟩ − ⟨v_LOS⟩²)` over the mass in a pixel. It is a **width of a distribution
inside one pixel**, not a per-cell quantity — many cells along the ray land in the same pixel, each
with its own `v·ŵ`, and σ is how spread out they are. Edge-on, that spread is dominated by *ordered
rotation along the sightline*, not by turbulence — do not call it a turbulent dispersion.

In the map below that shows up as the **brightest σ_LOS off the disc plane, not in it**: a sightline
through the disc samples gas that is nearly co-rotating, while one passing above it crosses infalling
and outflowing material with a far wider velocity spread. σ_LOS runs 15 → 1071 km/s here, so the
panels are on a log scale.

The obvious next worry is that σ_LOS is then an artefact of how finely you pixelate. The code below
measures whether it is."""

KIN_CLOSE = """Now the result, and it is not the one the "width inside a pixel" picture suggests: a **16× change
in `pxsize` moves the median σ_LOS by a few km/s**, and the mean barely at all. σ_LOS is set by the
spread of velocities **along the ray**, and the ray is the same ray whatever the pixel width. Making
pixels smaller sub-divides the sky, not the sightline.

That is a useful licence: choose `pxsize` for the *image* you want, and σ_LOS will not move under
you. Quote it anyway, so a reader can check.

!!! note "Shipped separately"
    Position–position–velocity cubes, emission and absorption forward modelling, mock observations
    and FITS export are **in development in a separate module** and are not part of the released
    package. This page covers only the moment maps `:vlos` and `:σlos`. (Stated once, here.)"""

# The blueprint asserted σ_LOS "depends on the pixel" — measurement says otherwise (93.6 → 102.6
# km/s across a 24× pixel range). Keyed by index because the text-match rewrite never fired.
REWRITES[(7, 0)] = KIN_INTRO
REWRITES[(7, 5)] = KIN_CLOSE
REWRITES[(7, 2)] = KIN_CODE
REWRITES[(7, 3)] = KIN_FIG

ORBIT_FIG = '''# ── figure code from here: panels, overlays, colorbars — no new Mera concepts ──
# The frames are already computed above; showing them is the visual half of the same claim.
cr = sharedrange(frames, :sd)
maprow(collect(frames), :sd, ["azimuth $(a)°" for a in 0:90:270]; crange=cr)'''

ORBIT_PROSE = '''Four frames, four azimuths, one frame size and one extent to three decimals — the montage and the
numbers say the same thing from opposite directions. That invariance is what makes the sequence
usable as a movie: nothing breathes, so the eye reads rotation rather than zoom.

Write the frames to disk with any Makie/`FileIO` recorder, or hand the vector straight to
`Makie.record`. For a long sweep, `parallel_frames=true` renders the frames concurrently (each
projection single-threaded) — typically 1.5–2× faster once you have more frames than threads.'''

OTHER_FIG = '''# The same camera, pointed at a different data type. `fov` frames both identically, so the two
# panels can be compared pixel for pixel.
# 0.6 kpc pixels: fine enough to show both discs, coarse enough that the STAR map is not
# dominated by Poisson noise (453 200 particles — the outskirts get very few per pixel)
shot = (direction=:edgeon, center=[:bc], fov=20, fov_unit=:kpc, aperture=:square,
        pxsize=[0.6, :kpc], verbose=false, show_progress=false)
gas_eo  = projection(gas,  :sd, :Msol_pc2; shot...)
star_eo = projection(part, :sd, :Msol_pc2; shot...)
# gravity rides on the hydro grid: the two-object form, same camera, same framing
pot_eo  = projection(gas, grav, :epot, :km2_s2; shot...)
println("gas   frame ", size(gas_eo.maps[:sd]),
        "   stars ", size(star_eo.maps[:sd]),
        "   potential ", size(pot_eo.maps[:epot]))
println("φ along the line of sight: ", round.(extrema(pot_eo.maps[:epot]), sigdigits=4), " km²/s²")


# ── figure code from here: panels, overlays, colorbars — no new Mera concepts ──
# separate colour ranges: gas and stars differ by orders of magnitude in surface density,
# and forcing one scale would flatten whichever loses
lo(m) = quantile(log10.(filter(>(0), vec(Float64.(m.maps[:sd])))), 0.25)  # clip the empty rim
hi(m) = maximum(log10.(filter(>(0), vec(Float64.(m.maps[:sd])))))

fig = Figure(size=(1420, 400))
ax1 = Axis(fig[1,1], title="gas  Σ", xlabel="x' [kpc]", ylabel="y' [kpc]")
h1 = showmap!(ax1, gas_eo, :sd; crange=(lo(gas_eo), hi(gas_eo)))
Colorbar(fig[1,2], h1, label="log10 Σ_gas [M⊙/pc²]")

ax2 = Axis(fig[1,4], title="stars  Σ", xlabel="x' [kpc]")
h2 = showmap!(ax2, star_eo, :sd; crange=(lo(star_eo), hi(star_eo)))
Colorbar(fig[1,5], h2, label="log10 Σ_★ [M⊙/pc²]")

# the potential is negative everywhere and spans a small range — a linear scale on the raw
# value, no log, and a sequential map so "deeper" reads as one direction
ax3 = Axis(fig[1,7], title="gravitational potential φ", xlabel="x' [kpc]")
h3 = showmap!(ax3, pot_eo, :epot; logscale=false, cmap=:magma)
Colorbar(fig[1,8], h3, label="φ [km²/s²]")

hideydecorations!(ax2, grid=false); hideydecorations!(ax3, grid=false)
colsize!(fig.layout, 3, Fixed(14)); colsize!(fig.layout, 6, Fixed(14))
fig'''

OTHER_PROSE = '''Same keywords, same camera, three different kinds of data — and each one says something the
others cannot. The stars form a **thinner, smoother disc** than the gas, which is exactly the
comparison that motivates making both maps in one orientation. The potential is smoother than
either: it is an integral over all the mass, so it does not care about the clumps that dominate
the gas map, and its contours are rounder than the disc that produced them.

Gravity comes through the **two-object form**, `projection(hydro, gravity, var)`: the hydro object
supplies the weights and the gravity object the field, so both must describe the same cells —
load them from the same `info` at the same `lmax`. `fov` cuts both together, so the three panels
above are framed identically and can be compared pixel for pixel.

`fov` works for particles as it does for the grid — the framing is a selection, so it does not care
what is being deposited. What *does* differ is the deposit itself: points have no footprint, so
particle projections use `:cic` and the footprint kernels fall back to it.

That difference is visible if you push the pixels: a grid map degrades smoothly, while a particle
map becomes **grainy**, because each pixel is counting a finite number of objects and inherits a
√N uncertainty. The cure is the same as in any counting experiment — coarsen the pixels until each
one holds enough particles to mean something.'''

# ── EXTRA CELLS: two chapters computed results and printed numbers without ever showing a
#    picture — the orbit sequence (Ch 9) and the other-data-types chapter (Ch 11). Both are
#    claims about what an image looks like, so both get one.
EXTRAS = {
    (9, 1):  [("code", ORBIT_FIG), ("markdown", ORBIT_PROSE)],
    (11, 1): [("code", OTHER_FIG), ("markdown", OTHER_PROSE)],
}
EXTRAS.setdefault((11, 1), []).append(("code", COMPAT))   # AFTER `part` is loaded
EXTRAS.setdefault((3, 1), []).append(("markdown", LADDER_NOTE))

# Added after reader feedback: the fov depth taper (measured) and why the projection panel
# looked like stacked slabs.
EXTRAS.setdefault((4, 4), []).append(("markdown", FOV_SEC))
EXTRAS.setdefault((8, 2), []).append(("markdown", SLICE_NOTE))

def apply(cell, ch, k):
    kind, t = cell["kind"], cell["content"]
    if (ch, k) in REWRITES:
        return kind, REWRITES[(ch, k)]
    if kind == "code":
        t = t.replace(PATH_OLD, PATH_NEW).replace(SAVE_OLD, SAVE_NEW).replace(LOAD_OLD, LOAD_NEW)
        t = t.replace(EPOT_OLD, EPOT_NEW)
        if SIGMA_CODE_OLD_HEAD in t:
            t = SIGMA_CODE
        if (ch, k) in _APPEND:                 # executed check appended to this code cell
            t = t.rstrip() + "\n" + _APPEND[(ch, k)]
    else:
        # ── figure references. The blueprint invented "_v2" filenames for illustrations it
        # never drew, so the page shipped two broken images. `offaxis_cell_treatment.svg`
        # already IS the four-kernel diagram and was referenced by nothing; the geometry _v2
        # is now drawn by make_offaxis_geometry_svg.py. The old geometry PNG is dropped: it
        # duplicated the new one and its embedded panel still called `:cic` the fast
        # alternative to `:overlap`, i.e. two of the four kernels and the wrong default.
        t = t.replace("assets/offaxis/offaxis_cell_treatment_v2.svg",
                      "assets/offaxis/offaxis_cell_treatment.svg")
        t = t.replace(
            "![Off-axis projection geometry: parallel rays from the observer through the "
            "simulation box onto the image plane](assets/offaxis/offaxis_geometry.png)\n\n", "")
        t = t.replace("Left inset:", "Right inset:")
        t = t.replace('| `weighting` | **Array**, `[:mass, missing]` | **Symbol**, `:mass` — and `:sph`/`:voronoi` are accepted but silently give a mass-weighted map off-axis |', '| `weighting` | **Array**, `[:mass, missing]` | **Symbol**, `:mass`, `:volume`, `:sph`, `:voronoi` — all available off-axis. `:sph` conserves mass to ~0.2 % independent of angle; `:voronoi` trades that for sharp cell edges (~3 % angle spread), so prefer `:sph` for quantitative maps |')
        t = t.replace('| `fov` / `fov_unit` / `aperture` | yes | **absent** — passing them is a `MethodError`; use world ranges with an explicit `zrange` |', '| `fov` / `fov_unit` / `aperture` | yes | **yes** — same rotation-invariant sphere selection; the framing is a selection, so it does not care what is deposited |')

        t = t.replace("`fov` selects a **sphere** of radius `fov` about `center`",
                      "`fov` selects a **sphere** about `center` (radius `fov`, or `√2·fov` "
                      "for `aperture=:square`)")
        t = t.replace("<FILL IN — measure before writing prose>", RUNTIME)
        t = t.replace("&lt;FILL IN — measure before writing prose&gt;", RUNTIME)
        if "σ_LOS is a width measured INSIDE a pixel" in t or "depends on the pixel" in t:
            t = SIGMA_PROSE
    return kind, t


CELLS = []
for c in b["chapters"]:
    for k, cell in enumerate(c["cells"]):
        kind, text = apply(cell, c["n"], k)
        # The blueprint keeps each chapter's title in a `title` FIELD, not in the cell text, so a
        # naive assembly loses every heading and the page becomes an unnavigable wall of prose.
        # Give each chapter its heading on its first cell, unless the cell already opens with one.
        if k == 0:
            head = c["title"] if c["title"].lstrip().startswith("Appendix") else f'{c["n"]}. {c["title"]}'
            if not text.lstrip().startswith("#"):
                if kind == "markdown":
                    text = f"## {head}\n\n" + text
                else:
                    CELLS.append(("markdown", f"## {head}\n"))
        CELLS.append((kind, text))
        for extra in EXTRAS.get((c["n"], k), []):
            CELLS.append(extra)


def build():
    cells = []
    for kind, text in CELLS:
        src = (text.rstrip("\n") + "\n").splitlines(keepends=True)
        if kind == "markdown":
            cells.append({"cell_type": "markdown", "metadata": {}, "source": src})
        else:
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                          "outputs": [], "source": src})
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Mera-Docs 1.12 (4t) 1.12",
                                        "language": "julia", "name": "mera-docs-1.12-_4t_-1.12"},
                         "language_info": {"file_extension": ".jl", "mimetype": "application/julia",
                                           "name": "julia", "version": "1.12.3"}},
            "nbformat": 4, "nbformat_minor": 4}


def preflight():
    out = ["# AUTO-GENERATED pre-flight for the rebuilt 06_offaxis notebook.\n__t0 = time()\n"]
    for i, (kind, text) in enumerate(CELLS):
        if kind != "code":
            continue
        out.append(f"\n# ===================== cell {i} =====================\n")
        out.append(text)
        out.append(f'\nprintln(">>> cell {i} ok  (", round(time()-__t0, digits=1), " s)")\n__t0 = time()\n')
    return "".join(out)


if __name__ == "__main__":
    open(OUT_JL, "w").write(preflight())
    print("wrote", OUT_JL)
    if "--preflight-only" not in sys.argv:
        json.dump(build(), open(OUT_NB, "w"), indent=1)
        open(OUT_NB, "a").write("\n")
        ncode = sum(1 for k, _ in CELLS if k == "code")
        print(f"wrote {OUT_NB}: {len(CELLS)} cells ({ncode} code, {len(CELLS)-ncode} md)")
