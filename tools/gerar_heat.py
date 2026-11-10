#!/usr/bin/env python3
"""Gera data/heat.js (mapa de calor REAL) a partir de dados/editais_analise.csv.

CSV (separador ; ou ,) com colunas:  tipo;modulo;edital;ano;ref;item
  tipo   lei | sumula | enunciado | juris
  modulo oab | magsc | mpsc | magfed
  edital nome do concurso/prova (cada edital distinto conta 1, no máximo 5 por módulo)
  ref    lei: id da lei (cf, cc, cpc, cp, cpp...)  | sumula: STF, STF-SV, STJ  | enunciado: fonte | juris: referência exata
  item   lei: nº do artigo (ex.: 1.829 ou 121-A) | sumula/enunciado: número | juris: use -

Uma linha = "este item foi cobrado nesta prova". Várias linhas do mesmo item/edital contam uma vez só.
Uso: python tools/gerar_heat.py [caminho.csv]
"""
import csv, glob, json, os, re, sys
from collections import defaultdict

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
norm = lambda n: re.sub(r"[.º°o\s]", "", str(n)).lower()
MODS = {"oab", "magsc", "mpsc", "magfed"}

def main():
    arq = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "dados", "editais_analise.csv")
    if not os.path.exists(arq):
        sys.exit("Crie dados/editais_analise.csv (copie dados/editais_analise_modelo.csv).")
    txt = open(arq, encoding="utf-8-sig").read()
    delim = ";" if txt.split("\n")[0].count(";") >= txt.split("\n")[0].count(",") else ","
    rows = list(csv.DictReader(txt.splitlines(), delimiter=delim))
    if not rows:
        sys.exit("CSV sem linhas de dados.")

    # artigos existentes (para validar)
    existentes = {}
    for f in glob.glob(os.path.join(RAIZ, "data", "leis", "*.js")):
        d = json.loads(open(f, encoding="utf-8").read()[len("DATA.leis.push("):-3])
        existentes[d["id"]] = {norm(a["n"]) for a in d["artigos"]}

    cont = defaultdict(set)   # (tipo, chave, modulo) -> {editais}
    avisos = set()
    for i, r in enumerate(rows, 2):
        tipo, mod = r["tipo"].strip().lower(), r["modulo"].strip().lower()
        ed, ref, item = r["edital"].strip(), r["ref"].strip(), r["item"].strip()
        if mod not in MODS or tipo not in ("lei", "sumula", "enunciado", "juris"):
            avisos.add(f"linha {i}: tipo/módulo inválido ({tipo}/{mod})"); continue
        if tipo == "lei":
            chave = (ref.lower(), norm(item))
            if ref.lower() in existentes and norm(item) not in existentes[ref.lower()]:
                avisos.add(f"linha {i}: art. {item} não existe na lei '{ref}'")
            elif ref.lower() not in existentes:
                avisos.add(f"linha {i}: lei '{ref}' não importada (data/leis) — heat será gravado mesmo assim")
        elif tipo == "sumula": chave = ("s", f"{ref}|{item}")
        elif tipo == "enunciado": chave = ("e", f"{ref}|{item}")
        else: chave = ("j", ref)
        cont[(tipo,) + chave + (mod,)].add(ed)

    heat = {"ilustrativo": False}
    x = {}
    for k, eds in cont.items():
        n = min(5, len(eds)); tipo, a, b, mod = k
        if tipo == "lei": heat.setdefault(a, {}).setdefault(b, {m: 0 for m in MODS})[mod] = n
        else: x.setdefault(f"{a}|{b}", {m: 0 for m in MODS})[mod] = n
    heat["x"] = x
    with open(os.path.join(RAIZ, "data", "heat.js"), "w", encoding="utf-8") as f:
        f.write("// GERADO por tools/gerar_heat.py a partir de dados/editais_analise.csv\nwindow.HEAT = "
                + json.dumps(heat, ensure_ascii=False, indent=1) + ";\n")
    eds_mod = defaultdict(set)
    for r in rows: eds_mod[r["modulo"].strip().lower()].add(r["edital"].strip())
    print(f"{len(cont)} itens contados; editais por módulo:", {m: len(v) for m, v in eds_mod.items()})
    for a in sorted(avisos): print("AVISO", a)

main()
