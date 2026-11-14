#!/usr/bin/env python3
"""Limpa os arquivos data/leis/*.js gerados pelo importador (idempotente):
 1) artigo "22-A" que veio como n="22" com o texto começando por "A. " (hífen perdido na fonte) -> n="22-A";
 2) redações sucessivas do mesmo artigo coladas uma após a outra (a página compilada do Planalto traz a antiga e a nova): mantém só a ÚLTIMA,
    descartando "(VETADO)" solto e fragmentos que começam em minúscula. Só mexe em duplicatas vizinhas (até 3 posições de distância);
    duplicatas distantes são apenas listadas, para conferência manual.
Uso: python tools/limpar_leis.py [--ver]   (--ver só mostra o que mudaria)"""
import glob, json, os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def lixo(t):
    t = t.strip()
    return (not t) or bool(re.fullmatch(r"\(VETADO\)\.?(?:\s*\([^)]*\))*", t)) or t[:1].islower()

def limpa(arts):
    mud = []
    # 1) letra solta
    ns = {a["n"] for a in arts}
    for a in arts:
        m = re.match(r"^([A-Z])\.\s+(.*)$", a["t"], re.S)
        if m and re.fullmatch(r"\d+", a["n"]) and (a["n"] + "-" + m.group(1)) not in ns:
            mud.append("n %s -> %s-%s" % (a["n"], a["n"], m.group(1)))
            a["n"] = a["n"] + "-" + m.group(1); a["t"] = m.group(2).strip(); ns.add(a["n"])
    # 2) versões vizinhas
    pos = {}
    for i, a in enumerate(arts): pos.setdefault(a["n"], []).append(i)
    remover = set(); longe = []
    for n, ix in pos.items():
        if len(ix) < 2: continue
        grupos = [[ix[0]]]
        for i in ix[1:]:
            (grupos[-1].append(i) if i - grupos[-1][-1] <= 3 else grupos.append([i]))
        if len(grupos) > 1: longe.append(n)
        for g in grupos:
            if len(g) < 2: continue
            bons = [i for i in g if not lixo(arts[i]["t"])] or g
            fica = bons[-1]
            for i in g:
                if i != fica: remover.add(i)
            mud.append("art. %s: %d redações -> mantida a última" % (n, len(g)))
    return [a for i, a in enumerate(arts) if i not in remover], mud, longe

def main():
    ver = "--ver" in sys.argv; tot = 0
    for f in sorted(glob.glob(os.path.join(R, "data", "leis", "*.js"))):
        s = open(f, encoding="utf-8").read(); ini = s.index("(") + 1; fim = s.rindex(");")
        lei = json.loads(s[ini:fim]); novo, mud, longe = limpa(lei["artigos"])
        if mud or longe:
            print("%s: %d -> %d artigos | %s%s" % (lei["id"], len(lei["artigos"]), len(novo), "; ".join(mud[:3]) + ("…" if len(mud) > 3 else ""),
                  ("  | duplicatas distantes (conferir): " + ",".join(longe[:8])) if longe else ""))
        if mud and not ver:
            lei["artigos"] = novo; tot += 1
            open(f, "w", encoding="utf-8").write(s[:ini] + json.dumps(lei, ensure_ascii=False) + s[fim:])
    print(tot, "arquivos reescritos" if not ver else "(simulação)")

if __name__ == "__main__":
    main()
