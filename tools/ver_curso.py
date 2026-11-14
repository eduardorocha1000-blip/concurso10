#!/usr/bin/env python3
"""Imprime o texto extrativo de um tema do curso: python tools/ver_curso.py <slug> <parte do título> [máx. caracteres por parágrafo]"""
import glob, json, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
slug, parte = sys.argv[1], sys.argv[2].lower(); mx = int(sys.argv[3]) if len(sys.argv) > 3 else 520
for f in sorted(glob.glob(os.path.join(R, "dados", "curso", slug, "*.json"))):
    c = json.load(open(f, encoding="utf-8"))
    if parte in c["titulo"].lower():
        print("#", c["titulo"], os.path.basename(f))
        for s in c["secoes"]:
            print("##", s["t"][:70])
            for b in s["b"]: print(b[1][:mx])
