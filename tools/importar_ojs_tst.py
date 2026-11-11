#!/usr/bin/env python3
"""Importa as Orientações Jurisprudenciais (OJ) do TST a partir da compilação 'Jurisprudência consolidada — TRT3 e TST'
(PDF do TRT-3, atualizado em 28/06/2024), 2ª parte (TST): Tribunal Pleno/Órgão Especial, SBDI-1, SBDI-1 Transitória, SBDI-2 e SDC.
Uso: python tools/importar_ojs_tst.py caminho/arquivo.pdf [pag_ini pag_fim]    (padrão: páginas 154 a 256)
Gera data/jur_tst_oj.js. Descarta as notas remissivas do TRT-3 e guarda enunciado, situação e histórico.
Se tiver as OJs direto do site do TST (PDF), o formato pode ser outro: ajuste o parser.
"""
import json, os, re, sys
from collections import Counter
import pypdf

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
arq = sys.argv[1]
ini = int(sys.argv[2]) if len(sys.argv) > 2 else 154
fim = int(sys.argv[3]) if len(sys.argv) > 3 else 256
ORGAOS = {"TP/OE": ("Tribunal Pleno/Órgão Especial", 1), "SDI1": ("SBDI-1", 2), "SDI1T": ("SBDI-1 Transitória", 3), "SDI2": ("SBDI-2", 4), "SDC": ("SDC", 5)}
SIGLAS = ["FGTS", "CF", "CLT", "INSS", "PIS", "ICMS", "TST", "CPC", "CC", "CP", "CPP", "SUS", "IPI", "IPTU", "ISS", "EC", "RFFSA", "ECT", "CEF", "BNDES", "INCRA", "ADCT", "UFIR", "CIPA", "MP", "RAIS", "IR", "IRPF", "CSLL", "CONAB", "APPA", "FUB", "URV", "TR", "SELIC", "TRCT", "DSR", "TRT", "SAT", "RAT", "FAP", "PCCS", "PLR"]

t = "\n".join((pypdf.PdfReader(arq).pages[i].extract_text() or "") for i in range(ini - 1, fim))
t = re.sub("[-●]", "", t)
RUIDO = re.compile(r"^\s*(ORIENTAÇÕES JURISPRUDENCIAIS [A-ZÇÃÕ\- 0-9ªI/]+TST|SUMÁRIO|\d{2,3}|ORIENTAÇÕES|JURISPRUDENCIAIS DA|JURISPRUDENCIAIS DO|SBDI-1|SBDI-1-TRANSITÓRIA|SBDI-2|SDC|TST|TRIBUNAL PLENO/ÓRGÃO ?ESPECIAL)\s*$", re.I)
t = "\n".join(l for l in t.split("\n") if not RUIDO.match(l))
partes = re.split(r"(?m)^\s*OJ-(SDI1T|SDI1|SDI2|SDC|TP/OE)-(\d+)\s+", t)

def limpa(s): return re.sub(r"\s+", " ", s or "").strip()

def sentenca(txt):
    txt = txt.strip(" .")
    if txt != txt.upper(): return txt[:1].upper() + txt[1:]   # (o 'º' conta como minúscula em str.isupper)
    txt = txt.lower()
    txt = re.sub(r"(^|[.:]\s+)([a-zà-ú])", lambda m: m.group(1) + m.group(2).upper(), txt)
    for sg in SIGLAS: txt = re.sub(r"\b" + re.escape(sg.lower()) + r"\b", sg, txt)
    return txt

DATA = re.compile(r"(?:Res\.\s*\d+/\d{4}\s*,\s*)?(?:DEJT\s+divulgado\s+em|DJe?\b|DEJT\b)[^(]{0,90}?\d{4}", re.S)
PAREN = re.compile(r"\((?:inserid[ao]|nova reda[çc][ãa]o|t[íi]tulo alterado|mantid[ao]|republicad[ao]|redação original)[^)]*\)", re.S | re.I)
EXT1 = re.compile(r"\s*[-–]\s*Republicad[ao][^(]{0,90}?\d{4}", re.S)
EXT2 = re.compile(r"\s*\((?:mantid[ao]|republicad[ao]|conforme|decisão)[^)]*\)", re.S)

PROC = re.compile("recurso|prazo|custas|execu|rescis[óo]ria|mandado de seguran|honor[áa]rios|compet[êe]ncia|nulidade|intima|cita[çc]|dep[óo]sito recursal|agravo|embargos|preclus|revelia|ônus da prova|penhora|precat[óo]rio|ju[ií]zo|processo", re.I)
itens = {}
for i in range(1, len(partes), 3):
    org, n, corpo = partes[i], int(partes[i + 1]), partes[i + 2]
    pre, _, pos = corpo.partition("Histórico:")
    hist = ""
    if pos:
        hl = []
        for l in pos.split("\n"):
            if not l.strip() and hl: break
            if re.match(r"^\s*\d+\.\s*[A-ZÀ-Ú]", l): break
            hl.append(l.strip())
        hist = limpa(" ".join(hl))
    pre = pre.strip()
    canc = bool(re.search(r"\(\s*cancelad", pre[:700], re.I))
    cab, enun = pre, ""
    pre = "\n".join(l for l in pre.split("\n") if not l.lstrip().startswith("•"))   # notas remissivas do TRT-3
    if not canc:
        m = DATA.search(pre[:500]); pm = PAREN.search(pre[:500])
        fim_cab = None
        if m and (not pm or m.start() >= pm.start()) and (not pm or m.start() - pm.end() < 40): fim_cab = m.end()
        elif pm: fim_cab = pm.end()
        if fim_cab is not None:
            for ext in (EXT1, EXT2, EXT2):
                e = ext.match(pre, fim_cab)
                if e: fim_cab = e.end()
            cab, enun = pre[:fim_cab], pre[fim_cab:]
    cab_l, enun_l = limpa(cab), limpa(enun)
    enun_l = re.sub(r"^[)\].,;:\-–\s]+", "", enun_l)
    paren = re.findall(r"\((?:[^()]|\([^)]*\))*\)", cab_l)
    assunto = re.sub(r"\s*\((?:[^()]|\([^)]*\))*\)", "", cab_l)
    assunto = limpa(re.split(r"\s*[-–]?\s*(?:Res\.|DJ|DEJT)", assunto)[0])
    assunto = re.sub(r"[\s(\[\-–]+$", "", assunto)
    sit_txt = limpa(" ".join(paren))
    texto = enun_l or sentenca(assunto)
    nome, base = ORGAOS[org]
    obs = " · ".join(x for x in (sit_txt, ("Histórico: " + hist) if hist else "") if x) or None
    itens[(base, n)] = {"tribunal": "TST-OJ", "n": f"{nome} nº {n}", "ord": base * 1000 + n, "texto": texto, "vinculante": False, "materia": sentenca(assunto), "ramo": ("Processual do Trabalho" if (org == "SDI2" or PROC.search(assunto)) else "Trabalhista"), "ramo_auto": True,
                        "orgao": f"TST — {nome}", "situacao": "Cancelada" if canc else "Vigente", "obs": obs, "so_titulo": (not enun_l) or None}
res = [itens[k] for k in sorted(itens)]
dest = os.path.join(R, "data", "jur_tst_oj.js")
open(dest, "w", encoding="utf-8").write("(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(res, ensure_ascii=False) + ");\n")
print(len(res), "OJs;", dict(Counter(x["orgao"] for x in res)), "| canceladas:", sum(x["situacao"] == "Cancelada" for x in res),
      "| vigentes sem enunciado:", sum(1 for x in res if x["situacao"] == "Vigente" and x.get("so_titulo")))
