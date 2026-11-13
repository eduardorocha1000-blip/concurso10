#!/usr/bin/env python3
"""Baixa do Portal de Dados Abertos do STJ (dadosabertos.web.stj.jus.br) os temas repetitivos (precedentes qualificados)
e os espelhos de acórdãos (todos os órgãos). Guarda em dados/verificacao/stj/ (ignorado pelo git; é cache grande).
Uso: python tools/baixar_stj_dados_abertos.py"""
import json, os, urllib.request, zipfile
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(R, "dados", "verificacao", "stj"); os.makedirs(D, exist_ok=True)
API = "https://dadosabertos.web.stj.jus.br/api/3/action/"
def get(url, n=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=n).read()
pks = ["precedentes-qualificados"] + [p for p in json.loads(get(API + "package_list"))["result"] if p.startswith("espelhos-de-acordaos-")]
for pk in pks:
    d = json.loads(get(API + "package_show?id=" + pk))["result"]
    pasta = os.path.join(D, pk); os.makedirs(pasta, exist_ok=True)
    for r in d["resources"]:
        nome = r["name"]; destino = os.path.join(pasta, nome)
        if not nome.lower().endswith((".json", ".zip", ".csv")) or os.path.exists(destino): continue
        try:
            open(destino, "wb").write(get(r["url"], 600))
            if nome.endswith(".zip"):
                with zipfile.ZipFile(destino) as z: z.extractall(pasta)
                os.remove(destino); open(destino + ".ok", "w").write("extraido")
        except Exception as e: print("falha", pk, nome, str(e)[:80])
    print("ok", pk, flush=True)
