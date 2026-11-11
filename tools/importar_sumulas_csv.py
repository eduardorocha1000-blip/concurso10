#!/usr/bin/env python3
"""Importa súmulas que você copiar de sites que bloqueiam robôs (TST, TSE, STM...) -> data/jur_<tribunal>.js
CSV UTF-8 com ';' e cabeçalho: tribunal;n;materia;texto     (ex.: TST;331;Terceirização;Contrato de prestação de serviços...)
Uso: python tools/importar_sumulas_csv.py dados/sumulas_tst.csv tst   (depois inclua <script src="data/jur_tst.js"> no index.html)
"""
import csv, json, os, sys
out = [{"tribunal": r["tribunal"].strip().upper(), "n": r["n"].strip(), "materia": (r.get("materia") or "Geral").strip(), "texto": " ".join(r["texto"].split()), "vinculante": False}
       for r in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig"), delimiter=";") if r.get("texto", "").strip()]
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", f"jur_{sys.argv[2]}.js")
open(dest, "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(out, ensure_ascii=False) + ");\n")
print(len(out), "súmulas ->", dest)
