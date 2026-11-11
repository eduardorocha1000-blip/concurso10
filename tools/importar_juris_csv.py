#!/usr/bin/env python3
"""Importa jurisprudência colada/exportada por você (ex.: ementas/teses do TJSC, TRF4) -> data/jur_<fonte>.js
CSV UTF-8 com ';' e cabeçalho: tribunal;ref;materia;tese   (ex.: TJSC;Apelação 5001234-56.2024.8.24.0023 (3ª Câm. Dir. Civil, 2025);Civil (Família);Ementa/tese...)
Uso: python tools/importar_juris_csv.py dados/juris_tjsc.csv tjsc
"""
import csv, json, os, sys
src, nome = sys.argv[1], sys.argv[2]
out = []
for r in csv.DictReader(open(src, encoding="utf-8-sig"), delimiter=";"):
    if r.get("tese", "").strip():
        out.append({"tribunal": r["tribunal"].strip(), "ref": r["ref"].strip(), "materia": r.get("materia", "Geral").strip() or "Geral",
                    "tese": " ".join(r["tese"].split()), "mods": ["oab", "magsc", "mpsc", "magfed"]})
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", f"jur_{nome}.js")
open(dest, "w", encoding="utf-8").write("DATA.juris.push(...(" + json.dumps(out, ensure_ascii=False) + "));\n")
print(len(out), "itens ->", dest, "(adicione <script src=\"data/jur_%s.js\"> no index.html se for novo)" % nome)
