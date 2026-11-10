#!/usr/bin/env python3
"""Importa Súmulas Vinculantes (base 26) e Súmulas (base 30) do portal do STF -> data/jur_stf.js
Uso: python tools/importar_sumulas_stf.py
"""
import html, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp"
HDR = {"User-Agent": "Mozilla/5.0 (estudo-pessoal)"}

def get(url):
    for t in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=60).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(2)
    return ""

def txt(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", h))).strip()

def indice(base, rotulo):
    h = get(f"{BASE}?base={base}")
    itens = {}
    for href, t in re.findall(r'(?s)<a[^>]+href="([^"]*sumula=\d+[^"]*)"[^>]*>(.*?)</a>', h):
        m = re.match(rf"{rotulo} (\d+)", txt(t))
        if m: itens[int(m.group(1))] = href.replace("&amp;", "&")
    return itens

def item(args):
    base, n, href = args
    url = href if href.startswith("http") else "https://portal.stf.jus.br/jurisprudencia/" + href.lstrip("/")
    h = get(url)
    h = re.sub(r"(?is)<(script|style).*?</\1>", "", h)
    ps = [txt(p) for p in re.findall(r"(?s)<p[^>]*>(.*?)</p>", h)]
    ps = [p for p in ps if len(p) > 20 and not p.startswith(("Peticione", "Praça", "Veja a localiza", "E-mail", "Telefone", "Fax", "Confirmação", "Horário", "A pesquisa no banco", "●", "Data de", "Para informa", "Ver ", "Veja "))]
    if not ps: return None
    pub = ""
    return {"tribunal": "STF-SV" if base == 26 else "STF", "n": str(n), "texto": ps[0], "vinculante": base == 26, "pub": pub}

def main():
    tarefas = []
    for base, rot in ((26, "Súmula Vinculante"), (30, "Súmula")):
        idx = indice(base, rot); print(rot, len(idx), "itens no índice")
        tarefas += [(base, n, h) for n, h in sorted(idx.items())]
    with ThreadPoolExecutor(6) as ex: res = [r for r in ex.map(item, tarefas) if r]
    print(len(res), "súmulas extraídas de", len(tarefas))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "jur_stf.js")
    open(out, "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(res, ensure_ascii=False) + ");\n")

main()
