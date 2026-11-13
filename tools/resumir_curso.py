#!/usr/bin/env python3
"""Biblioteca de resumo extrativo para material de curso (degravações e apostilas em PDF já convertidos em texto).
Limpa ruído do curso, divide em seções, mantém só frases com conteúdo jurídico (definições, regras, artigos, súmulas, temas,
listas, prazos) e descarta exemplos, conversa de aula e o que já existe no app (similaridade TF-IDF por parágrafo)."""
import math, re, unicodedata
from collections import Counter

def sa(t): return unicodedata.normalize("NFD", (t or "").lower()).encode("ascii", "ignore").decode()
def limpa(s): return re.sub(r"\s+", " ", s or "").strip()

RUIDO = re.compile(r"(?i)^(\d+ de \d+\s*gran\.com\.br|gran\.com\.br|direito administrativo|curso preparat[óo]rio.*|quest[õo]es objetivas|[-�]+.*|"
                   r"este material foi elaborado.*|a presente degrava[çc][ãa]o.*|n[ãa]o recomendamos.*|preparado e ministrado.*|p[áa]gina \d+.*|\d+)$")
FILLER = re.compile(r"(?i)^(inicialmente|vamos|veja|ent[ãa]o,? |bem,? |pessoal|aluno|galera|na aula|nesta aula|nessa aula|como (vimos|dissemos|j[áa] estudamos)|lembrem|aten[çc][ãa]o|"
                    r"imagine|por exemplo|exemplo:|ex\.:|um exemplo|suponha|digamos|sabem|percebam|notem|observem|repito|fica a dica|dica:|o direito administrativo [ée] uma mat[ée]ria pequena|em direito administrativo, o aluno)")
SINAL = re.compile(r"(?i)(\bart(?:igo)?s?\.? ?\d|\bs[úu]mulas?\b|\btema\b|\bSTF\b|\bSTJ\b|\blei\b.{0,12}\d|\bCF\b|\bCRFB\b|\bdecreto\b|considera-se|constitui|consiste|[ée] (a|o|um|uma) |s[ãa]o (as|os)|"
                   r"veda|proibi|[ée] vedad|n[ãa]o (pode|poder[áa]|cabe|[ée] poss[íi]vel|se aplica)|poder[áa]|dever[áa]|compet[êe]ncia|prazo|\d+ (dias|anos|meses)|regra|exce[çc][ãa]o|excepcion|requisitos?|elementos?|caracter[íi]sticas?|esp[ée]cies?|modalidades?|hip[óo]teses?|cabe |dispensa|inexigibilidade|vedado|obrigat[óo]ri)")

def sentencas(par):
    par = re.sub(r"(?<=[a-z0-9\)])\.\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕ0-9])", ".\n", par)
    par = re.sub(r"(?<=[a-z0-9\)])[:;]\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕ])", lambda m: m.group(0).strip() + "\n", par) if False else par
    return [s.strip() for s in par.split("\n") if s.strip()]

def blocos(texto):
    """texto -> lista de ('h', título) | ('p', parágrafo)"""
    linhas = [l.rstrip() for l in texto.split("\n")]
    linhas = [l for l in linhas if l.strip() and not RUIDO.match(l.strip())]
    # remove cabeçalhos repetidos (linhas que aparecem muitas vezes)
    freq = Counter(l.strip() for l in linhas)
    linhas = [l for l in linhas if not (freq[l.strip()] >= 4 and len(l.strip()) < 80)]
    out, buf = [], ""
    def fl():
        nonlocal buf
        if buf.strip(): out.append(("p", limpa(buf)))
        buf = ""
    for l in linhas:
        s = l.strip()
        # título: caixa alta, terminando em ':' ou curto; ou "1) TÍTULO"
        cab = (s.upper() == s and len(s) > 3 and len(s) < 110 and re.search(r"[A-ZÁÉÍÓÚ]{4}", s)) or re.match(r"^\d+\)\s*[A-ZÁÉÍÓÚ ]{6,}:?$", s)
        if cab: fl(); out.append(("h", s.rstrip(":").strip())); continue
        if re.match(r"^([a-z]\)|[-•▪●]|\d+\.|[IVX]+\s*[-–.)])\s", s): fl(); buf = s; continue
        if buf and (buf.endswith((".", ":", ";", "?", "!"))) and re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕ0-9]", s) and len(buf) > 60: fl()
        buf += " " + s
    fl(); return out

def resumir_paragrafo(par, nivel=1):
    """mantém frases com sinal jurídico; descarta enchimento. nivel 1 = moderado, 2 = agressivo"""
    keep = []
    for s in sentencas(par):
        if len(s) < 25 or FILLER.match(s): continue
        if SINAL.search(s) or re.match(r"^([a-z]\)|[-•▪●]|\d+\.|[IVX]+\s*[-–.)])\s", s): keep.append(s)
        elif nivel == 1 and len(s) > 120 and re.search(r"(?i)(porque|pois|ou seja|isto [ée]|dessa forma|portanto)", s) is None: keep.append(s)
    return " ".join(keep)

class Indice:
    """TF-IDF para medir quanto um parágrafo já existe no app."""
    def __init__(self, textos):
        self.docs = [self.vet(t) for t in textos]
        df = Counter(); [df.update(d.keys()) for d in self.docs]
        self.n = max(1, len(self.docs)); self.idf = {t: math.log(1 + self.n / c) for t, c in df.items()}
        self.norm = [self._n(d) for d in self.docs]
    @staticmethod
    def vet(t):
        w = [x[:7] for x in re.findall(r"[a-z]{4,}", sa(t))]
        return Counter(w)
    def _n(self, d): return math.sqrt(sum((n * self.idf.get(t, 1)) ** 2 for t, n in d.items())) or 1
    def maxsim(self, t):
        q = self.vet(t); qn = math.sqrt(sum((n * self.idf.get(k, 1)) ** 2 for k, n in q.items())) or 1; best = 0
        for d, dn in zip(self.docs, self.norm):
            x, y = (q, d) if len(q) <= len(d) else (d, q)
            s = sum(n * self.idf.get(k, 1) ** 2 * y.get(k, 0) for k, n in x.items()) / (qn * dn)
            if s > best: best = s
        return best
