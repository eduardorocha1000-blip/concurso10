#!/usr/bin/env python3
"""Servidor local do Jus Concursos: serve o app e faz a PESQUISA DE JURISPRUDÊNCIA ao vivo, sem armazenar nada.
  python tools/servidor.py [porta]        (padrão 8765)
Endpoints:
  GET  /api/tribunais                      lista de tribunais e do modo de pesquisa de cada um
  GET  /api/juris?t=<id>&q=<texto>&p=<pág>[&relator=&classe=&de=AAAA-MM-DD&ate=&tipo=acordaos|decisoes]
  POST /api/ia                             {tarefa, pergunta, decisoes:[...]}  (exige ANTHROPIC_API_KEY no ambiente deste PC)
Fontes: STF (pesquisa de texto completo, API pública do portal), DataJud/CNJ (metadados de processos de ~90 tribunais,
sem ementa/inteiro teor). Onde o site do tribunal bloqueia robôs (STJ, TJSC, TSE...), o app só oferece o link para a
pesquisa oficial. Nada é contornado: sem captcha, sem burla de bloqueio.
"""
import json, os, re, sys, threading, time, urllib.error, urllib.parse, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UA = {"User-Agent": "Mozilla/5.0 (estudo-pessoal)"}
DATAJUD_KEY = os.environ.get("DATAJUD_API_KEY", "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==")  # chave pública publicada pelo CNJ
DATAJUD = "https://api-publica.datajud.cnj.jus.br/api_publica_%s/_search"

# ---------------- catálogo de tribunais ----------------
def catalogo():
    T = []
    def add(id, nome, grupo, modo, alias=None, link=None):
        T.append({"id": id, "nome": nome, "grupo": grupo, "modo": modo, "alias": alias, "link": link})
    add("stf", "STF – Supremo Tribunal Federal", "Superiores", "texto", None, "https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&queryString={q}")
    add("stj", "STJ – Superior Tribunal de Justiça", "Superiores", "metadados", "stj", "https://scon.stj.jus.br/SCON/pesquisar.jsp?livre={q}")
    add("tst", "TST – Tribunal Superior do Trabalho", "Superiores", "metadados", "tst", "https://jurisprudencia.tst.jus.br/")
    add("tse", "TSE – Tribunal Superior Eleitoral", "Superiores", "metadados", "tse", "https://jurisprudencia.tse.jus.br/")
    add("stm", "STM – Superior Tribunal Militar", "Superiores", "metadados", "stm", "https://jurisprudencia.stm.jus.br/")
    ufs = "ac al am ap ba ce es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to".split()
    for u in ufs:
        add("tj" + u, "TJ" + u.upper(), "Justiça Estadual", "metadados", "tj" + u, {"sc": "https://busca.tjsc.jus.br/jurisprudencia/", "sp": "https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do"}.get(u, "https://www.tj%s.jus.br/" % u))
    add("tjdft", "TJDFT", "Justiça Estadual", "metadados", "tjdft", "https://www.tjdft.jus.br/")
    for n in range(1, 7): add("trf%d" % n, "TRF%d" % n, "Justiça Federal", "metadados", "trf%d" % n, "https://jurisprudencia.trf4.jus.br/pesquisa/pesquisa.php" if n == 4 else "https://www.trf%d.jus.br/" % n)
    for n in range(1, 25): add("trt%d" % n, "TRT%d" % n, "Justiça do Trabalho", "metadados", "trt%d" % n, "https://www.trt%d.jus.br/" % n)
    for u in ufs + ["dft"]:
        if u == "dft": add("tredft", "TRE-DFT", "Justiça Eleitoral", "metadados", "tre-dft", "https://www.tre-dft.jus.br/")
        else: add("tre" + u, "TRE-" + u.upper(), "Justiça Eleitoral", "metadados", "tre-" + u, "https://www.tre-%s.jus.br/" % u)
    for u in ("mg", "rs", "sp"): add("tjm" + u, "TJM-" + u.upper(), "Justiça Militar", "metadados", "tjm" + u, "https://www.tjm%s.jus.br/" % u)
    return T
TRIB = {t["id"]: t for t in catalogo()}

# ---------------- utilitários ----------------
_cache, _lock = {}, threading.Lock()
def cache_get(k):
    with _lock:
        v = _cache.get(k)
        return v[1] if v and time.time() - v[0] < 600 else None
def cache_set(k, v):
    with _lock: _cache[k] = (time.time(), v)
def http_json(url, corpo, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode("utf-8"), headers=dict(UA, **{"Content-Type": "application/json"}, **headers))
    for tentativa in range(3):
        try: return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 502, 503, 504) or tentativa == 2: raise
            time.sleep(4 * (tentativa + 1))
def conserta(s):
    """O DataJud às vezes devolve texto UTF-8 lido como Latin-1 ('PRESIDÃNCIA'); desfaz quando for o caso."""
    if isinstance(s, str) and re.search("[ÂÃ][-¿]", s):
        try: return s.encode("latin-1").decode("utf-8")
        except Exception: return s
    return s
def data_iso(v):
    d = re.sub(r"\D", "", str(v or ""))
    return "%s-%s-%s" % (d[0:4], d[4:6], d[6:8]) if len(d) >= 8 else None
def agora(): return time.strftime("%Y-%m-%dT%H:%M:%S")
def vazio(t):
    """Registro normalizado: todo campo pode ser nulo quando a fonte não informa."""
    return {"tribunal": t["nome"], "tribunal_id": t["id"], "grupo": t["grupo"], "id_original": None, "numero_processo": None, "classe": None, "relator": None,
            "orgao_julgador": None, "data_julgamento": None, "data_publicacao": None, "tipo_decisao": None, "ementa": None, "texto_integral": None,
            "inteiro_teor_url": None, "url_origem": None, "assuntos": None, "palavras_chave": None, "legislacao_citada": None, "precedente_qualificado": None,
            "disponibilidade": None, "verificado_em": agora(), "fonte": None}

# ---------------- STF ----------------
def buscar_stf(t, a):
    q = a["q"].strip() or "*"
    must = [{"query_string": {"query": q, "default_operator": "AND"}}]
    filt = [{"term": {"base": a.get("tipo") or "acordaos"}}]
    if a.get("relator"): must.append({"match_phrase": {"relator_processo_nome": a["relator"]}})
    if a.get("classe"): filt.append({"term": {"processo_classe_processual_unificada_classe_sigla": a["classe"].upper()}})
    if a.get("de") or a.get("ate"): filt.append({"range": {"julgamento_data": {k: v for k, v in (("gte", a.get("de")), ("lte", a.get("ate"))) if v}}})
    corpo = {"query": {"bool": {"must": must, "filter": filt}}, "from": (a["p"] - 1) * 10, "size": 10, "sort": [{"_score": "desc"}, {"julgamento_data": "desc"}],
             "_source": ["id", "titulo", "processo_codigo_completo", "processo_classe_processual_unificada_extenso", "relator_processo_nome", "relator_acordao_nome", "orgao_julgador",
                         "julgamento_data", "publicacao_data", "base", "ementa_texto", "inteiro_teor_url", "documental_indexacao_texto", "documental_legislacao_citada_texto", "is_repercussao_geral", "documental_tese_texto"]}
    r = http_json("https://jurisprudencia.stf.jus.br/api/search/search", corpo, {}, 60)["result"]["hits"]
    out = []
    for h in r["hits"]:
        s = h["_source"]; x = vazio(t)
        ind = s.get("documental_indexacao_texto"); leg = s.get("documental_legislacao_citada_texto")
        x.update({"id_original": s.get("id"), "numero_processo": s.get("processo_codigo_completo") or s.get("titulo"), "classe": s.get("processo_classe_processual_unificada_extenso"),
                  "relator": s.get("relator_acordao_nome") or s.get("relator_processo_nome"), "orgao_julgador": s.get("orgao_julgador"), "data_julgamento": s.get("julgamento_data"),
                  "data_publicacao": s.get("publicacao_data"), "tipo_decisao": "Acórdão" if s.get("base") == "acordaos" else s.get("base"), "ementa": s.get("ementa_texto") or s.get("documental_tese_texto"),
                  "inteiro_teor_url": s.get("inteiro_teor_url"), "url_origem": s.get("inteiro_teor_url"), "palavras_chave": [i.strip(" -.") for i in re.split(r",|\n", ind) if i.strip(" -.")][:15] if ind else None,
                  "legislacao_citada": (" ".join(leg) if isinstance(leg, list) else leg), "precedente_qualificado": bool(s.get("is_repercussao_geral")), "disponibilidade": "inteiro teor disponível no portal do STF", "fonte": "API de pesquisa do portal de jurisprudência do STF"})
        out.append(x)
    return out, r["total"]["value"]

# ---------------- DataJud (metadados) ----------------
def buscar_datajud(t, a):
    q = a["q"].strip(); num = re.sub(r"\D", "", q)
    must = []
    if len(num) == 20: must.append({"match": {"numeroProcesso": num}})
    elif q: must.append({"multi_match": {"query": q, "fields": ["assuntos.nome", "classe.nome", "orgaoJulgador.nome"], "operator": "and"}})
    if a.get("classe"): must.append({"match": {"classe.nome": a["classe"]}})
    if a.get("orgao"): must.append({"match": {"orgaoJulgador.nome": a["orgao"]}})
    if a.get("de") or a.get("ate"): must.append({"range": {"dataAjuizamento": {k: v for k, v in (("gte", a.get("de")), ("lte", a.get("ate"))) if v}}})
    corpo = {"size": 10, "from": (a["p"] - 1) * 10, "query": {"bool": {"must": must or [{"match_all": {}}]}}, "sort": [{"dataAjuizamento": {"order": "desc"}}], "track_total_hits": True}
    r = http_json(DATAJUD % t["alias"], corpo, {"Authorization": "APIKey " + DATAJUD_KEY}, 55)
    out = []
    for h in r.get("hits", {}).get("hits", []):
        s = h["_source"]; x = vazio(t); n = s.get("numeroProcesso") or ""
        fmt = "%s-%s.%s.%s.%s.%s" % (n[0:7], n[7:9], n[9:13], n[13:14], n[14:16], n[16:20]) if len(n) == 20 else n
        x.update({"id_original": h.get("_id"), "numero_processo": fmt, "classe": conserta((s.get("classe") or {}).get("nome")), "orgao_julgador": conserta((s.get("orgaoJulgador") or {}).get("nome")),
                  "data_julgamento": None, "data_publicacao": None, "assuntos": list(dict.fromkeys(conserta(a2.get("nome")) for a2 in (s.get("assuntos") or []) if a2.get("nome"))) or None,
                  "tipo_decisao": "Processo (metadados)", "disponibilidade": "somente metadados do DataJud; ementa e inteiro teor não são fornecidos", "fonte": "DataJud/CNJ",
                  "data_ajuizamento": data_iso(s.get("dataAjuizamento")), "grau": s.get("grau")})
        out.append(x)
    return out, (r.get("hits", {}).get("total") or {}).get("value", 0)

def pesquisar(a):
    t = TRIB.get(a["t"])
    if not t: raise ValueError("tribunal desconhecido")
    chave = json.dumps([a, t["id"]], sort_keys=True)
    c = cache_get(chave)
    if c: return c
    ini = time.time()
    try:
        res, total = buscar_stf(t, a) if t["id"] == "stf" else buscar_datajud(t, a)
        ans = {"tribunal": t["id"], "ok": True, "total": total, "resultados": res, "ms": int((time.time() - ini) * 1000), "modo": t["modo"], "link": (t["link"] or "").replace("{q}", urllib.parse.quote(a["q"]))}
    except Exception as e:
        ans = {"tribunal": t["id"], "ok": False, "erro": "%s: %s" % (type(e).__name__, str(e)[:160]), "resultados": [], "total": 0, "ms": int((time.time() - ini) * 1000), "modo": t["modo"], "link": (t["link"] or "").replace("{q}", urllib.parse.quote(a["q"]))}
    if ans["ok"]: cache_set(chave, ans)
    return ans

# ---------------- IA (opcional) ----------------
SISTEMA = ("Você é um assistente de estudo de Direito brasileiro. Trabalhe SOMENTE com as decisões fornecidas no JSON. "
           "Cite sempre tribunal e número do processo de cada decisão que usar. Não invente precedentes, números, datas, teses ou dispositivos que não estejam nos textos. "
           "Se as decisões fornecidas não bastarem para responder, diga isso claramente. Se só houver metadados (sem ementa), diga que não é possível analisar o mérito. Responda em português, de forma objetiva.")
def ia(corpo):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave: return {"ok": False, "erro": "IA indisponível: defina a variável de ambiente ANTHROPIC_API_KEY neste PC e reinicie o servidor."}
    dec = (corpo.get("decisoes") or [])[:12]
    tarefas = {"resumo": "Resuma cada decisão em até 4 linhas.", "tese": "Identifique a tese jurídica de cada decisão.", "fundamentos": "Liste os fundamentos utilizados.",
               "legislacao": "Liste a legislação citada.", "precedentes": "Liste os precedentes mencionados.", "comparar": "Compare as decisões.", "divergencias": "Identifique divergências entre as decisões, se houver.", "livre": ""}
    pedido = "%s\nPergunta/Instrução: %s\n\nDecisões recuperadas (JSON):\n%s" % (tarefas.get(corpo.get("tarefa"), ""), corpo.get("pergunta", ""), json.dumps(dec, ensure_ascii=False)[:60000])
    body = {"model": os.environ.get("JUS_MODEL", "claude-sonnet-5-5"), "max_tokens": 1800, "system": SISTEMA, "messages": [{"role": "user", "content": pedido}]}
    try:
        r = http_json("https://api.anthropic.com/v1/messages", body, {"x-api-key": chave, "anthropic-version": "2023-06-01"}, 120)
        return {"ok": True, "texto": "".join(b.get("text", "") for b in r.get("content", [])), "base": [d.get("numero_processo") for d in dec]}
    except Exception as e:
        return {"ok": False, "erro": "%s: %s" % (type(e).__name__, str(e)[:200])}

# ---------------- HTTP ----------------
class H(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map, **{".js": "text/javascript; charset=utf-8"})
    def __init__(s, *a, **k): super().__init__(*a, directory=RAIZ, **k)
    def log_message(s, f, *a): pass
    def _json(s, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        s.send_response(code); s.send_header("Content-Type", "application/json; charset=utf-8"); s.send_header("Content-Length", str(len(b))); s.send_header("Cache-Control", "no-store"); s.end_headers(); s.wfile.write(b)
    def do_GET(s):
        u = urllib.parse.urlparse(s.path)
        if u.path == "/api/tribunais": return s._json([{k: v for k, v in t.items() if k != "alias"} for t in TRIB.values()])
        if u.path == "/api/status": return s._json({"ia": bool(os.environ.get("ANTHROPIC_API_KEY"))})
        if u.path == "/api/juris":
            q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
            try: a = {"t": q.get("t", ""), "q": q.get("q", ""), "p": max(1, int(q.get("p", "1"))), "relator": q.get("relator"), "classe": q.get("classe"), "orgao": q.get("orgao"), "de": q.get("de"), "ate": q.get("ate"), "tipo": q.get("tipo")}
            except ValueError: return s._json({"erro": "parâmetros inválidos"}, 400)
            try: return s._json(pesquisar(a))
            except ValueError as e: return s._json({"erro": str(e)}, 400)
        return super().do_GET()
    def do_POST(s):
        if s.path != "/api/ia": return s._json({"erro": "não encontrado"}, 404)
        n = int(s.headers.get("Content-Length", "0") or 0)
        if n > 400000: return s._json({"erro": "corpo grande demais"}, 413)
        try: corpo = json.loads(s.rfile.read(n).decode("utf-8"))
        except Exception: return s._json({"erro": "JSON inválido"}, 400)
        return s._json(ia(corpo))

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print("Jus Concursos em http://localhost:%d (IA: %s)" % (porta, "ativa" if os.environ.get("ANTHROPIC_API_KEY") else "desativada"))
    class Srv(ThreadingHTTPServer):
        request_queue_size = 256   # o app abre dezenas de conexões de uma vez; o padrão (5) causa "connection reset"
        daemon_threads = True
    Srv(("0.0.0.0", porta), H).serve_forever()
