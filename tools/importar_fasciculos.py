#!/usr/bin/env python3
"""Importa os fascículos individuais (um PDF por fascículo) da pasta 'Minha Doutrina' e os estrutura:
Apresentação e objetivos · Sumário · Teoria (seções numeradas) · Casos práticos · Questões objetivas (com gabarito e comentário) ·
Questões discursivas (com espelho) · Referências.
Uso: python tools/importar_fasciculos.py "<pasta com os PDFs>"
Gera data/doutrina/index.js e data/doutrina/fNNN.js (carregados sob demanda), data/doutrina/mapas/*.svg e dados/doutrina/estrutura.json.
"""
import json, math, os, re, shutil, sys, unicodedata
from collections import Counter
import pypdf

PASTA = sys.argv[1]
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
OUT = os.path.join(RAIZ, "data", "doutrina")
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(os.path.join(OUT, "mapas"), exist_ok=True)
os.makedirs(os.path.join(RAIZ, "dados", "doutrina"), exist_ok=True)

def sa(t): return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
def limpa(s): return re.sub(r"\s+", " ", s or "").strip()

# ---------------- leitura e limpeza ----------------
def ler(caminho):
    t = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(caminho).pages)
    t = re.sub("[-●•]", "", t).replace("­", "")
    return [l.rstrip() for l in t.split("\n")]

def sem_cabecalhos(linhas):
    freq = Counter(l.strip() for l in linhas if l.strip())
    def ruido(l):
        s = l.strip()
        if not s: return True
        if re.match(r"^P[áa]gina\s+\d+(\s+de\s+\d+)?$", s) or re.match(r"^\d{1,3}$", s): return True
        if re.match(r"(?i)^(Direito|Processo|Direitos)\b.{0,60}(Fasc[íi]culo|Volume)\b.*$", s) and freq[s] >= 2: return True
        if freq[s] >= 3 and len(s) < 120 and re.search(r"(?i)fasc[íi]culo|volume|cole[çc][ãa]o|concursos p[úu]blicos|p[áa]gina|material (autoral|original)|\| \d+$", s) and not re.match(r"^(Gabarito|Caso|A\)|B\))", s): return True
        return False
    return [l for l in linhas if not ruido(l)]

# ---------------- metadados do arquivo ----------------
def meta(nome):
    n = nome.replace("_", " ")
    d = "OUTRA"
    for rx, v in ((r"^Direito Administrativo", "DIREITO ADMINISTRATIVO"), (r"^Direito Civil|^Direito Real", "DIREITO CIVIL"), (r"^Direito Constitucional", "CONSTITUCIONAL"), (r"^Direito Empresarial", "DIREITO EMPRESARIAL"),
                  (r"^Direito Penal|^OAB 47", "DIREITO PENAL"), (r"^Direito Processual Civil|^Processo Civil", "DIREITO PROCESSUAL CIVIL"), (r"^Direito Processual Penal|^Processo Penal", "DIREITO PROCESSUAL PENAL"), (r"^Direito do Consumidor", "DIREITO DO CONSUMIDOR"),
                  (r"^Fasciculo (14|15|16|17|18|19)", "DIREITO ADMINISTRATIVO")):
        if re.search(rx, n): d = v; break
    m = re.search(r"Fasciculos?\s+(\d+)", n); num = int(m.group(1)) if m else 0
    return d, num

# ---------------- título e matéria (reaproveita a lógica da capa) ----------------
SKIP = re.compile(r"(?i)^(DIREITO\b(?!.*[—:])|CONCURSOS|VOLUME|FASC[ÍI]CULO|OAB\b|MINIST|MAGISTR|MATERIAL|PREPARA|N[ÍI]VEL|EDI[ÇC]|DATA |ATUALIZA|COLE[ÇC][ÃA]O|BRASIL|PROCESSO (CIVIL|PENAL)$|\d+ horas|\d+ dias|Teoria\s+Legisla|Introdu|Como utilizar|Posicionamento|Texto original|Edição de estudo|Projeto)")
def titulo_capa(linhas, nome):
    capa = [l.strip() for l in linhas[:40] if l.strip()]
    mnum = re.search(r"(?i)FASC[ÍI]CULOS?\s+(\d+(?:\s+A\s+\d+)?)", " ".join(capa[:14]))
    capa2 = []
    for l in capa:
        l2 = re.sub(r"(?i)^(VOLUME\s+[IVX]+\s*[—–·-]?\s*)?FASC[ÍI]CULOS?\s+\d+\s*[—–-]*\s*", "", l) if re.match(r"(?i)^(VOLUME\s+[IVX]+\s*[—–·-]?\s*)?FASC[ÍI]CULOS?\s+\d+\s*[—–-]*\s*\S", l) else l
        l2 = re.sub(r"(?i)^(Direito [A-Za-zç ]+?)\s*[·—-]\s*Volume [IVX]+\s*[·—-]\s*Fasc[íi]culo \d+\s*[—–-]*\s*", "", l2)
        capa2.append(l2)
    cand = [l for l in capa2 if l and not SKIP.match(l) and len(l) > 5 and not re.match(r"(?i)^p[áa]gina", l)]
    tit = []
    for l in cand:
        if l.isupper() or (tit and len(tit) < 3 and len(" ".join(tit)) < 70): tit.append(l)
        if len(tit) >= 3 or (tit and not l.isupper()): break
    texto = " ".join(tit) if tit else (cand[0] if cand else nome.replace("_", " "))
    texto = re.sub(r"(?i)\s*(OAB|MINIST[ÉE]RIO P[ÚU]BLICO|MAGISTRATURA).*$", "", texto).strip(" —–-|·")
    texto = re.split(r"\s{2,}| · | • | Código | CC,| Lei | Questões| Carga | Objetivo| Base legal| Estudo | Delimitação| Ideia ", texto)[0]
    m = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,:;/()\-–—&.]{10,}?)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç])", texto)
    if m: texto = m.group(1)
    texto = re.sub(r"(?i)^DIREITO (CIVIL|ADMINISTRATIVO|PENAL|PROCESSUAL CIVIL|PROCESSUAL PENAL|DO CONSUMIDOR|EMPRESARIAL|CONSTITUCIONAL)\s*(—\s*DIREITOS REAIS)?\s+(?=\S{3})", "", texto) if len(texto) > 25 else texto
    if len(texto) < 8:   # fallback: nome do arquivo (sem acentos)
        texto = re.sub(r"^(Direito|Processo)[A-Za-z ]*?(Volume\s+\w+\s+)?Fasciculos?\s+\d+(\s+a\s+\d+)?\s*", "", nome.replace("_", " "))
        texto = re.sub(r"^(Fasciculo\s+\d+\s+)", "", texto)
    return texto.strip()[:120], (int(re.match(r"\d+", mnum.group(1)).group()) if mnum else 0)

def tit_case(t):
    if t != t.upper(): return t
    t = t.lower(); t = t[:1].upper() + t[1:]
    t = re.sub(r"(^|[.:—–]\s+)([a-zà-ú])", lambda m: m.group(1) + m.group(2).upper(), t)
    for sg in ("CF", "CPC", "CPP", "CP", "CC", "CLT", "CDC", "STF", "STJ", "TCE", "SC", "MPSC", "TJSC", "PAD", "LGPD", "PPP", "MROSC", "OS", "OSCIP", "LEF", "CDA", "REsp", "RE", "ANPP", "PIC", "LEP", "TSE", "CNMP", "MS", "ACP", "IA", "FGTS", "MEI", "ME", "EPP", "LC", "EC", "II", "III", "IV", "VI", "VII", "VIII"):
        t = re.sub(r"\b" + re.escape(sg.lower()) + r"\b", sg, t, flags=re.I) if sg.isupper() and len(sg) > 1 else t
    return t

REGRAS = {
 "DIREITO ADMINISTRATIVO": [("Direito Eleitoral", "eleitoral"), ("Direito Tributário", r"\btribut"), ("Direito Financeiro e Orçamentário", "financeir|orcament"), ("Direito Urbanístico", "urbanis|cidade"), ("Direito Ambiental", "ambient"),
   ("Ministério Público e Tutela Coletiva", "ministerio publico|inquerito civil|organizacao do|mpsc, cnmp"), ("Improbidade e Anticorrupção", "improbidade"), ("Licitações, Contratos e Parcerias", "licita|contrata|terceiro setor|consorcio|convenio|mrosc"),
   ("Agentes Públicos e Regime Disciplinar", "agentes|disciplinar|servidor|pad"), ("Serviços Públicos, Regulação e Estatais", "servico|concess|regula|agencia|economic|ppp|estatais|digital|13.303"),
   ("Bens Públicos e Intervenção na Propriedade", "bens publicos|propriedade|desapropri|interven"), ("Responsabilidade Civil do Estado", "responsabilidade civil"), ("Administração Municipal", "municipal"),
   ("Processo Administrativo, Controle e Fazenda Pública", "controle|tribunais de contas|tce|processo administrativo|fazenda|judicializacao|sancionador|revisao|simulado|precatorios")],
 "DIREITO CIVIL": [("Revisão e simulados", "simulado|revisao integrada|revisao geral|revisao dirigida|caderno|folha de respostas|gabarito analitico|errata|lote |atualizacao aprofundada"),
   ("Prescrição e Decadência", "prescricao"), ("LINDB", "lindb|introducao as normas"),
   ("Títulos de Crédito", "titulos? de credito|letra de cambio|cheque|duplicata|cedula de credito|ccb|cpr e titulos"),
   ("Contratos Bancários e Crédito", "bancari|conta-corrente|cartao de credito|consignado|tarifas, seguros|pix|superendividamento|abertura de credito|contas de pagamento"),
   ("Direito Imobiliário", "multipropriedade|condominio de lotes|parcelamento do solo|incorporacao|patrimonio de afetacao|distrato imobiliario|built|adjudicacao compulsoria|reurb|registro imobiliario|loteamento"),
   ("Direito Digital e Herança Digital", "digital|criptoativ|plataformas|dados pessoais apos"),
   ("Direito de Empresa e Sociedades", "sociedade|empresari|estabelecimento|franquia|factoring|leasing|arrendamento mercantil|cooperativ|comandita|associacoes|fundacoes|pessoas juridicas|desconsideracao|prepostos|registro publico de empresas|escrituracao empresarial|representacao comercial|transferencia de tecnologia|engenharia|concessao comercial|nome empresarial|publicidade, prova, sigilo"),
   ("Obrigações", "promessa de recompensa|gestao de negocios|pagamento indevido|enriquecimento"),
 ("Garantias e Propriedade Fiduciária", "fiduciari|hipoteca|penhor|anticrese|garantias reais"), ("Direitos Reais", "reais|posse|propriedade|usucap|condominio|laje|superficie|vizinhanca|usufruto|servidoes|uso e habitacao|promitente"),
   ("Família", "familia|tutela|curatela|decisao apoiada|adocao|poder familiar|filiacao|reproducao humana|casamento|uniao estavel|alimentos, guarda"), ("Sucessões", "sucess|legados|inventario|heranca|testament"), ("Responsabilidade Civil", "responsabilidade"), ("Contratos", "contrat|seguro|corretagem|transporte|renda|jogo|fianca|transacao|compromisso|comissao|agencia|vicios|aleatorios|evicao|compra e venda|troca|doacao|locacao|emprestimo|prestacao de servicos|empreitada|deposito|mandato"),
   ("Obrigações", "obriga|adimplemento|inadimpl|pagamento|transmiss|extincao")],
 "DIREITO PROCESSUAL CIVIL": [("Recursos e Precedentes", "recurso|apelacao|precedente|irdr|reclamacao|embargos"), ("Execução e Cumprimento de Sentença", "execu|cumprimento|fiscal|insolv"), ("Procedimentos Especiais", "procedimentos especiais|monitoria|alimentos|locatic|inventario|oposicao|jurisdicao voluntaria|consignacao|dissolucao|juizados|restauracao"),
   ("Processo Coletivo e Ações Constitucionais", "coletiv|mandado de seguranca|acoes constitucionais|saude, educacao|estruturais"), ("Provas", "prova"), ("Tutela Provisória", "tutela provisoria"), ("Revisão e Simulados", "simulado|revisao"), ("Sentença e Coisa Julgada", "sentenca|coisa julgada")],
 "DIREITO PROCESSUAL PENAL": [("Recursos e Execução Penal", "recurso|execucao"), ("Prisões e Medidas Cautelares", "prisoes|prisao|cautelar|assecurat"), ("Provas", "prova|pericia|medicina legal|cibernetic"), ("Procedimentos, Nulidades e Legislação Especial", "procedimento|nulidade|legislacao|hediondos|juizados|atos processuais"),
   ("Jurisdição, Competência e Sujeitos", "jurisdicao|competencia|sujeitos|organizacao judiciaria"), ("Ação Penal e Investigação", "acao penal|principios|investig|inquerito"), ("Direitos Humanos e Revisão", "direitos humanos|revisao|atualizacao|probatoria")],
 "DIREITO PENAL": [("Exame de Ordem (OAB): peça e questões", "exame de ordem|oab 47|modelo de resolucao"), ("Revisão e simulados", "simulado|revisao"), ("Parte Geral e Penas", "teoria geral|penas|dosimetria"), ("Crimes em Espécie", "crimes|dignidade|administracao|propriedade")],
 "CONSTITUCIONAL": [("Direito Constitucional", ".")], "DIREITO EMPRESARIAL": [("Direito Empresarial", ".")], "DIREITO DO CONSUMIDOR": [("Direito do Consumidor", ".")]}
PADRAO = {"DIREITO ADMINISTRATIVO": "Teoria Geral do Direito Administrativo", "DIREITO CIVIL": "Parte Geral do Direito Civil", "DIREITO PROCESSUAL CIVIL": "Processo de Conhecimento e Teoria Geral", "DIREITO PROCESSUAL PENAL": "Outros Temas de Processo Penal", "DIREITO PENAL": "Direito Penal"}
def materia(disc, titulo, nome):
    for t in (sa(titulo), sa(nome.replace("_", " "))):
        for nm, rx in REGRAS.get(disc, []):
            if re.search(rx, t): return nm
    return PADRAO.get(disc, disc.title())


SIGLAS_T = {"pad", "tce", "sc", "mpsc", "ms", "acp", "re", "resp", "ppp", "mrosc", "os", "oscip", "lgpd", "anpp", "pic", "lep", "lef", "cda", "irdr", "iac", "rpv", "cf", "ec", "mei", "me", "epp", "lc", "oab", "cnmp", "ia", "aij", "cc", "cpc", "cpp", "cp", "cdc", "stf", "stj", "tjsc", "reurb", "reurb", "rpv"}
MINUS = {"de", "da", "do", "das", "dos", "e", "em", "a", "o", "as", "os", "no", "na", "nos", "nas", "para", "com", "ao", "contra", "sobre", "por", "sem"}
def titulo_arquivo(nome, linhas):
    n = re.sub(r"^.*?Fasciculos?_\d+(?:_a_\d+)?_?", "", nome)
    if n == nome or not n.strip("_"):
        n = re.sub(r"^(Direito|Processo)_(Civil|Real|Constitucional|Administrativo|Penal|Empresarial|do_Consumidor|Processual_Civil|Processual_Penal)_", "", nome) if re.match(r"^(Direito|Processo)_", nome) and "Caderno" in nome else ""
    toks = [t for t in n.split("_") if t]
    if not toks: return ""
    cont = Counter()
    for l in linhas:
        for w in re.findall(r"[A-Za-zÀ-ú]{3,}", l): cont[w.lower()] += 1
    mapa = {}
    for w, c in cont.items():
        k = sa(w)
        if k not in mapa or (c > cont[mapa[k]] and w != k) or (mapa[k] == k and w != k): mapa[k] = w
    out = []
    for i, t in enumerate(toks):
        k = t.lower()
        if k in SIGLAS_T: out.append(t.upper() if k != "resp" else "REsp")
        elif k in MINUS and i: out.append(k)
        else:
            w = mapa.get(sa(k), k); out.append(w)
    r = " ".join(out); r = r[:1].upper() + r[1:]
    return r

# ---------------- seções ----------------
RX_CASOS = re.compile(r"^(?:\d+\.\s*)?casos?\s+(?:pr[áa]ticos?|concretos?|e\s+quest)", re.I)
RX_OBJ = re.compile(r"^(?:\d+\.\s*)?(?:quest[õo]es\s*$|quest[õo]es\s+(?:objetivas?|comentadas|de m[úu]ltipla|de fixa[çc][ãa]o|autorais|de prova|tipo)|gabarito objetivo|simulado objetivo|exerc[íi]cios? de fixa)", re.I)
RX_FIM2 = re.compile(r"^(?:\d+\.\s*)?(?:roteiro de prova|s[íi]ntese para prova|s[íi]ntese para revis|plano de estudo|revis[ãa]o final|quadro|checklist|mapa|erros|pontos de alta)", re.I)
RX_DISC = re.compile(r"^(?:\d+\.\s*)?(?:quest[õo]es\s+discursivas?|simulado discursivo)\b", re.I)
RX_FIM = re.compile(r"^(?:\d+\.\s*)?(?:refer[êe]ncias|fontes (?:normativas|oficiais)|revis[ãa]o e refer|quadro (?:de revis[ãa]o|geral)|checklist|gabarito e plano|plano de estudo|roteiro de resolu|gabarito anal[íi]tico|mapa de revis)", re.I)

def classifica(s):
    s = s.strip()
    if len(s) > 110: return None
    for nome, rx in (("casos", RX_CASOS), ("disc", RX_DISC), ("obj", RX_OBJ), ("fim", RX_FIM), ("fim", RX_FIM2)):
        if rx.match(s): return nome
    return None

def reflow(ls):
    """linhas -> blocos [('h', texto) | ('p', texto) | ('li', texto)]"""
    ls = [l.strip() for l in ls if l.strip()]
    if not ls: return []
    med = sorted(len(l) for l in ls)[len(ls) // 2] or 80
    out, buf, ult = [], "", 999
    def flush():
        nonlocal buf
        if buf.strip(): out.append(["p", re.sub(r"\s+", " ", buf).strip()])
        buf = ""
    for l in ls:
        sub = re.match(r"^(\d+\.\d+(?:\.\d+)*)\.?\s+\S.{2,100}$", l) and not l.rstrip().endswith((".", ";", ",", ":"))
        caps = l.isupper() and 6 < len(l) < 100
        li = l[:1] in "•▪●◦-–·" and len(l) > 2
        if sub or caps: flush(); out.append(["h", l]); ult = len(l); continue
        if li: flush(); out.append(["li", l.lstrip("•▪●◦-–· ").strip()]); ult = len(l); continue
        if buf and re.search(r"[.:;?!]\s*$", buf) and ult < 0.7 * med: flush(); buf = l
        else: buf += " " + l
        ult = len(l)
    flush(); return out

def parse_casos(ls):
    casos, cur = [], None
    for l in ls:
        m = re.match(r"^\s*Caso\s+(\d+)\s*(?:[—–:.\-]\s*(.*))?$", l, re.I)
        if m: cur = {"n": int(m.group(1)), "titulo": limpa(m.group(2) or ""), "corpo": []}; casos.append(cur)
        elif cur is not None: cur["corpo"].append(l)
    if not casos:
        txt = limpa(" ".join(l for l in ls if l.strip()))
        return [{"n": 1, "t": "", "e": txt, "s": ""}] if len(txt) > 40 else []
    res = []
    for c in casos:
        txt = " ".join(x.strip() for x in c["corpo"] if x.strip())
        # título inline "Caso 1 — Cheque apresentado tardiamente: texto..."
        titulo = c["titulo"]
        if not txt and ":" in titulo: titulo, txt = titulo.split(":", 1)
        elif txt == "" : txt = titulo; titulo = ""
        m = re.search(r"(?is)(?:enunciado|fatos?|situa[çc][ãa]o)\s*:\s*(.*?)(?=(?:diretriz de solu[çc][ãa]o|solu[çc][ãa]o|resolu[çc][ãa]o|resposta|an[áa]lise|gabarito|orienta[çc][ãa]o)\s*(?:esperada|comentada|sugerida)?\s*:|$)", txt)
        enun = limpa(m.group(1)) if m else ""
        m2 = re.search(r"(?is)((?:diretriz de solu[çc][ãa]o|solu[çc][ãa]o|resolu[çc][ãa]o|resposta|an[áa]lise|gabarito|orienta[çc][ãa]o)\s*(?:esperada|comentada|sugerida)?\s*:\s*.*)$", txt)
        sol = limpa(re.sub(r"^[^:]+:\s*", "", m2.group(1))) if m2 else ""
        if not enun: enun = limpa(txt[: m2.start()] if m2 else txt)
        res.append({"n": c["n"], "t": limpa(titulo), "e": enun, "s": sol})
    return res

GAB = re.compile(r"^\s*(?:Gabarito|Coment[áa]rio|Resposta)(?:\s+comentad[oa])?\s*:?\s*\(?([A-Ea-e])(?:\)|[.:;]|$)\s*(.*)$", re.I)
GABIN = re.compile(r"\b(?:Gabarito|Coment[áa]rio|Resposta)(?:\s+comentad[oa])?\s*:?\s*\(?([A-E])\)?[.:;)]?(?:\s+(.*))?$")
def _alts(e):
    pos, letra = [], 0
    for m in re.finditer(r"(?:(?<=\s)|^)\(?([A-E])\)\s", e):
        if letra < 5 and m.group(1) == "ABCDE"[letra]: pos.append(m); letra += 1
    if len(pos) >= 2:
        return e[: pos[0].start()].strip(), [limpa(e[m.end(): (pos[k + 1].start() if k + 1 < len(pos) else len(e))]).rstrip(";").strip() for k, m in enumerate(pos)]
    return e, []
def parse_obj(ls, chave_final=None):
    """Questões de múltipla escolha. Alternativas em linhas próprias ou inline; gabarito/comentário logo depois."""
    qs, cur, esperado, modo = [], None, None, "enun"
    for l in ls:
        s = l.strip()
        if not s: continue
        mg = GAB.match(s)
        if mg and cur is not None and modo != "com": cur["g"] = mg.group(1).upper(); cur["c"] = [mg.group(2)] if mg.group(2) else []; modo = "com"; continue
        mq = re.match(r"^(?:Quest[ãa]o\s+)?(\d{1,3})\s*[.)—–-]\s+(.*)$", s) or re.match(r"^Quest[ãa]o\s+(\d{1,3})()\s*$", s)
        if mq and (esperado is None or int(mq.group(1)) == esperado) and (cur is None or modo == "com" or GABIN.search(" ".join(cur["e"])) or len(" ".join(cur["e"])) > 40):
            esperado = int(mq.group(1)); cur = {"n": esperado, "e": [mq.group(2)], "g": None, "c": []}; qs.append(cur); esperado += 1; modo = "enun"; continue
        if cur is None: continue
        (cur["c"] if modo == "com" else cur["e"]).append(s)
    res = []
    for q in qs:
        e = limpa(" ".join(q["e"])); g = q["g"]; c = limpa(" ".join(q["c"]))
        if not g:
            m = GABIN.search(e)
            if m: g, c, e = m.group(1), (m.group(2) or ""), e[: m.start()].strip()
        e, alts = _alts(e)
        if len(alts) < 2 and not g: continue
        res.append({"n": q["n"], "e": e, "a": alts, "g": g, "c": c})
    return res

def parse_qa(ls):
    """Pergunta + 'Comentário:'/'Resposta:' (sem alternativas). Pergunta pode vir como 'Questão: ...' ou 'N. ...'."""
    res, cur = [], None
    for l in ls:
        t = l.strip()
        if not t: continue
        mc = re.match(r"^(?:Coment[áa]rio|Resposta|Gabarito)\s*:\s*(.*)$", t, re.I)
        if mc and cur is not None: cur["_c"] = True; cur["c"].append(mc.group(1)); continue
        m = re.match(r"^Quest[ãa]o\s*(?:\d+)?\s*:\s*(.*)$", t, re.I) or re.match(r"^(?:Quest[ãa]o\s+)?\d{1,3}\s*[.)—–-]\s+(.*)$", t)
        if m and (cur is None or cur["_c"]):
            cur = {"n": len(res) + 1, "e": [m.group(1)], "a": [], "g": None, "c": [], "_c": False}; res.append(cur); continue
        if cur is None: continue
        (cur["c"] if cur["_c"] else cur["e"]).append(t)
    if not any(q["_c"] for q in res):
        txt = limpa(" ".join(l for l in ls if l.strip()))
        sent = re.split(r"(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", txt); qs, cur2 = [], None
        for st in sent:
            if st.endswith("?"):
                if cur2 and not cur2["c"]: cur2["e"] += " " + st
                else: cur2 = {"e": st, "c": []}; qs.append(cur2)
            elif cur2 is not None: cur2["c"].append(st)
        return [{"n": k + 1, "e": q["e"], "a": [], "g": None, "c": " ".join(q["c"])} for k, q in enumerate(qs) if q["c"]]
    out = []
    for q in res:
        e, c = limpa(" ".join(q["e"])), limpa(" ".join(q["c"]))
        if not c:
            m = re.search(r"\s(?:Resposta|Coment[áa]rio)\s*:\s*", e)
            if m: e, c = e[: m.start()].strip(), e[m.end():].strip()
        if c: out.append({"n": len(out) + 1, "e": e, "a": [], "g": None, "c": c})
    return out

def parse_disc(ls):
    its, cur, esperado = [], None, None
    for l in ls:
        s = l.strip()
        if not s: continue
        mq = re.match(r"^(?:(?:Quest[ãa]o|Discursiva|Pergunta)\s+)?(\d{1,3})\s*[.)—–:-]\s*(.*)$", s) or re.match(r"^(?:Quest[ãa]o|Discursiva)\s+(\d{1,3})()\s*$", s)
        if mq and (esperado is None or int(mq.group(1)) == esperado) and (re.match(r"(?i)^(quest|discursiva|pergunta)", s) or re.match(r"^\d", s)):
            esperado = int(mq.group(1)); cur = {"n": esperado, "e": [mq.group(2)], "s": []}; its.append(cur); esperado += 1; continue
        if cur is None: continue
        if re.match(r"(?i)^(espelho|padr[ãa]o de resposta|resposta esperada|gabarito|resposta-modelo|crit[ée]rios?)\b", s) or cur["s"]: cur["s"].append(s)
        else: cur["e"].append(s)
    out = []
    for i in its:
        e, s = limpa(" ".join(i["e"])), limpa(" ".join(i["s"]))
        if not s:
            m = re.search(r"\s(?:Padr[ãa]o(?: de resposta)?|Espelho(?: de resposta)?|Resposta esperada|Resposta-modelo)\s*(?:\([^)]*\))?\s*:\s*", e)
            if m: e, s = e[: m.start()].strip(), e[m.end():].strip()
        s = re.sub(r"^(espelho(?: de resposta)?|padr[ãa]o de resposta|resposta esperada|resposta-modelo)\s*(?:\([^)]*\))?\s*:?\s*", "", s, flags=re.I)
        if e: out.append({"n": i["n"], "e": e, "s": s})
    return out

def gabarito_final(ls):
    """'Questão 7 — alternativa C' + comentário (cadernos de simulado)."""
    res, cur = {}, None
    for l in ls:
        m = re.match(r"^\s*Quest[ãa]o\s+(\d+)\s*[—–-]\s*alternativa\s+([A-E])\b[.:]?\s*(.*)$", l, re.I)
        if m: cur = int(m.group(1)); res[cur] = [m.group(2).upper(), [m.group(3)] if m.group(3) else []]
        elif cur is not None and l.strip() and not re.match(r"^\s*(\d+\.|Gabarito)", l): res[cur][1].append(l.strip())
    return {k: (v[0], limpa(" ".join(v[1]))) for k, v in res.items()}

def estruturar(linhas, nome):
    ls = sem_cabecalhos(linhas)
    # posições das seções especiais (usa a ÚLTIMA ocorrência de cada tipo: a primeira costuma ser o sumário)
    esp = [(i, classifica(l)) for i, l in enumerate(ls) if classifica(l)]
    ult = {}
    for i, k in esp:
        if re.match(r"^\s*\d+\.\s", ls[i]): ult[k] = i
    for i, k in esp:
        if k not in ult: ult[k] = i
    # sumário
    i_sum = next((i for i, l in enumerate(ls) if re.match(r"(?i)^sum[áa]rio\b", l.strip()) and len(l.strip()) < 40), None)
    sumario = []
    if i_sum is not None:
        j = i_sum + 1
        prox = 1
        while j < len(ls):
            mn = re.match(r"^\s*(\d{1,2})\.\s+\S", ls[j])
            if mn and int(mn.group(1)) == prox: sumario.append(limpa(ls[j])); prox += 1
            elif sumario and not mn and len(ls[j]) < 70 and j - i_sum < 45 and ls[j][:1].islower(): sumario[-1] += " " + limpa(ls[j])
            else: break
            j += 1
        fim_sum = j
    else: fim_sum = 0
    posicoes = sorted(set(i for i, k in esp if re.match(r"^\s*\d+\.\s", ls[i])) | set(ult.values()))
    primeiro_esp = min([p for k, p in ult.items() if k in ("casos", "obj", "disc")] or [len(ls)])
    # abertura (capa fora) até a 1ª seção numerada
    ini = next((i for i, l in enumerate(ls) if re.match(r"(?i)^(apresenta[çc][ãa]o|objetivos?|roteiro|orienta[çc]|nota editorial|projeto editorial|como utilizar|como estudar|delimita|posicionamento|ao final)", l.strip())), 0)
    # cabeçalhos numerados do corpo (cadeia sequencial 1..N após o sumário)
    heads, esperado = [], 1
    for i in range(fim_sum, primeiro_esp):
        s = ls[i].strip(); m = re.match(r"^(\d{1,2})\.\s+(.{3,110})$", s)
        if m and int(m.group(1)) == esperado and not s.rstrip().endswith((".", ":", "?", ";", ",")) and not classifica(s):
            heads.append((i, s)); esperado += 1
    # corpo teórico
    secoes = []
    if heads:
        abertura = ls[ini: heads[0][0]] if not sumario else [l for l in ls[ini: i_sum]] + ls[fim_sum: heads[0][0]]
        for (i, s), (j, _) in zip(heads, heads[1:] + [(primeiro_esp, "")]):
            secoes.append({"t": re.sub(r"^\d+\.\s*", "", s), "b": reflow(ls[i + 1: j])})
    else:
        abertura = ls[ini: (i_sum if (i_sum is not None and i_sum < primeiro_esp) else min(primeiro_esp, ini + 60))]
        corpo = ls[max(fim_sum, ini): primeiro_esp]
        if corpo: secoes.append({"t": "Conteúdo", "b": reflow(corpo)})
    abertura = [l for l in abertura if not re.match(r"(?i)^(sum[áa]rio)\s*$", l.strip())]
    ap = reflow([l for l in abertura][max(0, next((k for k, l in enumerate(abertura) if len(l.strip()) > 70 or re.match(r"(?i)^\s*(apresenta|objetivo)", l)), 0)):])
    if not sumario: sumario = [f"{k + 1}. {sc['t']}" for k, sc in enumerate(secoes)]
    # casos / objetivas / discursivas / referências
    def trecho(k):
        if k not in ult: return []
        i = ult[k]; fim = min([p for p in posicoes if p > i] or [len(ls)])
        return ls[i + 1: fim]
    ci, oi, di = ult.get("casos"), ult.get("obj"), ult.get("disc")
    casos = []; iq = None; tc = []
    if ci is not None:
        tc = trecho("casos"); iq = next((k for k, l in enumerate(tc) if re.match(r"^\s*Quest[ãa]o\s*:", l)), None)
        casos = parse_casos(tc[:iq] if iq is not None else tc)
    obj = parse_obj(trecho("obj")) if oi is not None else []
    if oi is not None and not obj: obj = parse_qa(trecho("obj"))
    if ci is not None and not obj and iq is not None: obj = parse_qa(tc[iq:])
    disc = parse_disc(trecho("disc")) if di is not None else []
    # questões embutidas na seção de casos ("Casos práticos e questões comentadas")
    if ci is not None and not obj and any(re.match(r"^\s*\(?[A-E]\)\s", l) for l in trecho("casos")): obj = parse_obj(trecho("casos"))
    # gabarito ao final (cadernos): completa quem não tem gabarito
    gf = gabarito_final(ls)
    for q in obj:
        if not q["g"] and q["n"] in gf: q["g"], q["c"] = gf[q["n"]]
    ref_i = ult.get("fim")
    refs = reflow(ls[ref_i + 1: ref_i + 80]) if ref_i is not None and ref_i > (di or oi or ci or 0) else []
    return {"ap": ap[:60], "sumario": sumario, "secoes": secoes, "casos": casos, "obj": obj, "disc": disc, "refs": refs[:40]}

# ---------------- varredura ----------------
arqs = sorted(f for f in os.listdir(PASTA) if f.lower().endswith(".pdf"))
cap = []
for f in arqs:
    nome = f[:-4]
    if nome.startswith(("Relatorio_", "Auditoria_", "Indice_", "Protocolo_")): continue
    linhas = ler(os.path.join(PASTA, f))
    disc, num_arq = meta(nome)
    bruto = [l for l in linhas if l.strip()]
    # consolidados (vários fascículos no mesmo PDF): divide em 'FASCÍCULO N — TÍTULO'
    partes = [(None, linhas)]
    if "Consolidado" in nome:
        idx = [i for i, l in enumerate(linhas) if re.match(r"^\s*FASC[ÍI]CULO\s+\d+\s*[—–-]\s*\S", l.strip()) and l.strip().isupper() or re.match(r"^\s*FASC[ÍI]CULO\s+\d+\s*[—–-]\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3}", l.strip())]
        if len(idx) >= 2:
            partes = []
            for a, b in zip(idx, idx[1:] + [len(linhas)]):
                m = re.match(r"^\s*FASC[ÍI]CULO\s+(\d+)\s*[—–-]\s*(.*)$", linhas[a].strip(), re.I)
                tit = m.group(2); k = a + 1
                while k < b and linhas[k].strip().isupper() and len(linhas[k].strip()) < 70 and not re.match(r"^\d+\.", linhas[k].strip()): tit += " " + linhas[k].strip(); k += 1
                partes.append(((int(m.group(1)), limpa(tit)), linhas[k:b]))
    if partes[0][0] is None and "Consolidado" in nome:
        idx2 = [i for i, l in enumerate(linhas) if re.match(r"^\s*FASC[ÍI]CULO\s+\d+\s*$", l.strip())]
        if len(idx2) >= 2:
            partes = []
            for a, b in zip(idx2, idx2[1:] + [len(linhas)]):
                num_f = int(re.search(r"\d+", linhas[a]).group()); k = a + 1; tit = []
                while k < b and len(tit) < 3 and not re.match(r"(?i)^\s*(base normativa|desenvolvimento|\d+\.\s|objetivo|pressuposto|escopo|fontes|delimita)", linhas[k]) and linhas[k].strip():
                    tit.append(linhas[k].strip()); k += 1
                t = limpa(" ".join(tit)); t = re.split(r"(?<=[a-zà-ú\)])\s+(?=Base normativa)", t)[0]
                partes.append(((num_f, t[:140]), linhas[k:b]))
    if partes[0][0] is None and "Consolidado" in nome:
        ult_f = {}
        for i, l in enumerate(linhas):
            m = re.match(r"^\s*F(\d{1,3})\s*[—–-]\s*(\S.*)$", l.strip())
            if m and len(l.strip()) < 200 and not re.match(r"(?i)^F\d+\s*[—–-]\s*F\d+", l.strip()): ult_f[int(m.group(1))] = (i, m.group(2))
        mr = re.search(r"Fasciculos_(\d+)_a_(\d+)", nome)
        ult_f = {n: v for n, v in ult_f.items() if mr and int(mr.group(1)) <= n <= int(mr.group(2))}
        blocos = sorted(ult_f.values())
        if len(blocos) >= 2:
            partes = []
            for (a, tit), nb in zip(blocos, blocos[1:] + [(len(linhas), "")]):
                num_f = [n for n, v in ult_f.items() if v[0] == a][0]
                partes.append(((num_f, limpa(tit)[:140]), linhas[a + 1: nb[0]]))
    for meta_p, trecho in partes:
        if meta_p: num, titulo = meta_p
        else:
            titulo, num = titulo_capa([l for l in trecho if l.strip()], nome); num = num or num_arq
            ta = titulo_arquivo(nome, trecho)
            if ta: titulo = ta
            if nome == "Direito_Civil_Volume_1_Fasciculo_1": titulo = "Fundamentos, personalidade e capacidade civil"
        est = estruturar(trecho, nome)
        mcut = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,:;/()\-–—&.]{10,}?)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç])", titulo)
        if mcut: titulo = mcut.group(1).strip(" ,:;-–—")
        titulo = tit_case(titulo) if titulo.isupper() else titulo
        cap.append({"arquivo": f, "disc": disc, "titulo": titulo, "num": num, "materia": materia(disc, titulo, nome), "est": est})

# ---------------- similaridade (para marcar temas repetidos) ----------------
STOP = set("para como mais pela pelo entre sobre quando onde deve podem será apenas ainda sendo essa esse isso cada outro outra seus suas desta deste nesta neste são foi era ser tem não uma com por que dos das nos nas aos ao em de da do a o e os as um ou se sua seu".split())
def texto_cap(c):
    e = c["est"]; partes = [b[1] for s in e["secoes"] for b in s["b"]] + [b[1] for b in e["ap"]]
    return " ".join(partes)
for c in cap:
    w = [x for x in re.findall(r"\w+", sa(texto_cap(c))) if len(x) > 3 and x not in STOP]
    c["tf"] = Counter(w)
df = Counter(); [df.update(c["tf"].keys()) for c in cap]
N = len(cap)
for c in cap:
    c["v"] = {t: (1 + math.log(n)) * math.log(N / df[t]) for t, n in c["tf"].items() if df[t] < N * 0.5}; c["nv"] = math.sqrt(sum(x * x for x in c["v"].values())) or 1
def cos(a, b):
    x, y = (a, b) if len(a["v"]) <= len(b["v"]) else (b, a)
    return sum(v * y["v"].get(t, 0) for t, v in x["v"].items()) / (a["nv"] * b["nv"])
pai = list(range(N))
def f(x):
    while pai[x] != x: pai[x] = pai[pai[x]]; x = pai[x]
    return x
pares = []
for i in range(N):
    for j in range(i + 1, N):
        if cap[i]["disc"] != cap[j]["disc"] and not (cap[i]["disc"] == "DIREITO CIVIL" or cap[j]["disc"] == "DIREITO CIVIL"): continue
        c = cos(cap[i], cap[j])
        if c >= 0.45: pai[f(i)] = f(j); pares.append((i, j, c))
grupos = {}
for i in range(N): grupos.setdefault(f(i), []).append(i)
for g in grupos.values():
    if len(g) > 1:
        manter = max(g, key=lambda k: len(texto_cap(cap[k])) + 800 * (len(cap[k]["est"]["obj"]) + len(cap[k]["est"]["casos"])))
        for k in g: cap[k]["grupo"] = f(k); cap[k]["manter"] = (k == manter); cap[k]["parecidos"] = [x for x in g if x != k]

# ---------------- mapa mental (a partir dos títulos das seções) ----------------
def arvore(c):
    raiz = {"t": c["titulo"][:90], "c": []}
    for s in c["est"]["secoes"][:14]:
        no = {"t": s["t"], "c": []}
        for tp, tx in s["b"]:
            if tp == "h" and re.match(r"^\d+\.\d+", tx): no["c"].append({"t": re.sub(r"^\d+(\.\d+)*\.?\s*", "", tx)})
        no["c"] = no["c"][:8]; raiz["c"].append(no)
    for nm, k in (("Casos práticos", "casos"), ("Questões objetivas", "obj"), ("Questões discursivas", "disc")):
        if c["est"][k]: raiz["c"].append({"t": f"{nm} ({len(c['est'][k])})"})
    return raiz

# ---------------- gravação ----------------
idx = []
for k, c in enumerate(sorted(cap, key=lambda c: (c["disc"], c["materia"], c["num"], c["titulo"]))):
    c["id"] = f"f{k:03d}"
for c in cap:
    e = c["est"]; tem_mapa = len(e["secoes"]) >= 3
    if tem_mapa: open(os.path.join(OUT, "mapas", c["id"] + ".svg"), "w", encoding="utf-8").write(svg_mapa(c["titulo"], arvore(c)))
    corpo = {"ap": e["ap"], "sumario": e["sumario"], "secoes": e["secoes"], "casos": e["casos"], "obj": e["obj"], "disc": e["disc"], "refs": e["refs"]}
    open(os.path.join(OUT, c["id"] + ".js"), "w", encoding="utf-8").write(f'(window.DOUT=window.DOUT||{{}})["{c["id"]}"]=' + json.dumps(corpo, ensure_ascii=False) + ";\n")
    paginas = max(1, round(sum(len(b[1]) for s in e["secoes"] for b in s["b"]) / 2400))
    idx.append({"id": c["id"], "disc": c["disc"], "materia": c["materia"], "titulo": c["titulo"], "ordem": c["num"], "paginas": paginas, "mapa": tem_mapa,
                "casos": len(e["casos"]), "obj": len(e["obj"]), "disc_q": len(e["disc"]), "secoes": len(e["secoes"]),
                "status": ("dup" if not c.get("manter", True) else ("manter" if c.get("grupo") is not None else "unico")),
                "grupo": c.get("grupo"), "parecidos": [cap[x]["id"] for x in c.get("parecidos", [])], "origem": c["arquivo"]})
open(os.path.join(OUT, "index.js"), "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
resumo = [{k: v for k, v in i.items()} for i in idx]
json.dump(resumo, open(os.path.join(RAIZ, "dados", "doutrina", "estrutura.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(idx), "capítulos |", sum(1 for i in idx if i["casos"]), "com casos |", sum(1 for i in idx if i["obj"]), "com objetivas |", sum(1 for i in idx if i["disc_q"]), "com discursivas |",
      "total: casos", sum(i["casos"] for i in idx), "obj", sum(i["obj"] for i in idx), "disc", sum(i["disc_q"] for i in idx), "| repetidos:", sum(1 for i in idx if i["status"] == "dup"))
