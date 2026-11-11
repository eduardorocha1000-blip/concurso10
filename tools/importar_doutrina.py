#!/usr/bin/env python3
"""Converte dados/doutrina/segmentos.json (gerado por auditar_doutrina.py) em arquivos carregados sob demanda:
data/doutrina/index.js (lista) e data/doutrina/fNNN.js (texto). Duplicatas ficam marcadas, nada é apagado.
"""
import json, os, re
from statistics import median
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
segs = json.load(open(os.path.join(RAIZ, "dados", "doutrina", "segmentos.json"), encoding="utf-8"))
OUT = os.path.join(RAIZ, "data", "doutrina"); os.makedirs(OUT, exist_ok=True)
import shutil
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT, exist_ok=True)
ruido = re.compile(r"^(?:VOLUME\s+[IVX]+.*|.*FASC[ÍI]CULOS?\s+\d+.{0,60}|CONCURSOS P[ÚU]BLICOS.*|DIREITO (?:ADMINISTRATIVO|CIVIL|PENAL|PROCESSUAL CIVIL|PROCESSUAL PENAL|DO CONSUMIDOR|EMPRESARIAL|CONSTITUCIONAL))$")
ruido0 = re.compile(r"^(?:.*P[áa]gina\s+\d+\s*|.*Fasc[íi]culos?\s+[\d A-Za-z]+\s*\|\s*\d+\s*|COLE[ÇC][ÃA]O DE DOUTRINA.*|CONCURSOS P[ÚU]BLICOS.*P[áa]gina.*)$")
cab = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+\S.{2,100}$")
def blocos(texto):
    texto = texto.replace(chr(127), " · ")
    ls = [l.strip() for l in texto.split("\n")]
    ls = [l for l in ls if l and not ruido.match(l) and not ruido0.match(l)]
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
    ls0 = [l.strip() for l in s["texto"].split(chr(10)) if l.strip()]
    m0 = re.match(r"(?i)^FASC[ÍI]CULO\s+(\d+)\s*[—–-]\s*(\S.*)$", ls0[0]) if ls0 else None
    if m0 and m0.group(2).strip()[:10].isupper():
        t0 = m0.group(2).strip()
        if len(ls0) > 1 and ls0[1].isupper() and len(ls0[1]) < 60 and not re.match(r"(?i)^(FASC|BASE LEGAL|PARTE|OBJETIVO)", ls0[1]): t0 += " " + ls0[1]
        return t0.replace(chr(127), " · ")[:105], int(m0.group(1))
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
    return texto[:105], (int(re.match(r"\d+", mnum.group(1)).group()) if mnum else 0)
import unicodedata
def sa(t): return unicodedata.normalize("NFD", t.lower()).encode("ascii", "ignore").decode()
REGRAS = {
 "DIREITO ADMINISTRATIVO": [("Direito Eleitoral", "eleitoral"), ("Direito Tributário", "\btribut"), ("Direito Financeiro e Orçamentário", "financeir|orcament"), ("Direito Urbanístico", "urbanis|cidade"), ("Direito Ambiental", "ambient"),
   ("Ministério Público e Tutela Coletiva", "ministerio publico|inquerito civil|organizacao do"), ("Improbidade e Anticorrupção", "improbidade"), ("Licitações, Contratos e Parcerias", "licita|contrata|terceiro setor|consorcio|convenio"),
   ("Serviços Públicos, Regulação e Estatais", "servico|concess|regula|agencia|economic|ppp|estatais|digital"), ("Agentes Públicos e Regime Disciplinar", "agentes|disciplinar|servidor"),
   ("Bens Públicos e Intervenção na Propriedade", "bens publicos|propriedade|desapropri|interven"), ("Responsabilidade Civil do Estado", "responsabilidade civil"), ("Processo Administrativo, Controle e Fazenda Pública", "controle|tribunais de contas|tce|processo administrativo|fazenda|judicializacao|sancionador|revisao|simulado"),
   ("Administração Municipal", "municipal")],
 "DIREITO CIVIL": [("Garantias e Propriedade Fiduciária", "fiduciari|hipoteca|penhor|anticrese|garantias reais"), ("Direitos Reais", "reais|posse|propriedade|usucap|condominio|laje|superficie|vizinhanca"), ("Família", "familia"), ("Sucessões", "sucess|legados|inventario|heranca|testament"), ("Responsabilidade Civil", "responsabilidade"),
   ("Contratos", "contrat|seguro|corretagem|transporte|renda|jogo|fianca|transacao|compromisso|comissao|agencia|vicios|aleatorios|evicao"), ("Obrigações", "obriga|adimplemento|inadimpl|pagamento|transmiss")],
 "DIREITO PROCESSUAL CIVIL": [("Recursos e Precedentes", "recurso|apelacao|precedente|irdr|reclamacao"), ("Execução e Cumprimento de Sentença", "execu|cumprimento|fiscal|insolv"), ("Procedimentos Especiais", "procedimentos especiais|monitoria|alimentos|locatic|inventario|oposicao|jurisdicao voluntaria|consignacao|dissolucao|juizados"),
   ("Processo Coletivo e Ações Constitucionais", "coletiv|mandado de seguranca|acoes constitucionais|saude, educacao"), ("Provas", "prova"), ("Tutela Provisória", "tutela provisoria"), ("Revisão e Simulados", "simulado|revisao"), ("Sentença e Coisa Julgada", "sentenca|coisa julgada")],
 "DIREITO PROCESSUAL PENAL": [("Recursos e Execução Penal", "recurso|execucao"), ("Prisões e Medidas Cautelares", "prisoes|prisao|cautelar|assecurat"), ("Provas", "prova|pericia|medicina legal|cibernetic"), ("Procedimentos, Nulidades e Legislação Especial", "procedimento|nulidade|legislacao|hediondos|juizados"),
   ("Jurisdição, Competência e Sujeitos", "jurisdicao|competencia|sujeitos|organizacao judiciaria"), ("Ação Penal e Investigação", "acao penal|principios|investig|inquerito"), ("Direitos Humanos e Revisão", "direitos humanos|revisao|atualizacao|probatoria")],
 "DIREITO PENAL": [("Parte Geral e Penas", "teoria geral|penas|dosimetria"), ("Crimes em Espécie", "crimes|dignidade|administracao|propriedade")],
 "CONSTITUCIONAL": [("Direito Constitucional", ".")], "DIREITO EMPRESARIAL": [("Direito Empresarial", ".")], "DIREITO DO CONSUMIDOR": [("Direito do Consumidor", ".")]}
NOME = {"DIREITO ADMINISTRATIVO": "Teoria Geral do Direito Administrativo", "DIREITO CIVIL": "Parte Geral do Direito Civil", "DIREITO PROCESSUAL CIVIL": "Processo de Conhecimento e Teoria Geral", "DIREITO PROCESSUAL PENAL": "Outros Temas de Processo Penal", "DIREITO PENAL": "Direito Penal"}
def curto(t):
    t = re.sub(r"(?i)^p[áa]gina \d+\s*", "", t.replace(chr(127), " "))
    t = re.sub(r"(?i)^.*?fasc[íi]culos?\s+\d+\s*[—–-]+\s*", "", t)
    t = re.split(r"\s{2,}| · | • | Código | CC,| Lei | Questões| Carga | Objetivo| Base legal| Estudo | Delimitação| Ideia | Estrutura | Esta | Este | Teoria,| Em Santa Catarina", t)[0]
    m = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9][A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,:;/()\-–—&.]{10,}?)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç])", t)
    if m: t = m.group(1)
    return t.strip(" —-:.")
def materia(disc, titulo, capa=""):
    for t in (sa(curto(titulo)), sa(capa)):
        for nome, rx in REGRAS.get(disc, []):
            if re.search(rx, t): return nome
    return NOME.get(disc, disc.title())
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_svg import svg_mapa
os.makedirs(os.path.join(OUT, "mapas"), exist_ok=True)
def arvore(blocos, titulo):
    """Árvore do capítulo a partir dos títulos numerados (1., 1.1, 1.1.1)."""
    raiz = {"t": titulo, "c": []}; pilha = [(0, raiz)]
    for tipo, txt in blocos:
        if tipo != "h": continue
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", txt)
        if not m: continue
        nome = m.group(2).strip()
        if re.match(r"(?i)^(sum[áa]rio|refer[êe]ncias|quest[õo]es|casos pr[áa]ticos|objetivos|como estudar)", nome): continue
        nome = nome.capitalize() if nome.isupper() else nome
        nv = m.group(1).count(".") + 1
        if nv > 2: continue
        while pilha and pilha[-1][0] >= nv: pilha.pop()
        no = {"t": nome, "c": []}; pilha[-1][1]["c"].append(no); pilha.append((nv, no))
    raiz["c"] = raiz["c"][:14]
    for n in raiz["c"]: n["c"] = n["c"][:8]
    return raiz
idx = []
for k, s in enumerate(segs):
    b = blocos(s["texto"])
    fid = f"f{k:03d}"
    open(os.path.join(OUT, fid + ".js"), "w", encoding="utf-8").write(f'(window.DOUT=window.DOUT||{{}})["{fid}"]=' + json.dumps(b, ensure_ascii=False) + ";\n")
    tt, num = titulo_limpo(s)
    if "CONCURSOS" in tt.upper() or len(tt.strip()) < 15:
        hs = [x[1] for x in b if x[0] == "h" and re.match(r"\d+\.", x[1]) and "SUM" not in x[1].upper()][:2]
        if hs: tt = " / ".join(re.sub(r"^\d+\.\s*", "", h) for h in hs)
    ar = arvore(b, (curto(tt) or tt)[:90]); tem_mapa = len(ar["c"]) >= 3
    if tem_mapa: open(os.path.join(OUT, "mapas", fid + ".svg"), "w", encoding="utf-8").write(svg_mapa(ar["t"], ar))
    st = "unico" if "grupo" not in s else ("manter" if s["manter"] else "dup")
    idx.append({"id": fid, "disc": s["disciplina"], "titulo": (curto(tt) or tt)[:120], "materia": materia(s["disciplina"], tt, " ".join(l for l in s["texto"][:500].split(chr(10)) if re.search(r"(?i)direito|volume", l))), "ordem": num, "mapa": tem_mapa, "paginas": s["paginas"], "status": st,
                "grupo": s.get("grupo"), "parecidos": [f"f{x:03d}" for x in s.get("parecidos", [])], "origem": s["arquivo"].replace("ilovepdf_merged", "m") + " p." + str(s["pag_ini"])})
open(os.path.join(OUT, "index.js"), "w", encoding="utf-8").write("window.DOUTRINA_IDX=" + json.dumps(idx, ensure_ascii=False) + ";\n")
print(len(idx), "fascículos;", sum(i["status"] == "dup" for i in idx), "marcados como possível duplicata;", sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) // 1024, "KB")
