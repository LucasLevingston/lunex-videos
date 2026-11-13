"""Gera (e guarda em cache) o PNG de qualquer ator ou cenário do kit.

ids:
  ruan:<pose>:<expressao>   poses do ruan.py (em_pe, apontando, celular, abacaxi, correndo, comemorando,
                            derrotado) + rede, escondido, cabeca
  bia:<pose>:<expressao>    poses: em_pe, acenando, bracos_cruzados, nariz_tapado
                            expressões: sorrindo, desconfiada, enojada, surpresa
  coroa:<expressao>         julgando, chocado, orgulhoso
  zefa:<expressao>          fofocando, espiando
  galo:<estado>             cantando, desistindo
  cenario:<nome>            banca_abacaxi, quarto, rua_dona_zefa, feira, casa_bia (1080x1920)
O Ruan sai sempre com os ajustes do estado.json (banho, olheira, barba, cabelo, músculo).
"""
import hashlib, json, os, subprocess, sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
SERIE = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(SERIE, "kit"))
import ruan as R      # noqa: E402
import elenco as E    # noqa: E402

CACHE = os.path.join(SERIE, ".cache_atores")
os.makedirs(CACHE, exist_ok=True)

def ajustes_do_estado():
    try:
        a = json.load(open(os.path.join(SERIE, "estado.json")))["ajustes"]
    except Exception:
        a = {}
    return dict(dirty=not a.get("banho", False), bags=not a.get("acorda_cedo", False),
                stubble=not a.get("barba", False), messy_hair=not a.get("cabelo", False),
                muscle=a.get("academia", False))

def svg_de(ident, kw):
    p = ident.split(":")
    who = p[0]
    if who == "ruan":
        pose = p[1] if len(p) > 1 else "em_pe"
        expr = p[2] if len(p) > 2 else "neutro"
        if pose == "rede":
            return R.svg(R.sleeping(expr, **kw), 1000, 700, "0 60 1000 700")
        if pose == "escondido":
            return R.svg(R.hiding(expr, **kw), 660, 700, "-30 130 660 700")
        if pose == "cabeca":
            return R.svg(R.head(expr, stubble=kw["stubble"], bags=kw["bags"], messy_hair=kw["messy_hair"]), 520, 460, "40 70 520 460")
        return R.svg(R.character(pose, expr, **kw))
    if who == "bia":
        return R.svg(E.melina(p[1] if len(p) > 1 else "em_pe", p[2] if len(p) > 2 else "sorrindo")) if hasattr(E, "melina") else \
               R.svg(E.bia(p[1] if len(p) > 1 else "em_pe", p[2] if len(p) > 2 else "sorrindo"))
    if who == "bia_cabeca":
        return R.svg(E.m_head(p[1] if len(p) > 1 else "sorrindo"), 520, 460, "40 70 520 460")
    if who == "coroa":
        return R.svg(E.seu_coroa(p[1] if len(p) > 1 else "julgando"), 600, 800, "60 -110 480 640")
    if who == "zefa":
        return R.svg(E.dona_zefa(p[1] if len(p) > 1 else "fofocando"), 600, 600, "40 40 540 600")
    if who == "galo":
        return R.svg(E.galo(p[1] if len(p) > 1 else "cantando"), 600, 560, "30 60 560 500")
    if who == "cenario":
        return R.svg(E.SCENES[p[1]](), E.W, E.H)
    raise ValueError(f"ator desconhecido: {ident}")

def png(ident, h=None):
    """Caminho do PNG do ator. Cenários saem em 1080x1920; o resto na altura h (padrão 1000)."""
    kw = ajustes_do_estado()
    if ident.startswith("cenario:"):
        h = 1920
    h = h or 1000
    key = hashlib.md5(f"{ident}|{h}|{sorted(kw.items())}".encode()).hexdigest()[:12]
    out = os.path.join(CACHE, f"{ident.replace(':', '_')}_{key}.png")
    if not os.path.exists(out):
        R._uid[0] = 0
        s = svg_de(ident, kw)
        args = ["rsvg-convert", "-h", str(h), "-o", out]
        if ident.startswith("cenario:"):
            args = ["rsvg-convert", "-w", "1080", "-h", "1920", "-o", out]
        subprocess.run(args, input=s.encode(), check=True)
    return out

def imagem(ident, h=None):
    return Image.open(png(ident, h)).convert("RGBA")

if __name__ == "__main__":
    for i in sys.argv[1:]:
        print(png(i))
