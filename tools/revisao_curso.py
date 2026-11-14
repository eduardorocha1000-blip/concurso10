#!/usr/bin/env python3
"""Gera dados/curso/REVISAO.md: por capítulo do curso, quantos pontos «segundo o curso», quais súmulas/ADIs/decretos dependem de conferência e o status da conferência automática. Uso: python tools/revisao_curso.py"""
import glob, json, os, re, subprocess, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def texto(c):
    out=[]
    for s in c.get("secoes",[]):
        out.append(s["t"])
        for b in s["b"]: out.append(b[1])
    for k in c.get("casos",[]): out += [k.get("e",""), k.get("s","")]
    for o in c.get("obj",[]): out += [o.get("e",""), o.get("c","")]
    for d in c.get("disc",[]): out += [d.get("e",""), d.get("s","")]
    return "\n".join(out)
rx = re.compile(r"(Súmulas?(?: Vinculantes?)? \d+[^,;.)]{0,25}|ADIs? [\d.]+|ADC \d+|OJ \d+[^,;.)]{0,20}|Decreto \d[\d.]*/\d+|Resolução [\d.]+/\d+|LC \d+/\d+|Lei [\d.]+/\d+)")
rows=[]
for f in sorted(glob.glob(os.path.join(R,"dados","curso","*","*.json"))):
    pasta=os.path.basename(os.path.dirname(f))
    if pasta.endswith("_resumos") or pasta=="adm": grupo="Administrativo"
    else: grupo=pasta
    try: c=json.load(open(f,encoding="utf-8"))
    except Exception: continue
    t=texto(c); n=len(re.findall(r"segundo o curso",t,re.I))
    cit=sorted({m.group(1).strip() for m in rx.finditer(t)})
    rows.append((grupo,c.get("titulo","")[:80],n,cit))
md=["# Revisão dos capítulos do curso\n","Gerado por tools/revisao_curso.py. «Segundo o curso» = ponto que veio da aula e não do texto de lei do app.\n"]
atual=None
for g,t,n,cit in sorted(rows):
    if g!=atual: md.append("\n## "+g.upper()+"\n"); atual=g
    md.append(f"- **{t}** — {n} pontos «segundo o curso»")
    if cit: md.append("  - citar/conferir: "+"; ".join(cit[:25]))
open(os.path.join(R,"dados","curso","REVISAO.md"),"w",encoding="utf-8").write("\n".join(md)+"\n")
print(len(rows),"capítulos →",os.path.join("dados","curso","REVISAO.md"))
