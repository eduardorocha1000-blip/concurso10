#!/usr/bin/env python3
"""Confere citações de decisões judiciais (Tema, REsp, AREsp, RE, ARE, ADI, ADPF, ADC, HC, RHC, MS, Rcl...) em fontes oficiais:
  - STF: API de pesquisa do portal de jurisprudência (jurisprudencia.stf.jus.br);
  - STJ: Portal de Dados Abertos (espelhos de acórdãos + precedentes qualificados), baixado por tools/baixar_stj_dados_abertos.py.
Lê dados/verificacao/citacoes.json (gerado por `node tools/conferir.js`) e grava dados/verificacao/resultado.json
(r: ok = existe e a ementa/tese trata do assunto citado; fraco = existe, mas o texto parece não tratar do assunto; nao = não encontrado).
Depois rode `node tools/conferir.js` de novo para atualizar as marcas. Retomável: só consulta o que ainda não está no resultado.
Uso: python tools/verificar_tribunais.py"""
import csv, glob, json, os, re, sys, time, unicodedata, urllib.request

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V = os.path.join(R, "dados", "verificacao")
cit = json.load(open(os.path.join(V, "citacoes.json"), encoding="utf-8"))
resf = os.path.join(V, "resultado.json")
RES = json.load(open(resf, encoding="utf-8")) if os.path.exists(resf) else {}

def sa(t): return unicodedata.normalize("NFD", (t or "").lower()).encode("ascii", "ignore").decode()
def stems(t): return {w[:5] for w in re.findall(r"[a-z]{6,}", sa(t))}
def sobrepoe(ctx, texto, minimo=2):
    return len(stems(ctx) & stems(texto)) >= minimo

# ---------------- STF ----------------
def stf_post(corpo, tent=3):
    for i in range(tent):
        try:
            r = urllib.request.Request("https://jurisprudencia.stf.jus.br/api/search/search", data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=60))["result"]["hits"]
        except Exception as e:
            time.sleep(3 * (i + 1)); err = e
    raise err
SRC = ["titulo", "processo_codigo_completo", "ementa_texto", "documental_tese_texto", "documental_tese_tema_texto", "documental_indexacao_texto", "julgamento_data", "inteiro_teor_url"]
def stf_proc(classe, num):
    for base in ("acordaos", "decisoes"):
        h = stf_post({"query": {"bool": {"must": [{"query_string": {"query": 'processo_codigo_completo:"%s %s"' % (classe, num), "default_operator": "AND"}}], "filter": [{"term": {"base": base}}]}}, "size": 5, "_source": SRC})
        if h["hits"]:
            s = h["hits"][0]["_source"]
            txt = " ".join(str(s.get(k) or "") for k in ("ementa_texto", "documental_tese_texto", "documental_tese_tema_texto", "documental_indexacao_texto", "titulo"))
            return {"t": "STF", "u": "https://portal.stf.jus.br/processos/listarProcessos.asp?classe=%s&numeroProcesso=%s" % (classe, num), "txt": txt, "d": (s.get("ementa_texto") or "")[:160]}
    return None
def stf_tema(n):
    h = stf_post({"query": {"bool": {"must": [{"query_string": {"query": 'documental_tese_tema_texto:"%s"' % n}}], "filter": [{"term": {"is_repercussao_geral": True}}]}}, "size": 6, "_source": SRC})
    for x in h["hits"]:
        s = x["_source"]; t = str(s.get("documental_tese_tema_texto") or "")
        if t.startswith("%s - " % n):
            txt = t + " " + str(s.get("documental_tese_texto") or "") + " " + str(s.get("ementa_texto") or "")
            return {"t": "STF", "u": "https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=%s" % n, "txt": txt, "d": t[:160]}
    return None

# ---------------- STJ ----------------
STJ = os.path.join(V, "stj")
_temas = None; _acord = None
NEEDED = {"%s %s" % (v["tipo"], v["num"]) for v in cit.values()}
def _lecsv(p):
    raw = open(p, "rb").read()
    try: t = raw.decode("utf-8-sig")
    except UnicodeDecodeError: t = raw.decode("latin-1")
    return list(csv.DictReader(t.splitlines()))
def stj_tema(n):
    global _temas
    if _temas is None: _temas = {r["numeroPrecedente"]: r for r in _lecsv(os.path.join(STJ, "precedentes-qualificados", "Temas.csv"))}
    r = _temas.get(str(n))
    if not r: return None
    return {"t": "STJ", "u": "https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?novaConsulta=true&tipo_pesquisa=T&cod_tema_inicial=%s&cod_tema_final=%s" % (n, n),
            "txt": " ".join(r.get(k) or "" for k in ("questaoSubmetidaAJulgamento", "teseFirmada", "Assuntos")), "d": (r.get("questaoSubmetidaAJulgamento") or "")[:160]}
def stj_indice():
    global _acord
    if _acord is not None: return
    _acord = {}
    for f in glob.glob(os.path.join(STJ, "espelhos-de-acordaos-*", "*.json")):
        try: dados = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        for d in dados:
            if not d.get("siglaClasse") or not d.get("numeroProcesso"): continue
            k = "%s %s" % (d["siglaClasse"].strip(), re.sub(r"\D", "", str(d["numeroProcesso"])))
            if k not in NEEDED: continue
            txt = " ".join(str(d.get(c) or "") for c in ("ementa", "teseJuridica", "tema", "informacoesComplementares"))
            if k not in _acord: _acord[k] = {"txt": txt, "d": (d.get("ementa") or "")[:160], "reg": d.get("numeroRegistro")}
            else: _acord[k]["txt"] += " " + txt
def stj_proc(classe, num):
    stj_indice(); a = _acord.get("%s %s" % (classe, num))
    if not a: return None
    return {"t": "STJ", "u": "https://scon.stj.jus.br/SCON/pesquisar.jsp?livre=%s+%s" % (classe, num), "txt": a["txt"], "d": a["d"]}

# ---------------- decisão ----------------
STFCL = {"ADI", "ADPF", "ADC", "ADO", "RE", "ARE", "Rcl"}
def trib_por_ctx(ctx):
    c = ctx.upper(); stf = len(re.findall(r"\bSTF\b|SUPREMO|REPERCUSS", c)); stj = len(re.findall(r"\bSTJ\b|SUPERIOR TRIBUNAL|REPETITIV", c))
    return "STF" if stf > stj else "STJ" if stj > stf else None
def conferir(id_, c):
    tipo, num, ctx = c["tipo"], c["num"], c["ctx"]; cand = []
    if tipo == "Tema":
        t = trib_por_ctx(ctx)
        for tr, fn in (("STF", stf_tema), ("STJ", stj_tema)):
            if t in (None, tr):
                r = fn(num)
                if r: cand.append(r)
    elif tipo in STFCL: r = stf_proc(tipo, num); cand = [r] if r else []
    elif tipo in ("REsp", "AREsp"): r = stj_proc(tipo, num); cand = [r] if r else []
    elif tipo in ("HC", "RHC", "MS", "RMS"):
        n = int(num); ordem = [("STJ", stj_proc), ("STF", stf_proc)] if n > 300000 and tipo in ("HC", "RHC") else [("STF", stf_proc), ("STJ", stj_proc)]
        for tr, fn in ordem:
            r = fn(tipo, num)
            if r: cand.append(r); break
    else: return None
    if not cand: return {"r": "nao", "t": "STF/STJ"}
    cand.sort(key=lambda r: -len(stems(ctx) & stems(r["txt"])))
    r = cand[0]
    return {"r": "ok" if sobrepoe(ctx, r["txt"], 1 if (tipo == "Tema" or tipo in STFCL) else 2) else "fraco", "t": r["t"], "u": r["u"], "d": r["d"]}

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    pend = [(k, v) for k, v in cit.items() if k not in RES and v["tipo"] not in ("IRDR", "IAC")]
    print(len(pend), "citações a conferir", flush=True)
    if any(v["tipo"] in ("REsp", "AREsp", "HC", "RHC", "MS", "RMS", "Tema") for _, v in pend): stj_indice(); print("índice do STJ pronto:", len(_acord), "processos citados localizados", flush=True)
    def uma(kv):
        k, v = kv
        try: return k, conferir(k, v)
        except Exception as e: return k, {"erro": str(e)[:80]}
    feitos = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for k, r in ex.map(uma, pend):
            feitos += 1
            if r and "erro" not in r: RES[k] = r
            if feitos % 25 == 0:
                json.dump(RES, open(resf, "w", encoding="utf-8"), ensure_ascii=False); print(feitos, "/", len(pend), flush=True)
    json.dump(RES, open(resf, "w", encoding="utf-8"), ensure_ascii=False)
    from collections import Counter
    print(Counter((v["r"], v.get("t")) for v in RES.values()))
