#!/usr/bin/env python3
"""Converte dados/doutrina/segmentos.json (gerado por auditar_doutrina.py) em arquivos carregados sob demanda:
data/doutrina/index.js (lista) e data/doutrina/fNNN.js (texto). Duplicatas ficam marcadas, nada é apagado.
"""
import json, os, re
from statistics import median
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
segs = json.load(open(os.path.join(RAIZ, "dados", "doutrina", "segmentos.json"), encoding="utf-8"))
OUT = os.path.join(RAIZ, "data", "doutrina"); os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
ruido = re.compile(r"^(?:.*P[áa]gina\s+\d+\s*|.*Fasc[íi]culos?\s+[\d A-Za-z]+\s*\|\s*\d+\s*|COLE[ÇC][ÃA]O DE DOUTRINA.*|CONCURSOS P[ÚU]BLICOS.*P[áa]gina.*)$")
cab = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+\S.{2,100}$")
def blocos(texto):
    ls = [l.strip() for l in texto.split("\n")]
    ls = [l for l in ls if l and not ruido.match(l)]
    if not ls: return []
    med = median(len(l) for l in ls) or 80
    out, buf, ult = [], "", 999
    def flush():
        nonlocal buf
        if buf.strip(): out.append(["p", re.sub(r"\s+", " ", buf).strip()])
        buf = ""
    for l in ls:
        titulo = (cab.match(l) and len(l) < 110 and not l.rstrip().endswith((".", ";", ",")) ) or (l.isupper() and 6 < len(l) < 100)
        pontilha = l[:1] in "•▪●◦-–" or l[:1] == ""
        if titulo: flush(); out.append(["h", l]); continue
        if pontilha: flush(); buf = l.lstrip("•▪●◦-– ")
        elif buf and buf.rstrip()[-1:] in ".:;?!" and ult < 0.7 * med: flush(); buf = l
        else: buf += " " + l
        ult = len(l)
    flush(); return out
STOP = r"(?:Material|Prepara[çc][ãa]o|N[íi]vel|Edi[çc][ãa]o|Data editorial|Atualiza[çc][ãa]o|Organiza[çc][ãa]o|Como utilizar|Posicionamento|Recorte|Orienta[çc][ãa]o|OAB\s+Minist|Minist[ée]rio P[úu]blico\s+Magistratura|Ideia central|Introdu[çc][ãa]o|Objetivos|Fechamento|\d+ horas)"
SKIP = re.compile(r"(?i)^(DIREITO(?!.*[—–:])|CONCURSOS|VOLUME|FASC[ÍI]CULO|OAB|MINIST|MAGISTR|MATERIAL|PREPARA|N[ÍI]VEL|EDI[ÇC]|DATA |ATUALIZA|COLE[ÇC][ÃA]O|BRASIL|PROCESSO (CIVIL|PENAL)$|\d+ horas|\d+ dias|Teoria\s+Legisla|Introdu|Como utilizar|Posicionamento)")
def titulo_limpo(s):
    capa = [l.strip() for l in s["texto"][:1400].split(chr(10)) if l.strip() and not ruido.match(l.strip())]
    mnum = re.search(r"(?i)FASC[ÍI]CULOS?\s+(\d+(?:\s+A\s+\d+)?)", s["texto"][:1400])
    capa = [re.sub(r"(?i)^(VOLUME\s+[IVX]+\s*[—–-]?\s*)?FASC[ÍI]CULOS?\s+\d+\s*[—–-]*\s*", "", l) if re.match(r"(?i)^(VOLUME\s+[IVX]+\s*[—–-]?\s*)?FASC[ÍI]CULOS?\s+\d+\s*\S", l) else l for l in capa]
    cand = [l for l in capa if not SKIP.match(l) and len(l) > 6 and not re.match(r"(?i)^p[áa]gina", l)]
    # capa tem o título em 1-3 linhas MAIÚSCULAS; pega até 3 linhas seguidas
    tit = []
    for l in cand:
        if l.isupper() or (tit and len(tit) < 3 and len(" ".join(tit)) < 70): tit.append(l)
        if len(tit) >= 3 or (tit and not l.isupper()): break
    texto = " ".join(tit) if tit else (cand[0] if cand else " ".join(capa[:2]))
    texto = re.sub(r"(?i)\s*(OAB|MINIST[ÉE]RIO P[ÚU]BLICO|MAGISTRATURA).*$", "", texto).strip(" —–-|")
    texto = re.sub(r"(?i)^DIREITO (CIVIL|ADMINISTRATIVO|PENAL|PROCESSUAL CIVIL|PROCESSUAL PENAL|DO CONSUMIDOR|EMPRESARIAL|CONSTITUCIONAL)\s*(—\s*DIREITOS REAIS)?\s+(?=\S{3})", "", texto) if len(texto) > 25 else texto
    if len(texto) < 15 and capa: texto = " ".join(capa[:4])[:105]
    return (f"Fasc. {mnum.group(1)} — " if mnum else "") + texto[:105]
idx = []
for k, s in enumerate(segs):
    b = blocos(s["texto"])
    fid = f"f{k:03d}"
    open(os.path.join(OUT, fid + ".js"), "w", encoding="utf-8").write(f'(window.DOUT=window.DOUT||{{}})["{fid}"]=' + json.dumps(b, ensure_ascii=False) + ";\n")
    tt = titulo_limpo(s)
    if "CONCURSOS" in tt.upper() or len(tt.split("—")[-1].strip()) < 15:
        hs = [x[1] for x in b if x[0] == "h" and re.match(r"\d+\.", x[1]) and "SUM" not in x[1].upper()][:2]
        if hs: tt = tt.split("—")[0].strip() + " — " + " / ".join(hs)
    st = "unico" if "grupo" not in s else ("manter" if s["manter"] else "dup")
    idx.append({"id": fid, "disc": s["disciplina"], "titulo": tt[:130], "paginas": s["paginas"], "status": st,
                "grupo": s.get("grupo"), "parecidos": [f"f{x:03d}" for x in s.get("parecidos", [])], "origem": s["arquivo"].replace("ilovepdf_merged", "m") + " p." + str(s["pag_ini"])})
open(os.path.join(OUT, "index.js"), "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
print(len(idx), "fascículos;", sum(i["status"] == "dup" for i in idx), "marcados como possível duplicata;", sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) // 1024, "KB")
