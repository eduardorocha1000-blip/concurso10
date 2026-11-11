'use strict';
/* Jus Concursos — PWA offline. Estado do aluno em localStorage. */
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const store = {
  get(k, d) { try { const v = JSON.parse(localStorage.getItem('jus.' + k)); return v ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('jus.' + k, JSON.stringify(v)); } catch {} }
};
const TABS = [
  ['visao','Visão geral'],['leis','Leis'],['sumulas','Súmulas'],['principios','Princípios'],['enunciados','Enunciados'],
  ['juris','Jurisprudência'],['doutrina','Doutrina e prática']
];
const TAB_ENAM = ['enam', 'Guia ENAM'];   // só no módulo ENAM
const tabsDe = mod => mod.id === 'enam' ? [TABS[0], TAB_ENAM, ...TABS.slice(1)] : TABS;
const inMod = (x, m) => !x.mods || x.mods.includes(m);
const norm = n => String(n).replace(/[.º°ºo\s]/g, '').toLowerCase();

// ---- Mapa de calor (0–5 editais) ----
function score(item, leiId, m) {
  if (leiId) { const h = (HEAT[leiId] || {})[norm(item.n)]; return h ? (h[m] || 0) : 0; }
  const h = HEAT.x && leiId === null && item._k ? HEAT.x[item._k] : null;   // análise real (gerar_heat.py)
  if (h) return h[m] || 0;
  return (item.f && item.f[m]) || 0;
}
const stars = n => '<span class="stars" title="' + n + ' de 5 editais">' + '★'.repeat(n) + '☆'.repeat(5 - n) + '</span>';
const heatBadge = n => `<span class="heat h${n}">${n}/5 editais</span>`;
const legend = () => `<div class="legend mut"><span>Frequência nos 5 últimos editais:</span>${[0,1,2,3,4,5].map(n => `<span class="heat h${n}">${n}</span>`).join('')} ${HEAT.ilustrativo ? '' : ''}</div>`;
const demoBanner = () => HEAT.ilustrativo ? '<div class="banner">⚠️ Os números de frequência são <b>ILUSTRATIVOS</b> (amostra). Substitua por análise real dos editais em <code>data/heat.js</code> — veja SUGESTOES.md.</div>' : '';

// ---- Filtro ----
const filterBox = ph => `<input type="search" data-filter placeholder="${esc(ph || 'Filtrar…')}" aria-label="filtrar">`;
function applyFilter(q) {
  q = q.toLowerCase();
  document.querySelectorAll('[data-item]').forEach(el => { el.style.display = !q || el.textContent.toLowerCase().includes(q) ? '' : 'none'; });
}
function matSelect(items, m) {
  const mats = [...new Set(items.map(i => i.materia).filter(Boolean))];
  return mats.length > 1 ? `<select data-mat><option value="">Todas as matérias</option>${mats.map(x => `<option>${esc(x)}</option>`).join('')}</select>` : '';
}

// ---- Router ----
const state = { flow: null, card: null, show: false, quiz: {} };
function route() {
  const [, p1, p2, p3] = location.hash.split('/');
  const app = $('#app');
  $('#crumb').textContent = '';
  if (p1 === 'm' && DATA.modulos.find(x => x.id === p2)) {
    const mod = DATA.modulos.find(x => x.id === p2);
    const tab = VIEWS[p3] ? p3 : 'visao';
    $('#crumb').textContent = '› ' + mod.nome;
    app.innerHTML = `<h1>${mod.icone} ${esc(mod.nome)}</h1>
      <nav class="tabs">${tabsDe(mod).map(([k, n]) => `<a href="#/m/${mod.id}/${k}" class="${k === tab || (k === 'doutrina' && ['mapas','fluxos','exemplos','questoes','cards','discursivas','orais'].includes(tab)) ? 'on' : ''}">${n}</a>`).join('')}</nav>
      <div id="tab">${VIEWS[tab](mod)}</div>`;
    const on = app.querySelector('.tabs a.on'); on && on.scrollIntoView({ inline: 'center', block: 'nearest' });
  } else if (p1 === 'editais') {
    app.innerHTML = window.editaisView ? editaisView(p2) : '<p>Módulo indisponível.</p>'; window.editaisInit && editaisInit(p2);
  } else if (p1 === 'jurisprudencia') {
    app.innerHTML = window.jurisView ? jurisView() : '<p>Módulo indisponível.</p>'; window.jurisInit && jurisInit();
  } else if (p1 === 'busca') {
    app.innerHTML = buscaView();
  } else if (p1 === 'novidades') {
    app.innerHTML = novidadesView();
  } else if (p1 === 'backup') {
    app.innerHTML = backupView();
  } else app.innerHTML = home();
  window.scrollTo(0, 0);
}

function home() {
  const cards = store.get('cards', {}), qs = store.get('q', {});
  const now = Date.now(), due = DATA.cards.filter(c => !cards[c.id] || cards[c.id].due <= now).length;
  const ans = Object.values(qs), ok = ans.filter(a => a.ok).length;
  return `<p class="mut">Plataforma de estudos para concursos jurídicos. Funciona offline; seu progresso fica neste aparelho.</p>
  <div class="grid">${DATA.modulos.map(m => `<a class="card mod" style="--c:${m.cor}" href="#/m/${m.id}/visao"><h2>${m.icone} ${esc(m.nome)}</h2><div class="mut">${esc(m.desc)}</div></a>`).join('')}</div>
  <a class="card mod" style="--c:#334155" href="#/editais"><h2>📋 Editais</h2><div class="mut">A matéria (conteúdo programático) dos últimos editais de cada grande grupo: OAB, Magistratura SC, MPSC, Magistratura Federal e ENAM.</div></a>
  <div class="card"><h2>Seu progresso</h2>
    <p>🃏 Flashcards para revisar hoje: <b>${due}</b> de ${DATA.cards.length}</p>
    <p>✅ Questões respondidas: <b>${ans.length}</b> · Acertos: <b>${ans.length ? Math.round(100 * ok / ans.length) : 0}%</b></p>
    <div class="bar"><i style="width:${DATA.questoes.length ? Math.round(100 * ans.length / DATA.questoes.length) : 0}%"></i></div></div>
  ${statusAtualizacao()}
  <p><a href="#/editais">📋 Editais</a> · <a href="#/jurisprudencia">⚖️ Pesquisar jurisprudência</a> · <a href="#/busca">🔎 Pesquisar nos documentos</a> · <a href="#/novidades">🔔 Novidades</a> · <a href="#/backup">Backup / restaurar progresso</a></p>`;
}

const _alt = (() => { const m = {}; (window.CHANGELOG || []).forEach(e => e.tipo === 'lei' && (e.alterados.concat(e.novos)).forEach(n => ((m[e.id] = m[e.id] || {})[n] = e.data))); return m; })();
const _ch = () => window.CHANGELOG || [];
function statusAtualizacao() {
  const at = window.ATUALIZACAO; if (!at) return '<div class="banner">Atualização automática ainda não executada (rode tools/atualizar.py).</div>';
  const dias = (Date.now() - new Date(at.ultima).getTime()) / 864e5;
  const rec = _ch().filter(e => e.data >= new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10));
  return `<div class="card"><h3>🔔 Atualizações</h3><p class="mut">Última atualização da base: <b>${esc(at.ultima.replace('T', ' '))}</b>${dias > 2 ? ' — <b>desatualizada há mais de 2 dias</b>: verifique a tarefa agendada.' : ''}</p>
    <p>${rec.length ? rec.slice(-5).reverse().map(e => `• ${esc(e.data)} — ${esc(e.nome)}: ${e.total} mudança(s)`).join('<br>') : 'Nenhuma mudança nos últimos 7 dias.'}</p></div>`;
}
function novidadesView() {
  const h = _ch().slice().reverse();
  return `<h1>🔔 Novidades e controle de vigência</h1>${statusAtualizacao()}` + (h.map(e => `<details class="card"><summary>${esc(e.data)} — ${esc(e.nome)} <span class="tag">${e.total} mudança(s)</span></summary>
    ${e.obs ? `<p>${esc(e.obs)}</p>` : ''}${['novos', 'alterados', 'removidos'].map(k => (e[k] || []).length ? `<p><b>${{ novos: 'Artigos novos', alterados: 'Redação alterada', removidos: 'Removidos/revogados' }[k]}:</b> ${e[k].map(esc).join(', ')}</p>` : '').join('')}
    <p><a href="${esc(e.fonte)}" target="_blank" rel="noopener">Fonte oficial</a></p></details>`).join('') || '<p class="mut">Sem mudanças registradas ainda. O histórico se forma a cada execução diária.</p>') + '<p><a href="#/">Voltar</a></p>';
}
function buscaView() {
  return `<h1>🔎 Pesquisa nos documentos</h1><div class="card"><input data-bq type="search" placeholder="Ex.: saisine, art. 1.829, dolo eventual…" style="width:100%">
    <p class="mut">Pesquisa local em leis, súmulas, enunciados, jurisprudência e doutrina armazenados, com o trecho e a fonte. Não usa IA; não inventa resposta.</p></div><div id="bres"></div><p><a href="#/">Voltar</a></p>`;
}
function buscar(q) {
  q = q.trim().toLowerCase(); const out = $('#bres'); if (!out) return;
  if (q.length < 3) { out.innerHTML = ''; return; }
  const hits = [], add = (tipo, ref, texto, fonte) => { const i = texto.toLowerCase().indexOf(q); if (i >= 0 && hits.length < 80) hits.push({ tipo, ref, fonte, tr: (i > 60 ? '…' : '') + texto.slice(Math.max(0, i - 60), i + 200) }); };
  DATA.leis.forEach(l => l.artigos.forEach(a => add('Lei', l.nome.split('(')[0] + ' · art. ' + a.n, a.t, l.fonte)));
  DATA.sumulas.forEach(s => add('Súmula', s.tribunal + ' ' + s.n, s.texto, ''));
  (DATA.enunciados || []).forEach(s => add('Enunciado', s.fonte + ' ' + s.n, s.texto, ''));
  (DATA.juris || []).forEach(s => add('Jurisprudência', s.tribunal + ' ' + s.ref, s.tese, ''));
  DATA.doutrina.forEach(d => add('Doutrina', d.titulo, d.corpo.replace(/<[^>]+>/g, ' '), ''));
  const re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
  out.innerHTML = hits.map(h => `<div class="card"><span class="tag">${h.tipo}</span> <b>${esc(h.ref)}</b><div>${esc(h.tr).replace(re, '<mark>$1</mark>')}</div>${/^http/.test(h.fonte) ? `<a href="${esc(h.fonte)}" target="_blank" rel="noopener">Fonte oficial</a>` : ''}</div>`).join('') || '<p class="mut">Nada encontrado.</p>';
}
function exportar(id, fmt) {
  const l = DATA.leis.find(x => x.id === id); if (!l) return;
  const txt = l.nome + '\nFonte: ' + l.fonte + '\n\n' + l.artigos.map(a => 'Art. ' + a.n + ' ' + a.t).join('\n\n');
  const html = '<html><meta charset="utf-8"><body><h1>' + esc(l.nome) + '</h1>' + l.artigos.map(a => '<p><b>Art. ' + esc(a.n) + '</b> ' + esc(a.t).replace(/\n/g, '<br>') + '</p>').join('') + '</body></html>';
  const b = new Blob([fmt === 'doc' ? html : txt], { type: fmt === 'doc' ? 'application/msword' : 'text/plain;charset=utf-8' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = id + '.' + (fmt === 'doc' ? 'doc' : 'txt'); a.click();
}

const PRAT = { 'DIREITO CIVIL': ['Civil'], 'DIREITO PROCESSUAL CIVIL': ['Processo Civil'], 'DIREITO PENAL': ['Penal'], 'DIREITO PROCESSUAL PENAL': ['Processo Penal'], 'CONSTITUCIONAL': ['Constitucional'], 'DIREITO ADMINISTRATIVO': ['Administrativo'], 'DIREITO DO CONSUMIDOR': ['Consumidor'], 'DIREITO EMPRESARIAL': [] };
const PRAT_MAT = { 'Sucessões': ['Civil (Sucessões)'], 'Família': ['Civil (Família)'] };   // refinamentos dentro de Direito Civil
function pratica(mod, keys, titulo) {
  if (!keys || !keys.length) return '';
  const cat = [['mapas', '🧠 Mapas mentais', 'mapas'], ['fluxos', '🔀 Fluxogramas', 'fluxos'], ['exemplos', '💡 Exemplos', 'exemplos'], ['questoes', '✅ Questões comentadas', 'questoes'], ['cards', '🃏 Flashcards', 'cards'], ['discursivas', '✍️ Discursivas', 'discursivas'], ['orais', '🎤 Prova oral', 'orais']];
  const blocos = cat.map(([k, nome]) => { const n = DATA[k].filter(x => inMod(x, mod.id) && keys.includes(x.materia)).length; return n ? `<details class="card"><summary>${nome} <span class="tag">${n}</span></summary>${VIEWS[k](mod, keys)}</details>` : ''; }).join('');
  return blocos ? `<details class="card" style="border-left:4px solid var(--c,#1e6fb8)"><summary><b>📝 ${esc(titulo)}</b></summary>${blocos}</details>` : '';
}
function biblioteca(mod) {
  const idx = window.DOUTRINA_IDX; if (!idx || !idx.length) return '';
  const lido = store.get('dread', {}), mostrar = state.dup, byId = Object.fromEntries(idx.map(x => [x.id, x]));
  const vis = idx.filter(x => mostrar || x.status !== 'dup'), nLido = idx.filter(x => lido[x.id]).length, nDup = idx.filter(x => x.status === 'dup').length;
  const item = x => {
    const par = x.parecidos.map(id => byId[id]), jaLido = par.find(p => lido[p.id]);
    const aviso = x.status === 'dup' ? `<div class="banner">⚠ Mesmo assunto de: ${par.map(p => esc(p.titulo.slice(0, 80))).join(' · ')}. ${jaLido ? '<b>✅ Assunto já estudado em outro material.</b>' : ''}</div>` : '';
    return `<details class="card" data-item data-id="${x.id}"><summary>${esc(x.titulo)} <span class="tag">${x.paginas} pág.</span>${lido[x.id] ? '<span class="tag">✅ lido</span>' : ''}${x.status === 'dup' ? '<span class="tag">repetido</span>' : ''}</summary>${aviso}
      <p class="row"><button data-act="dread" data-id="${x.id}">${lido[x.id] ? 'Marcar como não lido' : 'Marcar como lido'}</button></p><div id="d-${x.id}"><button class="sec" data-act="dload" data-id="${x.id}">Abrir texto</button></div></details>`;
  };
  const porDisc = {}; vis.forEach(x => ((porDisc[x.disc] = porDisc[x.disc] || {})[x.materia] = (porDisc[x.disc][x.materia] || [])).push(x));
  const nome = d => d.replace(/^DIREITO /, 'Direito ').replace('PROCESSUAL', 'Processual').replace('CIVIL', 'Civil').replace('PENAL', 'Penal').replace('CONSTITUCIONAL', 'Direito Constitucional').replace('ADMINISTRATIVO', 'Administrativo').replace('EMPRESARIAL', 'Empresarial').replace('DO CONSUMIDOR', 'do Consumidor');
  return `<div class="card"><h3>📖 Doutrina própria (${vis.length} títulos)</h3><p class="mut">Lidos: <b>${nLido}</b>. ${nDup} títulos repetem o assunto de outro e ficam ocultos${mostrar ? ' (agora visíveis)' : ''}. Nada foi apagado.</p>
    <button class="sec" data-act="dup">${mostrar ? 'Ocultar' : 'Mostrar'} repetidos</button></div>`
    + Object.entries(porDisc).map(([d, ms]) => `<details class="card"><summary><b>${esc(nome(d))}</b> <span class="tag">${Object.values(ms).flat().length}</span></summary>
      ${pratica(mod, PRAT[d], 'Prática de ' + nome(d))}${Object.entries(ms).map(([m, xs]) => `<details class="card"><summary>${esc(m)} <span class="tag">${xs.length}</span></summary>${pratica(mod, d === 'DIREITO CIVIL' ? PRAT_MAT[m] : null, 'Prática: ' + m)}${xs.sort((a, b) => a.ordem - b.ordem || a.titulo.localeCompare(b.titulo)).map(item).join('')}</details>`).join('')}</details>`).join('')
    + pratica(mod, ['ECA', 'Ética (OAB)'], 'Prática de outras matérias (ECA e Ética)');
}
function carregarDoutrina(id) {
  const box = document.getElementById('d-' + id); if (!box) return;
  const ix = (window.DOUTRINA_IDX || []).find(x => x.id === id), mapaImg = ix && ix.mapa ? `<details class="card" open><summary>🧠 Mapa mental deste capítulo</summary><a href="data/doutrina/mapas/${id}.svg" target="_blank" rel="noopener"><img loading="lazy" src="data/doutrina/mapas/${id}.svg" alt="Mapa mental" style="max-width:100%;height:auto;background:#fff;border-radius:8px"></a><p class="mut">Toque para abrir em tamanho grande. Gerado a partir dos títulos do capítulo.</p></details>` : '';
  const pintar = () => { const b = (window.DOUT || {})[id]; box.innerHTML = b ? mapaImg + b.map(([t, x]) => t === 'h' ? `<h4>${esc(x)}</h4>` : `<p>${esc(x)}</p>`).join('') : '<p class="mut">Texto indisponível (arquivo não encontrado).</p>'; };
  if ((window.DOUT || {})[id]) return pintar();
  box.textContent = 'Carregando…';
  const sc = document.createElement('script'); sc.src = 'data/doutrina/' + id + '.js'; sc.onload = pintar; sc.onerror = pintar; document.head.appendChild(sc);
}

function backupView() {
  return `<h1>Backup do progresso</h1><div class="card"><p>Copie o texto abaixo para guardar seu progresso, ou cole um backup e restaure.</p>
  <textarea id="bk">${esc(JSON.stringify({ cards: store.get('cards', {}), q: store.get('q', {}), errcards: store.get('errcards', []), dread: store.get('dread', {}) }))}</textarea>
  <p class="row"><button data-act="restore">Restaurar</button><a class="btn sec" href="#/">Voltar</a></p></div>`;
}

// ---- Views ----
const VIEWS = {
  visao(mod) {
    const cnt = k => DATA[k].filter(x => inMod(x, mod.id)).length;
    const top = [];
    DATA.leis.filter(l => inMod(l, mod.id)).forEach(l => l.artigos.forEach(a => { const s = score(a, l.id, mod.id); if (s) top.push({ s, l, a }); }));
    top.sort((a, b) => b.s - a.s);
    return `${demoBanner()}<div class="card"><h3>📌 ${esc(mod.desc)}</h3><p><a class="btn" href="#/editais/${mod.id}">📋 Ver a matéria dos últimos editais deste grupo</a></p>
      <p><b>Editais analisados:</b> ${mod.editais.length ? mod.editais.map(e => esc(e.nome + ' (' + e.ano + ')')).join(' · ') : '<span class="mut">nenhum cadastrado ainda — edite data/core.js (veja SUGESTOES.md)</span>'}</p>
      <p><b>Matérias:</b> ${mod.materias.map(x => `<span class="tag">${esc(x)}</span>`).join('')}</p></div>
    <div class="card"><h3>🔥 Artigos mais cobrados</h3>${legend()}
      ${top.slice(0, 12).map(({ s, l, a }) => `<div class="art h${s}"><b>${esc(l.nome.split('(')[0])} · art. ${esc(a.n)}</b> ${stars(s)} ${heatBadge(s)}</div>`).join('') || '<p class="mut">Sem dados de frequência.</p>'}</div>
    <div class="card"><h3>📚 Conteúdo disponível</h3><div class="grid">
      ${[['leis','Leis'],['sumulas','Súmulas'],['principios','Princípios'],['enunciados','Enunciados'],['juris','Jurisprudência'],['doutrina','Textos de doutrina'],['mapas','Mapas mentais'],['fluxos','Fluxogramas'],['exemplos','Exemplos'],['questoes','Questões'],['cards','Flashcards'],['discursivas','Discursivas'],['orais','Perguntas orais']]
        .map(([k, n]) => `<a class="card" href="#/m/${mod.id}/${['mapas','fluxos','exemplos','questoes','cards','discursivas','orais'].includes(k) ? 'doutrina' : k}"><b>${cnt(k)}</b> ${n}</a>`).join('')}</div></div>`;
  },

  leis(mod) {
    const ls = DATA.leis.filter(l => inMod(l, mod.id));
    return `${demoBanner()}${legend()}<div class="row"><select data-minscore><option value="0">Todos os artigos</option><option value="1">★ 1+ editais</option><option value="3">★★★ 3+ editais</option><option value="5">★★★★★ 5 editais</option></select></div>
    ${filterBox('Buscar artigo ou texto…')}
    ${ls.map(l => `<details class="card" ${ls.length === 1 ? 'open' : ''}><summary>${esc(l.nome)} <span class="tag">${esc(l.materia)}</span>${l.parcial ? '<span class="tag">trecho</span>' : ''}</summary>
      <p class="row">${/^http/.test(l.fonte || '') ? `<a class="btn sec" href="${esc(l.fonte)}" target="_blank" rel="noopener">🔗 Publicação oficial</a>` : ''}<button class="sec" data-act="exp" data-id="${l.id}" data-f="txt">TXT</button><button class="sec" data-act="exp" data-id="${l.id}" data-f="doc">Word</button><button class="sec" onclick="window.print()">PDF (imprimir)</button></p>
      ${l.parcial ? '<p class="mut">Amostra. Para o texto completo, use tools/importar_lei.py.</p>' : ''}
      ${l.artigos.map(a => { const s = score(a, l.id, mod.id); return `<div class="art h${s}" data-item data-score="${s}"><b class="n">Art. ${esc(a.n)}</b>${/^\s*\((Revogad|Vetad)/i.test(a.t) ? '<span class="tag" style="background:#c0392b;color:#fff">não vigente</span>' : ''}${(_alt[l.id] || {})[a.n] ? `<span class="tag">alterado em ${_alt[l.id][a.n]}</span>` : ''}${stars(s)} ${s ? heatBadge(s) : ''}<div>${esc(a.t)}</div></div>`; }).join('')}</details>`).join('') || '<p>Sem leis para este módulo.</p>'}`;
  },

  sumulas(mod) { return listaJuris(mod, 'sumulas', x => `<b>${esc(x.tribunal === 'STF-SV' ? 'Súmula Vinculante' : 'Súmula ' + x.tribunal)} ${esc(x.n)}</b> ${x.vinculante ? '<span class="tag">vinculante</span>' : ''}${x.materia && x.materia !== 'Geral' && _sa(x.materia) !== _sa(ramoDe(x)) ? `<span class="tag">${esc(x.materia)}</span>` : ''}${x.orgao ? `<span class="tag">${esc(x.orgao)}${x.data ? ' · ' + esc(x.data) : ''}</span>` : ''}`, x => x.texto); },
  enunciados(mod) { return listaJuris(mod, 'enunciados', x => `<b>${esc(x.fonte)} · Enunc. ${esc(x.n)}</b><span class="tag">${esc(x.materia)}</span>`, x => x.texto); },
  juris(mod) { return '<div class="card"><a class="btn" href="#/jurisprudencia">⚖️ Pesquisar jurisprudência ao vivo nos tribunais</a></div>' + listaJuris(mod, 'juris', x => `<b>${esc(x.tribunal)}</b> — ${esc(x.ref)}<span class="tag">${esc(x.materia)}</span>`, x => x.tese); },

  principios(mod) {
    const it = DATA.principios.filter(x => inMod(x, mod.id));
    return filterBox('Filtrar princípios…') + matSelect(it, mod.id) + it.map(p => `<div class="card" data-item data-mat="${esc(p.materia)}"><b>${esc(p.nome)}</b> <span class="tag">${esc(p.materia)}</span><div>${esc(p.desc)}</div></div>`).join('');
  },

  doutrina(mod) {
    const it = DATA.doutrina.filter(x => inMod(x, mod.id));
    return biblioteca(mod) + filterBox('Filtrar doutrina…') + it.map(d => `<details class="card" data-item open><summary>${esc(d.titulo)} <span class="tag">${esc(d.materia)}</span></summary>${d.corpo}</details>`).join('');
  },

  mapas(mod, keys) {
    const tree = n => `<li><span class="nd">${esc(n.t)}</span>${n.c ? '<ul>' + n.c.map(tree).join('') + '</ul>' : ''}</li>`;
    return DATA.mapas.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia))).map(m => { const img = (window.MAPAS_IMG || {})[m.titulo]; return `<div class="card"><h3>🧠 ${esc(m.titulo)} <span class="tag">${esc(m.materia)}</span></h3>${img ? `<a href="${img}" target="_blank" rel="noopener"><img src="${img}" alt="Mapa mental: ${esc(m.titulo)}" loading="lazy" style="max-width:100%;height:auto;background:#fff;border-radius:8px"></a><p class="mut">Toque na imagem para abrir em tamanho grande.</p>` : `<ul class="tree">${tree(m.arvore)}</ul>`}</div>`; }).join('');
  },

  fluxos(mod, keys) {
    const fl = DATA.fluxos.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia)));
    return fl.map(f => {
      const i = DATA.fluxos.indexOf(f);
      const st = state.flow && state.flow.i === i ? state.flow : null;
      let body;
      if (!st) body = `<button data-act="flow" data-i="${i}">▶ Iniciar fluxograma</button> <details><summary>Ver todas as etapas</summary>${Object.entries(f.nos).map(([k, n]) => `<div class="node ${n.tipo}">${esc(n.t)}${(n.op || []).map(o => `<div class="mut">↳ ${esc(o[0])}</div>`).join('')}</div>`).join('')}</details>`;
      else {
        const n = f.nos[st.at];
        body = st.path.map(p => `<div class="node"><span class="mut">${esc(f.nos[p.id].t)}</span><br>➜ <b>${esc(p.ans)}</b></div><div class="arrow">↓</div>`).join('') +
          `<div class="node ${n.tipo}"><b>${esc(n.t)}</b></div>` +
          (n.op ? `<div class="row">${n.op.map(o => `<button class="sec" data-act="flowgo" data-i="${i}" data-to="${o[1]}" data-ans="${esc(o[0])}">${esc(o[0])}</button>`).join('')}</div>` : '<p><b>Fim.</b></p>') +
          `<p><button class="sec" data-act="flow" data-i="${i}">↺ Reiniciar</button></p>`;
      }
      return `<div class="card flow"><h3>🔀 ${esc(f.titulo)} <span class="tag">${esc(f.materia)}</span></h3>${body}</div>`;
    }).join('');
  },

  exemplos(mod, keys) {
    const it = DATA.exemplos.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia)));
    return (keys ? '' : filterBox('Filtrar exemplos…')) + it.map(x => `<details class="card" data-item><summary>${esc(x.titulo)} <span class="tag">${esc(x.materia)}</span></summary><p><b>Caso:</b> ${esc(x.caso)}</p><p><b>Resolução:</b> ${x.solucao}</p></details>`).join('');
  },

  questoes(mod, keys) {
    const all = DATA.questoes.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia))), st = store.get('q', {});
    const nOk = all.filter(q => st[q.id]?.ok).length, nErr = all.filter(q => st[q.id] && !st[q.id].ok).length, nNew = all.length - nOk - nErr;
    const f = keys ? 'todas' : (state.qf || 'todas');
    const qcard = q => { const a = st[q.id]; return `<div class="card" data-item><div class="mut">${esc(q.materia)} · ${esc(q.banca)} ${esc(q.ano)}</div><p>${esc(q.enun)}</p>
      ${q.alts.map((t, i) => `<button class="alt ${a ? (i === q.gab ? 'right' : i === a.pick ? 'wrong' : '') : ''}" data-act="ans" data-q="${q.id}" data-i="${i}" ${a ? 'disabled' : ''}>${'ABCDE'[i]}) ${esc(t)}</button>`).join('')}
      ${a ? `<div class="banner">${a.ok ? '✅ Correto.' : '❌ Errou.'} <b>Gabarito: ${'ABCDE'[q.gab]}</b><br>${esc(q.coment)}<br><button class="sec" data-act="redo" data-q="${q.id}">Refazer</button></div>` : ''}</div>`; };
    const qs = all.filter(q => f === 'erradas' ? st[q.id] && !st[q.id].ok : f === 'novas' ? !st[q.id] : true);
    const ms = {}; all.forEach(q => { const s = (ms[q.materia] = ms[q.materia] || { t: 0, ok: 0 }); if (st[q.id]) { s.t++; if (st[q.id].ok) s.ok++; } });
    const desemp = Object.entries(ms).filter(([, s]) => s.t).sort((a, b) => a[1].ok / a[1].t - b[1].ok / b[1].t)
      .map(([m, s]) => `<span class="tag">${esc(m)}: ${Math.round(100 * s.ok / s.t)}% (${s.ok}/${s.t})</span>`).join(' ');
    const btn = (v, n, c) => `<button class="${f === v ? '' : 'sec'}" data-act="qf" data-v="${v}">${n} (${c})</button>`;
    if (keys) return qs.map(qcard).join('') ;
    return `<div class="card"><div class="row">${btn('todas', 'Todas', all.length)}${btn('novas', 'Novas', nNew)}${btn('erradas', '📕 Caderno de erros', nErr)}</div>
      <p class="mut">Acertos: <b>${nOk}</b> · Erros: <b>${nErr}</b>. Cada erro vira um flashcard automático (aba Flashcards).</p>${desemp ? `<p class="mut">Desempenho por matéria (pior primeiro): ${desemp}</p>` : ''}</div>`
      + filterBox('Filtrar questões…') + (qs.length ? '' : '<p class="mut">Nenhuma questão neste filtro.</p>') + qs.map(qcard).join('');
  },

  cards(mod, keys) {
    if (keys) { const l = DATA.cards.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia))); return `<p class="mut">Toque no cartão para ver a resposta. Para revisar com repetição espaçada: <a href="#/m/${mod.id}/cards">revisão do dia</a>.</p>` + l.map(c => `<details class="card"><summary>${esc(c.f)}</summary><p><b>${esc(c.v)}</b></p></details>`).join(''); }
    const all = DATA.cards.concat(store.get('errcards', [])).filter(x => inMod(x, mod.id)), st = store.get('cards', {}), now = Date.now();
    const due = all.filter(c => !st[c.id] || st[c.id].due <= now);
    if (!due.length) return `<div class="card"><h3>🎉 Nada para revisar agora</h3><p class="mut">${all.length} flashcards neste módulo. Volte mais tarde.</p></div>`;
    const c = due[0];
    return `<p class="mut">${due.length} para revisar · repetição espaçada (algoritmo SM-2)</p>
    <div class="card flash" data-act="flip"><div><div class="tag">${esc(c.materia)}</div><p>${state.show ? '<b>' + esc(c.v) + '</b>' : esc(c.f)}</p>${state.show ? '' : '<span class="mut">toque para ver a resposta</span>'}</div></div>
    ${state.show ? `<div class="row"><button class="bad" data-act="rate" data-id="${c.id}" data-q="0">Errei</button><button class="mid" data-act="rate" data-id="${c.id}" data-q="3">Difícil</button><button class="ok" data-act="rate" data-id="${c.id}" data-q="4">Bom</button><button class="sec" data-act="rate" data-id="${c.id}" data-q="5">Fácil</button></div>` : ''}`;
  },

  discursivas(mod, keys) {
    const it = DATA.discursivas.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia)));
    return it.map(d => { const i = DATA.discursivas.indexOf(d); return `<details class="card"><summary>${esc(d.tema)} <span class="tag">${esc(d.materia)}</span></summary>
      <p>${esc(d.enun)}</p><textarea placeholder="Escreva sua resposta aqui (rascunho salvo automaticamente)" data-draft="d${i}">${esc(store.get('draft.d' + i, ''))}</textarea>
      <h3>Espelho de correção (autoavaliação)</h3>${d.espelho.map((e, j) => `<label style="display:block"><input type="checkbox" data-chk="d${i}_${j}" ${store.get('chk.d' + i + '_' + j, false) ? 'checked' : ''}> ${esc(e)}</label>`).join('')}</details>`; }).join('');
  },

  orais(mod, keys) {
    const it = DATA.orais.filter(x => inMod(x, mod.id) && (!keys || keys.includes(x.materia)));
    return `${keys ? '' : '<p class="mut">Responda em voz alta (cronometre 2–3 min) e só então abra a resposta-modelo.</p>'}${it.map(o => `<details class="card"><summary>${esc(o.pergunta)} <span class="tag">${esc(o.materia)}</span></summary><p>${esc(o.resposta)}</p></details>`).join('')}`;
  }
};

// ---- Guia do ENAM ----
const ENAM_DIST = [['Direito Constitucional (pode incluir Constitucional do Trabalho, Constitucional Tributário e normas constitucionais de Processo Penal)', 16, ['CONSTITUCIONAL']], ['Direito Civil', 12, ['DIREITO CIVIL']], ['Direito Processual Civil', 12, ['DIREITO PROCESSUAL CIVIL']], ['Direito Penal', 12, ['DIREITO PENAL']],
  ['Direito Administrativo', 10, ['DIREITO ADMINISTRATIVO']], ['Direitos Humanos', 6, []], ['Direito Empresarial', 6, ['DIREITO EMPRESARIAL']], ['Noções gerais de Direito e formação humanística', 6, []]];
VIEWS.enam = function (mod) {
  const idx = window.DOUTRINA_IDX || [], lido = store.get('dread', {}), chk = store.get('enamchk', {}), horas = +(store.get('enamh', 20));
  const linhas = ENAM_DIST.map(([nome, q, discs], i) => {
    const its = idx.filter(x => discs.includes(x.disc) && x.status !== 'dup'), n = its.length, l = its.filter(x => lido[x.id]).length;
    const h = Math.round(horas * q / 80 * 10) / 10;
    return `<tr><td>${esc(nome)}</td><td style="text-align:center"><b>${q}</b></td><td style="text-align:center">${Math.round(q / 0.8)}%</td><td style="text-align:center">${h} h</td>
      <td>${n ? `<div class="bar"><i style="width:${Math.round(100 * l / n)}%"></i></div><span class="mut">${l}/${n} lidos</span>` : '<span class="mut">sem doutrina importada</span>'}</td><td style="text-align:center"><input type="checkbox" data-enamchk="${i}" ${chk[i] ? 'checked' : ''}></td></tr>`;
  }).join('');
  return `<div class="card"><h3>📝 ENAM — Exame Nacional da Magistratura</h3>
    <p>Exame nacional organizado pela ENFAM (banca: FGV) que antecede os concursos de ingresso na magistratura. Prova objetiva única, de caráter <b>eliminatório</b> (não classificatório), com <b>80 questões</b> de múltipla escolha e 5 alternativas, sem nota negativa. Segundo as fontes consultadas, exige no mínimo <b>56 acertos</b> (40 para candidatos de vagas reservadas) e ocorre duas vezes por ano.</p>
    <div class="banner">A distribuição de questões e o programa abaixo foram conferidos nos editais do 5º (2026.1) e do 6º ENAM (2026.2) em <a href="#/editais/enam">Editais › ENAM</a>. A regra de aprovação (mínimo de 56 acertos; 40 nas vagas reservadas) vem de fontes secundárias: <b>confirme no edital da edição que você vai prestar</b> (FGV: conhecimento.fgv.br/exames/enam).</div></div>
  <div class="card"><h3>Distribuição de questões e plano de estudo</h3>
    <p class="row"><label>Horas de estudo por semana: <input type="number" min="1" max="80" value="${horas}" data-enamh style="width:70px"></label></p>
    <div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%"><thead><tr><th style="text-align:left">Disciplina</th><th>Questões</th><th>Peso</th><th>Horas/sem.</th><th>Leitura da doutrina</th><th>Revisada</th></tr></thead><tbody>${linhas}</tbody></table></div>
    <p class="mut">As horas semanais são proporcionais ao número de questões (80 no total). "Leitura da doutrina" conta os capítulos marcados como lidos em <a href="#/m/${mod.id}/doutrina">Doutrina e prática</a>, sem os repetidos.</p></div>
  <div class="card"><h3>Como usar este módulo</h3><ul>
    <li><b>Leis, súmulas, jurisprudência e doutrina</b> da magistratura estão neste módulo (os mesmos conteúdos de Magistratura Estadual SC e Federal).</li>
    <li>Em <a href="#/m/${mod.id}/doutrina">Doutrina e prática</a>, cada matéria traz os mapas mentais, exemplos, questões, flashcards, discursivas e prova oral relacionados.</li>
    <li>Pesquise decisões nos tribunais em <a href="#/jurisprudencia">⚖️ Pesquisa de jurisprudência</a>.</li>
    <li>Formação humanística e Direitos Humanos <b>ainda não têm doutrina nem questões</b> no app: precisam ser importadas ou escritas.</li></ul></div>`;
};
document.addEventListener('change', e => {
  const t = e.target;
  if (t.matches && t.matches('[data-enamchk]')) { const c = store.get('enamchk', {}); c[t.dataset.enamchk] = t.checked; store.set('enamchk', c); }
  if (t.matches && t.matches('[data-enamh]')) { store.set('enamh', Math.max(1, +t.value || 20)); route(); }
});

const chaveHeat = (key, x) => key === 'sumulas' ? 's|' + x.tribunal + '|' + x.n : key === 'enunciados' ? 'e|' + x.fonte + '|' + x.n : 'j|' + x.ref;
// ---- Ramo do direito das súmulas ----
const _sa = t => String(t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const RAMO_REGRAS = [['Consumidor', /consumidor|\bcdc\b|fornecedor/], ['Eleitoral', /eleitor|candidat|partido politic|eleicoes/], ['Previdenciário', /previdenci|aposentad|beneficio|pensao por morte|salario-maternidade|\binss\b|auxilio-doenca|\bloas\b/],
  ['Tributário', /tribut|imposto|\bicms\b|\biss\b|\bipi\b|\biptu\b|\bipva\b|\bpis\b|cofins|fisco|fiscal|contribuicao (social|de melhoria|previdenciaria)|taxa\b|alfandeg/], ['Trabalhista', /trabalhist|empregad|\bclt\b|justica do trabalho|\bfgts\b|rescisao|horas extras|sindical|sindicato/],
  ['Empresarial', /falencia|recuperacao judicial|sociedade (anonima|empresaria|limitada)|titulo de credito|cheque|duplicata|nota promissoria|marca\b|patente|arrendamento mercantil/], ['Administrativo', /servidor|concurso publico|licitac|administracao publica|ato administrativo|desapropria|improbidade|agente publico|policial militar/],
  ['Constitucional', /constitu|direitos fundamentais|mandado de (seguranca|injuncao)|extradicao|repercussao geral|\bstf\b|supremo/], ['Processual Penal', /habeas corpus|inquerito|denuncia|pronuncia|\bjuri\b|acao penal|prisao preventiva|liberdade provisoria|queixa-crime|justica criminal|juizo criminal|recurso em sentido estrito/],
  ['Penal', /crime|\bpena\b|penal|furto|roubo|trafico|homicid|reincidencia|regime (fechado|semiaberto|aberto)|dosimetria|falta grave|livramento condicional|execucao penal/], ['Civil', /contrato|indeniza|dano moral|responsabilidade civil|posse\b|propriedade|usucapi|familia|alimentos|heranca|locacao|seguro|condominio|casamento|uniao estavel|filiacao/],
  ['Processual Civil', /recurso|apelacao|agravo|embargos|execucao|penhora|citacao|competencia|honorarios|liminar|tutela|acao rescisoria|coisa julgada|cumprimento de sentenca|jurisdicao|prazo/]];
const RAMO_MAP = { 'processo civil': 'Processual Civil', 'processo penal': 'Processual Penal', 'processual do trabalho': 'Processual do Trabalho', 'do consumidor': 'Consumidor', 'da crianca e do adolescente': 'ECA' };
const RAMO_NOMES = ['Tributário', 'Previdenciário', 'Empresarial', 'Constitucional', 'Administrativo', 'Processual Civil', 'Processual Penal', 'Civil', 'Penal', 'Militar', 'Eleitoral', 'Ambiental', 'Bancário', 'Consumidor', 'Trabalhista', 'Internacional', 'Processual do Trabalho'];
function ramoDe(x) {
  if (x._ramo) return x._ramo;
  let r = String(x.ramo || '').trim(), auto = false;
  if (!r && x.materia && x.materia !== 'Geral') r = String(x.materia).split(/\s[–-]\s/)[0].trim();
  if (r) { const k = _sa(r.split(/\s*[(/]/)[0]).replace(/^direito\s+/, '').trim(); r = RAMO_MAP[k] || RAMO_NOMES.find(o => _sa(o) === k) || (k ? k.charAt(0).toUpperCase() + k.slice(1) : ''); }
  if (!r) { const t = _sa(x.texto); const reg = RAMO_REGRAS.find(([, rx]) => rx.test(t)); r = reg ? reg[0] : 'Sem classificação'; auto = true; }
  x._ramo = r; x._auto = auto; return r;
}
const SGRUPOS = [['STF-SV', 'Súmulas Vinculantes (STF)'], ['STF', 'Súmulas do STF'], ['STJ', 'Súmulas do STJ'], ['TST', 'Súmulas do TST'], ['TSE', 'Súmulas do TSE'], ['STM', 'Súmulas do STM']];
function listaJuris(mod, key, head, body) {
  let it = DATA[key].filter(x => inMod(x, mod.id)).map(x => ({ x, s: score(Object.assign(x, { _k: chaveHeat(key, x) }), null, mod.id) }));
  let chips = '', ordem = 'num';
  if (key === 'sumulas') {
    const cont = {}; it.forEach(({ x }) => cont[x.tribunal] = (cont[x.tribunal] || 0) + 1);
    const sel = new Set(store.get('sgrp', null) || SGRUPOS.map(g => g[0]));
    const noGrupo = it.filter(({ x }) => sel.has(x.tribunal));
    const ramos = {}; noGrupo.forEach(({ x }) => { const r = ramoDe(x); ramos[r] = (ramos[r] || 0) + 1; });
    const sr = store.get('sram', null), selR = sr ? new Set(sr) : null, sit = store.get('ssit', 'todas'); ordem = store.get('sord', 'num');
    const vigente = x => !x.situacao || x.situacao === 'Vigente';
    chips = `<div class="card"><b>Grupos de súmulas</b> <span class="mut">(marque os que quer estudar)</span><div class="row">${SGRUPOS.map(([g, n]) => cont[g] ? `<button class="${sel.has(g) ? '' : 'sec'}" data-act="sg" data-g="${g}">${sel.has(g) ? '✓ ' : ''}${n} (${cont[g]})</button>` : `<button class="sec" disabled title="Sem itens: o site do tribunal bloqueia leitura automática. Importe com tools/importar_sumulas_csv.py">${n} (0)</button>`).join('')}</div>
      <p class="row"><button class="sec" data-act="sgall" data-v="1">Todos</button><button class="sec" data-act="sgall" data-v="0">Nenhum</button></p>
      <b>Ramo do direito</b> <span class="mut">(dos grupos marcados)</span><div class="row">${Object.entries(ramos).sort((a, b) => a[0] === 'Sem classificação' ? 1 : b[0] === 'Sem classificação' ? -1 : b[1] - a[1]).map(([r, n]) => `<button class="${!selR || selR.has(r) ? '' : 'sec'}" data-act="sr" data-r="${esc(r)}">${!selR || selR.has(r) ? '✓ ' : ''}${esc(r)} (${n})</button>`).join('')}</div>
      <p class="row"><button class="sec" data-act="srall" data-v="1">Todos os ramos</button><button class="sec" data-act="srall" data-v="0">Nenhum</button>
      <select data-act="ssit" aria-label="situação"><option value="todas" ${sit === 'todas' ? 'selected' : ''}>Todas as situações</option><option value="vigentes" ${sit === 'vigentes' ? 'selected' : ''}>Só vigentes</option><option value="outras" ${sit === 'outras' ? 'selected' : ''}>Canceladas, alteradas ou superadas</option></select>
      <select data-act="sord" aria-label="ordem"><option value="num" ${ordem === 'num' ? 'selected' : ''}>Por número (crescente)</option><option value="numd" ${ordem === 'numd' ? 'selected' : ''}>Mais novas primeiro (número decrescente)</option><option value="ramo" ${ordem === 'ramo' ? 'selected' : ''}>Agrupar por ramo do direito</option><option value="heat" ${ordem === 'heat' ? 'selected' : ''}>Mais cobradas (estrelas)</option></select></p>
      <p class="mut">Os ramos do STF (CSV do portal) e do STJ (lista oficial) vêm das próprias fontes; onde a fonte não informa (Súmulas Vinculantes, STJ a partir da 650), o ramo é <b>classificação automática por palavras-chave</b> (marcada "auto") e pode errar.</p></div>`;
    it = noGrupo.filter(({ x }) => (!selR || selR.has(ramoDe(x))) && (sit === 'todas' || (sit === 'vigentes' ? vigente(x) : !vigente(x))));
  }
  const num = x => parseInt(x.n) || 0, trib = (a, b) => (a.x.tribunal > b.x.tribunal ? 1 : a.x.tribunal < b.x.tribunal ? -1 : 0);
  const cmp = { numd: (a, b) => trib(a, b) || num(b.x) - num(a.x), ramo: (a, b) => ramoDe(a.x).localeCompare(ramoDe(b.x)) || trib(a, b) || num(a.x) - num(b.x), heat: (a, b) => b.s - a.s };
  if (key !== 'sumulas') it.sort((a, b) => b.s - a.s); else if (cmp[ordem]) it.sort(cmp[ordem]);
  const extra = x => key === 'sumulas' ? `${x.situacao && x.situacao !== 'Vigente' ? `<span class="tag" style="background:#c0392b;color:#fff">${esc(x.situacao)}</span>` : ''}<span class="tag">${esc(ramoDe(x))}${x._auto ? ' (auto)' : ''}</span>` : '';
  const corpo = x => key === 'sumulas' && x.obs ? `<div class="mut">${esc(x.obs)}</div>` : '';
  return `${demoBanner()}${legend()}${filterBox('Filtrar…')}${chips}<p class="mut">${it.length} item(ns)</p>${it.map(({ x, s }) => `<div class="art h${s}" data-item data-score="${s}">${head(x)}${extra(x)} ${stars(s)} ${s ? heatBadge(s) : ''}<div>${esc(body(x))}</div>${corpo(x)}</div>`).join('') || '<p class="mut">Sem itens.</p>'}`;
}

// ---- SM-2 ----
function rate(id, q) {
  const st = store.get('cards', {}), c = st[id] || { ef: 2.5, n: 0, int: 0 };
  if (q < 3) { c.n = 0; c.int = 0; c.due = Date.now() + 10 * 60 * 1000; }
  else {
    c.n++; c.int = c.n === 1 ? 1 : c.n === 2 ? 6 : Math.round(c.int * c.ef);
    c.ef = Math.max(1.3, c.ef + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
    c.due = Date.now() + c.int * 86400000;
  }
  st[id] = c; store.set('cards', st);
}

// ---- Eventos ----
document.addEventListener('click', e => {
  const t = e.target.closest('[data-act]'); if (!t) return;
  const a = t.dataset.act, d = t.dataset, rerender = () => { const y = window.scrollY; route(); window.scrollTo(0, y); };
  if (a === 'flow') { state.flow = { i: +d.i, at: DATA.fluxos[+d.i].inicio, path: [] }; rerender(); }
  else if (a === 'flowgo') { state.flow.path.push({ id: state.flow.at, ans: d.ans }); state.flow.at = d.to; rerender(); }
  else if (a === 'flip') { state.show = !state.show; rerender(); }
  else if (a === 'rate') { rate(d.id, +d.q); state.show = false; rerender(); }
  else if (a === 'ans') { const q = DATA.questoes.find(x => x.id === d.q), st = store.get('q', {}); st[q.id] = { pick: +d.i, ok: +d.i === q.gab }; store.set('q', st);
    if (!st[q.id].ok) { // erro vira flashcard (revisão imediata, SM-2 depois)
      const ec = store.get('errcards', []), id = 'e_' + q.id, cs = store.get('cards', {});
      if (!ec.some(c => c.id === id)) ec.push({ id, materia: q.materia + ' · caderno de erros', f: q.enun, v: 'Gabarito ' + 'ABCDE'[q.gab] + ') ' + q.alts[q.gab] + ' — ' + q.coment, mods: q.mods });
      store.set('errcards', ec); delete cs[id]; store.set('cards', cs);
    }
    rerender(); }
  else if (a === 'sg') { const sel = new Set(store.get('sgrp', null) || SGRUPOS.map(g => g[0])); sel.has(d.g) ? sel.delete(d.g) : sel.add(d.g); store.set('sgrp', [...sel]); rerender(); }
  else if (a === 'sgall') { store.set('sgrp', d.v === '1' ? SGRUPOS.map(g => g[0]) : []); rerender(); }
  else if (a === 'sr') { const todos = [...new Set(DATA.sumulas.map(ramoDe))]; const cur = new Set(store.get('sram', null) || todos); cur.has(d.r) ? cur.delete(d.r) : cur.add(d.r); store.set('sram', [...cur]); rerender(); }
  else if (a === 'srall') { store.set('sram', d.v === '1' ? null : []); rerender(); }
  else if (a === 'dload') carregarDoutrina(d.id);
  else if (a === 'dread') { const l = store.get('dread', {}); l[d.id] ? delete l[d.id] : (l[d.id] = 1); store.set('dread', l); const open = [...document.querySelectorAll('details[open]')].map(e => e.dataset.id || e.querySelector('summary')?.textContent.slice(0, 20)); rerender(); document.querySelectorAll('details').forEach(e => { if (open.includes(e.dataset.id || e.querySelector('summary')?.textContent.slice(0, 20))) e.open = true; }); }
  else if (a === 'dup') { state.dup = !state.dup; rerender(); }
  else if (a === 'exp') exportar(d.id, d.f);
  else if (a === 'qf') { state.qf = d.v; rerender(); }
  else if (a === 'redo') { const st = store.get('q', {}); delete st[d.q]; store.set('q', st); rerender(); }
  else if (a === 'restore') { try { const o = JSON.parse($('#bk').value); store.set('cards', o.cards || {}); store.set('q', o.q || {}); store.set('errcards', o.errcards || []); store.set('dread', o.dread || {}); alert('Restaurado.'); location.hash = '#/'; } catch { alert('Backup inválido.'); } }
});
const curMod = () => location.hash.split('/')[2];
document.addEventListener('input', e => {
  const t = e.target;
  if (t.matches('[data-bq]')) { clearTimeout(window._bt); window._bt = setTimeout(() => buscar(t.value), 250); }
  if (t.matches('[data-filter]')) applyFilter(t.value);
  if (t.matches('[data-draft]')) store.set('draft.' + t.dataset.draft, t.value);
});
document.addEventListener('change', e => {
  const t = e.target;
  if (t.matches('[data-act=ssit]')) { store.set('ssit', t.value); const y = window.scrollY; route(); window.scrollTo(0, y); }
  if (t.matches('[data-act=sord]')) { store.set('sord', t.value); const y = window.scrollY; route(); window.scrollTo(0, y); }
  if (t.matches('[data-chk]')) store.set('chk.' + t.dataset.chk, t.checked);
  if (t.matches('[data-minscore]')) document.querySelectorAll('.art[data-score]').forEach(el => { el.style.display = +el.dataset.score >= +t.value ? '' : 'none'; });
  if (t.matches('[data-mat]')) document.querySelectorAll('[data-item]').forEach(el => { el.style.display = !t.value || el.dataset.mat === t.value ? '' : 'none'; });
});
window.addEventListener('hashchange', () => { state.flow = null; state.show = false; route(); });

function herdaEnam() {   // o ENAM usa o mesmo conteúdo da magistratura (estadual/federal)
  ['leis', 'sumulas', 'principios', 'enunciados', 'juris', 'doutrina', 'mapas', 'fluxos', 'exemplos', 'cards', 'questoes', 'discursivas', 'orais'].forEach(k => (DATA[k] || []).forEach(x => { if (x.mods && (x.mods.includes('magsc') || x.mods.includes('magfed')) && !x.mods.includes('enam')) x.mods = x.mods.concat('enam'); }));
}
// ---- Boot: carrega leis completas (se houver) e inicia ----
function loadScript(src) { return new Promise(r => { const s = document.createElement('script'); s.src = src; s.onload = s.onerror = r; document.head.appendChild(s); }); }
(async () => {
  // 1) mostra o app já com as súmulas e a amostra; 2) carrega as leis em paralelo e atualiza ao terminar
  const ALLM = DATA.modulos.map(m => m.id), idx = new Map(DATA.sumulas.map(x => [x.tribunal + '|' + x.n, x]));
  (window.JUR_IMPORT || []).flat().forEach(x => {
    const k = x.tribunal + '|' + x.n, ex = idx.get(k);
    const EXTRA = ['ramo', 'orgao', 'data', 'situacao', 'pub', 'obs', 'url', 'texto_anterior'];
    if (ex) { Object.assign(ex, { texto: x.texto, vinculante: x.vinculante || ex.vinculante }); EXTRA.forEach(c => { if (x[c] != null && x[c] !== '') ex[c] = x[c]; }); if (x.materia && (!ex.materia || ex.materia === 'Geral')) ex.materia = x.materia; }
    else { const o = { tribunal: x.tribunal, n: x.n, materia: x.materia || 'Geral', texto: x.texto, vinculante: x.vinculante, mods: ALLM, f: {} }; EXTRA.forEach(c => { if (x[c] != null && x[c] !== '') o[c] = x[c]; }); DATA.sumulas.push(o); idx.set(k, o); }
  });
  DATA.sumulas.sort((a, b) => (a.tribunal > b.tribunal ? 1 : a.tribunal < b.tribunal ? -1 : (parseInt(a.n) || 0) - (parseInt(b.n) || 0)));
  herdaEnam();
  route();
  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) navigator.serviceWorker.register('sw.js').catch(() => {});
  const files = window.LEI_FILES || []; let feitos = 0, i = 0;
  const ld = document.createElement('div'); ld.style.cssText = 'position:fixed;bottom:8px;right:8px;background:#1e3a5f;color:#fff;padding:6px 10px;border-radius:8px;font-size:12px;z-index:9';
  if (files.length) document.body.appendChild(ld);
  const worker = async () => { while (i < files.length) { const f = files[i++]; await loadScript('data/leis/' + f); ld.textContent = '⏳ Carregando leis ' + (++feitos) + '/' + files.length; } };
  await Promise.all([worker(), worker(), worker(), worker(), worker(), worker()]);
  ld.remove(); herdaEnam();
  // lei importada com mesmo id substitui a amostra
  const map = new Map(); DATA.leis.forEach(l => map.set(l.id, l)); DATA.leis = [...map.values()];
  if (!document.activeElement || !['TEXTAREA', 'INPUT'].includes(document.activeElement.tagName)) { const y = window.scrollY; route(); window.scrollTo(0, y); }
})();
