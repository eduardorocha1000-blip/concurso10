#!/usr/bin/env python3
"""Extrai o CONTEÚDO PROGRAMÁTICO de editais em PDF (já baixados) -> data/editais.js
Uso: python tools/editais_extrair.py <pasta com os PDFs e os .txt extraídos>
Cada edital é descrito em EDITAIS (id, grupo, órgão, banca, link oficial, arquivo). O texto do programa é copiado do edital, sem resumir.
"""
import json, os, re, sys, unicodedata
import pypdf

PASTA = sys.argv[1] if len(sys.argv) > 1 else "."
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FGV = "https://conhecimento.fgv.br/sites/default/files/concursos/"
# modo: 'anexo1' (blocos/numeração por linha), 'inline' (DISCIPLINA : 1. ... 2. ...), 'oab2'
EDITAIS = [
 dict(id="tjsc-2026", grupo="magsc", nome="Edital nº 33/2026 — Juiz Substituto do TJSC", orgao="Tribunal de Justiça de Santa Catarina", ano=2026, arq="tjsc33", modo="anexo1", fonte=FGV + "edital-n-33-2026-edital-de-abertura.pdf", oficial=True),
 dict(id="tjsc-2024", grupo="magsc", nome="Edital nº 44/2024 — Juiz Substituto do TJSC", orgao="Tribunal de Justiça de Santa Catarina", ano=2024, arq="tjsc44_2024", modo="anexo1", fonte=FGV + "edital-n.-44-2024-abertura-concurso-magistratura.pdf", oficial=True),
 dict(id="mpsc-45", grupo="mpsc", nome="45º Concurso — Promotor de Justiça Substituto do MPSC (Edital de 05/12/2025)", orgao="Ministério Público de Santa Catarina", ano=2025, arq="mpsc45", modo="inline", ini=r"I\s*-\s*CONHECIMENTOS GERAIS DA L[ÍI]NGUA PORTUGUESA", fim=None, fonte="https://www.mpsc.mp.br/concurso-promotor-de-justica", oficial=True, nota="PDF consultado: cópia hospedada em arquivos.qconcursos.com; a página oficial do certame é a indicada no link."),
 dict(id="mpsc-2023-2", grupo="mpsc", nome="Edital de Concurso nº 2/2023/PGJ — Promotor de Justiça Substituto do MPSC", orgao="Ministério Público de Santa Catarina", ano=2023, arq="mpsc44", modo="inline", ini=r"(?m)^\s*14\s+DO PROGRAMA", fim=r"(?m)^\s*15\s+[A-ZÁ-Ú]{2,}", fonte="https://www.mpsc.mp.br/documents/d/guest/edital-mpsc-44-concurso-", oficial=True),
 dict(id="mpsc-2023-1", grupo="mpsc", nome="Edital de Concurso nº 001/2023/PGJ — Promotor de Justiça Substituto do MPSC", orgao="Ministério Público de Santa Catarina", ano=2023, arq="mpsc43", modo="inline", ini=r"(?m)^\s*14\s+DO PROGRAMA", fim=r"(?m)^\s*15\s+[A-ZÁ-Ú]{2,}", fonte="https://www.mpsc.mp.br/documents/d/guest/edital-n-001-2023-pgj", oficial=True),
 dict(id="mpsc-2020", grupo="mpsc", nome="Edital de Concurso nº 001/2020/PGJ — Promotor de Justiça Substituto do MPSC", orgao="Ministério Público de Santa Catarina", ano=2020, arq="mpsc2020", modo="inline", ini=r"(?m)^\s*14\s+DO PROGRAMA", fim=r"(?m)^\s*15\s+[A-ZÁ-Ú]{2,}", fonte="https://www.mpsc.mp.br/documents/d/guest/edital-de-concurso-n-001-2020-pgj", oficial=True),
 dict(id="trf5-xvi", grupo="magfed", nome="XVI Concurso — Juiz Federal Substituto do TRF da 5ª Região (Edital nº 01/2026)", orgao="TRF da 5ª Região", ano=2026, arq="trf5_16", modo="anexo1", fonte=FGV + "edital-01-de-2026-xvi-concurso-juiz-federal-retificado-em-01.09.26.pdf", oficial=True),
 dict(id="trf2-xix", grupo="magfed", nome="XIX Concurso — Juiz Federal Substituto do TRF da 2ª Região (Edital TRF2 nº 154/2025, retificado)", orgao="TRF da 2ª Região", ano=2025, arq="trf2_19", modo="anexo1", fonte="https://static.trf2.jus.br/nas-internet/documento/consultas/concursos/magistrados/19/SEI_1438979_Edital_154_Retificado.pdf", oficial=True),
 dict(id="trf6-i", grupo="magfed", nome="I Concurso — Juiz Federal Substituto do TRF da 6ª Região (Edital nº 1, de 22/08/2025)", orgao="TRF da 6ª Região", ano=2025, arq="trf6", modo="anexo1", fonte=FGV + "trf6-edital-de-abertura_0.pdf", oficial=True),
 dict(id="trf1-xviii", grupo="magfed", nome="XVIII Concurso — Juiz Federal Substituto do TRF da 1ª Região (Edital nº 01/2025)", orgao="TRF da 1ª Região", ano=2025, arq="trf1", modo="anexo1", fonte=FGV + "trf1-edital-de-abertura.pdf", oficial=True),
 dict(id="enam-2026-2", grupo="enam", nome="6º ENAM — 2026.2 (Edital publicado no DOU de 24/08/2026)", orgao="ENFAM / FGV", ano=2026, arq="enam", modo="anexo1", fonte="https://conhecimento.fgv.br/exames/enam", oficial=True, nota="PDF consultado: cópia do DOU hospedada em cj.estrategia.com; a página oficial é a indicada no link."),
 dict(id="enam-2026-1", grupo="enam", nome="5º ENAM — 2026.1 (Edital nº 1/2026)", orgao="ENFAM / FGV", ano=2026, arq="enam2026_1", modo="anexo1", fonte="https://conhecimento.fgv.br/exames/enam/5exame", oficial=True, nota="PDF consultado: cópia hospedada em arquivos.qconcursos.com; a página oficial é a indicada no link."),
 dict(id="oab-47", grupo="oab", nome="47º Exame de Ordem Unificado — Edital de Abertura (2026)", orgao="OAB / FGV", ano=2026, arq="oab47", modo="oab", fonte="https://oab.fgv.br", oficial=True, nota="PDF consultado: cópia hospedada em arquivos.qconcursos.com."),
 dict(id="oab-46", grupo="oab", nome="46º Exame de Ordem Unificado — Edital de Abertura (2026)", orgao="OAB / FGV", ano=2026, arq="oab46", modo="oab", fonte="https://oab.fgv.br", oficial=True, nota="PDF consultado: cópia hospedada em arquivos.qconcursos.com."),
]

RUIDO = re.compile(r"(?i)^(?:.*\|\s*CONCURSO P[ÚU]BLICO\s*20\d\d.*|TRIBUNAL (?:REGIONAL FEDERAL|DE JUSTI[ÇC]A).*|Edital \d+ \(\d+\).*|P[áa]gina \d+( de \d+)?|PARA TODAS AS ETAPAS.*|Aqui voc[êe] encontra.*|SUA JORNADA.*|CONSELHO FEDERAL DA ORDEM.*|\d+º EXAME DE ORDEM.*|EDITAL DE ABERTURA|\d{1,3}|EDITAL N[º°.\s]*\d+.*|DI[ÁA]RIO OFICIAL DA UNI[ÃA]O.*|Este conte[úu]do n[ãa]o substitui.*|Publicado em:.*)$")
def sa(t): return unicodedata.normalize("NFD", t).encode("ascii", "ignore").decode()

def carregar(arq):
    t = open(os.path.join(PASTA, arq + ".txt"), encoding="utf-8").read() if os.path.exists(os.path.join(PASTA, arq + ".txt")) else "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(os.path.join(PASTA, arq + ".pdf")).pages)
    return re.sub("[-]", "", t).replace("ﬁ", "fi").replace("ﬂ", "fl").replace("­", "")

def linhas_limpas(txt):
    out = []
    for l in txt.split("\n"):
        l = l.strip()
        if not l or RUIDO.match(l): continue
        out.append(l)
    return out

HEAD = re.compile(r"^(?:[IVXL]+\s*[.\-–]\s*)?(?:[A-Z]\)\s*)?([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,\-–/()ºª.]{5,100})$")
def titulo_disc(nome):
    nome = re.sub(r"^(?:[IVXL]+\s*[.\-–]\s*)?(?:[A-Z]\)\s*)?", "", nome.strip())
    n = nome.title()
    for a, b in ((" E ", " e "), (" Do ", " do "), (" Da ", " da "), (" De ", " de "), (" Dos ", " dos "), (" Das ", " das "), (" Ao ", " ao "), (" Em ", " em ")): n = n.replace(a, b)
    return n

def parse_anexo1(txt):
    discs, nota, bloco, cur = [], [], None, None
    for l in linhas_limpas(txt):
        if re.match(r"^BLOCO\s+[IVX\d]+", l): bloco = l.title(); cur = None; continue
        m = HEAD.match(l)
        if m and not re.match(r"^\d", l) and not l.endswith((".", ";", ",")):
            nome = m.group(1).strip()
            if len(nome) >= 6 and not re.search(r"(ANEXO|EDITAL|CARGO)", nome):
                cur = {"disc": titulo_disc(nome), "bloco": bloco, "corpo": []}; discs.append(cur); continue
        if cur is not None: cur["corpo"].append(l)
        else: nota.append(l)
    out = []
    for d in discs:
        pts = pontos_inline(" ".join(d["corpo"]))
        if pts and not re.match(r"(?i)^Bloco\s", d["disc"]): out.append({"disc": d["disc"], "bloco": d["bloco"], "pontos": pts})
    return out, " ".join(nota)[:700]

def pontos_inline(corpo):
    """Divide 'texto 1. a 2. b 3. c' em pontos, exigindo numeração sequencial (evita falsos cortes).
    Aceita '2. Texto', '2 Texto' e '1 . Texto'; a série pode começar em N>1 (continuação do quadro anterior)."""
    corpo = re.sub(r"\s+", " ", corpo).strip()
    corpo = re.sub(r"^(?:\([^)]{3,120}\)\s*)+", "", corpo)          # remove '(incluído pela Resolução ...)' no começo
    m0 = re.match(r"^(\d{1,2})\s?\.?\s+(?=\S)", corpo)
    if not m0: return [corpo] if corpo else []
    n = int(m0.group(1)); achou = [0]
    while True:
        pad = re.compile(r"(?:(?<=[\s.;:)])|^)%d\s?\.?\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9\"“(])" % (n + 1))
        m = pad.search(corpo, achou[-1] + 3)
        if not m: break
        achou.append(m.start()); n += 1
    achou.append(len(corpo))
    return [corpo[a:b].strip() for a, b in zip(achou, achou[1:]) if corpo[a:b].strip()]

HINL = re.compile(r"(?:(?<=\s)|^)(?:\d+\.\d+\s+|[IVXL]+\s*[-–]\s*)?([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç ,/()ºª\-]{4,90}?)\s*:\s+(?=1\s?\.?\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
def parse_inline(txt):
    t = re.sub(r"\s+", " ", " ".join(linhas_limpas(txt)))
    ms = list(HINL.finditer(t)); out = []
    for i, m in enumerate(ms):
        nome = m.group(1).strip()
        if nome.islower() or len(nome) < 6: continue
        corpo = t[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(t)]
        out.append({"disc": titulo_disc(re.sub(r"^[IVXL]+\s*[-–]\s*", "", nome)), "bloco": None, "pontos": pontos_inline(corpo)})
    return out

def parse_oab(t):
    a = [m.start() for m in re.finditer(r"ANEXO II\s*[–-]\s*CONTE[ÚU]DO PROGRAM[ÁA]TICO DA PROVA", t)][-1]
    b = re.search(r"ANEXO III\s*[–-]", t[a:])
    sec = t[a: a + b.start()] if b else t[a:]
    linhas = linhas_limpas(sec)[1:]
    # áreas: linhas em maiúsculas (ex.: DIREITO ADMINISTRATIVO) seguidas de 1. ...
    out, disc, buf = [], None, []
    def fecha():
        if disc is not None and buf: disc["pontos"] = pontos_inline(" ".join(buf))
    for l in linhas:
        if re.match(r"^DIREITO [A-ZÁÉÍÓÚÂÊÔÃÕÇ ]{3,60}$", l) or re.match(r"^(ESTATUTO DA ADVOCACIA.*|[ÉE]TICA PROFISSIONAL.*)$", l):
            fecha(); buf.clear(); disc = {"disc": l.title().replace(" E ", " e ").replace(" Do ", " do ").replace(" Da ", " da "), "bloco": None, "pontos": []}; out.append(disc)
        elif disc is not None: buf.append(l)
    fecha()
    return [d for d in out if d["pontos"]]

def recortar(t, ed):
    m = ed["modo"]
    if m == "oab":
        a = re.search(r"(?m)^\s*DIREITO ADMINISTRATIVO\s*:", t)
        b = re.search(r"(?m)^\s*(ANEXO III|MATERIAL/PROCEDIMENTOS|MATERIAIS? PERMITIDOS?)", t[a.end():]) if a else None
        return t[a.start(): a.end() + b.start()] if a and b else ""
    if m == "anexo1":
        a = re.search(r"(?m)^\s*ANEXO I\s*[–-]\s*CONTE[ÚU]DO PROGRAM[ÁA]TICO", t)
        b = re.search(r"(?m)^\s*ANEXO II\s*[–-]", t[a.end():]) if a else None
        return t[a.start(): a.end() + b.start()] if a and b else (t[a.start():] if a else "")
    if m == "inline":
        a = re.search(ed["ini"], t)
        if not a: return ""
        fim = re.search(ed["fim"], t[a.end():]) if ed.get("fim") else None
        return t[a.start(): a.end() + fim.start()] if fim else t[a.start():]
    return t

RUIDO_Q = re.compile(RUIDO.pattern.replace("|\d{1,3}|", "|"), re.I)
def quadro(t):
    """Quadro oficial de distribuição das questões da prova objetiva (copiado do edital)."""
    m = re.search(r"(?i)(o quadro a seguir[^\n]*|conforme quadro a seguir:|distribu[ií]das da seguinte\s+forma:|PROVA/TIPO\s+DISCIPLINAS[^\n]*)", t)
    if not m: return None
    resto = t[m.start(): m.start() + 4000]
    fim = re.search(r"TOTAL\s+\d+|(?m:^\s*11\.2\s*-)|(?m:^\s*5\.2\s+A fase)|(?m:^\s*5\.[2-9]\s)", resto[40:])
    corpo = resto[: 40 + (fim.end() if fim and fim.group(0).startswith("TOTAL") else (fim.start() if fim else 1500))]
    ls = [l.strip() for l in corpo.split("\n") if l.strip() and not RUIDO_Q.match(l.strip()) and not re.match(r"(?i)^PROCURADORIA-GERAL", l.strip())]
    return ls[:60] or None

def banca(t):
    c = {k: len(re.findall(k, t, re.I)) for k in ("FGV|Funda[çc][ãa]o Getulio Vargas", "CONSULPLAN", "VUNESP", "CEBRASPE|CESPE", "FCC|Funda[çc][ãa]o Carlos Chagas")}
    k = max(c, key=c.get); return {"FGV|Funda[çc][ãa]o Getulio Vargas": "FGV", "CONSULPLAN": "Consulplan", "VUNESP": "VUNESP", "CEBRASPE|CESPE": "Cebraspe", "FCC|Funda[çc][ãa]o Carlos Chagas": "FCC"}[k] if c[k] else None

def main():
    res = []
    for ed in EDITAIS:
        try: t = carregar(ed["arq"])
        except Exception as e: print(ed["id"], "ERRO", e); continue
        sec = recortar(t, ed)
        if ed["modo"] == "oab": prog, intro = parse_inline(sec), ""
        elif ed["modo"] == "anexo1": prog, intro = parse_anexo1(re.sub(r"^.*?CONTE[ÚU]DO PROGRAM[ÁA]TICO", "", sec, count=1, flags=re.S))
        else: prog, intro = parse_inline(sec), ""
        o = {k: v for k, v in ed.items() if k not in ("arq", "modo", "ini", "fim")}
        o.update({"banca": banca(t) if ed["grupo"] != "mpsc" else {"mpsc-45": "VUNESP", "mpsc-2023-2": "Consulplan", "mpsc-2023-1": "Cebraspe", "mpsc-2020": "Cebraspe"}[ed["id"]], "intro": intro, "programa": prog, "quadro": quadro(t) if ed["grupo"] != "oab" else None})
        if ed["modo"] == "oab":
            m = re.search(r"3\.4\.1\.\s*A prova objetiva.*?(?=3\.4\.1\.1)", t, re.S)
            o["prova"] = re.sub(r"\s+", " ", m.group(0)).strip()[:900] if m else None
            p1 = re.search(r"\(P1\) PROVA OBJETIVA.*?Car[áa]ter Eliminat[óo]rio", t, re.S); p2 = re.search(r"\(P2\) PROVA PR[ÁA]TICO-PROFISSIONAL.*?Car[áa]ter Eliminat[óo]rio", t, re.S)
            o["fase1"] = re.sub(r"\s+", " ", p1.group(0)).strip() if p1 else None
            o["fase2"] = re.sub(r"\s+", " ", p2.group(0)).strip() if p2 else None
        res.append(o)
        print(ed["id"], "| banca:", o["banca"], "| disciplinas:", len(prog), "| pontos:", sum(len(d["pontos"]) for d in prog))
    open(os.path.join(RAIZ, "data", "editais.js"), "w", encoding="utf-8").write("window.EDITAIS = " + json.dumps(res, ensure_ascii=False) + ";\n")

if __name__ == "__main__":
    main()
