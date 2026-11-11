"""Gera mapas mentais como imagem SVG (esquerda→direita) a partir de uma árvore {t, c:[...]}."""
from xml.sax.saxutils import escape
PAL = ["#1e6fb8", "#8a1c3c", "#1f7a4d", "#5b3a9a", "#c2570c", "#0f766e", "#a16207", "#be185d"]
CW = 7.2   # largura média de caractere (px) a 13px
def cortar(t, n):
    t = " ".join(str(t).split()); return t if len(t) <= n else t[: n - 1].rstrip() + "…"
def svg_mapa(titulo, raiz, maxch=46):
    nos = []
    def prep(n, nivel, cor):
        no = {"t": n["t"], "txt": cortar(n["t"], 58 if nivel == 0 else maxch), "nivel": nivel, "cor": cor, "f": []}
        for i, c in enumerate(n.get("c") or []):
            no["f"].append(prep(c, nivel + 1, cor if nivel else PAL[i % len(PAL)]))
        nos.append(no); return no
    r = prep(raiz, 0, "#334155")
    larg = {}
    for n in nos: larg[n["nivel"]] = max(larg.get(n["nivel"], 0), len(n["txt"]) * CW + 22)
    xs, x = {}, 14
    for nv in sorted(larg): xs[nv] = x; x += larg[nv] + 56
    W = x - 56 + 14; H = [0]
    def pos(n):
        if not n["f"]: n["y"] = H[0] + 15; H[0] += 34
        else:
            for f in n["f"]: pos(f)
            n["y"] = (n["f"][0]["y"] + n["f"][-1]["y"]) / 2
    pos(r); Ht = H[0] + 44
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {Ht:.0f}" width="{W:.0f}" height="{Ht:.0f}" font-family="Segoe UI,Roboto,Arial,sans-serif" font-size="13">',
         f'<rect width="100%" height="100%" fill="#ffffff"/><text x="14" y="22" font-size="15" font-weight="700" fill="#0f172a">{escape(cortar(titulo, 120))}</text><g transform="translate(0,34)">']
    def lig(n):
        for f in n["f"]:
            x1, y1, x2, y2 = xs[n["nivel"]] + larg[n["nivel"]], n["y"], xs[f["nivel"]], f["y"]; m = (x1 + x2) / 2
            o.append(f'<path d="M{x1:.0f},{y1:.0f} C{m:.0f},{y1:.0f} {m:.0f},{y2:.0f} {x2:.0f},{y2:.0f}" fill="none" stroke="{f["cor"]}" stroke-width="{2.2 if f["nivel"] == 1 else 1.4}" opacity=".75"/>'); lig(f)
    lig(r)
    for n in nos:
        w, x0 = larg[n["nivel"]], xs[n["nivel"]]
        if n["nivel"] <= 1: fill, stroke, tc = n["cor"], n["cor"], "#fff"
        else: fill, stroke, tc = "#f8fafc", n["cor"], "#0f172a"
        o.append(f'<g><title>{escape(" ".join(str(n["t"]).split()))}</title><rect x="{x0:.0f}" y="{n["y"] - 13:.0f}" width="{w:.0f}" height="26" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/><text x="{x0 + 11:.0f}" y="{n["y"] + 4.5:.0f}" fill="{tc}"{" font-weight=\"700\"" if n["nivel"] <= 1 else ""}>{escape(n["txt"])}</text></g>')
    o.append("</g></svg>"); return "\n".join(o)
