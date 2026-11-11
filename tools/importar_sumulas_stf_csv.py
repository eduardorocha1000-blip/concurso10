#!/usr/bin/env python3
"""Importa súmulas do STF exportadas do portal de jurisprudência (CSV 'export_sumulas_*.csv') -> data/jur_stf_sumulas.js
Colunas: Título;Título URL;Enunciado;Órgão julgador;Data de aprovação;Fonte de Publicação;Situação;Ramo do direito;Observação
Uso: python tools/importar_sumulas_stf_csv.py arquivo1.csv [arquivo2.csv ...]   (une os arquivos; o último prevalece)
Guarda situação (Aprovada, Cancelada, Alterada, Superada), ramo do direito, órgão, data, publicação e observação.
"""
import csv, json, os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
por_n = {}
for arq in sys.argv[1:]:
    for r in csv.DictReader(open(arq, encoding="utf-8-sig"), delimiter=";"):
        m = re.match(r"S[úu]mula (Vinculante )?(\d+)\s*$", (r.get("Título") or "").strip())
        if not m or not (r.get("Enunciado") or "").strip(): continue
        sv = bool(m.group(1)); n = m.group(2)
        por_n[(sv, int(n))] = {"tribunal": "STF-SV" if sv else "STF", "n": n, "texto": " ".join(r["Enunciado"].split()), "vinculante": sv,
            "materia": (r.get("Ramo do direito") or "").strip(), "ramo": (r.get("Ramo do direito") or "").strip(), "orgao": (r.get("Órgão julgador") or "").strip() or None,
            "data": (r.get("Data de aprovação") or "").strip() or None, "pub": " ".join((r.get("Fonte de Publicação") or "").split()) or None,
            "situacao": {"Aprovada": "Vigente"}.get((r.get("Situação") or "").strip(), (r.get("Situação") or "").strip() or "Vigente"),
            "obs": " ".join((r.get("Observação") or "").split()) or None, "url": (r.get("Título URL") or "").strip() or None}
res = [v for k, v in sorted(por_n.items(), key=lambda kv: (kv[0][0], kv[0][1]))]
open(os.path.join(R, "data", "jur_stf_sumulas.js"), "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(res, ensure_ascii=False) + ");\n")
from collections import Counter
print(len(res), "súmulas do STF;", dict(Counter(x["situacao"] for x in res)), "| ramos:", len({x["ramo"] for x in res if x["ramo"]}))
