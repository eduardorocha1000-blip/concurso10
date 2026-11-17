"""Le dados/curso/mapas/<id>.py (variavel ARV) e grava data/doutrina/mapas/<id>.svg.  Uso: python tools/gerar_mapas_premium.py [id ...]"""
import sys, os, glob, shutil, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
from mapa_premium import svg_premium, numerar, N, T
base = os.path.join(os.path.dirname(__file__), "..")
src, dst, bk = (os.path.join(base, p) for p in ("dados/curso/mapas", "data/doutrina/mapas", "dados/curso/mapas/orig"))
os.makedirs(bk, exist_ok=True)
ids = sys.argv[1:] or [os.path.basename(f)[:-3] for f in sorted(glob.glob(src + "/*.py"))]
for i in ids:
    sp = importlib.util.spec_from_file_location("m_" + i, f"{src}/{i}.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    out = f"{dst}/{i}.svg"
    if os.path.exists(out) and not os.path.exists(f"{bk}/{i}.svg"): shutil.copy(out, f"{bk}/{i}.svg")
    s = svg_premium(numerar(m.ARV)); open(out, "w", encoding="utf-8").write(s); print(i, len(s) // 1024, "KB")
