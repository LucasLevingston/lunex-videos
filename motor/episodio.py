"""Motor dos episódios de "30 dias pro Ruan".

python motor/episodio.py episodios/diaNN/episodio.json voz     # grava as falas (Kokoro pm_santa)
python motor/episodio.py episodios/diaNN/episodio.json quadros 3 12.5 30   # quadros de teste (segundos)
python motor/episodio.py episodios/diaNN/episodio.json video   # cenas -> video.mp4 + thumb.jpg + legenda.txt
O formato do episodio.json está em motor/FORMATO.md.
"""
import json, math, os, re, subprocess, sys, wave
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
SERIE = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import atores  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONT = os.path.join(SERIE, "assets", "Anton.ttf")
INK = (22, 18, 26)
CORES = {"amarelo": (255, 214, 64), "verde": (86, 200, 110), "azul": (90, 170, 255), "vermelho": (232, 68, 94),
         "rosa": (255, 140, 190), "branco": (255, 255, 255), "preto": INK, "laranja": (242, 150, 60), "roxo": (155, 107, 214)}
FUNDOS = {"vermelho": ((196, 44, 58), (214, 60, 72)), "azul": ((40, 70, 160), (54, 90, 180)), "roxo": ((70, 40, 120), (86, 54, 140)),
          "verde": ((30, 120, 70), (40, 140, 84)), "amarelo": ((220, 160, 30), (236, 180, 50))}
COR_DESTAQUE = {"ruan": "amarelo", "bia": "rosa", "você": "amarelo", "abacaxi": "amarelo", "banho": "azul", "zefa": "rosa",
                "coroa": "amarelo", "galo": "laranja"}

def cor(c):
    if isinstance(c, (list, tuple)): return tuple(c)
    return CORES.get(c, CORES["branco"])

@lru_cache(None)
def font(sz): return ImageFont.truetype(FONT, max(8, int(sz)))

@lru_cache(None)
def img(ident, h=None): return atores.imagem(ident, h)

@lru_cache(512)
def scaled(ident, s, h=None):
    im = img(ident, h)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)

def ease_out_back(t, k=1.7):
    t = min(max(t, 0), 1) - 1
    return 1 + (k + 1) * t**3 + k * t**2

def ease(t):
    t = min(max(t, 0), 1); return 1 - (1 - t) ** 3

def text(c, s, cx, cy, sz, fill=(255, 255, 255), stroke=10, anchor="mm", scale=1.0):
    if scale <= 0.01: return
    ImageDraw.Draw(c).text((cx, cy), s, font=font(sz * scale), fill=fill, stroke_width=max(0, int(stroke * scale)), stroke_fill=INK, anchor=anchor)

def rich(c, words, cx, cy, sz, scale=1.0, maxw=1000):
    if scale <= 0.01: return
    f = font(sz * scale); d = ImageDraw.Draw(c)
    sp = int(sz * scale * 0.28)
    ws = [d.textlength(w, font=f) for w, _ in words]
    tot = sum(ws) + sp * (len(ws) - 1)
    if tot > maxw:
        return rich(c, words, cx, cy, sz * maxw / tot, scale, maxw)
    x = cx - tot / 2
    for (w, col), wl in zip(words, ws):
        d.text((x, cy), w, font=f, fill=col, stroke_width=int(10 * scale), stroke_fill=INK, anchor="lm"); x += wl + sp

def rrect(c, box, r, fill, outline=INK, width=6):
    ImageDraw.Draw(c).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def tag(c, s, cx, cy, sz=44, fill=(255, 255, 255), fg=INK, rot=-3, scale=1.0):
    if scale <= 0.01: return
    f = font(sz * scale); tw = ImageDraw.Draw(c).textlength(s, font=f); pad = int(26 * scale)
    t = Image.new("RGBA", (int(tw + pad * 2 + 12), int(sz * scale * 1.5 + 12)), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.rounded_rectangle((6, 6, t.width - 6, t.height - 6), int(14 * scale), fill=fill, outline=INK, width=5)
    d.text((t.width / 2, t.height / 2), s, font=f, fill=fg, anchor="mm")
    t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

def camera(c, zoom=1.0, fx=W / 2, fy=H / 2, dx=0, dy=0):
    if abs(zoom - 1) < 1e-3 and dx == 0 and dy == 0: return c
    w, h = W / zoom, H / zoom
    x0 = min(max(fx - w / 2 + dx, 0), W - w); y0 = min(max(fy - h / 2 + dy, 0), H - h)
    return c.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)

# ======================================================================= episódio
class Ep:
    def __init__(self, path):
        self.path = os.path.abspath(path); self.dir = os.path.dirname(self.path)
        self.d = json.load(open(self.path))
        self.cenas = self.d["cenas"]
        self.vozdir = os.path.join(self.dir, "voz")

    # ------------------------------------------------ voz
    def falas(self):
        out = []
        for i, c in enumerate(self.cenas):
            if c.get("fala"): out.append((f"{i:02d}a", c["fala"]))
            if c.get("fim"): out.append((f"{i:02d}b", c["fim"]))
        return out

    def gravar_voz(self):
        import soundfile as sf
        from kokoro_onnx import Kokoro
        k = Kokoro(os.path.join(SERIE, "assets", "kokoro.onnx"), os.path.join(SERIE, "assets", "voices.bin"))
        os.makedirs(self.vozdir, exist_ok=True)
        for key, t in self.falas():
            s, sr = k.create(t, voice="pm_santa", speed=1.15, lang="pt-br")
            sf.write(os.path.join(self.vozdir, f"{key}.wav"), s, sr, subtype="PCM_16")
            print(key, round(len(s) / sr, 2), t)

    def dur(self, key):
        p = os.path.join(self.vozdir, f"{key}.wav")
        if not os.path.exists(p): return 0.0
        w = wave.open(p); return w.getnframes() / w.getframerate()

    # ------------------------------------------------ linha do tempo
    def montar(self):
        t = 0.0; self.tl = []; self.vozes = []; self.caps = []; self.sfx = []
        for i, c in enumerate(self.cenas):
            a = self.dur(f"{i:02d}a"); b = self.dur(f"{i:02d}b")
            lead = 0.25
            d = lead + a + 0.4
            if c.get("fim"): d += b + 0.2
            if c["tipo"] == "votacao": d += 2.5
            d = max(d, c.get("min", 2.0))
            if c.get("fala"): self.vozes.append((f"{i:02d}a", t + lead))
            if c.get("fim"): self.vozes.append((f"{i:02d}b", t + lead + a + 0.4))
            if c.get("fala") and c["tipo"] not in ("cards", "votacao") and not c.get("sem_legenda"):
                self.caps += self.legendas(c["fala"], t + lead, a)
            self.tl.append((t, t + d, i, c, a))
            self.sfx.append((t, "whoosh"))
            t += d
        self.total = t

    def legendas(self, fala, t0, d):
        txt = fala.upper()
        for n, w in [("TRINTA", "30"), ("VINTE", "20"), ("DEZ", "10"), ("CINCO", "5")]:
            txt = re.sub(rf"\b{n}\b", w, txt)
        ws = txt.split(); groups, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 2 or w.endswith((".", ",", "?", "!")) or len(w) > 7:
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        total = sum(len(" ".join(g)) for g in groups) or 1; dd = max(d - 0.2, 0.3)
        out = []
        for g in groups:
            L = len(" ".join(g)) / total * dd; out.append((t0, t0 + L, g)); t0 += L
        return out

    def sentencas(self, fala, d):
        """início (s) de cada frase dentro da fala, proporcional ao tamanho."""
        parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+", fala) if p.strip()]
        tot = sum(len(p) for p in parts) or 1; t = 0; out = []
        for p in parts:
            out.append(t); t += len(p) / tot * d
        return out

    # ------------------------------------------------ desenho
    def hud(self, c, T):
        dias = self.d.get("dias_restantes", 30)
        ch0 = self.d.get("chance", 0); ch1 = self.d.get("chance_fim", ch0)
        ch = ch0
        for a, b, i, cena, _ in self.tl:
            if cena.get("sobe_chance") and T >= a:
                ch = ch0 + (ch1 - ch0) * ease((T - a - 0.5) / 1.0)
        rrect(c, (36, 40, 300, 170), 18, (22, 18, 26, 235), outline=(255, 255, 255), width=3)
        text(c, "DIAS RESTANTES", 168, 72, 30, stroke=0)
        text(c, str(dias), 168, 126, 70, fill=CORES["amarelo"], stroke=4)
        rrect(c, (324, 40, 1044, 170), 18, (22, 18, 26, 235), outline=(255, 255, 255), width=3)
        text(c, "CHANCE COM A BIA", 684, 72, 30, stroke=0)
        rrect(c, (360, 104, 900, 146), 12, (60, 54, 70), outline=None, width=0)
        if ch > 0.5: rrect(c, (360, 104, 360 + 540 * min(ch, 100) / 100, 146), 12, CORES["verde"], outline=None, width=0)
        text(c, f"{int(round(ch))}%", 970, 126, 54, fill=CORES["verde"] if ch1 >= ch0 else CORES["vermelho"], stroke=4)

    def legenda(self, c, T, y):
        for a, b, g in self.caps:
            if a <= T < b + 0.08:
                s = ease_out_back((T - a) / 0.12, 2.2) if T - a < 0.12 else 1
                words = []
                for w in g:
                    k = w.strip(",.?!").lower()
                    col = cor(COR_DESTAQUE.get(k)) if k in COR_DESTAQUE else (CORES["amarelo"] if k.isdigit() else (255, 255, 255))
                    words.append((w.strip(",."), col))
                rich(c, words, W / 2, y, 118, scale=0.85 + 0.15 * s)
                return

    # ---- tipos de cena
    def cena(self, c0, t, d):
        bgname = c0.get("fundo", "banca_abacaxi")
        if bgname.startswith("#") or bgname in FUNDOS:
            c = Image.new("RGBA", (W, H), FUNDOS.get(bgname, ((40, 40, 40),))[0] + (255,))
        else:
            c = img(f"cenario:{bgname}").copy()
        if c0.get("desfoque_fundo"): c = c.filter(ImageFilter.GaussianBlur(c0["desfoque_fundo"]))
        for a in c0.get("atores", []):
            self.ator(c, a, t)
        if "coracoes" in c0.get("efeitos", []): self.coracoes(c, t, *c0.get("coracoes_pos", (250, 860)))
        if "escurecer" in c0.get("efeitos", []): c.alpha_composite(Image.new("RGBA", (W, H), (20, 14, 30, 160)))
        cam = c0.get("camera", {})
        z0, z1 = cam.get("zoom", [1.0, 1.0]); fx, fy = cam.get("foco", [W / 2, H / 2])
        zp = cam.get("punch")  # [t, zoom extra]
        z = z0 + (z1 - z0) * (ease(t / cam["zoom_em"]) if cam.get("zoom_em") else t / max(d, 0.1))
        if zp and zp[0] <= t < zp[0] + 0.2: z += zp[1]
        dx = math.sin(t * 50) * 8 if any(s[0] <= t < s[1] for s in cam.get("tremer", [])) else 0
        c = camera(c, z, fx, fy, dx=dx)
        for tg in c0.get("tags", []):  # tags ficam por cima da câmera
            if t >= tg.get("t", 0) and t < tg.get("ate", 1e9):
                tag(c, tg["texto"], tg.get("x", W / 2), tg.get("y", 400), tg.get("tam", 56), fill=cor(tg.get("cor", "branco")),
                    fg=cor(tg.get("cor_texto", "preto")), rot=tg.get("rot", -3), scale=ease_out_back((t - tg.get("t", 0)) / 0.3))
        return c

    def ator(self, c, a, t):
        ident = a["id"]
        for tr in a.get("troca", []):
            if t >= tr["t"]: ident = tr["id"]
        if t < a.get("t", 0): return
        tt = t - a.get("t", 0)
        x, y, s = a.get("x", W / 2), a.get("y", 1680), a.get("escala", 0.95)
        e = a.get("entra")
        if e == "esquerda": x = -400 + (x + 400) * ease(tt / a.get("dur_entrada", 0.6))
        elif e == "direita": x = W + 400 - (W + 400 - x) * ease(tt / a.get("dur_entrada", 0.6))
        elif e == "pop": s *= ease_out_back(tt / 0.35)
        elif e == "baixo": y = H + 1000 - (H + 1000 - y) * ease(tt / 0.5)
        sai = a.get("sai")
        if sai and t >= sai["t"]:
            k = ease((t - sai["t"]) / sai.get("dur", 0.6))
            x = x + ({"esquerda": -1600, "direita": 1600}.get(sai.get("para", "esquerda"), 0)) * k
        if a.get("pula"):
            for pt in a["pula"]:
                if pt <= t < pt + 0.3: y -= 70 * math.sin((t - pt) / 0.3 * math.pi)
        if a.get("balanca"): y += math.sin(t * 2.2) * 8
        if a.get("treme"): x += math.sin(t * 45) * 5
        if s <= 0.01: return
        im = scaled(ident, round(s, 3))
        if a.get("espelhar"): im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if a.get("centro"):
            c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        else:
            c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height)))

    def coracoes(self, c, t, x0, y0):
        d = ImageDraw.Draw(c); R = CORES["vermelho"]
        for i in range(3):
            tt = (t - i * 0.35) % 1.4; hx, hy = x0 + i * 60, y0 - tt * 220; al = int(255 * (1 - tt / 1.4))
            d.ellipse((hx - 22, hy - 22, hx, hy), fill=R + (al,)); d.ellipse((hx - 2, hy - 22, hx + 20, hy), fill=R + (al,))
            d.polygon([(hx - 22, hy - 10), (hx + 20, hy - 10), (hx - 1, hy + 22)], fill=R + (al,))

    def close(self, c0, t, d):
        base, raio = FUNDOS.get(c0.get("cor", "vermelho"), FUNDOS["vermelho"])
        c = Image.new("RGBA", (W, H), base + (255,)); dr = ImageDraw.Draw(c)
        for i in range(24):
            a = i / 24 * 2 * math.pi + t * 0.3
            dr.polygon([(W / 2, 1000), (W / 2 + 1600 * math.cos(a), 1000 + 1600 * math.sin(a)),
                        (W / 2 + 1600 * math.cos(a + 0.13), 1000 + 1600 * math.sin(a + 0.13))], fill=raio)
        sh = math.sin(t * 40) * 5 if c0.get("treme", True) else 0
        im = scaled(c0.get("id", "ruan:cabeca:suando"), round(c0.get("escala", 1.0), 3), 1300)
        c.alpha_composite(im, (int(W / 2 + sh - im.width / 2), int(820 - im.height / 2)))
        if c0.get("texto") and t > 0.3:
            text(c, c0["texto"], W / 2, 1420, c0.get("tam", 200), fill=cor(c0.get("cor_texto", "amarelo")), stroke=14,
                 scale=ease_out_back((t - 0.3) / 0.3))
        return c

    def tela_celular(self, c, t):
        px, py, pw, ph = 170, 300, 740, 1380
        rrect(c, (px, py, px + pw, py + ph), 70, (30, 30, 36), width=8)
        return (px + 26, py + 26, px + pw - 26, py + ph - 26)

    def fundo_celular(self):
        c = Image.new("RGBA", (W, H), (46, 34, 70, 255)); d = ImageDraw.Draw(c)
        for i in range(0, H, 90): d.line((0, i, W, i + 300), fill=(56, 42, 84), width=30)
        return c

    def avatar(self, c, x, y, ident="bia_cabeca:sorrindo", s=0.42):
        head = scaled(ident, s, 260)
        m = Image.new("L", head.size, 0); ImageDraw.Draw(m).ellipse((0, 0, head.width, head.height), fill=255)
        ImageDraw.Draw(c).ellipse((x - 4, y - 4, x + head.width + 4, y + head.height + 4), fill=(255, 255, 255))
        c.paste(head, (int(x), int(y)), Image.composite(head.getchannel("A"), Image.new("L", head.size, 0), m))
        return head.width

    def story(self, c0, t, d):
        c = self.fundo_celular(); scr = self.tela_celular(c, t)
        g = Image.new("RGBA", (scr[2] - scr[0], scr[3] - scr[1])); gd = ImageDraw.Draw(g)
        for yy in range(g.height):
            k = yy / g.height; gd.line((0, yy, g.width, yy), fill=(int(70 + 120 * k), int(140 + 40 * k), int(220 - 60 * k), 255))
        mk = Image.new("L", g.size, 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, g.width, g.height), 48, fill=255)
        c.paste(g, scr[:2], mk)
        dr = ImageDraw.Draw(c)
        dr.rounded_rectangle((scr[0] + 30, scr[1] + 30, scr[2] - 30, scr[1] + 40), 5, fill=(255, 255, 255, 120))
        dr.rounded_rectangle((scr[0] + 30, scr[1] + 30, scr[0] + 30 + (scr[2] - scr[0] - 60) * min(t / d, 1), scr[1] + 40), 5, fill=(255, 255, 255))
        aw = self.avatar(c, scr[0] + 30, scr[1] + 66, c0.get("avatar", "bia_cabeca:sorrindo"))
        text(c, c0.get("usuario", "dra.bia"), scr[0] + 60 + aw, scr[1] + 66 + aw / 2, 40, stroke=0, anchor="lm")
        if c0.get("desenho") == "caixa":
            bx, by = W / 2, 820; s = ease_out_back((t - 0.3) / 0.4)
            if s > 0.01:
                b = 170 * s
                dr.polygon([(bx - b, by - b * .3), (bx + b, by - b * .3), (bx + b, by + b * .9), (bx - b, by + b * .9)], fill=(200, 150, 78), outline=INK, width=6)
                dr.polygon([(bx - b, by - b * .3), (bx - b * 1.2, by - b * .75), (bx - b * .1, by - b * .75), (bx, by - b * .3)], fill=(220, 172, 98), outline=INK, width=6)
                dr.polygon([(bx + b, by - b * .3), (bx + b * 1.2, by - b * .75), (bx + b * .1, by - b * .75), (bx, by - b * .3)], fill=(220, 172, 98), outline=INK, width=6)
                text(c, c0.get("texto_desenho", "MUDANÇA"), bx, by + b * .35, 64 * s, fill=INK, stroke=0)
        elif c0.get("imagem"):
            s = ease_out_back((t - 0.3) / 0.4)
            if s > 0.01:
                im = scaled(c0["imagem"], round(0.5 * s, 3)); c.alpha_composite(im, (int(W / 2 - im.width / 2), int(1000 - im.height)))
        shown = (t - 0.9) * 26 if t > 0.9 else 0
        for i, ln in enumerate(c0.get("linhas", [])):
            n = max(0, min(len(ln), int(shown))); shown -= len(ln)
            big = i < len(c0["linhas"]) - 1 or len(c0["linhas"]) == 1
            if n: text(c, ln[:n], W / 2, 1130 + i * 110, 92 if big else 56, fill=(255, 255, 255) if big else (255, 245, 200), stroke=8 if big else 5)
        return camera(c, 1.0 + 0.04 * t / d, W / 2, 1000)

    def chat(self, c0, t, d):
        c = self.fundo_celular(); scr = self.tela_celular(c, t)
        rrect(c, scr, 48, (245, 245, 250), outline=None, width=0)
        dr = ImageDraw.Draw(c)
        dr.rectangle((scr[0], scr[1] + 40, scr[2], scr[1] + 170), fill=(255, 255, 255))
        aw = self.avatar(c, scr[0] + 40, scr[1] + 62, c0.get("avatar", "bia_cabeca:sorrindo"), 0.33)
        text(c, c0.get("contato", "Bia"), scr[0] + 70 + aw, scr[1] + 92, 46, fill=INK, stroke=0, anchor="lm")
        text(c, "online", scr[0] + 70 + aw, scr[1] + 138, 30, fill=(60, 170, 90), stroke=0, anchor="lm")
        msgs = c0.get("mensagens", []); y = scr[1] + 220
        for m in msgs:
            if t < m.get("t", 0): break
            s = ease_out_back((t - m.get("t", 0)) / 0.25)
            mine = m.get("de") == "ruan"
            f = font(44); lines = self.quebra(m["texto"], f, 420)
            bw = max(ImageDraw.Draw(c).textlength(l, font=f) for l in lines) + 60; bh = 62 * len(lines) + 30
            x0 = scr[2] - 40 - bw if mine else scr[0] + 40
            if s > 0.01:
                rrect(c, (x0, y, x0 + bw * s, y + bh * s), 26, (60, 130, 245) if mine else (225, 225, 232), outline=None, width=0)
                if s > 0.9:
                    for k, l in enumerate(lines):
                        ImageDraw.Draw(c).text((x0 + 30, y + 22 + 62 * k), l, font=f, fill=(255, 255, 255) if mine else INK)
            y += bh + 26
        return c

    def quebra(self, s, f, maxw):
        d = ImageDraw.Draw(Image.new("RGB", (1, 1))); out, cur = [], ""
        for w in s.split():
            n = (cur + " " + w).strip()
            if d.textlength(n, font=f) > maxw and cur: out.append(cur); cur = w
            else: cur = n
        return out + [cur]

    def cards(self, c0, t, d, a):
        c = img(f"cenario:{c0.get('fundo', 'banca_abacaxi')}").copy()
        if c0.get("ator"): self.ator(c, {"id": c0["ator"], "x": W / 2, "y": 1700}, t)
        c = c.filter(ImageFilter.GaussianBlur(6)); c.alpha_composite(Image.new("RGBA", (W, H), (20, 14, 30, 170)))
        text(c, c0.get("titulo", "COMO FUNCIONA"), W / 2, 520, 120, scale=ease_out_back(t / 0.3))
        starts = self.sentencas(c0.get("fala", ""), a)
        itens = c0["itens"]; offs = starts[-len(itens):] if len(starts) >= len(itens) else [0.6 + i * 1.6 for i in range(len(itens))]
        cols = [CORES["amarelo"], CORES["verde"], CORES["vermelho"], CORES["azul"]]
        for i, (l1, l2) in enumerate(itens):
            s = ease_out_back((t - 0.25 - offs[i]) / 0.3)
            if s <= 0.01: continue
            if i == 0: self.ev(t, "pop")
            y = 760 + i * 260; x0 = W / 2 - 440 * s; x1 = W / 2 + 440 * s
            rrect(c, (x0, y - 100 * s, x1, y + 100 * s), 26, (255, 255, 255), width=6)
            ImageDraw.Draw(c).ellipse((x0 + 30, y - 55 * s, x0 + 30 + 110 * s, y + 55 * s), fill=cols[i % 4], outline=INK, width=6)
            text(c, str(i + 1), x0 + 30 + 55 * s, y, 80 * s, fill=INK, stroke=0)
            ImageDraw.Draw(c).text((x0 + 170 * s, y - 34 * s), l1, font=font(54 * s), fill=INK, anchor="lm")
            ImageDraw.Draw(c).text((x0 + 170 * s, y + 34 * s), l2, font=font(54 * s), fill=CORES["vermelho"], anchor="lm")
        return c

    def ev(self, t, k): pass

    def votacao(self, c0, t, d, a):
        c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); dr = ImageDraw.Draw(c)
        ca, cb = (54, 96, 196), (40, 150, 90)
        dr.rectangle((0, 0, W / 2, H), fill=ca); dr.rectangle((W / 2, 0, W, H), fill=cb)
        for i in range(0, H, 60):
            dr.line((0, i, W / 2, i + 40), fill=(60, 106, 206), width=14); dr.line((W / 2, i + 40, W, i), fill=(46, 160, 98), width=14)
        dr.line((W / 2, 0, W / 2, H), fill=CORES["amarelo"], width=10)
        tag(c, "COMENTE UMA PALAVRA", W / 2, 290, 62, fill=CORES["amarelo"], rot=0, scale=ease_out_back(t / 0.3))
        tb = 0.25 + a * 0.62
        for lado, op, t0 in (("a", c0["a"], 0.35), ("b", c0["b"], tb)):
            cx = W / 4 if lado == "a" else W * 3 / 4; s = ease_out_back((t - t0) / 0.35)
            text(c, op["palavra"], cx, 470, 170 if len(op["palavra"]) <= 6 else 130, fill=CORES["amarelo"] if lado == "a" else (160, 220, 255), scale=s)
            text(c, op.get("sub", ""), cx, 580, 48, scale=s)
            if s > 0.01:
                im = scaled(op.get("id", "ruan:cabeca:neutro"), round(0.85 * s, 3), 700)
                c.alpha_composite(im, (int(cx - im.width / 2), int(1000 - im.height / 2)))
                self.icone(c, op.get("icone"), cx, 1330, t, s)
        sx = ease_out_back((t - tb - 0.4) / 0.3)
        if sx > 0.01:
            ImageDraw.Draw(c).ellipse((W / 2 - 70 * sx, 1000 - 70 * sx, W / 2 + 70 * sx, 1000 + 70 * sx), fill=INK, outline=CORES["amarelo"], width=8)
            text(c, "X", W / 2, 1000, 90 * sx, stroke=0)
        tf = 0.25 + a + 0.4
        if t > tf:
            dia = self.d.get("dia", 1); rest = self.d.get("dias_restantes", 30)
            tag(c, f"FALTAM {rest} DIAS", W / 2, 1530, 64, fill=CORES["vermelho"], fg=(255, 255, 255), rot=-2, scale=ease_out_back((t - tf) / 0.3))
            tag(c, c0.get("proximo", f"DIA {dia + 1} → DAQUI A POUCO"), W / 2, 1660, 52, rot=2, scale=ease_out_back((t - tf - 1.0) / 0.3))
        return c

    def icone(self, c, nome, cx, cy, t, s):
        if not nome or s <= 0.01: return
        d = ImageDraw.Draw(c)
        if nome == "despertador":
            r = 70 * s
            d.ellipse((cx - r - 35 * s, cy - r - 26 * s, cx - r + 18 * s, cy - r + 26 * s), fill=CORES["amarelo"], outline=INK, width=6)
            d.ellipse((cx + r - 18 * s, cy - r - 26 * s, cx + r + 35 * s, cy - r + 26 * s), fill=CORES["amarelo"], outline=INK, width=6)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=INK, width=8)
            d.line((cx, cy, cx, cy - 48 * s), fill=INK, width=8); d.line((cx, cy, cx + 35 * s, cy), fill=INK, width=8)
        elif nome == "chuveiro":
            d.pieslice((cx - 80 * s, cy - 90 * s, cx + 80 * s, cy + 30 * s), 180, 360, fill=(200, 206, 220), outline=INK, width=6)
            for i in range(7):
                x = cx - 60 * s + i * 20 * s; yy = cy - 20 * s + ((t * 300 + i * 37) % (140 * s))
                d.line((x, yy, x - 6, yy + 26 * s), fill=(150, 210, 255), width=8)
        elif nome == "coracao":
            r = 60 * s
            d.ellipse((cx - r, cy - r, cx, cy), fill=CORES["vermelho"], outline=INK, width=6)
            d.ellipse((cx, cy - r, cx + r, cy), fill=CORES["vermelho"], outline=INK, width=6)
            d.polygon([(cx - r + 3, cy - r / 2 + 10), (cx + r - 3, cy - r / 2 + 10), (cx, cy + r)], fill=CORES["vermelho"], outline=INK)
        elif nome == "haltere":
            d.rectangle((cx - 80 * s, cy - 8 * s, cx + 80 * s, cy + 8 * s), fill=(120, 120, 130), outline=INK, width=4)
            for k in (-1, 1):
                d.rounded_rectangle((cx + k * 80 * s - 22 * s, cy - 50 * s, cx + k * 80 * s + 22 * s, cy + 50 * s), 10, fill=(60, 60, 70), outline=INK, width=5)
        elif nome == "perfume":
            d.rounded_rectangle((cx - 45 * s, cy - 40 * s, cx + 45 * s, cy + 70 * s), 18, fill=(255, 170, 210), outline=INK, width=6)
            d.rectangle((cx - 15 * s, cy - 70 * s, cx + 15 * s, cy - 40 * s), fill=(220, 220, 230), outline=INK, width=5)
        elif nome == "flor":
            for k in range(6):
                a = k / 6 * 2 * math.pi
                d.ellipse((cx + 40 * s * math.cos(a) - 28 * s, cy + 40 * s * math.sin(a) - 28 * s, cx + 40 * s * math.cos(a) + 28 * s, cy + 40 * s * math.sin(a) + 28 * s), fill=CORES["rosa"], outline=INK, width=4)
            d.ellipse((cx - 24 * s, cy - 24 * s, cx + 24 * s, cy + 24 * s), fill=CORES["amarelo"], outline=INK, width=4)
        elif nome == "abacaxi":
            im = scaled("ruan:abacaxi:feliz", round(0.32 * s, 3)); c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        else:  # emoji/texto curto
            text(c, nome, cx, cy, 90 * s)

    # ------------------------------------------------ quadro
    def frame(self, T):
        for a, b, i, c0, adur in self.tl:
            if a <= T < b or i == len(self.tl) - 1:
                t, d = T - a, b - a; tp = c0["tipo"]
                if tp == "cena": c = self.cena(c0, t, d)
                elif tp == "close": c = self.close(c0, t, d)
                elif tp == "story": c = self.story(c0, t, d)
                elif tp == "chat": c = self.chat(c0, t, d)
                elif tp == "cards": c = self.cards(c0, t, d, adur)
                elif tp == "votacao": c = self.votacao(c0, t, d, adur)
                else: raise ValueError(tp)
                break
        c = c.convert("RGBA")
        if i == 0 and self.d.get("resultado"):
            tag(c, f"VOCÊS ESCOLHERAM: {self.d['resultado']}", W / 2, 250, 50, fill=CORES["amarelo"], rot=-2, scale=ease_out_back(T / 0.3))
        y = 1660 if c0["tipo"] == "close" else c0.get("legenda_y", 1450)
        self.legenda(c, T, y)
        self.hud(c, T)
        return c.convert("RGB")

    # ------------------------------------------------ saída
    def render(self):
        from concurrent.futures import ProcessPoolExecutor
        cdir = os.path.join(self.dir, "cenas"); os.makedirs(cdir, exist_ok=True)
        jobs = [(self.path, i, a, b) for a, b, i, _, _ in self.tl]
        with ProcessPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
            list(ex.map(_encode, jobs))
        with open(os.path.join(cdir, "lista.txt"), "w") as fh:
            for _, _, i, _, _ in self.tl: fh.write(f"file '{i:02d}.mp4'\n")
        mudo = os.path.join(self.dir, "video_mudo.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(cdir, "lista.txt"), "-c", "copy", mudo], check=True)
        import audio
        wav = os.path.join(self.dir, "audio.wav"); audio.mix(self, wav)
        out = os.path.join(self.dir, "video.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", out], check=True)
        self.thumb(); self.escrever_legenda()
        print("ok", out, round(self.total, 1), "s")

    def thumb(self):
        c = img("cenario:banca_abacaxi").copy()
        vt = [c0 for c0 in self.cenas if c0["tipo"] == "votacao"]
        im = scaled(self.d.get("thumb_ator", "ruan:em_pe:suando"), 1.15); c.alpha_composite(im, (int(W / 2 - im.width / 2), int(1880 - im.height)))
        c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 60)))
        tag(c, f"DIA {self.d.get('dia', 1)}", W / 2, 330, 150, fill=CORES["amarelo"], rot=-4)
        tag(c, self.d.get("thumb_texto", "30 DIAS PRO RUAN"), W / 2, 560, 70, fill=(255, 255, 255), rot=3)
        if vt:
            rich(c, [(vt[0]["a"]["palavra"], CORES["amarelo"]), ("OU", (255, 255, 255)), (vt[0]["b"]["palavra"] + "?", (160, 220, 255))], W / 2, 760, 120)
        c.convert("RGB").save(os.path.join(self.dir, "thumb.jpg"), quality=90)

    def escrever_legenda(self):
        open(os.path.join(self.dir, "legenda.txt"), "w").write(self.d.get("legenda_post", ""))

def _encode(job):
    path, i, a, b = job
    ep = Ep(path); ep.montar()
    cdir = os.path.join(ep.dir, "cenas"); out = os.path.join(cdir, f"{i:02d}.mp4"); tmp = os.path.join(cdir, f"{i:02d}.tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(round(a * FPS), round(b * FPS)):
        p.stdin.write(ep.frame(n / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)

if __name__ == "__main__":
    ep = Ep(sys.argv[1]); modo = sys.argv[2]
    if modo == "voz":
        ep.gravar_voz(); sys.exit()
    ep.montar()
    if modo == "quadros":
        os.makedirs(os.path.join(ep.dir, "teste"), exist_ok=True)
        for T in map(float, sys.argv[3:]):
            ep.frame(T).save(os.path.join(ep.dir, "teste", f"t{T:05.2f}.jpg"), quality=85)
        print("duração", round(ep.total, 1))
    elif modo == "video":
        ep.render()
