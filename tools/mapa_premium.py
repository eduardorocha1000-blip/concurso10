"""Mapa mental "premium" em SVG vetorial (alta resolucao), esquerda -> direita.

Arvore: dict {t, sub?, c:[ramos]}; cada no: dict {t, k?, c?} ou tabela {tab:{t, cols, rows}}.
Tipos de no (k): art, sum, prazo, exc, att, def, req, ex  -> etiqueta colorida + fundo proprio.
Mede o texto com a fonte real (PIL) para quebrar linhas sem estourar a caixa.
"""
import os
from xml.sax.saxutils import escape
from PIL import ImageFont

FD = r"C:\Windows\Fonts"
def _f(n, s):
    for p in (os.path.join(FD, n), n):
        try: return ImageFont.truetype(p, s)
        except Exception: pass
    return ImageFont.load_default()

SZ = 15          # corpo
F = _f("segoeui.ttf", SZ); FB = _f("segoeuib.ttf", SZ); FT = _f("segoeuib.ttf", 11)
FH = _f("segoeuib.ttf", 17); FR = _f("segoeuib.ttf", 30)
MARG = 1.07      # folga p/ fontes diferentes (Roboto no Android)
PAL = ["#1e6fb8", "#c2410c", "#15803d", "#7c3aed", "#be123c", "#0f766e", "#a16207", "#334155"]
KIND = {  # rotulo, cor, fundo
    "art":  ("ARTIGO", "#1d4ed8", "#eff6ff"),
    "sum":  ("SÚMULA/TEMA", "#6d28d9", "#f5f3ff"),
    "prazo": ("PRAZO", "#15803d", "#f0fdf4"),
    "exc":  ("EXCEÇÃO", "#b45309", "#fffbeb"),
    "att":  ("CAI EM PROVA", "#b91c1c", "#fef2f2"),
    "def":  ("CONCEITO", "#475569", "#f1f5f9"),
    "req":  ("REQUISITO", "#0f766e", "#f0fdfa"),
    "ex":   ("EXEMPLO", "#a16207", "#fefce8"),
}

def N(t, k=None, *c): return {"t": t, "k": k, "c": list(c)}
def T(t, cols, rows): return {"tab": {"t": t, "cols": cols, "rows": rows}}

def tw(s, font): return font.getlength(s) * MARG
def wrap(s, font, w):
    out, cur = [], ""
    for p in str(s).split("\n"):
        cur = ""
        for word in p.split():
            tt = (cur + " " + word).strip()
            if tw(tt, font) <= w or not cur: cur = tt
            else: out.append(cur); cur = word
        out.append(cur)
    return out or [""]

LH = 20; PADY = 9; PADX = 12
W1, W2, W3 = 250, 330, 350; GX = 46; GY = 10

def svg_premium(raiz, rodape="Resumo do curso, conferido com a lei do app. Itens só do curso ficam «segundo o curso»."):
    nodes = []
    def prep(n, d, cor):
        if "tab" in n: n["_tab"] = True
        n["d"] = d; n["cor"] = cor; n["f"] = []
        if d == 0 and n.get("k") and n["k"] not in KIND: n["sub"] = n["k"]; n["k"] = None
        for i, c in enumerate(n.get("c") or []):
            n["f"].append(prep(c, d + 1, cor if d else PAL[i % len(PAL)]))
        nodes.append(n); return n
    r = prep(raiz, 0, "#0f172a")
    W = {0: W1 + 20, 1: W1, 2: W2}
    def wd(d): return W.get(d, W3)
    xs, x = {}, 24
    maxd = max(n["d"] for n in nodes)
    for d in range(maxd + 1): xs[d] = x; x += wd(d) + GX
    totw = x - GX + 24
    # medir
    for n in nodes:
        d = n["d"]; w = wd(d)
        if n.get("_tab"):
            tb = n["tab"]; tw_ = W2 + (GX + W3 if maxd >= 3 else 0) if d == 2 else wd(d) * 1.0
            tw_ = max(tw_, 440); n["w"] = tw_
            nc = len(tb["cols"]); cw = tw_ / nc; n["cw"] = cw
            hh = [max(len(wrap(c, FB, cw - 14)) for c in tb["cols"]) * LH + 12]
            for row in tb["rows"]: hh.append(max(len(wrap(c, F, cw - 14)) for c in row) * LH + 12)
            n["rowh"] = hh; n["h"] = sum(hh) + 26; continue
        if d == 0:
            n["lines"] = wrap(n["t"], FR, w - 28); n["sub"] = wrap(n.get("sub", ""), F, w - 28) if n.get("sub") else []
            n["h"] = len(n["lines"]) * 36 + len(n["sub"]) * LH + 30; n["w"] = w; continue
        if d == 1:
            n["lines"] = wrap(n["t"], FH, w - 56); n["h"] = max(46, len(n["lines"]) * 23 + 20); n["w"] = w; continue
        k = n.get("k"); lab = KIND.get(k)
        tagw = (tw(lab[0], FT) + 14) if lab else 0
        n["lines"] = wrap(n["t"], F, w - 2 * PADX - 4 - (0 if not lab else 0))
        n["tagw"] = tagw
        n["h"] = len(n["lines"]) * LH + 2 * PADY + (18 if lab else 0); n["w"] = w
    # posicionar: ramos divididos em dois lados (direita/esquerda) equilibrados por altura
    def pos(n, cur):
        if not n["f"]:
            n["y"] = cur[0] + n["h"] / 2; cur[0] += n["h"] + GY
        else:
            for f in n["f"]: pos(f, cur)
            lo = min(f["y"] - f["h"] / 2 for f in n["f"]); hi = max(f["y"] + f["h"] / 2 for f in n["f"])
            n["y"] = (lo + hi) / 2
            if n["d"] == 1: cur[0] += GY * 1.6
    def alt(n):
        if not n["f"]: return n["h"] + GY
        return sum(alt(f) for f in n["f"]) + (GY * 1.6 if n["d"] == 1 else 0)
    ramos = r["f"]; al = [alt(b) for b in ramos]; best = None
    for i in range(1, len(ramos)):
        df = abs(sum(al[:i]) - sum(al[i:]))
        if best is None or df < best[0]: best = (df, i)
    cut = best[1] if best else len(ramos)
    R, L = ramos[:cut], ramos[cut:]
    def lado(gr, sinal):
        cur = [0]
        for b_ in gr: pos(b_, cur)
        return cur[0]
    hR, hL = lado(R, 1), lado(L, -1); Hm = max(hR, hL, r["h"])
    def shift(n, dy):
        n["y"] += dy
        for f in n["f"]: shift(f, dy)
    for gr, h in ((R, hR), (L, hL)):
        for b_ in gr: shift(b_, (Hm - h) / 2)
    r["y"] = Hm / 2
    colw = sum(wd(d) + GX for d in range(1, maxd + 1))
    rootx = 24 + colw; r["x"] = rootx; r["side"] = 0
    totw = rootx + r["w"] + colw + 24
    def setx(n, side):
        n["side"] = side
        off = sum(wd(d) + GX for d in range(1, n["d"]))
        n["x"] = rootx + r["w"] + GX + off if side > 0 else rootx - GX - off - n["w"]
        for f in n["f"]: setx(f, side)
    for b_ in R: setx(b_, 1)
    for b_ in L: setx(b_, -1)
    top = 96; totH = Hm + top + 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {totw:.0f} {totH:.0f}" width="{totw:.0f}" height="{totH:.0f}" font-family="Segoe UI,Roboto,Arial,sans-serif" font-size="{SZ}">',
         f'<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<rect x="0" y="0" width="{totw:.0f}" height="6" fill="#0f172a"/>']
    def lig(n):
        for f in n["f"]:
            if f["x"] >= n["x"]: x1 = n["x"] + n["w"]; x2 = f["x"]
            else: x1 = n["x"]; x2 = f["x"] + f["w"]
            y1 = n["y"] + top; y2 = f["y"] + top; m = (x1 + x2) / 2
            sw = 3.2 if n["d"] == 0 else (2.2 if n["d"] == 1 else 1.5)
            o.append(f'<path d="M{x1:.0f},{y1:.0f} C{m:.0f},{y1:.0f} {m:.0f},{y2:.0f} {x2:.0f},{y2:.0f}" fill="none" stroke="{f["cor"]}" stroke-width="{sw}" opacity=".7" stroke-linecap="round"/>')
            lig(f)
    lig(r)
    for n in nodes:
        d = n["d"]; x0 = n["x"]; w = n["w"]; y0 = n["y"] + top - n["h"] / 2; cor = n["cor"]
        if n.get("_tab"):
            tb = n["tab"]; cw = n["cw"]; yy = y0
            o.append(f'<text x="{x0:.0f}" y="{yy + 14:.0f}" font-weight="700" font-size="13" fill="{cor}">{escape(tb["t"].upper())}</text>'); yy += 22
            o.append(f'<rect x="{x0:.0f}" y="{yy:.0f}" width="{w:.0f}" height="{sum(n["rowh"]):.0f}" rx="8" fill="#fff" stroke="{cor}" stroke-width="1.4"/>')
            for ri, rh in enumerate(n["rowh"]):
                if ri == 0: o.append(f'<path d="M{x0:.0f},{yy + 8:.0f} a8,8 0 0 1 8,-8 h{w - 16:.0f} a8,8 0 0 1 8,8 v{rh - 8:.0f} h{-w:.0f} z" fill="{cor}"/>')
                elif ri % 2 == 0: o.append(f'<rect x="{x0 + 1:.0f}" y="{yy:.0f}" width="{w - 2:.0f}" height="{rh:.0f}" fill="#f8fafc"/>')
                cells = tb["cols"] if ri == 0 else tb["rows"][ri - 1]
                for ci, cell in enumerate(cells):
                    fo = FB if (ri == 0 or ci == 0) else F
                    for li, ln in enumerate(wrap(cell, fo, cw - 14)):
                        o.append(f'<text x="{x0 + ci * cw + 8:.0f}" y="{yy + 20 + li * LH:.0f}" fill="{"#fff" if ri == 0 else "#0f172a"}"{" font-weight=\"700\"" if (ri == 0 or ci == 0) else ""}>{escape(ln)}</text>')
                yy += rh
            for ci in range(1, len(tb["cols"])):
                o.append(f'<line x1="{x0 + ci * cw:.0f}" y1="{y0 + 22:.0f}" x2="{x0 + ci * cw:.0f}" y2="{y0 + 22 + sum(n["rowh"]):.0f}" stroke="{cor}" stroke-opacity=".25"/>')
            continue
        if d == 0:
            o.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{n["h"]:.0f}" rx="18" fill="#0f172a"/>')
            yy = y0 + 40
            for ln in n["lines"]: o.append(f'<text x="{x0 + 14:.0f}" y="{yy:.0f}" font-size="30" font-weight="700" fill="#fff">{escape(ln)}</text>'); yy += 36
            yy -= 8
            for ln in n["sub"]: o.append(f'<text x="{x0 + 14:.0f}" y="{yy + 12:.0f}" fill="#cbd5e1">{escape(ln)}</text>'); yy += LH
        elif d == 1:
            o.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{n["h"]:.0f}" rx="12" fill="{cor}"/>')
            o.append(f'<circle cx="{x0 + 24:.0f}" cy="{n["y"] + top:.0f}" r="13" fill="#fff" fill-opacity=".22"/><text x="{x0 + 24:.0f}" y="{n["y"] + top + 5:.0f}" text-anchor="middle" font-weight="700" fill="#fff">{n.get("_i", "")}</text>')
            yy = n["y"] + top - (len(n["lines"]) - 1) * 11.5 + 6
            for ln in n["lines"]: o.append(f'<text x="{x0 + 46:.0f}" y="{yy:.0f}" font-size="17" font-weight="700" fill="#fff">{escape(ln)}</text>'); yy += 23
        else:
            k = n.get("k"); lab = KIND.get(k)
            fill = lab[2] if lab else "#ffffff"; st = lab[1] if lab else cor
            o.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{n["h"]:.0f}" rx="9" fill="{fill}" stroke="{st}" stroke-width="{1.5 if lab else 1.2}" stroke-opacity="{1 if lab else .55}"/>')
            if not lab: o.append(f'<rect x="{x0:.0f}" y="{y0 + 6:.0f}" width="4.5" height="{n["h"] - 12:.0f}" rx="2" fill="{cor}"/>')
            yy = y0 + PADY + 14
            if lab:
                o.append(f'<rect x="{x0 + PADX - 2:.0f}" y="{y0 + 6:.0f}" width="{n["tagw"]:.0f}" height="16" rx="8" fill="{st}"/><text x="{x0 + PADX + 5:.0f}" y="{y0 + 18:.0f}" font-size="10.5" font-weight="700" fill="#fff" letter-spacing=".4">{escape(lab[0])}</text>'); yy += 18
            for ln in n["lines"]: o.append(f'<text x="{x0 + PADX + (3 if not lab else 0):.0f}" y="{yy:.0f}" fill="#0f172a">{escape(ln)}</text>'); yy += LH
    # titulo e legenda
    o.append(f'<text x="24" y="40" font-size="12" font-weight="700" fill="#64748b" letter-spacing="1.5">MAPA MENTAL</text>')
    lx = 24
    for k, (lab, c, bg) in KIND.items():
        wtag = tw(lab, FT) + 14
        o.append(f'<rect x="{lx:.0f}" y="{totH - 44:.0f}" width="{wtag:.0f}" height="16" rx="8" fill="{c}"/><text x="{lx + 7:.0f}" y="{totH - 32:.0f}" font-size="10.5" font-weight="700" fill="#fff" letter-spacing=".4">{escape(lab)}</text>'); lx += wtag + 10
    o.append(f'<text x="24" y="{totH - 14:.0f}" font-size="12" fill="#64748b">{escape(rodape)}</text>')
    o.append("</svg>"); return "\n".join(o)

def numerar(raiz):
    for i, c in enumerate(raiz["c"], 1): c["_i"] = i
    return raiz
