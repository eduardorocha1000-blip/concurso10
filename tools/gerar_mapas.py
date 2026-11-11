#!/usr/bin/env python3
"""Converte os mapas mentais de data/estudo.js em imagens SVG (data/mapas/*.svg) e grava data/mapas_img.js.
Requer node (para ler estudo.js). Uso: python tools/gerar_mapas.py"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
js = "global.window={DATA:{mapas:[],fluxos:[],exemplos:[],cards:[],questoes:[],discursivas:[],orais:[],principios:[],doutrina:[],leis:[],sumulas:[],juris:[],enunciados:[],modulos:[]}};global.DATA=window.DATA;require('./data/estudo.js');console.log(JSON.stringify(DATA.mapas))"
mapas = json.loads(subprocess.run(["node", "-e", js], cwd=R, capture_output=True, text=True, encoding="utf-8").stdout)
os.makedirs(os.path.join(R, "data", "mapas"), exist_ok=True); idx = {}
for i, m in enumerate(mapas):
    f = f"data/mapas/m{i}.svg"; open(os.path.join(R, f), "w", encoding="utf-8").write(svg_mapa(m["titulo"], m["arvore"])); idx[m["titulo"]] = f
open(os.path.join(R, "data", "mapas_img.js"), "w", encoding="utf-8").write("window.MAPAS_IMG = " + json.dumps(idx, ensure_ascii=False) + ";\n")
print(len(idx), "mapas mentais em imagem")
