#!/usr/bin/env python3
"""Importa acórdãos do STJ (Dados Abertos, espelhos de acórdãos) que tenham TESE JURÍDICA ou TEMA
(repetitivos/IAC) -> data/jur_stj.js (DATA.juris). Usa os N arquivos mensais mais recentes de cada órgão.
Uso: python tools/importar_stj.py [meses=6]
"""
import json, os, re, sys, time, urllib.request
API = "https://dadosabertos.web.stj.jus.br/api/3/action/"
HDR = {"User-Agent": "Mozilla/5.0 (estudo-pessoal)"}
ORGAOS = {"corte-especial": "Direito Público e Privado", "primeira-secao": "Direito Público", "primeira-turma": "Direito Público",
          "segunda-turma": "Direito Público", "segunda-secao": "Direito Privado", "terceira-turma": "Direito Privado",
          "quarta-turma": "Direito Privado", "terceira-secao": "Direito Penal", "quinta-turma": "Direito Penal", "sexta-turma": "Direito Penal"}
MESES = int(sys.argv[1]) if len(sys.argv) > 1 else 6

def get(u, t=180):
    for _ in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=HDR), timeout=t).read()
        except Exception: time.sleep(3)
    return None

def ok(v): return v and str(v).strip() not in ("None", "[]", "")

def main():
    out, vistos = [], set()
    for org, materia in ORGAOS.items():
        raw = get(API + "package_show?id=espelhos-de-acordaos-" + org)
        if not raw: print(org, "indisponível"); continue
        recs = sorted(json.loads(raw)["result"]["resources"], key=lambda r: r["name"])[-MESES:]
        for r in recs:
            b = get(r["url"])
            if not b: continue
            try: itens = json.loads(b.decode("utf-8", "replace"))
            except Exception: continue
            n = 0
            for x in itens:
                tese = x.get("teseJuridica") if ok(x.get("teseJuridica")) else None
                tema = x.get("tema") if ok(x.get("tema")) else None
                if not (tese or tema): continue
                ref = f"{x.get('siglaClasse','')} {x.get('numeroProcesso','')}/{x.get('numeroRegistro','')[:4]}".strip()
                if ref in vistos: continue
                vistos.add(ref); n += 1
                txt = re.sub(r"\s+", " ", (tese or "") + ((" [Tema: " + tema + "]") if tema else ""))
                out.append({"tribunal": "STJ", "ref": f"{ref} ({x.get('nomeOrgaoJulgador','').title()}, rel. {x.get('ministroRelator','').title()}, {x.get('dataDecisao','')})",
                            "materia": materia, "tese": txt.strip()[:700], "mods": ["oab", "magsc", "mpsc", "magfed"]})
            print(org, r["name"], n)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "jur_stj.js")
    open(path, "w", encoding="utf-8").write("DATA.juris.push(...(" + json.dumps(out, ensure_ascii=False) + "));\n")
    print(len(out), "teses importadas")
main()
