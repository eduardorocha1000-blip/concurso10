#!/usr/bin/env python3
"""Atualização diária: re-baixa as leis (fonte oficial http), detecta mudanças (vigência/redação),
atualiza súmulas do STF, grava data/changelog.js e faz backup. Seguro: se a nova coleta vier
vazia ou muito menor, restaura a versão anterior.
Uso: python tools/atualizar.py [--sem-leis] [--sem-stf]
"""
import datetime, glob, json, os, re, shutil, subprocess, sys, zipfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(RAIZ, "data")
PY = [sys.executable, "-I"]
HOJE = datetime.date.today().isoformat()
LOG = []

def log(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.append(s)

def carregar_lei(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"DATA\.leis\.push\((.*)\);\s*$", t, re.S)
    return json.loads(m.group(1)) if m else None

def norm(t): return re.sub(r"\s+", " ", t).strip()

def diff(velha, nova):
    a = {x["n"]: norm(x["t"]) for x in velha["artigos"]}
    b = {x["n"]: norm(x["t"]) for x in nova["artigos"]}
    return ([n for n in b if n not in a], [n for n in a if n not in b], [n for n in b if n in a and a[n] != b[n]])

def changelog_ler():
    p = os.path.join(DATA, "changelog.js")
    if not os.path.exists(p): return []
    m = re.search(r"=\s*(\[.*\]);", open(p, encoding="utf-8").read(), re.S)
    return json.loads(m.group(1)) if m else []

def atualizar_leis(ev):
    for p in sorted(glob.glob(os.path.join(DATA, "leis", "*.js"))):
        antiga_txt = open(p, encoding="utf-8").read()
        lei = carregar_lei(p)
        if not lei: continue
        if not str(lei.get("fonte", "")).startswith("http"):
            log(f"[{lei['id']}] fonte local — não atualizada automaticamente"); continue
        r = subprocess.run(PY + [os.path.join(RAIZ, "tools", "importar_lei.py"), lei["id"], lei["nome"], lei["materia"], ",".join(lei["mods"]), lei["fonte"]],
                           capture_output=True, text=True, timeout=600)
        nova = carregar_lei(p) if r.returncode == 0 else None
        if not nova or len(nova["artigos"]) < 0.8 * len(lei["artigos"]):
            open(p, "w", encoding="utf-8").write(antiga_txt)
            log(f"[{lei['id']}] coleta falhou/suspeita ({len(nova['artigos']) if nova else 0} x {len(lei['artigos'])}); mantida a versão anterior")
            continue
        add, rem, alt = diff(lei, nova)
        if add or rem or alt:
            log(f"[{lei['id']}] +{len(add)} -{len(rem)} alterados {len(alt)}")
            ev.append({"data": HOJE, "tipo": "lei", "id": lei["id"], "nome": lei["nome"], "fonte": lei["fonte"],
                       "novos": add[:60], "removidos": rem[:60], "alterados": alt[:60], "total": len(add) + len(rem) + len(alt)})

def atualizar_stf(ev):
    p = os.path.join(DATA, "jur_stf.js")
    antigo = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    n_ant = antigo.count('"tribunal"')
    r = subprocess.run(PY + [os.path.join(RAIZ, "tools", "importar_sumulas_stf.py")], capture_output=True, text=True, timeout=1800)
    novo = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    n_new = novo.count('"tribunal"')
    if r.returncode != 0 or n_new < 0.9 * n_ant:
        if antigo: open(p, "w", encoding="utf-8").write(antigo)
        log(f"[STF] coleta suspeita ({n_new} x {n_ant}); mantida a anterior"); return
    if n_new != n_ant:
        ev.append({"data": HOJE, "tipo": "sumulas", "id": "stf", "nome": "Súmulas do STF", "fonte": "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=30",
                   "novos": [], "removidos": [], "alterados": [], "total": abs(n_new - n_ant), "obs": f"{n_ant} → {n_new} súmulas"})
    log(f"[STF] {n_new} súmulas")

def backup():
    dest = os.path.join(RAIZ, "backups"); os.makedirs(dest, exist_ok=True)
    z = os.path.join(dest, f"data_{HOJE}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for raiz, _, arqs in os.walk(DATA):
            for a in arqs:
                f = os.path.join(raiz, a); zf.write(f, os.path.relpath(f, RAIZ))
    for velho in sorted(glob.glob(os.path.join(dest, "data_*.zip")))[:-7]: os.remove(velho)
    log("backup:", os.path.basename(z))

def main():
    ev = []
    backup()  # antes de mexer
    if "--sem-leis" not in sys.argv: atualizar_leis(ev)
    if "--sem-stf" not in sys.argv: atualizar_stf(ev)
    hist = [e for e in changelog_ler() if e["data"] != HOJE] + ev
    hist = hist[-400:]
    meta = {"ultima": datetime.datetime.now().isoformat(timespec="minutes"), "alteracoes_hoje": len(ev)}
    with open(os.path.join(DATA, "changelog.js"), "w", encoding="utf-8") as f:
        f.write("window.CHANGELOG = " + json.dumps(hist, ensure_ascii=False) + ";\nwindow.ATUALIZACAO = " + json.dumps(meta) + ";\n")
    open(os.path.join(RAIZ, "tools", "atualizar.log"), "a", encoding="utf-8").write(f"--- {HOJE}\n" + "\n".join(LOG) + "\n")
    log(f"concluído: {len(ev)} mudança(s) registradas")

main()
