#!/usr/bin/env python3
"""Importa TODAS as súmulas do STJ a partir do PDF oficial (www.stj.jus.br/docs_internet/SumulasSTJ.pdf)
-> data/jur_stj_sumulas.js. Uso: python tools/importar_sumulas_stj.py [arquivo.pdf]
"""
import json, os, re, sys, tempfile, urllib.request
import pypdf
URL = "https://www.stj.jus.br/docs_internet/SumulasSTJ.pdf"
pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "SumulasSTJ.pdf")
if len(sys.argv) <= 1:
    open(pdf, "wb").write(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (estudo-pessoal)"}), timeout=300).read())
txt = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(pdf).pages)
parts = re.split(r"(?m)^S[úu]mula\s+(\d+)\s*$", txt)
def sentenca(t):
    if t.upper() != t: return t
    t = t.lower()
    return re.sub(r"(^|[.!?]\s+)([a-zà-ú])", lambda m: m.group(1) + m.group(2).upper(), t)
out = []
for i in range(1, len(parts), 2):
    n, b = parts[i], parts[i + 1]
    m = re.search(r"(?s)^\s*(.*?)\s*Enunciado\s*(.*?)\s*[ÓO]rg[ãa]o Julgador\s*(.*?)\s*Data da Decis[ãa]o\s*(\d{2}/\d{2}/\d{4})", b)
    if not m: continue
    materia, enun, orgao, data = (re.sub(r"\s+", " ", x).strip() for x in m.groups())
    out.append({"tribunal": "STJ", "n": n, "texto": sentenca(enun), "vinculante": False, "materia": re.sub(r" (Do|Da|De|Dos|Das|E|Em|No|Na|Ao|A|O) ", lambda m: m.group(0).lower(), materia.title().replace(" - ", " – ")), "orgao": orgao.title(), "data": data})
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "jur_stj_sumulas.js")
open(dest, "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(out, ensure_ascii=False) + ");\n")
print(len(out), "súmulas do STJ importadas de", (len(parts) - 1) // 2, "no PDF")
