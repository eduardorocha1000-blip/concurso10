#!/usr/bin/env python3
"""Importa, de forma extrativa (sem inventar texto), o material de um curso de uma disciplina (apostilas, degravações e questões comentadas em PDF):
 - resume as aulas/apostilas por tema (só frases com conteúdo jurídico), sem repetir o que já está no app nem o que já entrou de outra fonte;
 - extrai as questões objetivas comentadas (enunciado, alternativas, gabarito e comentário da alternativa correta), sem repetir.
Saídas (privadas, ignoradas pelo git; vão para o backup privado): dados/curso/<slug>/*.json (capítulos) e data/curso/questoes_<slug>.js.
Uso: python tools/importar_curso.py "<pasta dos PDFs>" <slug> "<DISCIPLINA>"   ex.: ... "C:\\...\\Direito Administrativo" adm "DIREITO ADMINISTRATIVO"
Os textos dos PDFs são lidos com pypdf; dados pessoais (licenças, nomes) são descartados."""
import glob, hashlib, json, os, re, sys, unicodedata
from collections import Counter
import pypdf
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resumir_curso import Indice, sa, limpa

PASTA, SLUG, AREA = sys.argv[1], sys.argv[2], sys.argv[3]
OUTJ = os.path.join(R, "dados", "curso", SLUG); os.makedirs(OUTJ, exist_ok=True)
for f in glob.glob(os.path.join(OUTJ, "*.json")): os.remove(f)
os.makedirs(os.path.join(R, "data", "curso"), exist_ok=True)

# ---------------- leitura ----------------
def ler(p):
    return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(p).pages)
arquivos, vistos = [], {}
for p in sorted(glob.glob(os.path.join(PASTA, "*.pdf"))):
    t = ler(p); h = hashlib.md5(re.sub(r"\s+", "", t).encode()).hexdigest()
    if h in vistos: print("duplicado ignorado:", os.path.basename(p)[:60]); continue
    vistos[h] = p; arquivos.append((p, t))
print(len(arquivos), "arquivos distintos", flush=True)

# ---------------- limpeza ----------------
PESSOAL = re.compile(r"(?i)(licenciado para|vedada, por quaisquer meios|CPF|\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|[\uf000-\uf8ff]|gran\.com\.br|estrategia|este material foi elaborado|a presente degrava|n[ãa]o recomendamos a substitui|professor .* ministrada|\.{6,})")
def abrevia_seguras(s):
    return re.sub(r"\b(arts?|nº|n|inc|incs|al|par|cf|crfb|cc|cpc|cpp|ex|obs|p|pp|v|vs|dr|sr|min|ed)\.\s+(?=[\dA-Za-z§])", lambda m: m.group(0).replace(". ", ".\u0001"), s)
def sentencas(par):
    par = abrevia_seguras(par)
    par = re.sub(r"(?<=[a-zà-ú0-9\)\"”])\.\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕ“\"])", ".\n", par)
    return [x.replace("\u0001", " ").strip() for x in par.split("\n") if x.strip()]
def dobra(s):
    m = re.match(r"^(.{4,})\1$", s.replace(" ", "")); return s[: len(s) // 2].strip() if m and len(s) % 2 == 0 and s[: len(s) // 2] == s[len(s) // 2:] else (s[: len(s) // 2].strip() if re.match(r"^(\S.{3,}?)\1$", s) else s)
def blocos(texto):
    linhas = [l.rstrip() for l in texto.split("\n")]
    linhas = [l for l in linhas if l.strip() and not PESSOAL.search(l) and not re.match(r"^\s*(\d+ de \d+|P[áa]gina \d+.*|\d+|DIREITO [A-ZÇÃÕ ]+|QUEST[ÕO]ES OBJETIVAS)\s*$", l)]
    freq = Counter(l.strip() for l in linhas)
    linhas = [l for l in linhas if not (freq[l.strip()] >= 4 and len(l.strip()) < 90)]
    out, buf = [], ""
    def fl():
        nonlocal buf
        if buf.strip(): out.append(("p", limpa(buf)))
        buf = ""
    for l in linhas:
        s = l.strip()
        cab = (s.upper() == s and 3 < len(s) < 110 and re.search(r"[A-ZÁÉÍÓÚ]{4}", s) and not re.match(r"^[IVX]+\s*[-–.)]", s)) or re.match(r"^\d+(\.\d+)*\.?\s+[A-ZÁÉÍÓÚ][^.]{3,85}$", s) or re.match(r"^\d+\)\s*[A-ZÁÉÍÓÚ ]{6,}:?$", s)
        if cab: fl(); out.append(("h", dobra(s.rstrip(":").strip()))); continue
        if re.match(r"^([a-z]\)|[-•▪●]|[IVX]+\s*[-–.)])\s", s): fl(); buf = s; continue
        if buf and buf.endswith((".", ":", ";", "?", "!")) and re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕ0-9]", s) and len(buf) > 60: fl()
        buf += " " + s
    fl(); return out

# ---------------- seleção de frases ----------------
FILL = re.compile(r"(?i)^(inicialmente|vamos|veja|ent[ãa]o,? |bem,? |pessoal|aluno|galera|na aula|nesta aula|nessa aula|como (vimos|dissemos|j[áa] estudamos|veremos)|lembr|aten[çc][ãa]o|imagine|por exemplo|exemplo|ex\.:|um exemplo|suponha|digamos|sabem|percebam|notem|observem|repito|fica a dica|dica|sauda|trata-se de uma disciplina|nesta apostila|neste curso|bons estudos|[ée] importante (destacar|ressaltar|salientar) que o aluno|a seguir|passemos|passaremos)")
SIN = [re.compile(p, re.I) for p in (r"\bart(?:igo)?s?\.? ?\d|§", r"\bs[úu]mulas?\b|\btema\b|\bSTF\b|\bSTJ\b|\bTCU\b|\bADI\b|\bRE\b ?\d", r"\blei\b.{0,16}\d|\bdecreto\b|\bCRFB\b|\bCF\b", r"considera-se|constitui|consiste|[ée] (a|o|um|uma) |s[ãa]o (as|os)|significa|denomina|define",
       r"veda|proibi|[ée] vedad|n[ãa]o (pode|poder[áa]|cabe|[ée] poss[íi]vel|se aplica)|obrigat[óo]ri|dever[áa]|poder[áa]|cabe[m]? ", r"prazo|\d+ ?(dias|anos|meses|horas)|\d+ ?%|compet[êe]ncia|regra|exce[çc][ãa]o|requisito|elemento|caracter[íi]stic|esp[ée]cie|modalidade|hip[óo]tese|dispensa|inexigibilidade")]
def pontua(s): return sum(1 for r in SIN if r.search(s))
META = re.compile(r"(?i)(edital|prova|concurso|quest[ãa]o|banca|FGV|voc[êe]|aluno|cobrad|cai (muito|bastante)|custo-benef|segunda fase|primeira fase|aula|curso|professor|estud(e|ar|ante)|memoriz|macete|decor)")
LIGA = re.compile(r"(?i)^(ou seja|isso significa|dessa forma|assim,? |portanto|logo,? |em outras palavras|isto [ée]|com isso|nesse (sentido|contexto)|al[ée]m disso|por isso|dessa maneira|diante disso|nessa hip[óo]tese|nesse caso)")
def resumir(par, maxs, minimo=2):
    cand = []
    for i, s in enumerate(sentencas(par)):
        if not (28 <= len(s) <= 420) or FILL.match(s) or s.endswith("?"): continue
        sc = pontua(s)
        if META.search(s) and not (SIN[0].search(s) or SIN[1].search(s)): continue
        if LIGA.match(s): sc -= 1
        if re.match(r"^([a-z]\)|[-•▪●]|[IVX]+\s*[-–.)])\s", s): sc += 1
        if sc >= minimo: cand.append((sc, i, s))
    if len(cand) > maxs: cand = sorted(sorted(cand, key=lambda c: (-c[0], c[1]))[:maxs], key=lambda c: c[1])
    return " ".join(c[2] for c in cand)

# ---------------- corpus já existente no app (disciplina) ----------------
def corpus_existente():
    docs = []
    try: idx = json.loads(open(os.path.join(R, "data", "doutrina", "index.js"), encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
    except Exception: return docs
    ids = {x["id"] for x in idx if x["disc"] == AREA and x["id"][0] in "fi"}
    for id_ in ids:
        f = os.path.join(R, "data", "doutrina", id_ + ".js")
        if not os.path.exists(f): continue
        try: d = json.loads(open(f, encoding="utf-8").read().split("]=", 1)[1].rstrip().rstrip(";"))
        except Exception: continue
        for s in d.get("secoes", []):
            for b in s["b"]:
                if len(b[1]) > 60: docs.append(b[1])
    return docs
existentes = corpus_existente(); print(len(existentes), "parágrafos já no app (comparação)", flush=True)
IDX = Indice(existentes) if existentes else None
def shingles(t): w = re.findall(r"[a-z0-9]+", sa(t)); return {" ".join(w[i:i + 5]) for i in range(max(0, len(w) - 4))}
aceitos = []
def repetido(t, limiar=0.55):
    if IDX and IDX.maxsim(t) >= limiar: return True
    sh = shingles(t)
    if not sh: return False
    return any(len(sh & a) / max(1, min(len(sh), len(a))) >= 0.35 for a in aceitos)
def aceita(t): aceitos.append(shingles(t))

# ---------------- classificação por tema ----------------
def tema(nome, t):
    regras = [("Lei geral de proteção de dados (LGPD)", r"protecao-de-dados|lgpd|13-709"), ("Lei de acesso à informação", r"acesso-a-informacao|12-527"), ("Estatais (Lei 13.303/2016)", r"13-303|estatais"),
              ("Agências reguladoras (Lei 13.848/2019)", r"agencias-reguladoras|13-848"), ("Abuso de autoridade (Lei 13.869/2019)", r"abuso-de-autoridade|13-869"), ("Lei anticorrupção (Lei 12.846/2013)", r"anticorrupcao"),
              ("Improbidade administrativa", r"improbidade"), ("Licitações e contratos administrativos", r"licitac|contratos[- ]administrativos|nova-lei-de-licit"),
              ("Direito de petição e ações constitucionais", r"direito-de-peticao|acoes-constitucionais"), ("Intervenção do Estado na propriedade e domínio econômico", r"intervecao|intervencao"),
              ("Responsabilidade civil do Estado", r"responsabilidade-civil|responsabilidade civil"), ("Agentes públicos", r"agentes-publicos|agentes publicos"), ("Bens públicos", r"bens-publicos|bens publicos"),
              ("Serviços públicos", r"servico[- ]publico|servicos[- ]publicos"), ("Controle da administração pública", r"controle-da-administracao|controle da administracao"), ("Processo administrativo", r"processo[- ]administrativo"),
              ("Terceiro setor", r"terceiro-setor|terceiro setor"), ("Organização administrativa", r"organizacao-administrativa|organizacao administrativa"), ("Poderes da administração pública", r"poderes-da-administracao|poderes da administracao"),
              ("Atos administrativos", r"atos-administrativos|atos administrativos"), ("Princípios e introdução ao direito administrativo", r"introducao-ao-direito|principios do direito|^principios")]
    for alvo in (sa(t[:120]), sa(nome)):
        for nm, rx in regras:
            if re.search(rx, alvo): return nm
    return None

# temas já resumidos à mão (dados/curso/<slug>_resumos/*.json com campo "tema") não entram no resumo extrativo
SUBST = set()
for f in glob.glob(os.path.join(R, "dados", "curso", SLUG + "_resumos", "*.json")):
    try: SUBST.add(json.load(open(f, encoding="utf-8")).get("tema"))
    except Exception: pass
questoes_arq, teoria = [], {}
for p, t in arquivos:
    nome = os.path.basename(p)[:-4]
    primeira = next((l.strip() for l in t.split("\n")[1:4] if l.strip()), "")
    if re.search(r"(?i)^quest[õo]es objetivas$", primeira) or "preparacao-por-questoes" in nome: questoes_arq.append((nome, t)); continue
    tm = tema(nome, primeira)
    teoria.setdefault(tm or "Outros temas do curso", []).append((nome, t, primeira))

# ---------------- teoria ----------------
def eh_resumo(nome): return nome.startswith("resumo_")
capitulos = []
for tm in sorted(teoria):
    if tm in SUBST: print("tema substituído por resumo escrito:", tm); continue
    fontes = sorted(teoria[tm], key=lambda x: (not eh_resumo(x[0]), x[0]))   # aulas-resumo primeiro (já são condensadas), apostilas depois
    secoes, usados = [], 0; tem_aula = any(eh_resumo(x[0]) for x in fontes)
    for nome, t, primeira in fontes:
        corte = re.search(r"(?im)^\s*(quest[õo]es de concurso|lista de quest[õo]es|gabarito comentado|quest[õo]es comentadas)\s*$", t)
        if corte and corte.start() > 3000: t = t[: corte.start()]
        sec_atual = None; pular = False
        for k, x in blocos(t):
            if k == "h":
                sec_atual = {"t": x[:90], "b": []}; secoes.append(sec_atual); pular = bool(re.search(r"(?i)exerc[íi]cio|quest[õo]es|gabarito|^\d+\.\s*\d*\.?\s*\(|(CESPE|CEBRASPE|FCC|FGV|VUNESP|IBFC|IDECAN)", x)); continue
            if pular: continue
            r = resumir(x, 2 if (eh_resumo(nome) or not tem_aula) else 1, 2 if (eh_resumo(nome) or not tem_aula) else 3)
            if len(r) < 60 or re.match(r"^([a-d]\)|[IVX]+\s*[-–])", r) or repetido(r, 0.45): continue
            aceita(r)
            if sec_atual is None: sec_atual = {"t": "Visão geral", "b": []}; secoes.append(sec_atual)
            sec_atual["b"].append(["p", r]); usados += len(r)
    # junta seções homônimas, remove vazias
    fund, ordem = {}, []
    for s in secoes:
        if not s["b"]: continue
        k = sa(s["t"])
        if k in fund: fund[k]["b"] += s["b"]
        else: fund[k] = s; ordem.append(k)
    final = [fund[k] for k in ordem]
    if usados < 600 or not final: print("sem conteúdo inédito:", tm); continue
    capitulos.append({"area": AREA, "titulo": tm + " — resumo do curso", "materia": "Resumo do curso", "ordem": 500 + len(capitulos),
                      "fonte": "Material do curso (apostilas e degravações), resumido de forma extrativa; sem texto inventado.",
                      "ap": [["p", "Resumo extrativo do material do curso para este tema: foram mantidas só as frases com conteúdo jurídico (definições, regras, artigos, súmulas, prazos) e retirado o que já está em outros capítulos do app. Fonte: apostilas e degravações do curso."]],
                      "secoes": final, "casos": [], "obj": [], "disc": [], "refs": [["p", "Fonte: material do curso, de uso pessoal. Confira artigos, súmulas e temas citados (ver marca de conferência)."]]})
    print(f"{tm}: {usados} caracteres inéditos em {len(final)} seções", flush=True)
for i, c in enumerate(capitulos, 1):
    json.dump(c, open(os.path.join(OUTJ, "%02d_%s.json" % (i, re.sub(r"[^a-z0-9]+", "_", sa(c["materia"]))[:40])), "w", encoding="utf-8"), ensure_ascii=False)

# ---------------- questões ----------------
def parse_questoes(nome, t):
    t = "\n".join(l for l in t.split("\n") if not PESSOAL.search(l) and not re.match(r"^\s*(\d+ de \d+.*|Quest[õo]es Objetivas|DIREITO ADMINISTRATIVO|CURSO PREPARAT.*|QUEST[ÕO]ES OBJETIVAS)\s*$", l))
    g = re.search(r"(?m)^GABARITO\s*$", t); gab = {}
    if g:
        for m in re.finditer(r"(?m)^(\d{1,2})\.\s*([a-d])\s*$", t[g.end():]): gab[int(m.group(1))] = m.group(2).upper()
        t = t[: g.start()]
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^(\d{2})\. ", t)]
    res = []
    for k, (ini, num) in enumerate(marcas):
        fim = marcas[k + 1][0] if k + 1 < len(marcas) else len(t); bloco = t[ini:fim]
        linhas = bloco.split("\n"); enun, alts, i = [], [], 0
        enun.append(re.sub(r"^\d{2}\.\s*", "", linhas[0])); i = 1
        while i < len(linhas) and not re.match(r"^a\) ", linhas[i]): enun.append(linhas[i]); i += 1
        # alternativas a)..d), cada uma até o próximo marcador; a última até o fim do parágrafo
        cur = None
        while i < len(linhas):
            l = linhas[i]; m = re.match(r"^([a-d])\) (.*)$", l)
            if m and (cur is None or ord(m.group(1)) == ord(cur[0]) + 1) and len(alts) < 4: cur = [m.group(1), m.group(2)]; alts.append(cur); i += 1; continue
            if cur and len(alts) == 4 and cur[0] == "d":
                # fim da alternativa d: linha anterior termina em ponto/ponto-e-vírgula e esta começa com maiúscula
                prev = alts[-1][1]
                if prev.rstrip().endswith((".", ";", "?", "”")) and re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕ]", l.strip()): break
            if cur and len(alts) <= 4: cur[1] += " " + l.strip()
            i += 1
        resto = "\n".join(linhas[i:])
        if len(alts) != 4 or num not in gab: continue
        # comentário da alternativa correta: segunda ocorrência "x) ..." no resto
        letra = gab[num].lower(); com = ""
        m = re.search(r"(?ms)^%s\) (.*?)(?=^[a-d]\) |\Z)" % letra, resto)
        if m: com = limpa(m.group(1))
        res.append({"n": num, "e": limpa(" ".join(enun)), "a": [limpa(a[1]) for a in alts], "g": "ABCD".index(gab[num]), "c": com[:420].rsplit(" ", 1)[0] + ("…" if len(com) > 420 else "")})
    return res
todas, existentes_q = [], set()
for nome, t in questoes_arq: todas += [(nome, q) for q in parse_questoes(nome, t)]
def chave(q): return re.sub(r"[^a-z0-9]", "", sa(q["e"]))[:140]
uniq, vistos_q = [], set()
for nome, q in todas:
    k = chave(q)
    if k in vistos_q: continue
    vistos_q.add(k); uniq.append(q)
for i, q in enumerate(uniq, 1): q["id"] = "cq%s%d" % (SLUG, i)
js = "(function(){const M=['oab','magsc','mpsc','magfed'];const L=%s;L.forEach(q=>DATA.questoes.push({id:q.id,materia:%s,banca:'FGV/OAB (curso)',ano:'',enun:q.e,alts:q.a,gab:q.g,coment:q.c,mods:M}));})();\n" % (json.dumps(uniq, ensure_ascii=False), json.dumps({"DIREITO ADMINISTRATIVO": "Administrativo"}.get(AREA, AREA.title()), ensure_ascii=False))
open(os.path.join(R, "data", "curso", "questoes_%s.js" % SLUG), "w", encoding="utf-8").write(js)
print(len(todas), "questões lidas;", len(uniq), "distintas gravadas em data/curso/questoes_%s.js" % SLUG)
print(len(capitulos), "capítulos de teoria gerados em", OUTJ)
