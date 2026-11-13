#!/usr/bin/env node
/* Conferência automática das citações do conteúdo escrito por IA contra as fontes oficiais que o app já tem:
   - artigos de lei  -> texto das leis em data/leis/*.js (Planalto);
   - súmulas         -> súmulas importadas (STF, STV, STJ, TST, TSE, STM, TJSC).
   Temas, REsp, ADI etc. e leis que não estão no app NÃO são verificáveis aqui e ficam como "pendentes".
   Resultado: data/conferencia.js (window.CONF). Uso: node tools/conferir.js
   Status "ok" só quando TODAS as citações do item foram localizadas (e há pelo menos uma). Não valida a interpretação jurídica. */
const fs = require('fs'), path = require('path'), vm = require('vm');
const R = path.resolve(__dirname, '..');
const ctx = { console }; ctx.window = ctx; vm.createContext(ctx);
const run = f => vm.runInContext(fs.readFileSync(path.join(R, f), 'utf8'), ctx, { filename: f });
['data/core.js', 'data/heat.js', 'data/jurisprudencia.js', 'data/estudo.js', 'data/treino.js', 'data/principios.js',
 'data/jur_stf.js', 'data/jur_stf_sumulas.js', 'data/jur_stj_sumulas.js', 'data/jur_tst.js', 'data/jur_tse.js', 'data/jur_stm.js', 'data/sumulas_tjsc.js']
  .forEach(f => { try { run(f); } catch (e) { console.error('aviso', f, e.message); } });
const DATA = ctx.DATA; if (!DATA.leis) DATA.leis = [];
fs.readdirSync(path.join(R, 'data/leis')).forEach(f => run('data/leis/' + f));

const VER = path.join(R, 'dados/verificacao'); fs.mkdirSync(VER, { recursive: true });
let RES = {}; try { RES = JSON.parse(fs.readFileSync(path.join(VER, 'resultado.json'), 'utf8')); } catch (e) {}
const CIT = {};   // citações judiciais únicas (para tools/verificar_tribunais.py)
const sa = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
// ---------- leis ----------
const leiPorId = {}, leiPorNum = {};
DATA.leis.forEach(l => {
  leiPorId[l.id] = l;
  const m = /(Lei Complementar|Lei|Decreto-Lei|LC)\s*(?:n[ºo°]\s*)?([\d.]+)\s*\/\s*(\d{2,4})/i.exec(l.nome || '');
  if (m) { const tipo = /compl|^LC$/i.test(m[1]) ? 'LC' : /decreto/i.test(m[1]) ? 'DL' : 'L'; leiPorNum[tipo + m[2].replace(/\./g, '')] = l; }
  (l.nome.match(/(Lei|Decreto-Lei|Lei Complementar)\s*n?[ºo°]?\s*[\d.]+\s*\/\s*\d+/gi) || []).forEach(s => { const mm = /([\d.]+)/.exec(s); if (mm) { const tipo = /compl/i.test(s) ? 'LC' : /decreto/i.test(s) ? 'DL' : 'L'; leiPorNum[tipo + mm[1].replace(/\./g, '')] = l; } });
});
const SIGLA = { CF: 'cf', CC: 'cc', CPC: 'cpc', CPP: 'cpp', CP: 'cp', CLT: 'clt', CDC: 'cdc', CTN: 'ctn', ECA: 'eca', EOAB: 'eoab', LINDB: 'lindb', LRF: 'lrf', LEP: 'lep', CTB: 'ctb', LAI: 'lai', LGPD: 'l13709' };
const NOMES = [['Constituição Federal', 'CF'], ['Constituição da República', 'CF'], ['Constituição', 'CF'], ['Código de Processo Civil', 'CPC'], ['Código de Processo Penal', 'CPP'], ['Código Civil', 'CC'], ['Código Penal', 'CP'],
  ['Código de Defesa do Consumidor', 'CDC'], ['Código Tributário Nacional', 'CTN'], ['Estatuto da Criança e do Adolescente', 'ECA'], ['Lei de Introdução às Normas do Direito Brasileiro', 'LINDB']];
const nomesRx = NOMES.map(n => n[0]).join('|');
const SIG = `(?:${nomesRx}|CPC|CPP|CDC|CTN|CTB|CLT|ECA|EOAB|CED|LINDB|LRF|LEP|LAI|LGPD|CF|CC|CP|Lei Complementar\\s*(?:n[ºo°]\\s*)?[\\d.]+\\s*\\/\\s*\\d+|LC\\s*[\\d.]+\\s*\\/\\s*\\d+|Decreto-Lei\\s*(?:n[ºo°]\\s*)?[\\d.]+\\s*\\/\\s*\\d+|Lei\\s*(?:n[ºo°]\\s*)?[\\d.]+\\s*\\/\\s*\\d+)`;
function resolveLei(s) {
  s = s.trim();
  for (const [n, sg] of NOMES) if (s === n) return { sig: sg, lei: leiPorId[SIGLA[sg]] };
  if (SIGLA[s] !== undefined) return { sig: s, lei: leiPorId[SIGLA[s]] };
  if (s === 'CED') return { sig: 'CED', lei: null };
  const m = /([\d.]+)\s*\/\s*\d+/.exec(s); if (!m) return { sig: s, lei: null };
  const tipo = /^(Lei Complementar|LC)/i.test(s) ? 'LC' : /^Decreto/i.test(s) ? 'DL' : 'L';
  return { sig: s.replace(/\s+/g, ' '), lei: leiPorNum[tipo + m[1].replace(/\./g, '')] || null };
}
function artigos(lista) {
  lista = lista.replace(/§§?\s*[\d,\sº°e\-–]+/g, ' ').replace(/par[áa]grafo [úu]nico/gi, ' ').replace(/incisos?\s+[IVXLC, e]+/g, ' ').replace(/Lei\s*[\d.]+\/\d+/g, ' ');
  const out = new Set();
  for (const m of lista.matchAll(/(?<![\d.\-])(\d{1,4}(?:\.\d{3})?)\s*[º°]?(?:-([A-Z])\b)?/g)) out.add(m[1] + (m[2] ? '-' + m[2] : ''));
  return [...out];
}
const stems = t => new Set((sa(t).match(/[a-z]{6,}/g) || []).map(w => w.slice(0, 5)));
const artCache = {};
function achaArtigo(lei, n) {
  const k = lei.id; if (!artCache[k]) { artCache[k] = {}; (lei.artigos || []).forEach(a => { artCache[k][String(a.n).replace(/[º°]/g, '').trim()] = a; }); }
  return artCache[k][n] || artCache[k][n.replace(/\./g, '')] || null;
}
// ---------- súmulas ----------
const suml = {};
[...(DATA.sumulas || []), ...(ctx.JUR_IMPORT || []).flat()].forEach(x => { if (x && x.n != null) suml[x.tribunal + '|' + String(x.n).replace(/\./g, '')] = x; });

function conferir(texto) {
  const ok = [], falta = [], fraco = [], nao = [], ctxT = stems(texto);
  const vistos = new Set();
  const testa = (sigStr, lista, herdado) => {
    lista = lista.split(/\b(?:LC|Lei|Decreto)\b/)[0];
    if (/[a-zà-ú]{3,}/.test(lista.replace(/\b(?:caput|incisos?|par[áa]grafo|[úu]nico|al[íi]neas?|[ao]s?|do|da|de)\b/g, ' '))) return;
    const { sig, lei } = resolveLei(sigStr);
    for (const n of artigos(lista)) {
      const id = 'art.' + n + ' ' + sig; if (vistos.has(id)) continue; vistos.add(id);
      if (!lei) { nao.push(id + ' (lei fora da base do app)'); continue; }
      const a = achaArtigo(lei, n);
      if (!a) { (herdado ? nao : falta).push(id + (herdado ? ' (sem lei indicada ao lado; presumi ' + sig + ' e não achei — confira a lei)' : ' (artigo não encontrado)')); continue; }
      const sA = stems(a.t || ''); let comum = 0; ctxT.forEach(s => { if (sA.has(s)) comum++; });
      (comum >= 2 ? ok : fraco).push(id);
    }
    return true;
  };
  // SIGLA, arts. N ...   e   arts. N ... SIGLA
  const cobertas = [], leis = [];
  for (const m of texto.matchAll(new RegExp(`\\b(${SIG})\\s*[,:]?\\s*[Aa]rts?\\.\\s*([^;()]{1,90}?)(?=;|\\)|\\.\\s+[A-ZÁÉÍÓÚ]|$)`, 'g'))) { testa(m[1], m[2]); cobertas.push([m.index, m.index + m[0].length]); leis.push([m.index, m[1]]); }
  for (const m of texto.matchAll(new RegExp(`[Aa]rts?\\.\\s*([^;()]{1,80}?)[,\\s]+(?:d[oae]s?\\s+)?(${SIG})(?![A-Za-zÀ-ú])`, 'g'))) { if (testa(m[2], m[1])) { cobertas.push([m.index, m.index + m[0].length]); leis.push([m.index, m[2]]); } }
  // artigos sem sigla ao lado: herdam a lei citada mais próxima (anterior; senão a primeira do texto); sem lei no texto, ficam pendentes
  for (const m of texto.matchAll(/[Aa]rts?\.\s*([\d.º°\-A-Z, §e]{1,30})/g)) {
    if (cobertas.some(([a, b]) => m.index >= a && m.index < b)) continue;
    const ant = leis.filter(l => l[0] < m.index).pop() || leis[0];
    if (ant) testa(ant[1], m[1], true); else { const id = 'art. ' + m[1].trim() + ' (lei não identificada no texto)'; if (!vistos.has(id)) { vistos.add(id); nao.push(id); } }
  }
  // súmulas
  for (const m of texto.matchAll(/S[úu]mulas?\s+(Vinculantes?\s+)?([\d.,\se]+?)\s*(?:\/|,)?\s*(?:d[oae]\s+)?(STF|STJ|TST|TSE|STM|TJSC)\b/g)) {
    const trib = m[1] ? 'STF-SV' : m[3];
    for (const n of m[2].match(/\d[\d.]*/g) || []) { const id = (m[1] ? 'SV ' : 'Súmula ') + n + '/' + m[3]; if (vistos.has(id)) continue; vistos.add(id);
      const s = suml[trib + '|' + n.replace(/\./g, '')]; if (!s) { falta.push(id + ' (não encontrada na base de súmulas)'); continue; }
      const sS = stems(s.texto || ''); let comum = 0; ctxT.forEach(x => { if (sS.has(x)) comum++; }); (comum >= 2 ? ok : fraco).push(id); } }
  for (const m of texto.matchAll(/\bSV\s*(\d+)/g)) { const id = 'SV ' + m[1] + '/STF'; if (vistos.has(id)) continue; vistos.add(id); (suml['STF-SV|' + m[1]] ? ok : falta).push(id); }
  // decisões judiciais: conferidas por tools/verificar_tribunais.py (STF: API do portal de jurisprudência; STJ: Dados Abertos)
  for (const m of texto.matchAll(/\b(Tema(?:s)?\s+(?:Repetitivo\s+)?([\d.]+)(?:\/(?:STF|STJ))?|(REsp|AREsp|RE|ARE|HC|RHC|ADI|ADPF|ADC|ADO|MS|RMS|Rcl|IRDR|IAC)\s*(?:n[ºo°]\s*)?([\d.]+)(?:\/[A-Z]{2})?)/g)) {
    const tipo = m[2] ? 'Tema' : m[3], num = (m[2] || m[4]).replace(/\./g, ''); if (!num || num.length > 8 || (tipo !== 'Tema' && num.length < 3)) continue;
    const id = tipo + ' ' + num; if (vistos.has(id)) continue; vistos.add(id);
    const janela = texto.slice(Math.max(0, m.index - 220), m.index + m[0].length + 220);
    if (!CIT[id]) CIT[id] = { tipo, num, ctx: janela };
    const r = RES[id], rot = m[1].replace(/\s+/g, ' ');
    if (!r) nao.push(rot + ' (precisa ser conferido no site do tribunal)');
    else if (r.r === 'ok') ok.push(rot + (r.u ? ' [' + r.u + ']' : ''));
    else if (r.r === 'fraco') fraco.push(rot + (r.u ? ' [' + r.u + ']' : ''));
    else nao.push(rot + ' (não localizado nos dados oficiais consultados: pode ser decisão monocrática, muito recente ou citação errada; confira no site do tribunal)');
  }
  const total = ok.length + falta.length + fraco.length + nao.length;
  return { s: (ok.length && !falta.length && !fraco.length && !nao.length) ? 1 : 0, ok: ok.length, t: total, v: ok.filter(x => /\[http/.test(x)).slice(0, 12), p: [...falta, ...fraco.map(x => x + ' (existe, mas o texto do artigo/súmula parece não tratar do assunto)'), ...nao].slice(0, 12) };
}
// ---------- chave estável (mesmo algoritmo em app.js) ----------
const strs = (v, out = []) => { if (typeof v === 'string') out.push(v); else if (Array.isArray(v)) v.forEach(x => strs(x, out)); else if (v && typeof v === 'object') Object.values(v).forEach(x => strs(x, out)); return out; };
const textoItem = x => Object.entries(x).filter(([k]) => k !== 'mods' && k !== 'id').flatMap(([, v]) => strs(v)).join(' ');
const hash = s => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return (h >>> 0).toString(36); };

const CONF = {}; const cont = { ok: 0, pend: 0 };
for (const colecao of ['principios', 'doutrina', 'exemplos', 'questoes', 'cards', 'discursivas', 'orais']) {
  (DATA[colecao] || []).forEach(x => { const t = textoItem(x).replace(/<[^>]+>/g, ' '); CONF[colecao + ':' + hash(textoItem(x))] = conferir(t); });
}
// capítulos da doutrina própria
const dir = path.join(R, 'data/doutrina');
if (fs.existsSync(dir)) fs.readdirSync(dir).filter(f => /^[fic]\d+\.js$/.test(f)).forEach(f => {
  const w = { DOUT: {} }; vm.runInNewContext(fs.readFileSync(path.join(dir, f), 'utf8'), { window: w }); const id = f.slice(0, -3);
  CONF['cap:' + id] = conferir(strs(w.DOUT[id]).join(' ').replace(/\s+/g, ' '));
});
Object.values(CONF).forEach(c => c.s ? cont.ok++ : cont.pend++);
fs.writeFileSync(path.join(VER, 'citacoes.json'), JSON.stringify(CIT));
fs.writeFileSync(path.join(R, 'data/conferencia.js'), 'window.CONF=' + JSON.stringify(CONF) + ';\n');
const por = {}; Object.entries(CONF).forEach(([k, c]) => { const g = k.split(':')[0]; por[g] = por[g] || [0, 0, 0, 0]; por[g][c.s ? 0 : 1]++; por[g][2] += c.ok; por[g][3] += c.t; });
console.log('Itens conferidos (ok) / pendentes / citações localizadas / citações totais:'); console.table(por);
