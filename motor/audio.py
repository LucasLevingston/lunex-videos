"""Mixagem do episódio: narração + trilha sintetizada + efeitos automáticos (sem arquivos de terceiros)."""
import os, wave
import numpy as np

SR = 44100
RNG = np.random.default_rng(7)

def load(path):
    w = wave.open(path); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    return np.interp(np.arange(int(len(x) * SR / sr)) / SR, np.arange(len(x)) / sr, x)

def pluck(f, d=0.35, a=0.3):
    t = np.arange(int(d * SR)) / SR
    return a * np.exp(-t * 9) * (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t))
def kick():
    t = np.arange(int(0.25 * SR)) / SR; return 0.8 * np.exp(-t * 18) * np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t)
def hat():
    n = np.diff(RNG.standard_normal(int(0.05 * SR)), prepend=0); return 0.15 * n * np.exp(-np.arange(len(n)) / SR * 70)
def pop(f0=900):
    t = np.arange(int(0.12 * SR)) / SR; return 0.5 * np.exp(-t * 35) * np.sin(2 * np.pi * (f0 - 2500 * t) * t)
def whoosh(d=0.35):
    n = RNG.standard_normal(int(d * SR)); env = np.sin(np.linspace(0, np.pi, len(n)))
    return 0.35 * np.convolve(n, np.ones(40) / 40, "same") * env * 4
def ding():
    t = np.arange(int(0.6 * SR)) / SR
    return 0.3 * np.exp(-t * 6) * (np.sin(2 * np.pi * 1320 * t) + np.sin(2 * np.pi * 1760 * t * (t > 0.12)))
def thud():
    t = np.arange(int(0.35 * SR)) / SR; return 0.9 * np.exp(-t * 12) * np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 20)) * t)
def galo():
    t = np.arange(int(0.7 * SR)) / SR; f = 600 + 400 * np.sin(np.pi * t / 0.7) ** 2
    return 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.7) * (1 + 0.5 * np.sin(2 * np.pi * 30 * t))
def ronco():
    t = np.arange(int(0.9 * SR)) / SR
    x = 0.25 * RNG.standard_normal(len(t)) * np.sin(np.pi * t / 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    return np.convolve(x, np.ones(60) / 60, "same") * 3
def agua(d=1.5):
    n = RNG.standard_normal(int(d * SR)); return 0.12 * np.convolve(n, np.ones(6) / 6, "same") * np.minimum(1, np.linspace(0, 6, len(n))) * np.minimum(1, np.linspace(6, 0, len(n)))
def tada():
    return np.concatenate([pluck(523, 0.15, 0.4), pluck(659, 0.15, 0.4), pluck(784, 0.5, 0.5)])
def fail():
    t = np.arange(int(0.8 * SR)) / SR; return 0.3 * np.sin(2 * np.pi * (400 - 250 * t) * t) * np.exp(-t * 2)

SONS = {"pop": pop, "whoosh": whoosh, "ding": ding, "thud": thud, "galo": galo, "ronco": ronco, "agua": agua, "tada": tada, "fail": fail}

def mix(ep, out):
    N = int(ep.total * SR) + SR
    v = np.zeros(N); m = np.zeros(N); fx = np.zeros(N)
    def put(buf, x, t, g=1.0):
        i = int(t * SR)
        if i >= N: return
        x = x[: N - i]; buf[i:i + len(x)] += x * g
    for key, t in ep.vozes:
        x = load(os.path.join(ep.vozdir, f"{key}.wav")); put(v, x / (np.abs(x).max() + 1e-9) * 0.9, t)
    # trilha
    beat = 60 / 110
    chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    bass = [65.4, 55.0, 43.7, 49.0]
    tensao = [(a, b) for a, b, i, c, _ in ep.tl if c["tipo"] == "close"]
    for b in range(int(ep.total / beat)):
        t = b * beat; ch = chords[(b // 4) % 4]
        if b % 2 == 0:
            for f in ch: put(m, pluck(f * 2, 0.4, 0.12), t)
        else:
            put(m, pluck(ch[(b // 2) % 3] * 2, 0.25, 0.14), t)
        put(m, pluck(bass[(b // 4) % 4] * 2, 0.5, 0.35), t)
        if any(a <= t < z for a, z in tensao): put(m, kick(), t, 0.9)
        elif b % 2 == 0: put(m, kick(), t, 0.7)
        put(m, hat(), t + beat / 2, 0.6)
    # efeitos automáticos
    for a, b, i, c, adur in ep.tl:
        put(fx, whoosh(), a)
        tp = c["tipo"]
        if tp == "close": put(fx, thud(), a); put(fx, pop(600), a + 0.3)
        if tp == "story": put(fx, ding(), a + 0.05); put(fx, pop(), a + 0.35)
        if tp == "chat":
            for msg in c.get("mensagens", []): put(fx, pop(1100 if msg.get("de") == "ruan" else 800), a + msg.get("t", 0))
        if tp == "cards":
            for st in ep.sentencas(c.get("fala", ""), adur)[-len(c["itens"]):]: put(fx, pop(1000), a + 0.25 + st)
        if tp == "votacao":
            put(fx, pop(), a + 0.35); put(fx, pop(1300), a + 0.25 + adur * 0.62); put(fx, thud(), a + 0.65 + adur * 0.62)
            put(fx, pop(), a + 0.65 + adur); put(fx, pop(1200), a + 1.65 + adur)
        for tg in c.get("tags", []): put(fx, pop(), a + tg.get("t", 0))
        for at in c.get("atores", []):
            if at.get("entra") == "pop": put(fx, pop(800), a + at.get("t", 0))
            elif at.get("entra"): put(fx, whoosh(), a + at.get("t", 0))
            for p in at.get("pula", []): put(fx, pop(700), a + p)
        for t, nome in c.get("sons", []):
            put(fx, SONS[nome](), a + t)
    if ep.d.get("resultado"): put(fx, tada(), 0.05)
    outa = v + m / (np.abs(m).max() + 1e-9) * 0.16 + fx * 0.5
    fade = int(1.2 * SR); outa[-fade:] *= np.linspace(1, 0, fade)
    outa = outa[: int(ep.total * SR)]; outa = outa / (np.abs(outa).max() + 1e-9) * 0.95
    w = wave.open(out, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((outa * 32767).astype(np.int16).tobytes()); w.close()
