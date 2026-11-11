#!/usr/bin/env python3
"""Atualiza data/jur_stj_sumulas.js com o PDF 'VerbetesSTJ.pdf' (lista de súmulas do STJ, em ordem decrescente):
acrescenta as súmulas que faltam (ex.: 650 em diante), marca as CANCELADAS e guarda órgão e datas.
Uso: python tools/importar_verbetes_stj.py caminho/VerbetesSTJ.pdf
"""
import json, os, re, sys
import pypdf
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
arq = sys.argv[1]
t = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(arq).pages)
t = re.sub("[\uf000-\uf0ff\u25cf]", "*", t)
t = re.sub(r"scon\.stj\.jus\.br/SCON/sumstj/?\s*\d*", "", t)   # rodapé de cada página
partes = re.split(r"(?m)^\*?\s*S[ÚU]MULA\s+(\d+)\s*(\((?:S[ÚU]MULA )?CANCELADA\))?\s*VEJA MAIS\s*$", t)
novos = {}
for i in range(1, len(partes), 3):
    n, canc, corpo = partes[i], bool(partes[i + 1]), re.sub(r"\s+", " ", partes[i + 2]).strip()
    corpo = re.sub(r"scon\.stj\.jus\.br/SCON/sumstj/?\s*$", "", corpo).strip()
    obs = None
    if canc:
        m = re.search(r"S[ÚU]MULA CANCELADA:\s*(.*)$", corpo)
        if m: obs = "Súmula cancelada: " + m.group(1).strip(); corpo = corpo[:m.start()].strip()
    # (SÚMULA N, ÓRGÃO, julgado em dd/mm/aaaa, DJ ...)  ou  (ÓRGÃO, julgado em ..., DJe de ...)
    corpo = re.sub(r"\s*Enunciados das S[úu]mulas do STJ\s*$", "", corpo)
    m = re.search(r"\((?:S[ÚU]MULA\s+\d+,\s*)?([A-ZÇÃÕÉÊÍÓÚÂ ]+?),\s*(?:julgado em\s*(\d{1,2}/\d{1,2}/\d{4})[,;]?\s*)?([^)]*)\)\.?\s*$", corpo)
    if m and not (m.group(2) or re.search(r"DJ", m.group(3) or "")): m = None
    if m: texto, orgao, data, pub = corpo[:m.start()].strip(), m.group(1).title(), m.group(2), (m.group(3) or "").strip(" ,.")
    else: texto, orgao, data, pub = corpo, None, None, None
    novos[n] = {"texto": texto, "orgao": orgao, "data": data, "pub": pub, "cancelada": canc, "obs": obs}
dest = os.path.join(R, "data", "jur_stj_sumulas.js")
conteudo = open(dest, encoding="utf-8").read()
atual = json.loads(conteudo[conteudo.index("push(") + 5:].rstrip().rstrip(";").rstrip(")"))
por_n = {x["n"]: x for x in atual}
add = alt = canc = 0
for n, v in novos.items():
    x = por_n.get(n)
    if x is None:
        por_n[n] = x = {"tribunal": "STJ", "n": n, "texto": v["texto"], "vinculante": False, "materia": "", "orgao": v["orgao"], "data": v["data"]}; add += 1
    elif v["texto"] and re.sub(r"\W+", "", v["texto"].lower()) != re.sub(r"\W+", "", (x["texto"] or "").lower()):
        x["texto_anterior"] = x["texto"]; x["texto"] = v["texto"]; alt += 1
    if v["pub"]: x["pub"] = v["pub"]
    if v["orgao"] and not x.get("orgao"): x["orgao"] = v["orgao"]
    if v["data"] and not x.get("data"): x["data"] = v["data"]
    if v["cancelada"]: x["situacao"] = "Cancelada"; x["obs"] = v["obs"]; canc += 1
    elif "situacao" not in x: x["situacao"] = "Vigente"
res = sorted(por_n.values(), key=lambda x: int(x["n"]))
open(dest, "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(res, ensure_ascii=False) + ");\n")
print(f"{len(novos)} súmulas no PDF (de {max(map(int, novos))} a {min(map(int, novos))}); acrescentadas: {add}; texto diferente do anterior: {alt}; canceladas: {canc}; total agora: {len(res)}")
