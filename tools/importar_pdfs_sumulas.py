#!/usr/bin/env python3
"""Importa súmulas e enunciados a partir de PDFs salvos dos sites oficiais:
  TST (5 PDFs 'file*.pdf'), TSE ('tse-sumulas-tse.pdf'), STM ('STM - Súmulas.pdf'),
  TJSC (súmulas + enunciados dos grupos de câmaras, Turma de Uniformização, Fórum de Execução Penal, Jornada, Câmara de Recursos Delegados).
Uso: python tools/importar_pdfs_sumulas.py <pasta com os PDFs>
Gera: data/jur_tst.js, jur_tse.js, jur_stm.js, sumulas_tjsc.js (JUR_IMPORT) e data/enunciados_tjsc.js (DATA.enunciados).
"""
import glob, json, os, re, sys
import pypdf

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PASTA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expanduser("~"), "Downloads")
MODS = ["oab", "magsc", "mpsc", "magfed", "enam"]

def texto_pdf(caminho, marca=""):
    t = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(caminho).pages)
    return re.sub("[-●⌃-]", lambda m: "⌃" if m.group(0) == "⌃" else marca, t)   # glifos de ícone (uso privado) viram vazio

def limpa(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    for a, b in ((r"\bCL T\b", "CLT"), (r"\bAL TERADA\b", "ALTERADA"), (r"\bCP C\b", "CPC")):
        s = re.sub(a, b, s)
    return s

def grava(nome, itens, enun=False):
    caminho = os.path.join(R, "data", nome)
    if enun: conteudo = "DATA.enunciados.push(...(" + json.dumps(itens, ensure_ascii=False) + "));\n"
    else: conteudo = "(window.JUR_IMPORT = window.JUR_IMPORT || []).push(" + json.dumps(itens, ensure_ascii=False) + ");\n"
    open(caminho, "w", encoding="utf-8").write(conteudo)
    print(f"{nome}: {len(itens)} itens")

# ---------------- TST ----------------
def tst():
    itens = {}
    arqs = sorted(glob.glob(os.path.join(PASTA, "file*.pdf")))
    for a in arqs:
        t = texto_pdf(a)
        if "do TST" not in t[:400]: continue
        partes = re.split(r"(?m)^\s*Súmula nº (\d+) do TST\s*$", t)
        for i in range(1, len(partes), 2):
            n, corpo = partes[i], partes[i + 1]
            corpo = re.sub(r"Inteiro teor no formato HTML", "", corpo)
            m = re.search(r"(?s)^\s*(.*?)\s*Observação:\s*(.*?)\s*Tese:\s*(.*?)\s*Situação:\s*([A-Za-zÀ-ú ]+?)\s*$", corpo)
            if not m: continue
            tema, obs, tese, sit = (limpa(x) for x in m.groups())
            riscado = "<s>" in tese
            tese = re.sub(r"</?s>", "", tese); tese = limpa(tese)
            sit = limpa(sit).upper().replace("AL TERADA", "ALTERADA")
            proc = bool(re.search(r"recurso|prazo|custas|execu|rescis[óo]ria|mandado de seguran|honor[áa]rios|compet[êe]ncia|nulidade|intima|cita[çc]|dep[óo]sito recursal|agravo|embargos|preclus|revelia|[ôo]nus da prova|penhora|ju[ií]zo|processo", tema.lower()))
            itens[int(n)] = {"tribunal": "TST", "n": n, "texto": tese, "vinculante": False, "materia": tema.rstrip(". ").capitalize(), "ramo": "Processual do Trabalho" if proc else "Trabalhista", "ramo_auto": True,
                             "orgao": "Tribunal Superior do Trabalho", "situacao": "Cancelada" if sit == "CANCELADA" else "Vigente",
                             "obs": obs + (" · Contém itens cancelados (riscados na fonte)." if riscado else "") + ("" if sit in ("CANCELADA", "CRIADA", "ALTERADA") else f" · Situação: {sit}"), "situacao_fonte": sit}
    grava("jur_tst.js", [itens[k] for k in sorted(itens)])

# ---------------- TSE ----------------
def tse():
    t = texto_pdf(os.path.join(PASTA, "tse-sumulas-tse.pdf"), marca="")
    linhas = [l for l in t.split("\n") if not re.match(r"^\s*(Súmulas do TSE(, do STF e do STJ)?|SÚMULAS( DO TSE)?|\d{3,4})\s*$", l)]
    t = "\n".join(linhas)
    partes = re.split(r"(?m)^Súmula-TSE n\. (\d+)( \(cancelada\))?\s*$", t)
    itens = []
    for i in range(1, len(partes), 3):
        n, canc, corpo = partes[i], bool(partes[i + 1]), partes[i + 2]
        pub = re.search(r"Publicad[ao]s? n[oa]s? ([^\n]*(?:\n[^\n]*)?)", corpo)
        if canc:
            ne = re.search(r"(?s)NE:\s*(.*?)(?:Assim determinava:|$)", corpo); q = re.search(r"(?s)Assim determinava:\s*[“\"](.*?)[”\"]\s*\.?\s*$", corpo.strip())
            texto = limpa((q.group(1) if q else "").replace("-\n", "")); obs = limpa(ne.group(1)) if ne else None
        else:
            m = re.search(r"(?s)resolve\s+(?:editar\s+a\s+seguinte\s+s[úu]mula|aprovar\s+a\s+proposta\s+de\s+edi[çc][ãa]o\s+do\s+seguinte\s+verbete\s+de\s+s[úu]mula):\s*(.*)$", corpo)
            base = m.group(1) if m else corpo
            corte = re.search(r"(?m)^[ 	]*(?:|\s{2,}\S|Referências:|NE:|Ministro|Ac\.-TSE)", base)
            enun = base[: corte.start()] if corte else base
            texto = limpa(re.sub(r"\s*-\s*\n\s*(?=[a-zà-ú])", "", enun)); obs = None
            ne = re.search(r"(?s)(NE:.*?)(?:Referências:|Ministro|$)", base)
            if ne: obs = limpa(re.sub(r"\s*-\s*\n\s*(?=[a-zà-ú])", "", ne.group(1)))
        itens.append({"tribunal": "TSE", "n": n, "texto": texto, "vinculante": False, "materia": "Direito Eleitoral", "ramo": "Eleitoral", "orgao": "Tribunal Superior Eleitoral",
                      "situacao": "Cancelada" if canc else "Vigente", "obs": obs, "pub": limpa(pub.group(1)) if pub else None})
    grava("jur_tse.js", [x for x in itens if x["texto"]])

# ---------------- STM ----------------
def stm():
    t = texto_pdf(os.path.join(PASTA, "STM - Súmulas.pdf"))
    t = "\n".join(l for l in t.split("\n") if not re.match(r"^\s*(Súmulas|Referências)\s*$", l))
    partes = re.split(r"(?m)^SÚMULA Nº (\d+)\s*-?\s*(.*)$", t)
    itens = []
    for i in range(1, len(partes), 3):
        n, cab, corpo = partes[i], partes[i + 1], limpa(partes[i + 2])
        canc = "cancelada" in cab.lower()
        corpo = re.sub(r"^Texto anterior:\s*", "", corpo)
        corpo = corpo.strip(" \"“”")
        if corpo.count('"') % 2: corpo = corpo.replace('"', "")
        itens.append({"tribunal": "STM", "n": n, "texto": corpo, "vinculante": False, "materia": "Direito Militar", "ramo": "Militar", "orgao": "Superior Tribunal Militar",
                      "situacao": "Cancelada" if canc else "Vigente", "obs": limpa(cab) or None})
    grava("jur_stm.js", [x for x in itens if x["texto"]])

# ---------------- TJSC: súmulas ----------------
RUIDO_TJSC = re.compile(r"^(\*|O que você está procurando\?|Jurisprudência|Anuário das Turmas de Recursos|Diretrizes do TJSC|Enunciados do TJSC|Jurisprudência em Teses|STF - .*|STJ - .*|Súmulas do TJSC|Súmulas|Súmula Teor|FECHAR TODOS OS ITENS|\s*FECHAR TODOS OS ITENS|"
                        r"Atendimento e Contatos|Mapa do Site|Nossas Redes Sociais|Rua Álvaro Millen.*|Florianópolis/SC - CEP.*|\(48\) 3287-1000|Segunda a sexta.*|I Fórum Estadual.*|I Jornada Prevenção.*|Câmara de Recursos Delegados|Grupo de Câmaras de Direito .*|Órgão Especial|Turma de Uniformização dos Juizados Especiais)\s*$")
def tjsc_sumulas():
    arq = [f for f in glob.glob(os.path.join(PASTA, "Súmulas do TJSC*.pdf"))][0]
    t = texto_pdf(arq)
    linhas = [l.rstrip() for l in t.split("\n") if l.strip() and not RUIDO_TJSC.match(l.strip())]
    blocos, atual = [], None
    for l in linhas:
        m = re.match(r"^Súmula (\d+)\s*\*?\s*(.*)$", l.strip())
        if m: atual = [m.group(1), [m.group(2)] if m.group(2) else []]; blocos.append(atual)
        elif atual is not None: atual[1].append(l.strip())
    itens = []
    for n, ls in blocos:
        txt = limpa(" ".join(ls)); rev = bool(re.search(r"\(Revogad[ao]\)", txt)); txt = limpa(re.sub(r"\(Revogad[ao]\)\s*\*?", "", txt)).strip(" *")
        itens.append({"tribunal": "TJSC", "n": n, "texto": txt, "vinculante": False, "materia": "Súmula do TJSC", "orgao": "Tribunal de Justiça de Santa Catarina", "situacao": "Revogada" if rev else "Vigente", "obs": None})
    itens = {int(x["n"]): x for x in itens if x["texto"]}
    grava("sumulas_tjsc.js", [itens[k] for k in sorted(itens)])

# ---------------- TJSC: enunciados ----------------
ORGAOS = [("Grupo de Câmaras de Direito Civil", "Grupo de Câmaras de Direito Civil"), ("Grupo de Câmaras de Direito Comercial", "Grupo de Câmaras de Direito Comercial"), ("Grupo de Câmaras de Direito Público", "Grupo de Câmaras de Direito Público"),
          ("Câmara de Recursos Delegados", "Câmara de Recursos Delegados"), ("Turma de Uniformização dos Juizados Especiais", "Turma de Uniformização dos Juizados Especiais"),
          ("I Fórum Estadual de Magistrados da Execução Penal", "I Fórum Estadual de Magistrados da Execução Penal"), ("I Jornada Prevenção e Solução Extrajudicial de Litígios", "I Jornada Prevenção e Solução Extrajudicial de Litígios")]
ROMANOS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
def romano(s):
    if not re.fullmatch(r"[IVXLC]+", s): return int(s) if s.isdigit() else 0
    tot = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMANOS[a]; tot += -v if b != " " and ROMANOS.get(b, 0) > v else v
    return tot
LABEL = re.compile(r"^Enunciado\s+(\S+?)\s*(?:-\s*(CANCELADO|REVOGADO))?\s*(\((?:Revogad[oa]|nova reda[çc][ãa]o)\))?\s*⌃\s*$")
def enunciados():
    itens = []
    for nome_arq, orgao in ORGAOS:
        achados = [f for f in glob.glob(os.path.join(PASTA, nome_arq + "*Poder Judiciário de Santa Catarina.pdf"))]
        if not achados: print("não achei:", nome_arq); continue
        t = texto_pdf(achados[0])
        k = t.find("FECHAR TODOS OS ITENS"); t = t[k:] if k >= 0 else t
        linhas = [re.sub(r"\s*FECHAR TODOS OS ITENS\s*", " ", l).rstrip() for l in t.split("\n")]   # o cabeçalho às vezes se funde à linha de texto
        linhas = [l for l in linhas if l.strip() and not RUIDO_TJSC.match(l.strip())]
        fim = next((i for i, l in enumerate(linhas) if re.match(r"^\s*(Atendimento e Contatos)", l)), len(linhas)); linhas = linhas[:fim]
        its, buf = [], []
        for l in linhas:
            m = LABEL.match(l.strip())
            if m: its.append({"n": m.group(1), "canc": m.group(2) == "CANCELADO", "rev": m.group(2) == "REVOGADO" or bool(m.group(3) and "Revogad" in m.group(3)), "nova": bool(m.group(3) and "nova" in m.group(3).lower()), "buf": buf}); buf = []
            else: buf.append(l.strip())
        # texto que ficou depois do último rótulo não pertence a nenhum item
        for i in range(1, len(its)):   # continuação de página: linhas iniciadas em minúscula pertencem ao item anterior
            b = its[i]["buf"]
            while b and re.match(r"^[a-zà-ú]", b[0]): its[i - 1]["buf"].append(b.pop(0))
        for it in its:
            ctx, obs, corpo = [], [], []
            absorve = False
            for l in it["buf"]:
                if absorve and ctx:
                    ctx[-1] += " " + l; absorve = not re.search(r"[:.]\s*$", l)
                elif re.match(r"^(Os integrantes|Em sess[ãa]o)", l) or re.search(r"homologaram|aprovaram o seguinte", l[:140]): ctx.append(l); absorve = not re.search(r"[:.]\s*$", l)
                elif re.match(r"^(REDAÇÃO|NOVA REDAÇÃO|Publicad|PUBLICA|Disponibilizado|Florianópolis,|\(\*\)|CANCELADO)", l): obs.append(l)
                else: corpo.append(l)
            texto = limpa(" ".join(corpo))
            m = re.search(r"\s*\((Processo[^)]*(?:\([^)]*\)[^)]*)*\)?)\s*$", texto)
            if m: obs.append(m.group(1)); texto = texto[: m.start()].strip()
            texto = re.sub(r"^[IVXL]+\s*-\s*", "", texto.strip(" \"“”")).strip(" \"“”")
            if not texto: continue
            canc = it["canc"] or any("CANCELADO" in o for o in obs)
            itens.append({"fonte": "TJSC – " + orgao, "n": it["n"], "ord": romano(it["n"]), "texto": texto, "materia": "", "orgao": orgao, "situacao": "Cancelado" if canc else ("Revogado" if it["rev"] else "Vigente"),
                          "obs": limpa(" · ".join(ctx + obs + (["Nova redação."] if it["nova"] else []))) or None, "mods": MODS})
        print("  ", orgao, "->", len(its), "rótulos")
    grava("enunciados_tjsc.js", itens, enun=True)

if __name__ == "__main__":
    for f in (tst, tse, stm, tjsc_sumulas, enunciados): f()
