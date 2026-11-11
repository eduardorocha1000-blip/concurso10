#!/usr/bin/env python3
"""Audita PDFs de doutrina: separa os fascículos (reinício da numeração de página), mede a semelhança de
CONTEÚDO (TF-IDF) e de TEXTO COPIADO (trechos de 8 palavras) entre eles, e agrupa os que cobrem o mesmo tema.
Uso: python tools/auditar_doutrina.py [pdfs ou pastas...]  ->  dados/doutrina/auditoria.md + segmentos.json
"""
import glob, hashlib, json, math, os, re, sys
from collections import Counter
import pypdf
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SAIDA = os.path.join(RAIZ, "dados", "doutrina"); os.makedirs(SAIDA, exist_ok=True)
args = sys.argv[1:] or [r"C:/Users/cliente/Downloads/ilovepdf_merged*.pdf"]
arqs = sorted(set(f for a in args for f in (glob.glob(os.path.join(a, "*.pdf")) if os.path.isdir(a) else glob.glob(a))))
norm = lambda s: re.sub(r"\s+", " ", s).strip()
STOP = set("para como mais pela pelo pelas pelos entre sobre quando onde também deve devem pode podem será serão apenas ainda sendo essa esse essas esses isso aquele cada outro outra outros outras seus suas desta deste dessa desse nesta neste dele dela são foi era ser tem têm não uma uns umas com por que dos das nos nas aos ao em de da do a o e os as um ou se sua seu há".split())

def pagina(t):
    m = re.search(r"P[áa]gina\s+(\d+)", t[:350]) or re.search(r"Fasc[íi]culos?\s+[\d A-Za-z]+?\s*\|\s*(\d+)", t[:350])
    return int(m.group(1)) if m else None

segs = []
for f in arqs:
    pgs = [(p.extract_text() or "") for p in pypdf.PdfReader(f).pages]
    ks = [pagina(t) for t in pgs]; cur = None
    for i, t in enumerate(pgs):
        nxt = ks[i + 1] if i + 1 < len(ks) else None
        if i == 0 or ks[i] == 1 or (ks[i] is not None and ks[i - 1] is not None and ks[i] < ks[i - 1]) or (ks[i] is None and nxt == 2):
            cur = {"arquivo": os.path.basename(f), "pag_ini": i + 1, "paginas": 0, "texto": ""}; segs.append(cur)
        cur["paginas"] += 1; cur["texto"] += "\n" + t

def titulo(t):
    t = norm(t[:1200])
    m = re.search(r"(?i)(?:VOLUME\s+[IVX\d]+\s*[—–-]?\s*[^F]{0,40})?FASC[ÍI]CULOS?\s+(\d+(?:\s+A\s+\d+)?)\s*(?:\|\s*\d+)?\s*[—–-]*\s*(.{0,170}?)(?:\s(?:Material|Prepara|N[íi]vel|Edi[çc]|Data|Introdu|Como utilizar|Posicionamento|Ideia central|Recorte|Orienta|Atualiza|Organiza|Preparação)\b|$)", t)
    if not m: return t[:110]
    return f"Fasc. {m.group(1)} — {re.sub(r'^(?i:p[áa]gina 1)\s*', '', m.group(2)).strip()}"
def disciplina(t):
    t = t[:900].upper(); achados = []
    for d in ("DIREITO ADMINISTRATIVO", "DIREITO CIVIL", "DIREITO DO CONSUMIDOR", "DIREITO EMPRESARIAL", "DIREITO PENAL", "PROCESSUAL CIVIL", "PROCESSO CIVIL", "PROCESSUAL PENAL", "PROCESSO PENAL", "CONSTITUCIONAL", "ELEITORAL"):
        if d in t: achados.append((t.index(d), d))
    if not achados: return "OUTRA"
    d = min(achados)[1]
    return {"PROCESSO CIVIL": "DIREITO PROCESSUAL CIVIL", "PROCESSUAL CIVIL": "DIREITO PROCESSUAL CIVIL", "PROCESSO PENAL": "DIREITO PROCESSUAL PENAL", "PROCESSUAL PENAL": "DIREITO PROCESSUAL PENAL"}.get(d, d)

for s in segs:
    s["titulo"] = titulo(s["texto"]); s["disciplina"] = disciplina(s["texto"]); s["chars"] = len(s["texto"])
    corpo = re.sub(r"(?im)^.*(?:P[áa]gina \d+|Fasc[íi]culo \d+\s*\|).*$", "", s["texto"])
    w = re.findall(r"\w+", corpo.lower())
    s["tf"] = Counter(x for x in w if len(x) > 3 and x not in STOP)
    s["sh"] = set(hashlib.md5(" ".join(w[k:k + 8]).encode()).hexdigest()[:10] for k in range(max(0, len(w) - 8)))
df = Counter(); [df.update(s["tf"].keys()) for s in segs]
N = len(segs)
for s in segs:
    v = {t: (1 + math.log(c)) * math.log(N / df[t]) for t, c in s["tf"].items() if df[t] < N * 0.5}
    s["v"] = v; s["n"] = math.sqrt(sum(x * x for x in v.values())) or 1
def cos(a, b):
    if len(a["v"]) > len(b["v"]): a, b = b, a
    return sum(x * b["v"].get(t, 0) for t, x in a["v"].items()) / (a["n"] * b["n"])
pares = []
for i in range(N):
    for j in range(i + 1, N):
        c = cos(segs[i], segs[j])
        if c >= 0.30:
            sh = len(segs[i]["sh"] & segs[j]["sh"]) / max(1, min(len(segs[i]["sh"]), len(segs[j]["sh"])))
            pares.append((c, sh, i, j))
pares.sort(reverse=True)
# grupos de mesmo tema (cos >= 0.45)
pai = list(range(N))
def f(x):
    while pai[x] != x: pai[x] = pai[pai[x]]; x = pai[x]
    return x
for c, sh, i, j in pares:
    if c >= 0.45: pai[f(i)] = f(j)
grupos = {}
for i in range(N): grupos.setdefault(f(i), []).append(i)
rep = [g for g in grupos.values() if len(g) > 1]

for gi, g in enumerate(rep):
    mk = max(g, key=lambda k: segs[k]["chars"])
    for k in g: segs[k]["grupo"] = gi; segs[k]["manter"] = (k == mk); segs[k]["parecidos"] = [x for x in g if x != k]
L = ["# Auditoria de doutrina", "", f"{len(arqs)} PDFs → **{N} fascículos/blocos** identificados ({sum(s['paginas'] for s in segs)} páginas).", "",
     "Como ler: *semelhança de tema* (TF-IDF, 0–100%) mede se dois fascículos falam das mesmas coisas, mesmo com palavras diferentes; *texto copiado* mede trechos idênticos de 8 palavras. Tema ≥45% = **mesmo assunto** (estude só um); 30–45% = **sobreposição parcial**.", "",
     "## 1. Grupos que cobrem o mesmo assunto", ""]
if not rep: L.append("Nenhum grupo encontrado.")
for g in sorted(rep, key=lambda g: -len(g)):
    manter = max(g, key=lambda k: segs[k]["chars"])
    L.append(f"### {segs[g[0]]['disciplina']} — {len(g)} fascículos")
    L += ["", "| # | Arquivo (pág.) | Páginas | Título | Sugestão |", "|---|---|---|---|---|"]
    for k in g: L.append(f"| {k} | {segs[k]['arquivo'].replace('ilovepdf_merged','m')} (p.{segs[k]['pag_ini']}) | {segs[k]['paginas']} | {segs[k]['titulo'][:90]} | {'**manter (mais completo)**' if k == manter else 'revisar / possível duplicata'} |")
    L.append("")
L += ["## 2. Pares mais parecidos", "", "| A | B | Tema | Texto copiado |", "|---|---|---|---|"]
for c, sh, i, j in pares[:60]: L.append(f"| {i}: {segs[i]['titulo'][:55]} | {j}: {segs[j]['titulo'][:55]} | {c:.0%} | {sh:.0%} |")
nums = {}
for k, s in enumerate(segs):
    m = re.match(r"Fasc\. (\d+) ", s["titulo"])
    if m: nums.setdefault((s["disciplina"], m.group(1)), []).append(k)
L += ["", "## 3. Mesma disciplina e mesmo número de fascículo com assuntos diferentes (numeração conflitante)", ""]
for (d, n), ks in sorted(nums.items(), key=lambda x: (x[0][0], int(x[0][1]))):
    if len(ks) > 1: L.append(f"- {d} · Fasc. {n}: " + " | ".join(f"[{k}] {segs[k]['titulo'].split('—',1)[-1].strip()[:50]}" for k in ks))
L += ["", "## 4. Índice por disciplina", ""]
for d in sorted({s["disciplina"] for s in segs}):
    L += [f"### {d}", ""] + [f"- [{k}] {segs[k]['titulo'][:100]} ({segs[k]['paginas']} p.)" for k, s in enumerate(segs) if s["disciplina"] == d] + [""]
open(os.path.join(SAIDA, "auditoria.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
json.dump([{k: v for k, v in s.items() if k not in ("sh", "tf", "v", "n")} for s in segs], open(os.path.join(SAIDA, "segmentos.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(N, "segmentos;", len(rep), "grupos de mesmo tema;", len(pares), "pares >=30%")
