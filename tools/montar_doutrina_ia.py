#!/usr/bin/env python3
"""Monta no app os capítulos escritos a partir do texto das leis (dados/doutrina_ia/*.json), sem apagar os fascículos importados.
Gera data/doutrina/iNNN.js (carregado sob demanda), mapa mental em data/doutrina/mapas/ e acrescenta as entradas em data/doutrina/index.js.
Rode depois de tools/importar_fasciculos.py (que o chama no final) ou sozinho. Uso: python tools/montar_doutrina_ia.py"""
import glob, json, os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
OUT = os.path.join(R, "data", "doutrina"); os.makedirs(os.path.join(OUT, "mapas"), exist_ok=True)
ixp = os.path.join(OUT, "index.js")
idx = json.loads(open(ixp, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";")) if os.path.exists(ixp) else []
idx = [x for x in idx if not x["id"].startswith("i")]
for f in glob.glob(os.path.join(OUT, "i*.js")) + glob.glob(os.path.join(OUT, "mapas", "i*.svg")):
    if re.match(r"i\d+\.(js|svg)$", os.path.basename(f)): os.remove(f)
for n, f in enumerate(sorted(glob.glob(os.path.join(R, "dados", "doutrina_ia", "*.json"))), 1):
    c = json.load(open(f, encoding="utf-8")); id_ = "i%03d" % n
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
                "origem": "texto das leis do app (" + os.path.basename(f) + ")", "ia": True})
open(ixp, "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
print(sum(1 for x in idx if x["id"].startswith("i")), "capítulos baseados em lei montados")
