#!/usr/bin/env python3
"""Monta no app os capítulos escritos a partir do texto das leis (dados/doutrina_ia/*.json), sem apagar os fascículos importados.
Gera data/doutrina/iNNN.js (carregado sob demanda), mapa mental em data/doutrina/mapas/ e acrescenta as entradas em data/doutrina/index.js.
Rode depois de tools/importar_fasciculos.py (que o chama no final) ou sozinho. Uso: python tools/montar_doutrina_ia.py"""
import glob, json, os, re, sys
from collections import Counter
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
OUT = os.path.join(R, "data", "doutrina"); os.makedirs(os.path.join(OUT, "mapas"), exist_ok=True)
ixp = os.path.join(OUT, "index.js")
idx = json.loads(open(ixp, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";")) if os.path.exists(ixp) else []
idx = [x for x in idx if x["id"][0] not in "ic"]
for f in glob.glob(os.path.join(OUT, "[ic]*.js")) + glob.glob(os.path.join(OUT, "mapas", "[ic]*.svg")):
    if re.match(r"[ic]\d+\.(js|svg)$", os.path.basename(f)): os.remove(f)
fontes = [("i", f) for f in sorted(glob.glob(os.path.join(R, "dados", "doutrina_ia", "*.json")))] + [("c", f) for f in sorted(glob.glob(os.path.join(R, "dados", "curso", "*", "*.json")))]
cont = Counter()
for pref, f in fontes:
    cont[pref] += 1; n = cont[pref]
    c = json.load(open(f, encoding="utf-8")); id_ = "%s%03d" % (pref, n)
    corpo = {"ap": c.get("ap", []), "sumario": ["%d. %s" % (k + 1, s["t"]) for k, s in enumerate(c["secoes"])], "secoes": c["secoes"], "casos": c.get("casos", []),
             "obj": c.get("obj", []), "disc": c.get("disc", []), "refs": c.get("refs", [])}
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
open(ixp, "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
print(sum(1 for x in idx if x["id"][0] == "i"), "capítulos baseados em lei e", sum(1 for x in idx if x["id"][0] == "c"), "do curso montados")
