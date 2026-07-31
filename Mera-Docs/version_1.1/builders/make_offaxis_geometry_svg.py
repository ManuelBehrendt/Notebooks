#!/usr/bin/env python3
"""Draw assets/offaxis/offaxis_geometry_v2.svg for the off-axis projection chapter.

The chapter's caption promises two things the older PNG does not show: the camera basis
(r̂, û, ŵ) planted at `center` with genuinely PARALLEL rays (orthographic — camera distance
is not a parameter), and an inset contrasting the two reference axes `inclination` can be
measured from. Coordinates are computed from a real 3-D→2-D projection rather than eyeballed,
so the rays are parallel and the basis is orthonormal on the page as well as in the text.
"""
import math, os

W, H = 1200, 640
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "..", "..", "Users", "mabe", "code-github", "Mera.jl",
                   "docs", "src", "assets", "offaxis", "offaxis_geometry_v2.svg")
OUT = os.path.abspath(os.environ.get("OFFAXIS_SVG_OUT", OUT))

C = dict(ink="#0f172a", mute="#64748b", faint="#cbd5e1", box="#94a3b8",
         r="#ea580c", u="#b91c1c", w="#2563eb", plane="#16a34a", ang="#7c3aed", bg="#ffffff")


def sub(a, b):   return [a[i] - b[i] for i in range(3)]
def add(*vs):    return [sum(v[i] for v in vs) for i in range(3)]
def mul(v, s):   return [c * s for c in v]
def dot(a, b):   return sum(a[i] * b[i] for i in range(3))
def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(v):
    n = math.sqrt(dot(v, v));  return [c / n for c in v]


# ── viewing transform for the DRAWING itself (not the camera being illustrated) ──────────
VAZ, VEL = math.radians(28), math.radians(20)


def proj(p, cx, cy, s):
    """Axonometric 3-D → 2-D. Linear, so parallel lines stay parallel on the page."""
    x, y, z = p
    sx = (x * math.cos(VAZ) - y * math.sin(VAZ))
    sy = (x * math.sin(VAZ) + y * math.cos(VAZ)) * math.sin(VEL) - z * math.cos(VEL)
    return (cx + s * sx, cy + s * sy)


def path(pts, **kw):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    if kw.pop("close", False):
        d += " Z"
    return f'  <path d="{d}" {attrs(kw)}/>'


def attrs(kw):
    m = {"stroke": "stroke", "fill": "fill", "sw": "stroke-width", "op": "opacity",
         "dash": "stroke-dasharray", "marker": "marker-end", "cap": "stroke-linecap"}
    out = []
    for k, v in kw.items():
        out.append(f'{m.get(k,k)}="{v}"')
    return " ".join(out)


def text(x, y, s, size=15, fill=C["ink"], anchor="start", weight="normal", style="normal"):
    return (f'  <text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{s}</text>')


# ══ MAIN PANEL: the box, the camera basis, parallel rays, the image plane ════════════════
CX, CY, S = 420, 350, 104

# camera orientation being illustrated: inclination from +z, azimuth about z
inc, azi = math.radians(58), math.radians(35)
w = norm([math.sin(inc) * math.cos(azi), math.sin(inc) * math.sin(azi), math.cos(inc)])
# ŵ points INTO the image, away from the observer, so the observer sits at −ŵ
up_ref = [0, 0, 1]
r = norm(cross(up_ref, w))          # r̂ = image horizontal
u = cross(w, r)                     # û = image vertical, completes a right-handed basis

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
         f'  <rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
         '  <defs>']
for name, col in (("aR", C["r"]), ("aU", C["u"]), ("aW", C["w"]),
                  ("aM", C["mute"]), ("aA", C["ang"])):
    parts.append(f'    <marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" '
                 f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                 f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
parts.append('  </defs>')

parts.append(text(28, 40, "Off-axis projection is orthographic", 21, C["ink"], weight="bold"))
parts.append(text(28, 64, "rays are parallel — there is no camera distance to set, only a "
                          "field of view", 15, C["mute"]))

# ── simulation box (unit cube, edges ±1) ────────────────────────────────────────────────
V = [[sx, sy, sz] for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
E = [(0,1),(1,3),(3,2),(2,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,6),(3,7)]
for a, b in E:
    pa, pb = proj(V[a], CX, CY, S), proj(V[b], CX, CY, S)
    parts.append(path([pa, pb], stroke=C["box"], sw=1.4, fill="none", op=0.85))
sb = proj([1, -1, -1], CX, CY, S)
parts.append(text(sb[0] + 10, sb[1] + 16, "simulation box", 13, C["box"]))

# ── image plane: a quad spanned by r̂ and û, on the observer's side of `center` ──────────
d, hw, hh = 2.95, 1.35, 1.08
ctr_plane = mul(w, -d)
quad = [add(ctr_plane, mul(r,  hw), mul(u,  hh)),
        add(ctr_plane, mul(r, -hw), mul(u,  hh)),
        add(ctr_plane, mul(r, -hw), mul(u, -hh)),
        add(ctr_plane, mul(r,  hw), mul(u, -hh))]
parts.append(path([proj(p, CX, CY, S) for p in quad], close=True,
                  fill=C["plane"], op=0.13, stroke=C["plane"], sw=1.8))
lab = proj(add(ctr_plane, mul(r, -hw), mul(u, -hh)), CX, CY, S)
parts.append(text(lab[0] + 2, lab[1] + 20, "image plane", 14, C["plane"], anchor="middle"))

# ── parallel rays: from the image plane, along ŵ, straight through the box ──────────────
for a, b in ((-0.62, 0.5), (0.0, -0.1), (0.66, 0.42), (-0.3, -0.62)):
    start = add(ctr_plane, mul(r, a * hw), mul(u, b * hh))
    end = add(start, mul(w, d + 2.3))
    parts.append(path([proj(start, CX, CY, S), proj(end, CX, CY, S)],
                      stroke=C["w"], sw=1.6, fill="none", op=0.55, dash="8 5"))

# ── camera basis planted at `center` ────────────────────────────────────────────────────
O = proj([0, 0, 0], CX, CY, S)
for vec, col, mk, name, L in ((r, C["r"], "aR", "r̂", 1.15),
                              (u, C["u"], "aU", "û", 1.15),
                              (w, C["w"], "aW", "ŵ", 1.5)):
    tip = proj(mul(vec, L), CX, CY, S)
    parts.append(path([O, tip], stroke=col, sw=3.0, fill="none", marker=f"url(#{mk})",
                      cap="round"))
    # place the label OUTWARD along the arrow, so it never lands on its own shaft
    dx, dy = tip[0] - O[0], tip[1] - O[1]
    n = math.hypot(dx, dy) or 1.0
    parts.append(text(tip[0] + 20 * dx / n, tip[1] + 20 * dy / n + 6, name, 18, col,
                      weight="bold", anchor="middle"))
parts.append(f'  <circle cx="{O[0]:.1f}" cy="{O[1]:.1f}" r="5" fill="{C["ink"]}"/>')
parts.append(text(O[0] + 10, O[1] + 24, "center", 14, C["ink"]))

# box z axis, for the inclination angle
ztip = proj([0, 0, 1.5], CX, CY, S)
parts.append(path([O, ztip], stroke=C["mute"], sw=1.6, fill="none", dash="5 4",
                  marker="url(#aM)"))
parts.append(text(ztip[0] + 8, ztip[1] + 4, "box z", 13, C["mute"]))

# inclination arc between box z and ŵ
arc = [proj(norm(add(mul([0, 0, 1], 1 - t), mul(w, t))), CX, CY, S)
       for t in [i / 24 for i in range(25)]]
arc = [(x + (O[0] - proj([0, 0, 0], CX, CY, S)[0]), y) for x, y in arc]
parts.append(path([(x, y) for x, y in
                   [proj(mul(norm(add(mul([0,0,1], 1-t), mul(w, t))), 0.72), CX, CY, S)
                    for t in [i/24 for i in range(25)]]],
                  stroke=C["ang"], sw=2.2, fill="none"))
mid = proj(mul(norm(add(mul([0,0,1], 0.5), mul(w, 0.5))), 0.86), CX, CY, S)
parts.append(text(mid[0] + 6, mid[1] - 2, "inclination", 14, C["ang"], weight="bold"))

parts.append(text(28, H - 46, "ŵ points INTO the image, away from the observer", 14, C["w"]))
parts.append(text(28, H - 26, "so v·ŵ > 0 is receding — an edge-on v_LOS map must be "
                              "antisymmetric about the minor axis", 13, C["mute"]))

# ══ INSET: the two reference axes `inclination` can be measured FROM ═════════════════════
IX, IY, IS = 900, 300, 92
parts.append(f'  <line x1="770" y1="90" x2="770" y2="{H-70}" stroke="{C["faint"]}" '
             f'stroke-width="1.5"/>')
parts.append(text(812, 118, "inclination from WHICH axis?", 18, C["ink"], weight="bold"))
parts.append(text(812, 142, "the same number, two different pictures", 14, C["mute"]))

# a disc whose own normal L is tilted away from the box z
tilt = math.radians(34)
L = norm([math.sin(tilt), 0, math.cos(tilt)])
e1 = norm(cross(L, [0, 1, 0]))
e2 = cross(L, e1)
ring = [add(mul(e1, math.cos(t)), mul(e2, math.sin(t)))
        for t in [2 * math.pi * i / 72 for i in range(73)]]
parts.append(path([proj(p, IX, IY, IS) for p in ring], close=True,
                  fill=C["box"], op=0.30, stroke=C["box"], sw=1.6))

Oi = proj([0, 0, 0], IX, IY, IS)
zt = proj([0, 0, 1.45], IX, IY, IS)
lt = proj(mul(L, 1.45), IX, IY, IS)
parts.append(path([Oi, zt], stroke=C["mute"], sw=2.4, fill="none", marker="url(#aM)"))
parts.append(path([Oi, lt], stroke=C["ang"], sw=2.8, fill="none", marker="url(#aA)"))
parts.append(text(zt[0] - 8, zt[1] - 8, "box z", 14, C["mute"], anchor="end"))
parts.append(text(lt[0] + 8, lt[1] - 6, "L", 17, C["ang"], weight="bold"))
parts.append(path([proj(mul(norm(add(mul([0,0,1], 1-t), mul(L, t))), 0.80), IX, IY, IS)
                   for t in [i/24 for i in range(25)]],
                  stroke=C["ang"], sw=2.0, fill="none"))
tm = proj(mul(norm(add(mul([0,0,1], .5), mul(L, .5))), 0.95), IX, IY, IS)
parts.append(text(tm[0] + 4, tm[1] - 4, "34°", 14, C["ang"], weight="bold"))
parts.append(f'  <circle cx="{Oi[0]:.1f}" cy="{Oi[1]:.1f}" r="4" fill="{C["ink"]}"/>')

y0 = 448
parts.append(text(812, y0, "axis=:z", 15, C["mute"], weight="bold"))
parts.append(text(812, y0 + 20, "measured from the box z axis (the default)", 13, C["mute"]))
parts.append(text(812, y0 + 52, "axis=:angmom", 15, C["ang"], weight="bold"))
parts.append(text(812, y0 + 72, "measured from the disc's own angular-", 13, C["mute"]))
parts.append(text(812, y0 + 89, "momentum axis L", 13, C["mute"]))
parts.append(text(812, y0 + 121, "Here they differ by 34°, so inclination=60", 13, C["ink"]))
parts.append(text(812, y0 + 138, "means two different views. If the disc is not", 13, C["ink"]))
parts.append(text(812, y0 + 155, "aligned with the box, say which axis you mean.", 13, C["ink"]))

parts.append('</svg>')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write("\n".join(parts) + "\n")
print("wrote", OUT, f"({os.path.getsize(OUT)} bytes)")
