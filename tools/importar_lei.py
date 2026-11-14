#!/usr/bin/env python3
"""Baixa uma lei do Planalto (domínio público) e gera data/leis/<id>.js para o app.

Uso:
  python tools/importar_lei.py cf "Constituição Federal de 1988" "Direito Constitucional" oab,magsc,mpsc,magfed \
      https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm

Ids usados pelo heat.js: cf, cc, cpc, cp, cpp, cdc ... (use o mesmo id para substituir a amostra).
"""
import codecs, html, json, os, re, sys, urllib.request

def baixar(url):
    if os.path.exists(url):  # arquivo local: .pdf (requer pypdf) ou .txt/.html
        if url.lower().endswith(".pdf"):
            import pypdf
            t = chr(10).join((p.extract_text() or "") for p in pypdf.PdfReader(url).pages)
            return re.sub(r"(?m)^\s*-\s*\d+\s*-\s*$", "", t)  # remove numeração de páginas "- 3 -"
        return open(url, encoding="utf-8", errors="ignore").read()
    import time
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (estudo-pessoal)"})
    for tent in range(6):  # o servidor do Planalto às vezes derruba a conexão
        try:
            raw = urllib.request.urlopen(req, timeout=60).read()
            break
        except Exception as e:
            print("tentativa", tent + 1, "falhou:", e)
            time.sleep(3)
    else:
        sys.exit("não foi possível baixar")
    if raw[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):  # algumas páginas vêm em UTF-16
        return raw.decode("utf-16", errors="ignore")
    for enc in ("utf-8", "windows-1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue

def limpar(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", "", h)
    h = re.sub(r"(?is)<strike>.*?</strike>", "", h)           # dispositivos revogados
    h = re.sub(r"\s+", " ", h)                                # quebras de linha do HTML não são parágrafos
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", "", h)
    h = html.unescape(h).replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", h)

ART = re.compile(r"^\s*Art(?:igo)?\.?\s*(\d+(?:\.\d+)*)\s*[ºo°]?(?:-([A-Z])(?![a-zà-ú]))?\s*[-–.]?\s*(.*)$", re.I)

def artigos(txt, exigir_maiuscula=False):
    txt = re.sub(r"(\((?:Incluíd|Redação|Vide)[^)]*\))\s+(Art\.?\s*\d)", r"\1\n\2", txt)  # artigo colado à nota de alteração da linha anterior
    out, cur, pre = [], None, ""
    for ln in (l.strip() for l in txt.splitlines()):
        if not ln:
            continue
        if ln.upper().startswith("ATO DAS DISPOSI") and len(out) > 150:
            pre = "ADCT "
        m = ART.match(ln) if (not exigir_maiuscula or ln.startswith("Art")) else None
        if m and not ln.lower().startswith(("art. 1o do", "arts")):
            if cur: out.append(cur)
            n = pre + m.group(1) + ("-" + m.group(2).upper() if m.group(2) else "")
            cur = {"n": n, "t": (m.group(3) or "").strip()}
        elif cur:
            cur["t"] += "\n" + ln
    if cur: out.append(cur)
    for a in out: a["t"] = a["t"].strip()
    return out

def main():
    if len(sys.argv) < 6:
        sys.exit(__doc__)
    lid, nome, materia, mods, url = sys.argv[1:6]
    bruto = baixar(url)
    texto_puro = os.path.exists(url) and url.lower().endswith((".pdf", ".txt"))
    arts = artigos(bruto if texto_puro else limpar(bruto), exigir_maiuscula=texto_puro)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from limpar_leis import limpa; arts = limpa(arts)[0]  # versões sucessivas do mesmo artigo -> fica a última
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(os.path.join(base, "leis"), exist_ok=True)
    lei = {"id": lid, "nome": nome, "materia": materia, "mods": mods.split(","), "fonte": url, "artigos": arts}
    with open(os.path.join(base, "leis", lid + ".js"), "w", encoding="utf-8") as f:
        f.write("DATA.leis.push(" + json.dumps(lei, ensure_ascii=False) + ");\n")
    # atualiza manifesto
    arqs = sorted(x for x in os.listdir(os.path.join(base, "leis")) if x.endswith(".js"))
    with open(os.path.join(base, "leis_manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.LEI_FILES = " + json.dumps(arqs) + ";\n")
    print(f"{lid}: {len(arts)} artigos importados")

main()
