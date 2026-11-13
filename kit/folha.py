import glob, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

kit = sys.argv[1]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def png(svgp, h):
    out = svgp[:-4] + ".png"
    subprocess.run(["rsvg-convert", "-h", str(h), "-o", out, svgp], check=True)
    return Image.open(out).convert("RGBA")

def row(title, files, h, cols_bg="#EDE6F5"):
    ims = [(os.path.basename(f)[:-4], png(f, h)) for f in files]
    W = sum(i.width for _, i in ims) + 40 * (len(ims) + 1)
    H = h + 140
    c = Image.new("RGBA", (W, H), cols_bg)
    d = ImageDraw.Draw(c)
    d.text((40, 20), title, font=ImageFont.truetype(F, 40), fill="#16121A")
    x = 40
    for n, i in ims:
        c.alpha_composite(i, (x, 80))
        d.text((x + i.width // 2, 80 + h + 12), n.replace("_", " "), font=ImageFont.truetype(F, 26), fill="#16121A", anchor="ma")
        x += i.width + 40
    return c

order = ["em_pe", "apontando", "celular", "abacaxi", "correndo", "comemorando", "derrotado"]
r1 = row("RUAN · POSES", [f"{kit}/poses/{n}.svg" for n in order], 620)
r2 = row("POSES DE CENA", [f"{kit}/poses/dormindo_rede.svg", f"{kit}/poses/escondido.svg"], 520)
r3 = row("EXPRESSÕES", sorted(glob.glob(f"{kit}/expressoes/*.svg")), 300)
r4 = row("AJUSTES QUE FICAM (um por voto)", sorted(glob.glob(f"{kit}/ajustes/*.svg")), 560)
r5 = row("ELENCO", sorted(glob.glob(f"{kit}/elenco/bia_*.svg")) + sorted(glob.glob(f"{kit}/elenco/seu_coroa_*.svg"))[:2], 420)
r6 = row("", sorted(glob.glob(f"{kit}/elenco/dona_zefa_*.svg")) + sorted(glob.glob(f"{kit}/elenco/galo_*.svg")) + [f"{kit}/elenco/seu_coroa_orgulhoso.svg"], 340)
r7 = row("CENÁRIOS (1080x1920)", sorted(glob.glob(f"{kit}/cenarios/*.svg")), 760)
rows = (r1, r2, r3, r4, r5, r6, r7)
W = max(r.width for r in rows)
sheet = Image.new("RGBA", (W, sum(r.height for r in rows)), "#EDE6F5")
y = 0
for r in rows:
    sheet.alpha_composite(r, (0, y)); y += r.height
sheet.convert("RGB").save(f"{kit}/FOLHA_MODELO_RUAN.png", quality=92)
print(sheet.size)
