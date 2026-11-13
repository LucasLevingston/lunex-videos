"""Elenco e cenários da série "30 dias pro Ruan" (mesmo traço do ruan.py).
Uso: python elenco.py <pasta_kit>
"""
import os, sys
from ruan import st, seg, INK, SW, abacaxi, leaf, svg, character, uid

# ============================================================ BIA
M_SK = "#F4CFB2"; M_HAIR = "#F2CF5B"; M_HAIR_D = "#D9AE3A"; M_TOP = "#B9A3E8"; COAT = "#FBFBFF"; COAT_D = "#DCDDE8"
M_SKIRT = "#2E3F6E"; M_SHOE = "#F2F0EA"; LIP = "#D9536A"

def m_arm(side, a1, a2, x, y, extra=""):
    return (f'<g id="braco_{side}" transform="translate({x} {y}) rotate({a1})">{seg(100, 28, COAT)}'
            f'<g id="antebraco_{side}" transform="translate(0 100) rotate({a2})">'
            f'{seg(78, 26, COAT)}<circle cx="0" cy="98" r="15" {st(M_SK)}/>{extra}</g></g>')

def m_leg(side, a, x, y):
    s = -1 if side == "L" else 1
    return (f'<g id="perna_{side}" transform="translate({x} {y}) rotate({a})">{seg(250, 28, M_SKIRT)}'
            f'<path d="M{s*2} 246 q{s*30} -6 {s*34} 12 q-14 10 {-s*40} 4 z" {st(M_SHOE)}/></g>')

M_EXPR = {
    "sorrindo":    dict(lid=0,  brow=(-6, 0),  mouth="smile"),
    "desconfiada": dict(lid=.45, brow=(4, 10), mouth="side"),
    "enojada":     dict(lid=.55, brow=(8, 14), mouth="yuck", nose=True),
    "surpresa":    dict(lid=0,  brow=(-18, -6), mouth="o"),
}

def m_head(expr="sorrindo"):
    e = M_EXPR[expr]
    g = ['<g id="cabeca">']
    # cabelo loiro liso, comprido atrás
    g.append(f'<path d="M196 300 Q186 176 300 168 Q414 176 404 300 L410 440 Q398 470 380 448 Q340 462 300 452 Q260 462 220 448 Q202 470 190 440 Z" {st(M_HAIR)}/>'
             f'<path d="M236 330 L230 460 M364 330 L370 460" stroke="{M_HAIR_D}" stroke-width="6"/>')
    g.append(f'<path d="M206 300 Q204 190 300 184 Q396 190 394 300 Q392 386 300 404 Q208 386 206 300 Z" {st(M_SK)}/>')
    # franja de lado
    g.append(f'<path d="M200 292 Q190 172 300 170 Q410 176 404 290 Q384 214 330 206 Q290 250 214 262 Q206 276 200 292 Z" {st(M_HAIR)}/>'
             f'<path d="M330 210 Q300 236 250 248" fill="none" stroke="{M_HAIR_D}" stroke-width="5"/>')
    for cx, side in [(260, "L"), (340, "R")]:
        cid = uid("mo")
        g.append(f'<clipPath id="{cid}"><ellipse cx="{cx}" cy="290" rx="22" ry="25"/></clipPath>'
                 f'<ellipse cx="{cx}" cy="290" rx="22" ry="25" fill="#fff"/>'
                 f'<circle cx="{cx+2}" cy="294" r="12" fill="#4A90D9" clip-path="url(#{cid})"/>'
                 f'<circle cx="{cx+2}" cy="294" r="6" fill="{INK}" clip-path="url(#{cid})"/>'
                 f'<circle cx="{cx+6}" cy="290" r="3" fill="#fff"/>')
        if e["lid"]:
            ly = 265 + 50*e["lid"]
            g.append(f'<rect x="{cx-24}" y="262" width="48" height="{ly-262}" fill="{M_SK}" clip-path="url(#{cid})"/>'
                     f'<line x1="{cx-20}" y1="{ly}" x2="{cx+20}" y2="{ly}" stroke="{INK}" stroke-width="5" clip-path="url(#{cid})"/>')
        g.append(f'<ellipse cx="{cx}" cy="290" rx="22" ry="25" fill="none" stroke="{INK}" stroke-width="5"/>')
        # cílios
        d = -1 if side == "L" else 1
        g.append(f'<path d="M{cx+d*20} 274 l{d*10} -8 M{cx+d*22} 282 l{d*12} -4" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
        a = e["brow"][1] * (1 if side == "L" else -1)
        g.append(f'<path d="M{cx-18} 252 Q{cx} 244 {cx+18} 252" fill="none" stroke="{M_HAIR}" stroke-width="7" stroke-linecap="round" '
                 f'transform="translate(0 {e["brow"][0]}) rotate({a} {cx} 252)"/>')
    g.append(f'<path d="M296 306 Q290 330 302 332" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    g.append(f'<ellipse cx="240" cy="334" rx="16" ry="9" fill="#E87A8E" opacity=".5"/><ellipse cx="360" cy="334" rx="16" ry="9" fill="#E87A8E" opacity=".5"/>')
    mo = {"smile": f'<path d="M278 352 Q300 378 322 352 Q300 362 278 352 Z" {st(LIP, 4)}/>',
          "side":  f'<path d="M284 362 Q304 358 318 350" fill="none" stroke="{LIP}" stroke-width="7" stroke-linecap="round"/>',
          "yuck":  f'<path d="M280 362 q10 -10 20 0 q10 10 20 0" fill="none" stroke="{LIP}" stroke-width="7" stroke-linecap="round"/>',
          "o":     f'<ellipse cx="300" cy="362" rx="12" ry="16" {st(LIP, 4)}/>'}[e["mouth"]]
    g.append(mo)
    if e.get("nose"):
        g.append('<path d="M320 196 q12 -16 0 -32 q-12 -16 0 -32" fill="none" stroke="#7DBA3C" stroke-width="6" stroke-linecap="round"/>')
    g.append(f'<circle cx="208" cy="338" r="7" fill="#F3C431" stroke="{INK}" stroke-width="3"/><circle cx="392" cy="338" r="7" fill="#F3C431" stroke="{INK}" stroke-width="3"/>')
    g.append("</g>")
    return "".join(g)

M_POSES = {
    "em_pe":     dict(aL=(12, -6), aR=(-12, 6)),
    "acenando":  dict(aL=(12, -6), aR=(-140, -30)),
    "bracos_cruzados": dict(aL=(-25, -110), aR=(25, 110)),
    "nariz_tapado": dict(aL=(12, -6), aR=(130, 81)),
}

def bia(pose="em_pe", expr="sorrindo"):
    p = M_POSES[pose]
    parts = [m_leg("L", 3, 280, 690), m_leg("R", -3, 320, 690)]
    parts.append(f'<rect x="288" y="380" width="24" height="60" {st(M_SK)}/>')
    parts.append(f'<path d="M256 440 Q300 430 344 440 L346 600 L254 600 Z" {st(M_TOP)}/>')
    parts.append(f'<path d="M252 440 L286 440 L300 520 L298 740 L232 736 Z" {st(COAT)}/>'
                 f'<path d="M348 440 L314 440 L300 520 L302 740 L368 736 Z" {st(COAT)}/>'
                 f'<path d="M262 640 h26 v20 h-26z M312 640 h26 v20 h-26z" fill="none" stroke="{COAT_D}" stroke-width="4"/>')
    # estetoscópio
    parts.append(f'<path d="M276 444 Q262 520 300 540 Q338 520 324 444" fill="none" stroke="#3A3F52" stroke-width="7"/>'
                 f'<path d="M300 540 L300 572" stroke="#3A3F52" stroke-width="7"/>'
                 f'<circle cx="300" cy="582" r="13" fill="#C9CED8" stroke="{INK}" stroke-width="4"/>')
    # crachá
    parts.append(f'<rect x="318" y="560" width="36" height="24" rx="4" fill="#fff" stroke="{INK}" stroke-width="3"/>'
                 f'<path d="M324 568 h24 M324 576 h16" stroke="#4A90D9" stroke-width="3"/>')
    order = ["L", "R"]
    arms = {s: m_arm(s, *p[f"a{s}"], 258 if s == "L" else 342, 456) for s in order}
    if pose in ("acenando", "nariz_tapado"):
        parts += [arms["L"], m_head(expr), arms["R"]]
    else:
        parts += [arms["L"], arms["R"]]
        if pose == "bracos_cruzados":  # braço esquerdo por cima
            parts.append(arms["L"])
        parts.append(m_head(expr))
    return f'<g id="bia">{"".join(parts)}</g>'

# ============================================================ SEU COROA (abacaxi velho e ranzinza)
PINE = "#F2B63C"
def seu_coroa(expr="julgando"):
    cid = uid("sc")
    leaves = "".join(leaf(300, 112, dx, h, 30, 7) for dx, h in [(-110, 70), (110, 70), (-55, 110), (55, 110), (0, 135)])
    hatch = "".join(f'<path d="M{-100+k} 90 l250 420 M{700-k} 90 l-250 420" stroke="#B9781E" stroke-width="9"/>' for k in range(0, 800, 60))
    body = (f'{leaves}<clipPath id="{cid}"><ellipse cx="300" cy="300" rx="175" ry="205"/></clipPath>'
            f'<ellipse cx="300" cy="300" rx="175" ry="205" fill="{PINE}"/><g clip-path="url(#{cid})">{hatch}'
            f'<ellipse cx="300" cy="330" rx="120" ry="110" fill="{PINE}" opacity=".85"/></g>'
            f'<ellipse cx="300" cy="300" rx="175" ry="205" fill="none" stroke="{INK}" stroke-width="{SW+2}"/>'
            # bigode de coroa (o velho ranzinza)
            f'<path d="M232 354 Q266 330 300 352 Q334 330 368 354 Q340 372 300 362 Q260 372 232 354 Z" fill="#F4F0E6" stroke="{INK}" stroke-width="5"/>')
    e = {"julgando": dict(lidL=.5, lidR=.2, bL=(0, 8), bR=(-30, -12), mouth=f'<path d="M272 394 L328 390" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'),
         "chocado":  dict(lidL=0, lidR=0, bL=(-26, -8), bR=(-26, 8), mouth=f'<ellipse cx="300" cy="400" rx="22" ry="26" {st("#C8243A", 6)}/>'),
         "orgulhoso": dict(lidL=.5, lidR=.5, bL=(-6, -6), bR=(-6, 6), mouth=f'<path d="M270 388 Q300 414 330 388" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>')}[expr]
    face = []
    for cx, lid, (bdy, ba) in [(250, e["lidL"], e["bL"]), (350, e["lidR"], e["bR"])]:
        k = uid("sco")
        face.append(f'<clipPath id="{k}"><ellipse cx="{cx}" cy="290" rx="30" ry="34"/></clipPath>'
                    f'<ellipse cx="{cx}" cy="290" rx="30" ry="34" fill="#fff"/><circle cx="{cx}" cy="296" r="12" fill="{INK}" clip-path="url(#{k})"/>')
        if lid:
            ly = 256 + 68*lid
            face.append(f'<rect x="{cx-32}" y="254" width="64" height="{ly-254}" fill="{PINE}" clip-path="url(#{k})"/>'
                        f'<line x1="{cx-28}" y1="{ly}" x2="{cx+28}" y2="{ly}" stroke="{INK}" stroke-width="6" clip-path="url(#{k})"/>')
        face.append(f'<ellipse cx="{cx}" cy="290" rx="30" ry="34" fill="none" stroke="{INK}" stroke-width="6"/>'
                    f'<path d="M{cx-30} 236 Q{cx} 222 {cx+30} 236" fill="none" stroke="#F4F0E6" stroke-width="16" stroke-linecap="round" '
                    f'transform="translate(0 {bdy}) rotate({ba} {cx} 236)"/>'
                    f'<path d="M{cx-30} 236 Q{cx} 222 {cx+30} 236" fill="none" stroke="{INK}" stroke-width="3" '
                    f'transform="translate(0 {bdy}) rotate({ba} {cx} 236)"/>')
    face.append(e["mouth"])
    return f'<g id="seu_coroa">{body}{"".join(face)}</g>'

# ============================================================ DONA ZEFA (na janela)
Z_SK = "#E2B08A"; Z_HAIR = "#C9C4D2"
def dona_zefa(expr="fofocando"):
    wall = f'<rect x="60" y="60" width="480" height="560" fill="#F2C94C" stroke="{INK}" stroke-width="{SW}"/>'
    win = f'<rect x="120" y="120" width="360" height="380" fill="#3D3A5C" stroke="{INK}" stroke-width="{SW}"/>'
    curtains = (f'<path d="M120 120 L220 120 Q190 300 120 330 Z" {st("#E8445E")}/>'
                f'<path d="M480 120 L380 120 Q410 300 480 330 Z" {st("#E8445E")}/>')
    body = f'<path d="M190 500 Q190 400 300 396 Q410 400 410 500 Z" {st("#7AB0E0")}/>' + \
           "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#fff"/>' for x, y in [(240, 450), (300, 430), (360, 450), (270, 480), (330, 480)])
    head = (f'<ellipse cx="300" cy="300" rx="92" ry="100" {st(Z_SK)}/>'
            f'<path d="M210 280 Q206 186 300 184 Q394 186 390 280 Q370 220 300 222 Q230 220 210 280 Z" {st(Z_HAIR)}/>'
            + "".join(f'<rect x="{x}" y="{y}" width="34" height="26" rx="10" {st("#F06A86", 4)}/>' for x, y in [(232, 182), (283, 172), (334, 182)]))
    glasses = (f'<circle cx="264" cy="300" r="30" fill="#fff" fill-opacity=".35" stroke="{INK}" stroke-width="6"/>'
               f'<circle cx="336" cy="300" r="30" fill="#fff" fill-opacity=".35" stroke="{INK}" stroke-width="6"/>'
               f'<path d="M294 300 L306 300" stroke="{INK}" stroke-width="6"/>')
    if expr == "fofocando":
        eyes = f'<circle cx="270" cy="300" r="8" fill="{INK}"/><circle cx="342" cy="300" r="8" fill="{INK}"/>'
        mouth = f'<ellipse cx="300" cy="358" rx="22" ry="16" {st("#7A2232", 5)}/>'
        hand = f'<g transform="translate(400 350) rotate(-20)"><ellipse cx="0" cy="0" rx="26" ry="34" {st(Z_SK)}/></g>'
        extra = f'<path d="M430 290 l30 -20 M436 320 l36 0 M430 350 l30 20" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    else:  # espiando
        eyes = f'<circle cx="276" cy="306" r="8" fill="{INK}"/><circle cx="348" cy="306" r="8" fill="{INK}"/>' + \
               f'<path d="M236 290 L292 296 M308 296 L364 290" stroke="{Z_SK}" stroke-width="18"/>' + \
               f'<path d="M236 296 L292 300 M308 300 L364 296" stroke="{INK}" stroke-width="5"/>'
        mouth = f'<path d="M280 360 Q300 352 320 360" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        hand, extra = "", ""
    sill = (f'<rect x="100" y="490" width="400" height="34" {st("#B07A4A")}/>'
            f'<path d="M150 490 L160 440 L210 440 L220 490 Z" {st("#C8643A")}/>'
            f'<circle cx="175" cy="430" r="18" {st("#E8445E", 4)}/><circle cx="200" cy="424" r="16" {st("#F3C431", 4)}/>')
    return f'<g id="dona_zefa">{wall}{win}{curtains}{body}{head}{eyes}{glasses}{mouth}{hand}{extra}{sill}</g>'

# ============================================================ GALO DESISTENTE
def galo(state="cantando"):
    tail = (f'<path d="M150 300 Q60 180 110 120 Q140 220 190 260 Z" {st("#2F4A8C")}/>'
            f'<path d="M160 320 Q40 260 60 180 Q120 260 190 290 Z" {st("#3E7A3E")}/>'
            f'<path d="M170 330 Q90 330 70 260 Q150 300 200 310 Z" {st("#2F4A8C")}/>')
    body = f'<ellipse cx="290" cy="330" rx="140" ry="110" {st("#C8643A")}/><path d="M220 320 Q290 380 360 320" fill="none" stroke="#9E4A26" stroke-width="10"/>'
    legs = (f'<path d="M260 430 L254 520 M320 430 L326 520" stroke="#F3C431" stroke-width="12"/>'
            f'<path d="M230 524 L278 524 M302 524 L350 524" stroke="#F3C431" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M260 430 L254 520 M320 430 L326 520" stroke="{INK}" stroke-width="3" fill="none"/>')
    neck = f'<path d="M340 270 Q350 180 390 160 Q440 170 440 220 Q420 280 400 320 Z" {st("#E2803A")}/>'
    comb = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {st("#E8343E")}/>' for x, y, r in [(380, 120, 18), (404, 108, 20), (428, 118, 18)])
    wattle = f'<path d="M440 210 q10 30 -6 44 q-14 -14 -4 -44 z" {st("#E8343E")}/>'
    if state == "cantando":
        beak = (f'<path d="M440 180 L500 160 L446 196 Z" {st("#F3C431")}/><path d="M446 200 L496 214 L440 212 Z" {st("#F3C431")}/>')
        eye = f'<circle cx="412" cy="176" r="12" fill="#fff" stroke="{INK}" stroke-width="4"/><circle cx="416" cy="176" r="5" fill="{INK}"/>'
        fx = f'<text x="500" y="130" font-family="DejaVu Sans" font-weight="bold" font-size="46" fill="#fff" stroke="{INK}" stroke-width="3">CÓ!</text>'
    else:  # desistindo
        beak = f'<path d="M440 186 L488 200 L440 210 Z" {st("#F3C431")}/>'
        eye = (f'<circle cx="412" cy="180" r="12" fill="#fff" stroke="{INK}" stroke-width="4"/>'
               f'<path d="M398 178 L426 178" stroke="{INK}" stroke-width="5"/><circle cx="414" cy="184" r="4" fill="{INK}"/>')
        fx = f'<text x="470" y="140" font-family="DejaVu Sans" font-weight="bold" font-size="40" fill="#fff" stroke="{INK}" stroke-width="3">...</text>'
    return f'<g id="galo">{tail}{legs}{body}{neck}{comb}{wattle}{beak}{eye}{fx}</g>'

# ============================================================ CENÁRIOS (1080x1920)
W, H = 1080, 1920
FLOOR = 1640

def sky(day=True):
    if day:
        return (f'<rect width="{W}" height="{H}" fill="#8FD3F4"/><circle cx="880" cy="260" r="90" fill="#FFE27A" stroke="{INK}" stroke-width="{SW}"/>'
                + "".join(f'<g fill="#fff" stroke="{INK}" stroke-width="5"><ellipse cx="{x}" cy="{y}" rx="90" ry="40"/><ellipse cx="{x+60}" cy="{y-20}" rx="60" ry="40"/></g>'
                          for x, y in [(180, 300), (560, 200)]))
    return f'<rect width="{W}" height="{H}" fill="#2B2350"/>'

def sidewalk():
    tiles = "".join(f'<path d="M{x} {FLOOR-40} L{x-40} {H}" stroke="#B9B2A6" stroke-width="5"/>' for x in range(0, W+200, 160))
    return (f'<rect x="0" y="{FLOOR-40}" width="{W}" height="{H-FLOOR+40}" fill="#D9D2C4"/>{tiles}'
            f'<line x1="0" y1="{FLOOR-40}" x2="{W}" y2="{FLOOR-40}" stroke="{INK}" stroke-width="{SW}"/>')

def cen_banca():
    back = (f'<rect x="0" y="700" width="{W}" height="{FLOOR-740}" fill="#F0B27A"/>'
            f'<rect x="0" y="700" width="{W}" height="20" fill="#D98C4E"/>'
            f'<rect x="40" y="860" width="200" height="300" fill="#6E8FC0" stroke="{INK}" stroke-width="{SW}"/>'
            f'<rect x="820" y="820" width="180" height="420" fill="#8B5A2B" stroke="{INK}" stroke-width="{SW}"/>')
    awning = "".join(f'<path d="M{x} 880 L{x+80} 880 L{x+80} 990 Q{x+40} 1030 {x} 990 Z" fill="{c}" stroke="{INK}" stroke-width="{SW}"/>'
                     for x, c in zip(range(220, 900, 80), ["#2F8F4E", "#F3C431"] * 5))
    poles = f'<rect x="230" y="880" width="18" height="{FLOOR-880}" {st("#8B5A2B")}/><rect x="852" y="880" width="18" height="{FLOOR-880}" {st("#8B5A2B")}/>'
    sign = (f'<g transform="rotate(-3 540 820)"><rect x="330" y="760" width="420" height="110" rx="12" {st("#F4F0E6")}/>'
            f'<text x="540" y="806" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#2F8F4E">ABACAXI DO RUAN</text>'
            f'<text x="540" y="850" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#D9822B">R$ 8 · DOCINHO</text></g>')
    table = f'<rect x="250" y="1360" width="600" height="40" {st("#B07A4A")}/><rect x="270" y="1400" width="560" height="200" {st("#8B5A2B")}/>'
    pile = "".join(abacaxi(x, y, 48, 64) for x, y in [(410, 1200), (540, 1196), (670, 1200), (340, 1290), (470, 1296), (600, 1290), (730, 1296)])
    half = (f'<circle cx="250" cy="1560" r="60" fill="#F2B63C" stroke="{INK}" stroke-width="{SW}"/>'
            f'<circle cx="250" cy="1560" r="48" fill="none" stroke="#FBE08A" stroke-width="10"/>'
            f'<circle cx="250" cy="1560" r="14" fill="#FBE08A" stroke="#D9A02E" stroke-width="4"/>')
    return sky() + back + sidewalk() + poles + awning + sign + table + pile + half

def cen_quarto():
    wall = f'<rect width="{W}" height="{H}" fill="#6C5A9E"/>' + "".join(f'<rect x="{x}" y="0" width="40" height="{FLOOR}" fill="#62528F"/>' for x in range(0, W, 120))
    floor = f'<rect x="0" y="{FLOOR-60}" width="{W}" height="{H}" fill="#8B5A2B"/><line x1="0" y1="{FLOOR-60}" x2="{W}" y2="{FLOOR-60}" stroke="{INK}" stroke-width="{SW}"/>' + \
            "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#7A4C22" stroke-width="5"/>' for y in range(FLOOR, H, 70))
    window = (f'<rect x="640" y="380" width="340" height="380" fill="#8FD3F4" stroke="{INK}" stroke-width="{SW}"/>'
              f'<circle cx="900" cy="460" r="40" fill="#FFE27A"/><path d="M810 380 V760 M640 570 H980" stroke="{INK}" stroke-width="{SW}"/>')
    clock = (f'<circle cx="250" cy="420" r="80" {st("#F4F0E6")}/><path d="M250 420 L250 360 M250 420 L262 372" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
             f'<text x="250" y="540" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="40" fill="#fff">12:07</text>')
    bed = (f'<rect x="40" y="1300" width="560" height="200" rx="20" {st("#E8445E")}/><rect x="60" y="1240" width="160" height="80" rx="30" {st("#F4F0E6")}/>'
           f'<path d="M260 1300 Q400 1230 560 1300" {st("#2F8F4E")}/><rect x="40" y="1500" width="30" height="80" {st("#5A3A1A")}/><rect x="570" y="1500" width="30" height="80" {st("#5A3A1A")}/>')
    fan = (f'<rect x="860" y="1240" width="16" height="340" {st("#ccc")}/><circle cx="868" cy="1220" r="70" fill="#9ED8FF" fill-opacity=".6" stroke="{INK}" stroke-width="{SW}"/>'
           f'<ellipse cx="868" cy="1590" rx="70" ry="16" {st("#888")}/>')
    mess = "".join(f'<path d="M{x} {y} q30 -30 60 0 q-10 20 -60 0z" {st(c)}/>' for x, y, c in [(120, 1680, "#F4F0E6"), (700, 1720, "#2F8F4E"), (420, 1800, "#3E64B8")]) + \
           abacaxi(560, 1680, 36, 48)
    poster = f'<g transform="rotate(4 420 760)"><rect x="330" y="640" width="180" height="240" {st("#F3C431")}/><circle cx="420" cy="750" r="56" fill="#F2B63C" stroke="{INK}" stroke-width="5"/><circle cx="420" cy="750" r="16" fill="#FBE08A" stroke="{INK}" stroke-width="3"/></g>'
    return wall + floor + window + clock + poster + bed + fan + mess

def house(x, w, h, color, door=True, roof="#C8643A"):
    y = FLOOR - 40 - h
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="{INK}" stroke-width="{SW}"/>'
         f'<rect x="{x-10}" y="{y-40}" width="{w+20}" height="44" fill="{roof}" stroke="{INK}" stroke-width="{SW}"/>')
    if door:
        s += f'<rect x="{x+w/2-50}" y="{FLOOR-40-220}" width="100" height="220" {st("#8B5A2B")}/><circle cx="{x+w/2+30}" cy="{FLOOR-150}" r="7" fill="{INK}"/>'
    return s

def cen_rua_zefa():
    out = sky() + house(-20, 380, 760, "#F2C94C") + house(380, 340, 640, "#E8899A") + house(740, 360, 700, "#7FC8A9")
    out += sidewalk()
    out += f'<g transform="translate(20 640) scale(.62)">{dona_zefa("espiando")}</g>'
    out += f'<rect x="510" y="1100" width="16" height="500" {st("#555")}/><rect x="470" y="1060" width="96" height="50" rx="10" {st("#3B3B3F")}/>'
    return out

def cen_feira():
    out = sky() + f'<rect x="0" y="900" width="{W}" height="{FLOOR-940}" fill="#C9B79C"/>' + sidewalk()
    for i, (x, c1, c2, goods) in enumerate([(-60, "#3E64B8", "#F4F0E6", "#E8445E"), (360, "#F3C431", "#E8445E", "#F39A3C"), (760, "#2F8F4E", "#F4F0E6", "#7DBA3C")]):
        out += f'<rect x="{x+20}" y="1000" width="14" height="{FLOOR-1000}" {st("#8B5A2B")}/><rect x="{x+330}" y="1000" width="14" height="{FLOOR-1000}" {st("#8B5A2B")}/>'
        out += "".join(f'<path d="M{xx} 1000 L{xx+60} 1000 L{xx+60} 1090 Q{xx+30} 1120 {xx} 1090 Z" fill="{c}" stroke="{INK}" stroke-width="5"/>'
                       for xx, c in zip(range(x, x+360, 60), [c1, c2]*3))
        out += f'<rect x="{x+20}" y="1380" width="330" height="36" {st("#B07A4A")}/>'
        out += "".join(f'<circle cx="{x+60+k*50}" cy="{1350 - (k%2)*20}" r="26" {st(goods)}/>' for k in range(6))
    out += f'<g transform="rotate(-4 540 820)"><rect x="350" y="760" width="380" height="100" rx="12" {st("#E8445E")}/><text x="540" y="828" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="52" fill="#fff">FEIRA</text></g>'
    return out

def cen_casa_bia():
    out = sky() + house(120, 840, 820, "#C9B8F0", door=False, roof="#7E52B8")
    y = FLOOR - 40 - 820
    out += "".join(f'<rect x="{x}" y="{y+120}" width="200" height="200" fill="#8FD3F4" stroke="{INK}" stroke-width="{SW}"/>'
                   f'<path d="M{x} {y+220} H{x+200} M{x+100} {y+120} V{y+320}" stroke="{INK}" stroke-width="5"/>' for x in (200, 680))
    out += f'<rect x="440" y="{FLOOR-40-300}" width="200" height="300" {st("#7E52B8")}/><circle cx="600" cy="{FLOOR-190}" r="9" fill="#F3C431" stroke="{INK}" stroke-width="3"/>'
    out += sidewalk()
    out += "".join(f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" {st("#C8964E")}/><path d="M{x} {yy+18} H{x+w}" stroke="#A8783A" stroke-width="8"/>'
                   for x, yy, w, h in [(700, 1460, 200, 140), (740, 1340, 160, 120), (900, 1500, 150, 100)])
    out += f'<text x="820" y="1550" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="{INK}">MUDANÇA</text>'
    out += f'<text x="820" y="1416" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="26" fill="#E8445E">FRÁGIL</text>'
    out += f'<g transform="translate(60 1580)">' + "".join(f'<circle cx="{i*40}" cy="{-abs(i-2)*14}" r="34" {st("#3E7A3E")}/>' for i in range(5)) + '</g>'
    return out

SCENES = {"banca_abacaxi": cen_banca, "quarto": cen_quarto, "rua_dona_zefa": cen_rua_zefa,
          "feira": cen_feira, "casa_bia": cen_casa_bia}

def main(kit):
    for d in ("elenco", "cenarios"):
        os.makedirs(f"{kit}/{d}", exist_ok=True)
    for name, pose, expr in [("1_sorrindo", "em_pe", "sorrindo"), ("2_acenando", "acenando", "sorrindo"), ("3_desconfiada", "bracos_cruzados", "desconfiada"),
                             ("4_enojada", "nariz_tapado", "enojada"), ("5_surpresa", "em_pe", "surpresa")]:
        open(f"{kit}/elenco/bia_{name}.svg", "w").write(svg(bia(pose, expr)))
    for e in ("julgando", "chocado", "orgulhoso"):
        open(f"{kit}/elenco/seu_coroa_{e}.svg", "w").write(svg(seu_coroa(e), 600, 800, "60 -110 480 640"))
    for e in ("fofocando", "espiando"):
        open(f"{kit}/elenco/dona_zefa_{e}.svg", "w").write(svg(dona_zefa(e), 600, 600, "40 40 540 600"))
    for s in ("cantando", "desistindo"):
        open(f"{kit}/elenco/galo_{s}.svg", "w").write(svg(galo(s), 600, 560, "30 60 560 500"))
    for n, f in SCENES.items():
        open(f"{kit}/cenarios/{n}.svg", "w").write(svg(f(), W, H))
    # quadro de teste: escala dos personagens no cenário
    demo = (cen_banca()
            + f'<g transform="translate(560 1080) scale(.42)">{seu_coroa("julgando")}</g>'
            + f'<g transform="translate(-20 690) scale(.95)">{character("em_pe", "neutro")}</g>'
            + f'<g transform="translate(470 690) scale(.95)">{bia("nariz_tapado", "enojada")}</g>')
    open(f"{kit}/cenarios/_teste_escala.svg", "w").write(svg(demo, W, H))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "kit")
