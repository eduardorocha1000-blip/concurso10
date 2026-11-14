#!/usr/bin/env python3
"""Monta no app os capítulos escritos a partir do texto das leis (dados/doutrina_ia/*.json), sem apagar os fascículos importados.
Gera data/doutrina/iNNN.js (carregado sob demanda), mapa mental em data/doutrina/mapas/ e acrescenta as entradas em data/doutrina/index.js.
Rode depois de tools/importar_fasciculos.py (que o chama no final) ou sozinho. Uso: python tools/montar_doutrina_ia.py"""
import glob, json, os, re, sys
from collections import Counter
import random, zlib
def embaralha(o, titulo):
    """Distribui a alternativa correta entre A-D (nas fontes ela quase sempre é a B), ajustando as letras citadas no comentário."""
    a = o["a"]; L = "ABCD"
    if len(a) != 4 or o.get("g") not in list(L): return o
    rng = random.Random(zlib.crc32((titulo + str(o.get("n"))).encode("utf-8")))
    certo = L.index(o["g"]); alvo = (zlib.crc32((titulo + str(o.get("n")) + "k").encode("utf-8")) >> 3) % 4
    outros = [i for i in range(4) if i != certo]; rng.shuffle(outros)
    ordem = [None] * 4; ordem[alvo] = certo
    for pos in range(4):
        if ordem[pos] is None: ordem[pos] = outros.pop()
    novo = {old: L[pos] for pos, old in enumerate(ordem)}
    def troca(m): return re.sub(r"([A-D])", lambda k: novo[L.index(k.group(1))], m.group(0))
    c = re.sub(r"alternativas?\s+[A-D](?:(?:,|\s+e|\s+ou)\s+[A-D])*", troca, o.get("c", ""))
    return dict(o, a=[a[i] for i in ordem], g=L[alvo], c=c)
SIGLAS = ["OAB", "MPSC", "STJ", "STF", "LEP", "RPV", "SC", "TJSC", "TRF4", "ENAM", "CDC", "CPC", "CPP", "CC", "CP", "CF", "PIC", "ANPP", "IRDR", "IAC", "LEF", "EC136", "TCE", "PAD"]
def limpa_titulo(t):
    """Arruma títulos de fascículos que vieram em CAIXA ALTA ou com siglas em minúsculas (idempotente)."""
    t = re.sub(r"[-]+", ", ", t); t = re.sub(r"\s+", " ", t).strip(); t = re.sub(r"(,\s*)+", ", ", t)
    t = re.sub(r"(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,} ?){3,}", lambda m: m.group(0).lower().capitalize() if m.start() == 0 else m.group(0).lower(), t)
    letras = [ch for ch in t if ch.isalpha()]
    if letras and sum(ch.isupper() for ch in letras) / len(letras) > 0.5:
        t = t.lower(); t = t[:1].upper() + t[1:]
    for sg in SIGLAS: t = re.sub(r"\b" + sg + r"\b", sg, t, flags=re.I)
    t = re.sub(r"\bf(\d+)\b", r"F\1", t, flags=re.I)
    t = re.sub(r"\b(?:ec)(\d+)\b", r"EC \1", t, flags=re.I)
    return t.replace("revisao", "revisão")
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
OUT = os.path.join(R, "data", "doutrina"); os.makedirs(os.path.join(OUT, "mapas"), exist_ok=True)
ixp = os.path.join(OUT, "index.js")
idx = json.loads(open(ixp, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";")) if os.path.exists(ixp) else []
idx = [x for x in idx if x["id"][0] not in "ic"]
for f in glob.glob(os.path.join(OUT, "[ic]*.js")) + glob.glob(os.path.join(OUT, "mapas", "[ic]*.svg")):
    if re.match(r"[ic]\d+\.(js|svg)$", os.path.basename(f)): os.remove(f)
fontes = [("i", f) for f in sorted(glob.glob(os.path.join(R, "dados", "doutrina_ia", "*.json")))] + [("c", f) for f in sorted(glob.glob(os.path.join(R, "dados", "curso", "*", "*.json"))) if os.path.basename(os.path.dirname(f)) not in ("textos", "questoes")]
cont = Counter()
for pref, f in fontes:
    cont[pref] += 1; n = cont[pref]
    c = json.load(open(f, encoding="utf-8")); id_ = "%s%03d" % (pref, n)
    corpo = {"ap": c.get("ap", []), "sumario": ["%d. %s" % (k + 1, s["t"]) for k, s in enumerate(c["secoes"])], "secoes": c["secoes"], "casos": c.get("casos", []),
             "obj": [embaralha(o, c["titulo"]) for o in c.get("obj", [])], "disc": c.get("disc", []), "refs": c.get("refs", [])}
    open(os.path.join(OUT, id_ + ".js"), "w", encoding="utf-8").write('(window.DOUT=window.DOUT||{})["%s"]=' % id_ + json.dumps(corpo, ensure_ascii=False) + ";\n")
    arv = {"t": c["titulo"][:90], "c": [{"t": s["t"], "c": []} for s in c["secoes"][:14]]}
    for nm, k in (("Casos práticos", "casos"), ("Questões objetivas", "obj"), ("Questões discursivas", "disc")):
        if corpo[k]: arv["c"].append({"t": "%s (%d)" % (nm, len(corpo[k]))})
    mapa = len(c["secoes"]) >= 3
    if mapa: open(os.path.join(OUT, "mapas", id_ + ".svg"), "w", encoding="utf-8").write(svg_mapa(c["titulo"], arv))
    chars = sum(len(b[1]) for s in c["secoes"] for b in s["b"])
    idx.append({"id": id_, "disc": c["area"], "materia": c["materia"], "titulo": c["titulo"], "ordem": c.get("ordem", n), "paginas": max(1, round(chars / 2400)), "mapa": mapa,
                "casos": len(corpo["casos"]), "obj": len(corpo["obj"]), "disc_q": len(corpo["disc"]), "secoes": len(c["secoes"]), "status": "unico", "grupo": None, "parecidos": [],
                "origem": ("texto das leis do app (" if pref == "i" else "material do curso (") + os.path.basename(f) + ")", "ia": pref == "i", "curso": pref == "c"})
for x in idx: x["titulo"] = limpa_titulo(x["titulo"]) if x["id"][0] == "f" else x["titulo"]
open(ixp, "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
print(sum(1 for x in idx if x["id"][0] == "i"), "capítulos baseados em lei e", sum(1 for x in idx if x["id"][0] == "c"), "do curso montados")

# fascículos (fNNN): a alternativa correta também vinha quase sempre na B (73%); distribui A-D de forma determinística (idempotente)
def embaralha_f():
    import re as _re
    n = 0
    for f in sorted(glob.glob(os.path.join(OUT, "f[0-9]*.js"))):
        t = open(f, encoding="utf-8").read(); i = t.index("]={") + 2; j = t.rindex(";")
        d = json.loads(t[i:j]); id_ = os.path.basename(f)[:-3]; mudou = False
        for k, o in enumerate(d.get("obj", [])):
            a = o.get("a") or []
            if len(a) != 4 or o.get("g") not in list("ABCD"): continue
            alvo = "ABCD"[(zlib.crc32((id_ + str(o.get("n")) + "k").encode("utf-8")) >> 3) % 4]
            if o["g"] == alvo: continue
            d["obj"][k] = embaralha(o, id_); mudou = True; n += 1
        if mudou: open(f, "w", encoding="utf-8").write(t[:i] + json.dumps(d, ensure_ascii=False) + t[j:])
    return n
print(embaralha_f(), "gabaritos de fascículos redistribuídos")
