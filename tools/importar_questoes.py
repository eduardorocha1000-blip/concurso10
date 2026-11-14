#!/usr/bin/env python3
"""Extrai TODAS as questões dos textos do material (rodadas, simulados, resoluções de exames, super revisões...)
e gera dados/curso/questoes/questoes_material.json + data/curso/questoes_material.js (carregado pelo app).
Questões sem gabarito entram com gab = -1; o gabarito pode ser informado depois (no app ou em data/curso/gabaritos.js).
Uso: python tools/importar_questoes.py
Entrada: dados/curso/textos/<pasta>/NNN.txt (+ <pasta>.json / nv2.json com metadados). Saída é privada (gitignored)."""
import glob, hashlib, json, os, re, sys

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TXT = os.path.join(R, "dados", "curso", "textos")
SAIDA_J = os.path.join(R, "dados", "curso", "questoes"); os.makedirs(SAIDA_J, exist_ok=True)
SAIDA_JS = os.path.join(R, "data", "curso", "questoes_material.js")

MAT = [  # palavra-chave do título -> matéria do app (a ordem importa)
    ("processual do trabalho", "Direito Processual do Trabalho"), ("processo do trabalho", "Direito Processual do Trabalho"),
    ("processual civil", "Processo Civil"), ("processo civil", "Processo Civil"),
    ("processual penal", "Processo Penal"), ("processo penal", "Processo Penal"), ("ação penal", "Processo Penal"), ("juiz das garantias", "Processo Penal"),
    ("direito penal", "Direito Penal"), ("administrativo", "Direito Administrativo"), ("licitações", "Direito Administrativo"),
    ("constitucional", "Direito Constitucional"), ("tributário", "Direito Tributário"), ("do trabalho", "Direito do Trabalho"), ("do tabalho", "Direito do Trabalho"),
    ("empresarial", "Direito Empresarial"), ("empresário", "Direito Empresarial"), ("sociedade", "Direito Empresarial"), ("nome empresarial", "Direito Empresarial"),
    ("consumidor", "Direito do Consumidor"), ("cdc", "Direito do Consumidor"), ("criança", "ECA"), ("eca", "ECA"), ("ambiental", "Direito Ambiental"),
    ("humanos", "Direitos Humanos"), ("internacional", "Direito Internacional"), ("filosofia", "Filosofia do Direito"), ("previdenci", "Direito Previdenciário"),
    ("eleitoral", "Direito Eleitoral"), ("financeiro", "Direito Financeiro"), ("civil", "Direito Civil"), ("ética", "Ética Profissional"), ("etica", "Ética Profissional"),
    ("estatuto da advocacia", "Ética Profissional"), ("estatuto da oab", "Ética Profissional"), ("advogad", "Ética Profissional"), ("oab", "Ética Profissional"),
]
PAG = re.compile(r"^\s*\d+\s+de\s+\d+\s*gran\.com\.br\s*$", re.I)
INI = re.compile(r"^\s*(\d{1,3})\s*[\.\)]\s+(\S.*)$")
GAB_ITEM = re.compile(r"\b(\d{1,3})\s*[\.\-:)]\s*([a-eA-E])\b(?![a-zà-ú])")
ALT = re.compile(r"^\s*\(?([a-eA-E])\)\s*(.*)$")
FRASE_Q = re.compile(r"assinale|julgue|afirmativa|alternativa|responda|\?|correto|incorret|item|proposi", re.I)


def limpa_linhas(txt):
    L = [l.replace("\x0c", "").rstrip() for l in txt.splitlines()]
    cont = {}
    for l in L: cont[l.strip()] = cont.get(l.strip(), 0) + 1
    cab = {l.strip() for l in L[1:6] if l.strip() and len(l.strip()) < 130 and cont[l.strip()] > 1}  # só o que se repete em outras páginas
    out, pular = [], 0
    for l in L:
        if PAG.match(l): pular = 4; continue
        s = l.strip()
        if pular and (s in cab or not s or re.fullmatch(r"(RODADA DE QUEST[ÕO]ES|QUEST[ÕO]ES OBJETIVAS|FOCOAB!?.*|SIMULADO.*|SUPER REVIS[ÕO]ES.*|MAPAS MENTAIS)", s, re.I)): pular -= 1; continue
        pular = 0
        if not s: continue
        out.append(s)
    return out


def gabarito(L):
    """devolve (linhas sem o rodapé, mapa do ÚLTIMO bloco GABARITO, lista [(posição, mapa)] de todos os blocos)"""
    idx = [i for i, l in enumerate(L) if re.fullmatch(r"GABARITOS?\s*:?", l.strip(), re.I) or re.match(r"^GABARITOS?\s*:?\s+\d", l.strip(), re.I)]
    blocos = []
    for i in idx:
        bloco = []; j = i
        while j < len(L) and not re.match(r"^\W*Este material foi elaborado", L[j]) and not (j > i and j in idx):
            bloco.append(L[j]); j += 1
        mp = {int(n): g.upper() for n, g in GAB_ITEM.findall(" ".join(bloco))}
        blocos.append((i, mp))
    corpo = list(L)
    for k, l in enumerate(corpo):
        if re.match(r"^\W*Este material foi elaborado", l): corpo = corpo[:k]; break
    mapa = blocos[-1][1] if blocos else {}
    return corpo, mapa, blocos


def junta(linhas):
    t = ""
    for l in linhas:
        if t.endswith("-") and l[:1].islower() and len(t) > 1 and t[-2].isalpha(): t = t[:-1] + l
        else: t = (t + " " + l).strip()
    return re.sub(r"\s+", " ", t).strip()


def tag_origem(enun):
    m = re.match(r"^\(([^)]{3,160})\)\s*(.*)$", enun)
    if m and re.search(r"FGV|OAB|EXAME|CNU|DPE|TRF|TRT|TJ|MP|CESPE|VUNESP|FCC|Q\d{5,}|20\d\d", m.group(1), re.I): return m.group(1).strip(), m.group(2).strip()
    return "", enun


def cria_bloco(L, ini):
    """separa o bloco em enun, alts (lista), comentário"""
    bl = ini
    # procura alternativas
    pos_a = None
    for i, l in enumerate(bl):
        m = ALT.match(l)
        if m and m.group(1).lower() == "a" and any(ALT.match(x) and ALT.match(x).group(1).lower() == "b" for x in bl[i + 1:i + 30]): pos_a = i; break
    if pos_a is None: return junta(bl), [], ""
    enun = junta(bl[:pos_a]); resto = bl[pos_a:]
    inicios = []; esp = "a"
    for k, l in enumerate(resto):
        m = ALT.match(l)
        if m and m.group(1).lower() == esp and (not inicios or k > inicios[-1]):
            inicios.append(k); esp = chr(ord(esp) + 1)
    alts = []; fim_total = len(resto)
    for n, k in enumerate(inicios):
        if n + 1 < len(inicios):
            fim = inicios[n + 1]
        else:  # última alternativa: até a 1ª linha com pontuação final
            fim = k + 1
            while fim < len(resto) and not resto[fim - 1].endswith((".", ";", "?", "!", ")", ":")) : fim += 1
            fim_total = fim
        alts.append(junta([ALT.match(resto[k]).group(2)] + resto[k + 1:fim]))
    com = resto[fim_total:]
    corte = len(com)
    for i, l in enumerate(com):
        if re.match(r"^(QUADRO|TABELA|FIGURA|MAPA)\b", l) or (len(l) > 14 and l == l.upper() and re.search(r"[A-ZÁÉÍÓÚ]{4}", l) and not re.match(r"^\W*[A-E]\)", l)): corte = i; break
    return enun, alts, junta(com[:corte])


def titulo_arquivo(L):
    for l in L[:8]:
        if len(l) > 6 and not PAG.match(l) and "grancursos" not in l.lower() and "www." not in l.lower(): return l
    return ""


KW = {
    "Ética Profissional": r"advogad|estatuto da advocacia|OAB|honorários|procuração|substabelec|sociedade de advogados|código de ética|tribunal de ética|inscrição.*conselho seccional",
    "Direito Tributário": r"tribut|imposto|ICMS|ISS|IPTU|contribuição (social|de melhoria)|empréstimo compuls|lançamento|fato gerador|CTN|anterioridade",
    "Direito Constitucional": r"constitu[ci]|STF|controle de constitucionalidade|direitos fundamentais|poder constituinte|ADI|mandado de segurança|habeas|medida provisória|federa[çt]",
    "Direito Administrativo": r"administra[çt]ão pública|ato administrativo|licita|servidor público|improbidade|concessão|autarquia|poder de polícia|agente público",
    "Direito Civil": r"contrato|propriedade|posse|herança|sucess|casamento|obrigaç|responsabilidade civil|usucapi|testamento|negócio jurídico|CC|prescri",
    "Processo Civil": r"processo civil|CPC|petição inicial|contestação|recurso de apelação|tutela provisória|cumprimento de sentença|litisconsórcio|agravo",
    "Direito Penal": r"crime|pena|tentativa|dolo|culpa|furto|roubo|homicídio|prescrição penal|concurso de crimes|código penal",
    "Processo Penal": r"processo penal|inquérito|denúncia|prisão (preventiva|em flagrante)|CPP|ação penal|júri|habeas corpus|audiência de custódia",
    "Direito do Trabalho": r"empregad|empregador|CLT|justa causa|rescis|FGTS|jornada|horas extras|contrato de trabalho|aviso prévio",
    "Direito Processual do Trabalho": r"reclamação trabalhista|justiça do trabalho|TST|recurso ordinário|reclamante|reclamada|execução trabalhista",
    "Direito Empresarial": r"empresári|sociedade (limitada|empresária|anônima)|falência|recuperação judicial|título de crédito|duplicata|cheque|nota promissória|estabelecimento empresarial",
    "Direito do Consumidor": r"consumidor|fornecedor|CDC",
    "ECA": r"criança|adolescente|ato infracional|ECA|poder familiar|adoção",
    "Direito Ambiental": r"meio ambiente|ambiental|licenciamento|unidade de conservação|poluidor",
    "Direitos Humanos": r"direitos humanos|corte interamericana|convenção americana|sistema interamericano|pacto de san josé|ONU",
    "Direito Internacional": r"estrangeir|extradição|deportação|expulsão|asilo|refúgio|tratado internacional|imunidade diplomática",
    "Filosofia do Direito": r"kelsen|hart|dworkin|alexy|positivismo|jusnaturalis|utilitarismo|bentham|kant|hobbes|rousseau|aristóteles|platão|pós-positivismo",
    "Direito Previdenciário": r"previdenci|aposentadoria|INSS|segurado|pensão por morte|auxílio-doença",
    "Direito Eleitoral": r"eleitor|eleição|candidat|partido político|TSE|inelegib",
    "Direito Financeiro": r"orçamento|lei de responsabilidade fiscal|LRF|crédito adicional|LDO|receita pública",
}


def classifica(txt):
    melhor, n = "Geral", 0
    for k, rx in KW.items():
        c = len(re.findall(rx, txt, re.I))
        if c > n: melhor, n = k, c
    return melhor


def materia_de(titulo, meta):
    t = (titulo + " " + (meta or "")).lower()
    for k, v in MAT:
        if k in t: return v
    return "Geral"


def main():
    todos, vistos, stats = [], {}, {"arquivos": 0, "blocos": 0}
    pastas = [p for p in sorted(glob.glob(os.path.join(TXT, "*"))) if os.path.isdir(p)]
    for pasta in pastas:
        meta = {}
        for jf in (os.path.join(TXT, os.path.basename(pasta) + ".json"), os.path.join(TXT, "nv2.json") if os.path.basename(pasta) == "nv" else ""):
            if jf and os.path.exists(jf):
                try:
                    for x in json.load(open(jf, encoding="utf-8")): meta[x["k"]] = x
                except Exception: pass
        for f in sorted(glob.glob(os.path.join(pasta, "*.txt"))):
            k = os.path.basename(f)[:-4]
            txt = open(f, encoding="utf-8", errors="replace").read()
            L = limpa_linhas(txt); titulo = titulo_arquivo(L); corpo, gmap, blocos = gabarito(L)
            stats["arquivos"] += 1
            # blocos de questão
            cand = []; ult = None
            for i, l in enumerate(corpo):
                m = INI.match(l)
                if not m or re.fullmatch(r"\d+\s*\.\s*[a-eA-E]\.?", l): continue
                n = int(m.group(1))
                if n <= 120 and (ult is None or n > ult or n <= 3): cand.append((i, n)); ult = n
            starts = []; ult = None
            for ci, (i, n) in enumerate(cand):  # só vale como início se o bloco parecer questão
                j = cand[ci + 1][0] if ci + 1 < len(cand) else len(corpo)
                _e, _a, _c = cria_bloco(corpo, [INI.match(corpo[i]).group(2)] + corpo[i + 1:j])
                if _a or (FRASE_Q.search(_e[:600]) and len(_e) > 80 and not re.match(r"^[A-ZÁÉÍÓÚ ]{6,}$", _e[:40])): starts.append((i, n))
            # gabarito por número só vale dentro da região que precede cada bloco GABARITO e se os números ali forem únicos
            gpos = {}
            ant = -1
            for pos, mp in blocos:
                reg = [(i, n) for i, n in starts if ant <= i < pos]
                ns = [n for _, n in reg]
                if reg and len(ns) == len(set(ns)):
                    for i, n in reg:
                        if n in mp: gpos[i] = mp[n]
                ant = pos
            for si, (i, n) in enumerate(starts):
                j = starts[si + 1][0] if si + 1 < len(starts) else len(corpo)
                bl = [INI.match(corpo[i]).group(2)] + corpo[i + 1:j]
                enun, alts, com = cria_bloco(corpo, bl)
                g0 = gpos.get(i)
                if not alts and g0 in ("C", "E") and set(gpos.values()) <= {"C", "E"} and len(enun) >= 25: alts = ["Certo", "Errado"]  # itens certo/errado
                if not alts and not (len(enun) >= 120 and "•" not in enun and re.search(r"\?\s*$|justifique|fundamente|responda|indique|aponte|explique|discorra|\([abc]\)|assinale|julgue", enun[-350:], re.I)): continue
                stats["blocos"] += 1
                orig, enun = tag_origem(enun)
                g = gpos.get(i)
                if alts == ["Certo", "Errado"] and g in ("C", "E"): g = "A" if g == "C" else "B"
                if g is None:
                    mm = re.search(r"[Gg]abarito\s*[:\-–]?\s*(?:letra\s*)?\(?([A-Ea-e])\b", com or "")
                    if mm: g = mm.group(1).upper()
                m_ = meta.get(k, {})
                mat = materia_de(titulo, m_.get("mat", ""))
                if mat in ("Geral", "Ética Profissional") and re.search(r"simulado|prepara|resolu|exame|super revis|mega revis", titulo, re.I) or mat == "Geral":
                    c = classifica(enun + " " + " ".join(alts))
                    if c != "Geral": mat = c
                q = {"n": n, "pasta": os.path.basename(pasta), "arq": k, "fonte": titulo, "origem": orig, "materia": mat, "enun": enun, "alts": alts,
                     "gab": "ABCDE".index(g) if g and "ABCDE".index(g) < max(len(alts), 1) else -1, "coment": com}
                chave = re.sub(r"[^a-z0-9]", "", enun.lower())[:180]
                if chave in vistos:
                    o = vistos[chave]
                    if o["gab"] < 0 and q["gab"] >= 0: o["gab"] = q["gab"]
                    if not o["coment"] and q["coment"]: o["coment"] = q["coment"]
                    continue
                vistos[chave] = q; todos.append(q)
    for i, q in enumerate(todos): q["id"] = "qm%04d" % (i + 1)
    json.dump(todos, open(os.path.join(SAIDA_J, "questoes_material.json"), "w", encoding="utf-8"), ensure_ascii=False)
    corpo = json.dumps(todos, ensure_ascii=False)
    open(SAIDA_JS, "w", encoding="utf-8").write("(function(){const M=['oab'];const L=" + corpo + ";L.forEach(q=>DATA.questoes.push({id:q.id,materia:q.materia,banca:q.origem||q.fonte,ano:'',enun:q.enun,alts:q.alts,gab:q.gab,coment:q.coment,fonte:q.fonte,mods:M}));})();\n")
    comg = sum(1 for q in todos if q["gab"] >= 0); com4 = sum(1 for q in todos if len(q["alts"]) >= 4)
    print("arquivos", stats["arquivos"], "| blocos", stats["blocos"], "| questões únicas", len(todos), "| com gabarito", comg, "| sem gabarito", len(todos) - comg,
          "| com 4+ alternativas", com4, "| sem alternativas", sum(1 for q in todos if not q["alts"]))
    from collections import Counter
    print(Counter(q["materia"] for q in todos).most_common())

main()
