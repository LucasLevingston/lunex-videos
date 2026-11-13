"""Rig vetorial do Ruan (série "30 dias pro Ruan").

Cada membro é um <g> aninhado com id próprio e rotação em torno da junta,
para poder animar no HyperFrames/CSS (transform-origin = a junta).
Uso: python ruan.py <pasta_saida>
"""
import math, os, sys

INK = "#16121A"
SK = "#C68A5C"      # pele
SK_D = "#A86F45"    # sombra da pele
HAIR = "#2A1C14"
TOP = "#F4F0E6"     # regata
TOP_D = "#DCD6C8"
SHORT = "#2F8F4E"   # bermuda verde
SHORT_D = "#23703C"
STAIN = "#E8445E"
JUICE = "#E9A62A"
SEED = "#1E1A1A"
FLIP = "#F3C431"
SOLE = "#3B3B3F"
SW = 6  # espessura do contorno

_uid = [0]
def uid(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"

def st(fill, w=SW):
    return f'fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'

def seg(L, w, fill):
    return f'<rect x="{-w/2}" y="{-w/2}" width="{w}" height="{L+w}" rx="{w/2}" {st(fill)}/>'

# ---------------------------------------------------------------- membros
UA, FA, AW = 105, 95, 24     # braço, antebraço, largura
TH, SH, LW = 125, 150, 26    # coxa, canela, largura

def arm(side, a1, a2, x, y, prop="", fist=False, muscle=False):
    """side: 'L' (esquerda da tela) ou 'R'."""
    hand = f'<circle cx="0" cy="{FA+4}" r="{17 if not fist else 19}" {st(SK)}/>'
    if fist:
        hand += f'<path d="M-8 {FA} q8 6 16 0" fill="none" stroke="{INK}" stroke-width="4"/>'
    bic = ""
    if muscle:
        s = -1 if side == "L" else 1
        bic = f'<ellipse cx="{s*6}" cy="{UA*0.45}" rx="{AW*0.85}" ry="{UA*0.3}" {st(SK)}/>'
    return (f'<g id="braco_{side}" transform="translate({x} {y}) rotate({a1})">'
            f'{seg(UA, AW, SK)}{bic}'
            f'<g id="antebraco_{side}" transform="translate(0 {UA}) rotate({a2})">'
            f'{seg(FA, AW-2, SK)}{hand}{prop}</g></g>')

def hand_pos(a1, a2, x, y):
    r1 = math.radians(a1); ex, ey = x - UA*math.sin(r1), y + UA*math.cos(r1)
    r2 = math.radians(a1+a2); return ex - (FA+4)*math.sin(r2), ey + (FA+4)*math.cos(r2)

def leg(side, a1, a2, x, y, clean=False):
    s = -1 if side == "L" else 1
    foot = (f'<g transform="translate(0 {SH+6})">'
            f'<ellipse cx="{s*14}" cy="12" rx="38" ry="12" {st(SOLE)}/>'
            f'<ellipse cx="{s*14}" cy="4" rx="30" ry="11" {st(SK)}/>'
            f'<path d="M{s*2} -4 L{s*14} 8 L{s*30} -2" fill="none" stroke="{FLIP}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M{s*2} -4 L{s*14} 8 L{s*30} -2" fill="none" stroke="{INK}" stroke-width="2"/></g>')
    shorts = (f'<path d="M-30 -18 L30 -18 L33 92 Q0 100 -33 92 Z" {st(SHORT)}/>'
              f'<path d="M-20 78 L-20 92 M0 82 L0 96 M20 78 L20 92" stroke="{SHORT_D}" stroke-width="3"/>')
    return (f'<g id="coxa_{side}" transform="translate({x} {y}) rotate({a1})">'
            f'{seg(TH, LW, SK)}{shorts}'
            f'<g id="canela_{side}" transform="translate(0 {TH}) rotate({a2})">'
            f'{seg(SH, LW-2, SK)}{foot}</g></g>')

# ---------------------------------------------------------------- tronco
def torso(stains=True, clean=False):
    skin = (f'<rect x="284" y="380" width="32" height="70" {st(SK)}/>'
            f'<path d="M238 470 Q240 438 270 432 L330 432 Q360 438 362 470 L360 520 L240 520 Z" {st(SK)}/>')
    top = (f'<path d="M262 430 L282 430 Q300 462 318 430 L338 430 Q342 490 356 512 '
           f'L352 650 Q300 662 248 650 L244 512 Q258 490 262 430 Z" {st(TOP)}/>'
           f'<path d="M262 436 Q256 495 246 512" fill="none" stroke="{TOP_D}" stroke-width="5"/>')
    if stains:
        top += (f'<path d="M272 540 q14 -12 26 0 q10 14 -6 22 q-20 6 -20 -22z" fill="{JUICE}" opacity=".85"/>'
                f'<path d="M318 590 q10 -8 20 2 q4 12 -10 14 q-14 -2 -10 -16z" fill="{JUICE}" opacity=".85"/>'
                f'<circle cx="300" cy="612" r="8" fill="{JUICE}" opacity=".8"/><circle cx="262" cy="600" r="5" fill="{JUICE}" opacity=".8"/>'
                f'<path d="M330 536 q6 10 0 18" stroke="{JUICE}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    waist = (f'<path d="M248 628 L352 628 L356 676 L244 676 Z" {st(SHORT)}/>'
             f'<path d="M246 644 L354 644" stroke="{SHORT_D}" stroke-width="4"/>'
             f'<rect x="292" y="630" width="16" height="12" fill="{FLIP}" stroke="{INK}" stroke-width="3"/>')
    return f'<g id="tronco">{skin}{top}</g>', f'<g id="cintura">{waist}</g>'

# ---------------------------------------------------------------- cabeça
EXPR = {
    #          lid  brow(dy, ang)   mouth        pupils     extras
    "neutro":     dict(lid=.45, brow=(0, 4),    mouth="flat",  pupil="n"),
    "sono":       dict(lid=1.0, brow=(6, 0),    mouth="drool", pupil="n", extra=["z"]),
    "susto":      dict(lid=0,   brow=(-22, -10), mouth="o",    pupil="small"),
    "apaixonado": dict(lid=.15, brow=(-10, -6), mouth="smile", pupil="heart", extra=["blush"]),
    "suando":     dict(lid=0,   brow=(-8, -14), mouth="grit",  pupil="small", extra=["sweat"]),
    "confiante":  dict(lid=.4,  brow=(0, 12),   mouth="smirk", pupil="n", brow_r=(-18, -8)),
    "vergonha":   dict(lid=.35, brow=(-6, -14), mouth="wavy",  pupil="down", extra=["blush2", "sweat1"]),
    "feliz":      dict(lid=0,   brow=(-14, -4), mouth="grin",  pupil="n"),
}

def eye(cx, cy, e, side):
    rx, ry = 27, 31
    cid = uid("olho")
    out = (f'<clipPath id="{cid}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff"/>')
    p = e["pupil"]
    if p == "heart":
        out += (f'<path d="M{cx} {cy+12} l-15 -15 a8 8 0 0 1 15 -9 a8 8 0 0 1 15 9 z" fill="{STAIN}" '
                f'stroke="{INK}" stroke-width="3" clip-path="url(#{cid})"/>')
    else:
        r, dy, dx = {"n": (11, 4, 0), "small": (6, 0, 0), "down": (11, 14, 6 if side == "L" else 6)}[p]
        out += f'<circle cx="{cx+dx}" cy="{cy+dy}" r="{r}" fill="{INK}" clip-path="url(#{cid})"/>'
        out += f'<circle cx="{cx+dx+4}" cy="{cy+dy-4}" r="{max(2, r/3.5)}" fill="#fff" clip-path="url(#{cid})"/>'
    lid = e["lid"]
    if lid >= 1:
        out += (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{SK}"/>'
                f'<path d="M{cx-rx+2} {cy+4} Q{cx} {cy+16} {cx+rx-2} {cy+4}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
        return out
    if lid > 0:
        ly = cy - ry + 2*ry*lid
        out += f'<rect x="{cx-rx-2}" y="{cy-ry-2}" width="{2*rx+4}" height="{ly-cy+ry+2}" fill="{SK}" clip-path="url(#{cid})"/>'
        out += f'<line x1="{cx-rx+3}" y1="{ly}" x2="{cx+rx-3}" y2="{ly}" stroke="{INK}" stroke-width="5" stroke-linecap="round" clip-path="url(#{cid})"/>'
    out += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="5"/>'
    return out

def brow(cx, cy, dy, ang, side):
    a = ang if side == "L" else -ang
    return (f'<path d="M{cx-24} {cy} Q{cx} {cy-10} {cx+24} {cy}" fill="none" stroke="{HAIR}" stroke-width="10" '
            f'stroke-linecap="round" transform="translate(0 {dy}) rotate({a} {cx} {cy})"/>')

def mouth(kind):
    m = {
        "flat":  f'<path d="M278 372 Q300 366 322 372" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>',
        "drool": (f'<ellipse cx="300" cy="374" rx="16" ry="11" {st("#5A1E26", 5)}/>'
                  f'<path d="M312 380 q4 18 0 26 q-6 4 -6 -4 z" fill="#BFE6FF" stroke="{INK}" stroke-width="3"/>'),
        "o":     f'<ellipse cx="300" cy="380" rx="18" ry="24" {st("#5A1E26", 5)}/>',
        "smile": (f'<path d="M270 366 Q300 400 330 366 Z" {st("#5A1E26", 5)}/>'
                  f'<path d="M282 384 Q300 396 318 384" fill="#E8708A"/>'),
        "grit":  (f'<rect x="268" y="360" width="64" height="28" rx="10" {st("#fff", 5)}/>'
                  f'<path d="M268 374 H332 M284 360 V388 M300 360 V388 M316 360 V388" stroke="{INK}" stroke-width="3"/>'),
        "smirk": f'<path d="M276 374 Q304 382 326 362" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>',
        "wavy":  f'<path d="M276 376 q8 -8 16 0 q8 8 16 0 q8 -8 16 0" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>',
        "grin":  (f'<path d="M262 358 Q300 418 338 358 Z" {st("#5A1E26", 5)}/>'
                  f'<path d="M270 362 L330 362 L326 374 L274 374 Z" fill="#fff"/>'
                  f'<path d="M286 396 Q300 406 314 396 Q300 388 286 396" fill="#E8708A"/>'),
    }
    return m[kind]

def hair(messy=True):
    if messy:
        pts = [(196, 270), (190, 210), (214, 222), (212, 168), (244, 190), (256, 140), (282, 176),
               (300, 128), (318, 172), (348, 138), (352, 186), (390, 164), (384, 214), (410, 206), (404, 270)]
        d = "M" + " L".join(f"{x} {y}" for x, y in pts) + " Q300 196 196 270 Z"
        tuft = f'<path d="M300 132 q-14 -26 6 -40 q-2 20 14 26" {st(HAIR)}/>'
        return f'<g id="cabelo">{tuft}<path d="{d}" {st(HAIR)}/></g>'
    return (f'<g id="cabelo"><path d="M196 272 Q188 170 300 160 Q412 170 404 272 Q380 214 300 210 '
            f'Q238 206 214 238 Q206 250 196 272 Z" {st(HAIR)}/>'
            f'<path d="M262 170 Q282 196 330 194" fill="none" stroke="#4A3428" stroke-width="5"/></g>')

def head(expr="neutro", stubble=True, bags=True, messy_hair=True, tilt=0, dy=0):
    e = EXPR[expr]
    ex = e.get("extra", [])
    g = [f'<g id="cabeca" transform="translate(0 {dy}) rotate({tilt} 300 410)">']
    g.append(f'<circle cx="194" cy="306" r="22" {st(SK)}/><circle cx="406" cy="306" r="22" {st(SK)}/>')
    g.append(f'<path d="M196 300 Q192 182 300 176 Q408 182 404 300 Q402 392 300 414 Q198 392 196 300 Z" {st(SK)}/>')
    if stubble:
        g.append("".join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{SK_D}"/>'
                         for x, y in [(240, 362), (252, 382), (268, 396), (286, 404), (314, 404), (332, 396),
                                      (348, 382), (360, 362), (262, 380), (338, 380), (300, 398), (276, 388), (324, 388)]))
    g.append(hair(messy_hair))
    if bags:
        g.append(f'<path d="M236 322 Q258 334 280 322 M320 322 Q342 334 364 322" fill="none" stroke="#7B5A86" stroke-width="5" stroke-linecap="round"/>')
    for (cx, side) in [(256, "L"), (344, "R")]:
        g.append(eye(cx, 286, e, side))
    bl = e["brow"]; br = e.get("brow_r", bl)
    g.append(brow(256, 244, bl[0], bl[1], "L"))
    g.append(brow(344, 244, br[0], br[1], "R"))
    g.append(f'<path d="M292 304 Q284 336 300 340 Q312 340 310 328" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
    if "blush" in ex or "blush2" in ex:
        op = .55 if "blush" in ex else .8
        g.append(f'<ellipse cx="232" cy="340" rx="22" ry="12" fill="#F06A86" opacity="{op}"/>'
                 f'<ellipse cx="368" cy="340" rx="22" ry="12" fill="#F06A86" opacity="{op}"/>')
    g.append(mouth(e["mouth"]))
    if "sweat" in ex:
        for x, y, s in [(410, 220, 1), (190, 240, .8), (396, 268, .7)]:
            g.append(f'<path d="M{x} {y} q{10*s} {18*s} 0 {26*s} q{-10*s} {-8*s} 0 {-26*s}z" fill="#9ED8FF" stroke="{INK}" stroke-width="3"/>')
    if "sweat1" in ex:
        g.append(f'<path d="M402 236 q10 18 0 26 q-10 -8 0 -26z" fill="#9ED8FF" stroke="{INK}" stroke-width="3"/>')
    if "z" in ex:
        g.append(f'<text x="420" y="170" font-family="DejaVu Sans" font-weight="bold" font-size="54" fill="#fff" stroke="{INK}" stroke-width="3">Z</text>'
                 f'<text x="460" y="120" font-family="DejaVu Sans" font-weight="bold" font-size="38" fill="#fff" stroke="{INK}" stroke-width="3">z</text>')
    g.append("</g>")
    return "".join(g)

# ---------------------------------------------------------------- camadas de estado
def stink():
    lines = []
    for x, y, s in [(170, 520, 1), (420, 500, -1), (160, 700, 1), (440, 690, -1), (220, 170, 1), (380, 150, -1)]:
        lines.append(f'<path d="M{x} {y} q{12*s} -18 0 -36 q{-12*s} -18 0 -36 q{12*s} -18 0 -36" fill="none" '
                     f'stroke="#7DBA3C" stroke-width="7" stroke-linecap="round" opacity=".9"/>')
    return f'<g id="camada_cheiro">{"".join(lines)}</g>'

# ---------------------------------------------------------------- props
def phone():
    return (f'<g transform="translate(-6 {FA-36}) rotate(-8)"><rect x="-22" y="-40" width="44" height="78" rx="8" {st("#2B2B33", 5)}/>'
            f'<rect x="-15" y="-31" width="30" height="58" rx="4" fill="#7FD3FF"/>'
            f'<path d="M-6 -6 l6 6 l-6 6 M4 -6 l6 6 l-6 6" stroke="#fff" stroke-width="3" fill="none"/></g>')

def leaf(bx, by, dx, h, w, sw=5):
    tx, ty = bx + dx, by - h
    return (f'<path d="M{bx-w} {by} Q{bx-w+dx*0.3} {by-h*0.55} {tx} {ty} Q{bx+w+dx*0.3} {by-h*0.55} {bx+w} {by} Z" '
            f'fill="#3E9A4A" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')

def abacaxi(cx, cy, rx=52, ry=70):
    cid = uid("abx")
    leaves = "".join(leaf(cx, cy-ry+10, dx, h, 13) for dx, h in [(-40, 46), (40, 46), (-20, 70), (20, 70), (0, 86)])
    hatch = "".join(f'<path d="M{cx-rx-40+k} {cy-ry} l{2*ry*0.6} {2*ry} M{cx+rx+40-k} {cy-ry} l{-2*ry*0.6} {2*ry}" stroke="#B9781E" stroke-width="5"/>'
                    for k in range(0, int(2*rx+80), 26))
    return (f'{leaves}<clipPath id="{cid}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#F2B63C"/>'
            f'<g clip-path="url(#{cid})">{hatch}</g>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{SW}"/>')

def melon(cx, cy, rx=82, ry=60, face=False):
    stripes = "".join(f'<path d="M{cx+dx} {cy-ry+6} Q{cx+dx*1.25} {cy} {cx+dx} {cy+ry-6}" fill="none" stroke="#1E5E2F" stroke-width="9"/>'
                      for dx in (-48, -16, 16, 48))
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#4FA65A"/>{stripes}'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{SW}"/>')

# ---------------------------------------------------------------- poses
POSES = {
    #                 braço L        braço R        perna L    perna R
    "em_pe":        dict(aL=(10, -4),  aR=(-10, 4),  lL=(4, -2),  lR=(-4, 2)),
    "derrotado":    dict(aL=(3, 0),    aR=(-3, 0),   lL=(2, 4),   lR=(-2, -4), tilt=6, hdy=18),
    "comemorando":  dict(aL=(148, 18), aR=(-148, -18), lL=(10, -6), lR=(-10, 6), fist=True),
    "correndo":     dict(aL=(40, -75), aR=(-55, -40), lL=(28, -10), lR=(-38, 70), tilt=-4),
    "celular":      dict(aL=(10, -4),  aR=(28, 128), lL=(4, -2),  lR=(-4, 2), tilt=5, hdy=6, phone=True),
    "abacaxi":      dict(aL=(-40, -88), aR=(40, 88), lL=(8, -4),  lR=(-8, 4), melon=True),
    "apontando":    dict(aL=(10, -4),  aR=(-95, -5), lL=(4, -2),  lR=(-4, 2)),
}

SHOULDER = {"L": (252, 458), "R": (348, 458)}
HIP = {"L": (276, 660), "R": (324, 660)}

def character(pose="em_pe", expr="neutro", dirty=True, bags=True, stubble=True, messy_hair=True, muscle=False):
    p = POSES[pose]
    parts = []
    if dirty:
        parts.append(stink())
    for s in ("L", "R"):
        parts.append(leg(s, *p[f"l{s}"], *HIP[s]))
    tor, waist = torso(stains=dirty)
    parts.append(waist)
    parts.append(tor)
    for s in ("L", "R"):
        prop = phone() if (p.get("phone") and s == "R") else ""
        parts.append(arm(s, *p[f"a{s}"], *SHOULDER[s], prop=prop, fist=p.get("fist", False), muscle=muscle))
    if p.get("melon"):
        hl = hand_pos(*p["aL"], *SHOULDER["L"]); hr = hand_pos(*p["aR"], *SHOULDER["R"])
        cx, cy = (hl[0]+hr[0])/2, (hl[1]+hr[1])/2 + 6
        parts.append(abacaxi(cx, cy - 4, 50, 66))
        for hx, hy in (hl, hr):
            parts.append(f'<circle cx="{hx}" cy="{hy}" r="17" {st(SK)}/>')
    parts.append(head(expr, stubble=stubble, bags=bags, messy_hair=messy_hair, tilt=p.get("tilt", 0), dy=p.get("hdy", 0)))
    return f'<g id="ruan">{"".join(parts)}</g>'

def svg(body, w=600, h=1000, vb=None, bg=None):
    vb = vb or f"0 0 {w} {h}"
    b = f'<rect x="-2000" y="-2000" width="5000" height="5000" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{b}{body}</svg>'

def sleeping(expr="sono", **kw):
    rede_back = (f'<path d="M30 300 Q500 560 970 300" fill="none" stroke="#8B5A2B" stroke-width="10"/>'
                 f'<path d="M70 330 Q500 640 930 330 L930 350 Q500 680 70 350 Z" fill="#C9502A" stroke="{INK}" stroke-width="{SW}"/>')
    body = character("em_pe", expr, **kw).replace('<text', '<text display="none"')
    guy = f'<g transform="translate(960 330) rotate(82) translate(-300 0)">{body}</g>'
    rede_front = (f'<path d="M90 380 Q500 720 910 380 Q500 610 90 380 Z" fill="#F29A3C" stroke="{INK}" stroke-width="{SW}"/>'
                  f'<path d="M160 440 Q500 700 840 440" fill="none" stroke="#E86A3A" stroke-width="10"/>')
    z = (f'<text x="780" y="210" font-family="DejaVu Sans" font-weight="bold" font-size="64" fill="#fff" stroke="{INK}" stroke-width="3">Z</text>'
         f'<text x="840" y="150" font-family="DejaVu Sans" font-weight="bold" font-size="44" fill="#fff" stroke="{INK}" stroke-width="3">z</text>')
    return rede_back + guy + rede_front + z

def hiding(expr="susto", **kw):
    body = character("em_pe", expr, **kw)
    guy = f'<g transform="translate(0 210)">{body}</g>'
    pile = "".join(abacaxi(x, y, 66, 84) for x, y in [(240, 730), (420, 735), (150, 820), (330, 830), (510, 820)])
    hands = (f'<circle cx="215" cy="618" r="17" {st(SK)}/><circle cx="385" cy="618" r="17" {st(SK)}/>')
    return guy + pile + hands

def main(out):
    os.makedirs(f"{out}/poses", exist_ok=True)
    os.makedirs(f"{out}/expressoes", exist_ok=True)
    os.makedirs(f"{out}/ajustes", exist_ok=True)
    for name in POSES:
        expr = {"comemorando": "feliz", "derrotado": "vergonha", "correndo": "suando",
                "celular": "apaixonado", "abacaxi": "confiante", "apontando": "confiante"}.get(name, "neutro")
        open(f"{out}/poses/{name}.svg", "w").write(svg(character(name, expr)))
    open(f"{out}/poses/dormindo_rede.svg", "w").write(svg(sleeping(), 1000, 700, "0 60 1000 700"))
    open(f"{out}/poses/escondido.svg", "w").write(svg(hiding(), 660, 700, "-30 130 660 700"))
    for name in EXPR:
        open(f"{out}/expressoes/{name}.svg", "w").write(svg(head(name), 520, 460, "40 70 520 460"))
    # estados que mudam com os votos
    stages = {
        "0_inicio":        dict(dirty=True,  bags=True,  stubble=True,  messy_hair=True),
        "1_banho":         dict(dirty=False, bags=True,  stubble=True,  messy_hair=True),
        "2_acorda_cedo":   dict(dirty=False, bags=False, stubble=True,  messy_hair=True),
        "3_cabelo_barba":  dict(dirty=False, bags=False, stubble=False, messy_hair=False),
        "4_academia":      dict(dirty=False, bags=False, stubble=False, messy_hair=False, muscle=True),
    }
    for n, kw in stages.items():
        expr = "neutro" if n == "0_inicio" else "confiante" if n.startswith("4") else "feliz"
        open(f"{out}/ajustes/{n}.svg", "w").write(svg(character("em_pe", expr, **kw)))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "kit")
