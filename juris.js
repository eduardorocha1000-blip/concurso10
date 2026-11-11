// Pesquisa de jurisprudência AO VIVO (nada é armazenado, exceto seus favoritos neste aparelho).
// Exige o servidor local: python tools/servidor.py
(function () {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const J = { modo: 'juris', inf: null, selInf: new Set(['stf', 'stj']), trib: null, sel: new Set(['stf']), res: {}, st: {}, sel_ia: new Set(), q: '', f: {}, ia: false, fav: false, abertos: new Set() };
  const lsGet = (k, d) => { try { return JSON.parse(localStorage.getItem('jus.' + k)) ?? d; } catch { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem('jus.' + k, JSON.stringify(v)); } catch { } };
  const GRUPOS = ['Superiores', 'Justiça Estadual', 'Justiça Federal', 'Justiça do Trabalho', 'Justiça Eleitoral', 'Justiça Militar'];
  const key = r => r.tribunal_id + '|' + (r.id_original || r.numero_processo);

  async function api(path, opt) { const r = await fetch(path, opt); if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }

  window.jurisView = function () {
    return `<h1>⚖️ Pesquisa de jurisprudência e informativos</h1>
    <div class="card"><p class="row"><button id="jm1" data-ja="modo" data-m="juris">Jurisprudência</button><button id="jm2" class="sec" data-ja="modo" data-m="inf">Informativos</button></p>
      <p class="mut" id="jdesc">Pesquisa ao vivo nos sites dos tribunais, <b>sem armazenar</b> as decisões. Mostra só o que a fonte fornece (campos ausentes ficam em branco).</p>
      <div id="jserv"></div>
      <div class="row"><input id="jq" type="search" placeholder="Ex.: responsabilidade civil por erro médico" style="flex:1;min-width:220px"><button data-ja="buscar">Pesquisar</button></div>
      <details><summary>Filtros</summary>
        <div class="row"><input id="jrel" placeholder="Relator"><input id="jcls" placeholder="Classe (ex.: ARE, RE, ADI)"><input id="jorgao" placeholder="Órgão julgador"></div>
        <div class="row"><label>De <input id="jde" type="date"></label><label>Até <input id="jate" type="date"></label>
          <select id="jtipo"><option value="acordaos">Acórdãos (STF)</option><option value="decisoes">Decisões monocráticas (STF)</option></select></div>
        <p class="mut">Relator, tipo e classe valem para o STF. Os demais tribunais (DataJud) aceitam classe, órgão julgador e período de ajuizamento.</p></details>
      <h3>Tribunais <span class="mut" id="jcont"></span></h3><div id="jtrib">Carregando lista…</div></div>
    <div id="jfav"></div><div id="jres"></div>
    <div class="card" id="jia"></div>
    <p><a href="#/">Voltar</a></p>`;
  };

  const lista = () => J.modo === 'inf' ? ((J.inf || {}).ao_vivo || []) : (J.trib || []);
  function pintarModo() {
    const a = document.getElementById('jm1'), b = document.getElementById('jm2'); if (!a) return;
    a.className = J.modo === 'juris' ? '' : 'sec'; b.className = J.modo === 'inf' ? '' : 'sec';
    document.getElementById('jdesc').innerHTML = J.modo === 'inf' ? 'Pesquisa ao vivo nos <b>informativos de jurisprudência</b> dos tribunais que permitem consulta automática (STF e STJ), <b>sem armazenar</b> o conteúdo. Para os demais, há o link do site oficial.' : 'Pesquisa ao vivo nos sites dos tribunais, <b>sem armazenar</b> as decisões. Mostra só o que a fonte fornece (campos ausentes ficam em branco).';
    document.getElementById('jq').placeholder = J.modo === 'inf' ? 'Ex.: erro médico, responsabilidade civil do Estado' : 'Ex.: responsabilidade civil por erro médico';
  }
  function pintarTribunais() {
    const el = document.getElementById('jtrib'); if (!el) return;
    if (J.modo === 'inf') {
      if (!J.inf) { el.innerHTML = ''; return; }
      el.innerHTML = J.inf.ao_vivo.map(t => `<label style="display:inline-block;margin:2px 10px 2px 0"><input type="checkbox" data-jinf="${t.id}" ${J.selInf.has(t.id) ? 'checked' : ''}> ${esc(t.nome)} <span class="tag">ao vivo</span></label>`).join('')
        + `<details class="card"><summary>Outros tribunais (sem pesquisa ao vivo aqui)</summary><p class="mut">Esses sites bloqueiam consulta automática, não têm busca pública utilizável ou exigem captcha. Abra o portal oficial de jurisprudência de cada um:</p><p class="row">${J.inf.links.map(l => `<a class="btn sec" href="${esc(l.link)}" target="_blank" rel="noopener">${esc(l.nome)}</a>`).join('')}</p></details>`;
      document.getElementById('jcont').textContent = '(' + J.selInf.size + ' selecionados)'; return;
    }
    if (!J.trib) return;
    el.innerHTML = '<p class="row"><button class="sec" data-ja="todos">Todos</button><button class="sec" data-ja="nenhum">Nenhum</button></p>' + GRUPOS.map(g => {
      const ts = J.trib.filter(t => t.grupo === g), n = ts.filter(t => J.sel.has(t.id)).length;
      return `<details class="card"><summary>${esc(g)} <span class="tag">${n}/${ts.length}</span></summary><p class="row"><button class="sec" data-ja="grupo" data-g="${esc(g)}" data-v="1">marcar todos</button><button class="sec" data-ja="grupo" data-g="${esc(g)}" data-v="0">limpar</button></p>
        ${ts.map(t => `<label style="display:inline-block;margin:2px 10px 2px 0"><input type="checkbox" data-jt="${t.id}" ${J.sel.has(t.id) ? 'checked' : ''}> ${esc(t.nome)} ${t.modo === 'texto' ? '<span class="tag">texto completo</span>' : '<span class="tag">metadados</span>'}</label>`).join('')}</details>`;
    }).join('');
    document.getElementById('jcont').textContent = '(' + J.sel.size + ' selecionados)';
  }

  window.jurisInit = async function () {
    try { J.trib = await api('/api/tribunais'); J.inf = await api('/api/informativos/tribunais'); pintarModo(); const s = await api('/api/status'); J.ia = s.ia; document.getElementById('jserv').innerHTML = ''; pintarTribunais(); pintarIA(); if (J.q) { document.getElementById('jq').value = J.q; pintarRes(); } }
    catch (e) { document.getElementById('jserv').innerHTML = '<div class="banner">⚠ Servidor de pesquisa não encontrado. Esta tela só funciona quando o app roda pelo servidor local: <code>python tools/servidor.py</code>. A versão publicada (GitHub Pages) não consegue consultar os tribunais.</div>'; document.getElementById('jtrib').innerHTML = ''; }
    pintarFav();
  };

  async function buscarUm(t, pagina) {
    J.st[t.id] = { carregando: true }; pintarRes();
    const f = J.f, u = new URLSearchParams({ t: t.id, q: J.q, p: pagina || 1 });
    (J.modo === 'inf' ? ['orgao'] : ['relator', 'classe', 'orgao', 'de', 'ate', 'tipo']).forEach(k => f[k] && u.set(k, f[k]));
    try {
      const r = await api((J.modo === 'inf' ? '/api/informativos?' : '/api/juris?') + u);
      J.st[t.id] = { ok: r.ok, total: r.total, erro: r.erro, ms: r.ms, link: r.link, pagina: pagina || 1 };
      J.res[t.id] = (pagina > 1 ? (J.res[t.id] || []) : []).concat(r.resultados || []);
    } catch (e) { J.st[t.id] = { ok: false, erro: String(e.message || e) }; }
    pintarRes();
  }

  async function buscar() {
    J.q = document.getElementById('jq').value.trim();
    J.f = { relator: val('jrel'), classe: val('jcls'), orgao: val('jorgao'), de: val('jde'), ate: val('jate'), tipo: val('jtipo') };
    if (!J.q && !J.f.relator) return alert('Digite o que pesquisar.');
    J.res = {}; J.st = {}; J.sel_ia = new Set();
    const lista = (J.modo === 'inf' ? J.inf.ao_vivo.filter(t => J.selInf.has(t.id)) : J.trib.filter(t => J.sel.has(t.id))); let i = 0;
    const w = async () => { while (i < lista.length) await buscarUm(lista[i++]); };
    await Promise.all([w(), w(), w()]);  // no máx. 3 consultas simultâneas (respeita limites das fontes)
  }
  const val = id => (document.getElementById(id) || {}).value || '';

  function card(r) {
    const fav = lsGet('favj', {}), k = key(r), n = r.tribunal_id + '-' + k;
    const linha = (rot, v) => v ? `<div><span class="mut">${rot}:</span> ${esc(v)}</div>` : '';
    return `<div class="card" data-k="${esc(k)}"><div><b>${esc(r.tribunal)}</b> · ${esc(r.numero_processo || '(sem número)')} ${r.precedente_qualificado ? '<span class="tag">precedente qualificado</span>' : ''} ${fav[k] ? '⭐' : ''}</div>
      ${linha('Classe', r.classe)}${linha('Relator', r.relator)}${linha('Órgão', r.orgao_julgador)}${linha('Julgamento', r.data_julgamento)}${linha('Publicação', r.data_publicacao)}${linha('Ajuizamento', r.data_ajuizamento)}
      ${r.assuntos ? linha('Assuntos', r.assuntos.join('; ')) : ''}${r.palavras_chave ? linha('Palavras-chave', [].concat(r.palavras_chave).join('; ')) : ''}
      ${r.ementa ? `<div class="mut">Ementa</div><div style="${J.abertos.has(k) ? '' : 'max-height:7.5em;overflow:hidden'}">${esc(r.ementa)}</div><button class="sec" data-ja="exp" data-k="${esc(k)}">${J.abertos.has(k) ? 'Recolher' : 'Expandir ementa'}</button>` : `<div class="mut">${esc(r.disponibilidade || 'Sem ementa nesta fonte.')}</div>`}
      ${r.trechos && r.trechos.length ? `<div class="mut">Trechos do informativo (${esc(r.periodo || '')})</div><ul>${r.trechos.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
      ${r.legislacao_citada && J.abertos.has(k) ? `<div class="mut">Legislação citada</div><pre style="white-space:pre-wrap">${esc(r.legislacao_citada)}</pre>` : ''}
      <div class="mut" style="font-size:12px">Fonte: ${esc(r.fonte || '—')} · verificado em ${esc(r.verificado_em || '—')} · ${esc(r.disponibilidade || '')}</div>
      <p class="row">${r.inteiro_teor_url || r.url_origem ? `<a class="btn" href="${esc(r.inteiro_teor_url || r.url_origem)}" target="_blank" rel="noopener">Inteiro teor / fonte</a>` : ''}
        <button class="sec" data-ja="fav" data-k="${esc(k)}">${fav[k] ? 'Desfavoritar' : '⭐ Favoritar'}</button><button class="sec" data-ja="comp" data-k="${esc(k)}">Compartilhar</button>
        <label><input type="checkbox" data-jia="${esc(k)}" ${J.sel_ia.has(k) ? 'checked' : ''}> usar na IA/organização</label></p></div>`;
  }
  const todos = () => Object.values(J.res).flat();

  function pintarRes() {
    const el = document.getElementById('jres'); if (!el) return;
    const ids = Object.keys(J.st);
    const stat = ids.map(id => { const t = lista().find(x => x.id === id) || { nome: id }, s = J.st[id];
      const txt = s.carregando ? '⏳ consultando…' : s.ok ? `✅ ${s.total.toLocaleString('pt-BR')} encontrados${t.modo === 'metadados' ? ' (somente metadados)' : ''} · ${s.ms} ms` : `⚠ indisponível (${esc(s.erro || '')})`;
      return `<div class="card"><b>${esc(t.nome)}</b> — ${txt} ${s.link ? `<a href="${esc(s.link)}" target="_blank" rel="noopener">pesquisar no site oficial</a>` : ''}${s.ok && (J.res[id] || []).length < s.total ? ` <button class="sec" data-ja="mais" data-t="${id}">mais 10</button>` : ''}</div>`; }).join('');
    el.innerHTML = (ids.length ? '<h3>Resultados</h3>' : '') + stat + todos().map(card).join('');
    pintarIA();
  }

  function pintarFav() {
    const el = document.getElementById('jfav'); if (!el) return;
    const f = Object.values(lsGet('favj', {}));
    el.innerHTML = f.length ? `<details class="card"><summary>⭐ Favoritos (${f.length})</summary>${f.map(card).join('')}</details>` : '';
  }

  function pintarIA() {
    const el = document.getElementById('jia'); if (!el) return;
    const n = J.sel_ia.size;
    if (el.dataset.ok) { const c = document.getElementById('jian'); if (c) c.textContent = n; return; }
    el.dataset.ok = '1';
    el.innerHTML = `<h3>📋 Organizar decisões marcadas</h3><p class="mut">Marque "usar na IA/organização" nos resultados (<b id="jian">${n}</b> marcada(s)). Sem IA: só reorganiza o que a fonte forneceu, sem resumir nem interpretar.</p>
      <div class="row"><button data-ja="org" data-o="comparar">Comparar lado a lado</button><button class="sec" data-ja="org" data-o="leis">Legislação citada (consolidada)</button><button class="sec" data-ja="org" data-o="chaves">Palavras-chave em comum</button><button class="sec" data-ja="org" data-o="texto">Copiar lista</button></div>
      <div id="jorg"></div>
      ${J.ia ? `<h3>🤖 Análise com IA (opcional)</h3><div class="row">${[['resumo', 'Resumo'], ['tese', 'Tese jurídica'], ['fundamentos', 'Fundamentos'], ['legislacao', 'Legislação citada'], ['precedentes', 'Precedentes mencionados'], ['comparar', 'Comparar'], ['divergencias', 'Divergências']].map(([k, n2]) => `<button class="sec" data-ja="ia" data-tarefa="${k}">${n2}</button>`).join('')}</div>
      <div class="row"><input id="jiaq" placeholder="Pergunta livre sobre as decisões marcadas" style="flex:1;min-width:220px"><button data-ja="ia" data-tarefa="livre">Perguntar</button></div><div id="jiares"></div>` : ''}`;
  }

  // ---- organização sem IA ----
  const ordinal = n => (+n <= 9 ? '§ ' + (+n) + 'º' : '§ ' + (+n));
  function leisCitadas(txt) {
    if (!txt) return [];
    return String(txt).split(/LEG-/).slice(1).map(bl => {
      const ls = bl.split('\n').map(x => x.trim()).filter(Boolean), cab = ls[0] || '';
      const m = cab.match(/(LEI|DEL|LCP|DLG|MPV|DEC|EMC|RES)-0*(\d+)\s+ANO-(\d{4})/) , alt = cab.match(/\b([A-Z]{2,6}(?:-\d{2,4})?)\s+ANO-(\d{4})/) ;
      const sm = cab.match(/SUM(STF|STJ|V)?-0*(\d+)/);
      const nome = sm ? 'Súmula ' + sm[2] + (sm[1] === 'V' ? ' Vinculante' : sm[1] ? '/' + sm[1] : '') : m ? ({ LEI: 'Lei', DEL: 'Decreto-Lei', LCP: 'Lei Complementar', DLG: 'Decreto Legislativo', MPV: 'Medida Provisória', DEC: 'Decreto', EMC: 'Emenda Constitucional', RES: 'Resolução' }[m[1]] + ' ' + (+m[2]).toLocaleString('pt-BR') + '/' + m[3]) : (alt ? alt[1] + ' (' + alt[2] + ')' : cab.replace(/\s+/g, ' '));
      const resto = ls.slice(1).join(' ') + ' ' + cab, arts = [...resto.matchAll(/ART-0*(\d+[A-Z]?)/g)].map(x => 'art. ' + x[1]), pars = [...resto.matchAll(/PAR-0*(\d+)/g)].map(x => ordinal(x[1])), incs = [...resto.matchAll(/INC-0*(\d+)/g)].map(x => 'inc. ' + (+x[1]));
      return { lei: nome, disp: [...new Set(arts)].join(', ') + (pars.length ? ', ' + [...new Set(pars)].join(', ') : '') + (incs.length ? ', ' + [...new Set(incs)].join(', ') : '') };
    }).filter(x => x.lei);
  }
  const marcadas = () => todos().concat(Object.values(lsGet('favj', {}))).filter((r, i, a) => J.sel_ia.has(key(r)) && a.findIndex(x => key(x) === key(r)) === i);
  function organizar(o) {
    const box = document.getElementById('jorg'), dec = marcadas();
    if (!dec.length) { box.innerHTML = '<p class="mut">Marque ao menos uma decisão em "usar na IA/organização".</p>'; return; }
    if (o === 'comparar') {
      const lin = [['Tribunal / número', r => `<b>${esc(r.tribunal_id.toUpperCase())}</b> ${esc(r.numero_processo)}`], ['Classe', r => esc(r.classe || '—')], ['Relator', r => esc(r.relator || '—')], ['Órgão julgador', r => esc(r.orgao_julgador || '—')],
        ['Julgamento', r => esc(r.data_julgamento || r.data_ajuizamento || '—')], ['Precedente qualificado', r => r.precedente_qualificado == null ? '—' : (r.precedente_qualificado ? 'sim' : 'não')],
        ['Palavras-chave', r => esc([].concat(r.palavras_chave || ['—']).join('; '))], ['Legislação citada', r => leisCitadas(r.legislacao_citada).map(l => esc(l.lei + (l.disp ? ' — ' + l.disp : ''))).join('<br>') || '—'],
        ['Ementa', r => esc(r.ementa || r.disponibilidade || '—')], ['Fonte', r => (r.inteiro_teor_url || r.url_origem) ? `<a href="${esc(r.inteiro_teor_url || r.url_origem)}" target="_blank" rel="noopener">abrir</a>` : '—']];
      box.innerHTML = `<div style="overflow-x:auto"><table style="border-collapse:collapse;min-width:${dec.length * 260}px"><tbody>${lin.map(([t, f]) => `<tr><th style="text-align:left;vertical-align:top;padding:6px;border:1px solid var(--bd,#ccc);width:120px">${t}</th>${dec.slice(0, 8).map(r => `<td style="vertical-align:top;padding:6px;border:1px solid var(--bd,#ccc);font-size:13px">${f(r)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${dec.length > 8 ? '<p class="mut">Mostrando as 8 primeiras.</p>' : ''}`;
    } else if (o === 'leis') {
      const c = {};
      dec.forEach(r => leisCitadas(r.legislacao_citada).forEach(l => { const e = (c[l.lei] = c[l.lei] || { n: new Set(), d: new Set() }); e.n.add(r.numero_processo); if (l.disp) e.d.add(l.disp); }));
      const rows = Object.entries(c).sort((a, b) => b[1].n.size - a[1].n.size);
      box.innerHTML = rows.length ? `<table><tbody>${rows.map(([l, e]) => `<tr><td><b>${esc(l)}</b></td><td>${e.n.size}/${dec.length} decisões</td><td class="mut">${esc([...e.d].join(' | '))}</td></tr>`).join('')}</tbody></table>` : '<p class="mut">As decisões marcadas não trazem legislação citada na fonte (DataJud não fornece).</p>';
    } else if (o === 'chaves') {
      const c = {}; dec.forEach(r => [].concat(r.palavras_chave || r.assuntos || []).forEach(k => { const t = String(k).trim(); if (t && !/^VIDE EMENTA$/i.test(t)) (c[t] = c[t] || new Set()).add(r.numero_processo); }));
      const rows = Object.entries(c).sort((a, b) => b[1].size - a[1].size).slice(0, 40);
      box.innerHTML = rows.length ? rows.map(([k, s]) => `<span class="tag">${esc(k)} · ${s.size}</span>`).join(' ') : '<p class="mut">Sem palavras-chave/assuntos nas decisões marcadas.</p>';
    } else if (o === 'texto') {
      const tx = dec.map(r => `${r.tribunal} — ${r.numero_processo}${r.relator ? ' — Rel. ' + r.relator : ''}${r.data_julgamento ? ' — ' + r.data_julgamento : ''}\n${r.ementa || ''}\n${r.inteiro_teor_url || r.url_origem || ''}`).join('\n\n');
      if (navigator.clipboard) navigator.clipboard.writeText(tx).then(() => { box.innerHTML = '<p>✅ Lista copiada.</p>'; }, () => { box.innerHTML = `<textarea style="width:100%;height:10em">${esc(tx)}</textarea>`; });
      else box.innerHTML = `<textarea style="width:100%;height:10em">${esc(tx)}</textarea>`;
    }
  }

  async function usarIA(tarefa) {
    const dec = todos().filter(r => J.sel_ia.has(key(r)));
    const box = document.getElementById('jiares');
    if (!dec.length) { box.innerHTML = '<p class="mut">Marque ao menos uma decisão em "usar na IA".</p>'; return; }
    box.innerHTML = '<p>⏳ Analisando…</p>';
    try {
      const r = await api('/api/ia', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tarefa, pergunta: val('jiaq'), decisoes: dec.map(d => ({ tribunal: d.tribunal, numero_processo: d.numero_processo, classe: d.classe, relator: d.relator, orgao_julgador: d.orgao_julgador, data_julgamento: d.data_julgamento, ementa: d.ementa, legislacao_citada: d.legislacao_citada, assuntos: d.assuntos, url: d.inteiro_teor_url || d.url_origem })) }) });
      box.innerHTML = r.ok ? `<div class="card"><div style="white-space:pre-wrap">${esc(r.texto)}</div><p class="mut">Base: ${esc((r.base || []).join(', '))}. Resposta gerada por IA a partir apenas das decisões marcadas; confira nas fontes.</p></div>` : `<div class="banner">${esc(r.erro)}</div>`;
    } catch (e) { box.innerHTML = `<div class="banner">${esc(e.message)}</div>`; }
  }

  document.addEventListener('click', e => {
    const t = e.target.closest('[data-ja]'); if (!t) return; const a = t.dataset.ja, d = t.dataset;
    if (a === 'buscar') buscar();
    else if (a === 'todos') { J.trib.forEach(x => J.sel.add(x.id)); pintarTribunais(); }
    else if (a === 'nenhum') { J.sel.clear(); pintarTribunais(); }
    else if (a === 'grupo') { J.trib.filter(x => x.grupo === d.g).forEach(x => d.v === '1' ? J.sel.add(x.id) : J.sel.delete(x.id)); pintarTribunais(); }
    else if (a === 'mais') buscarUm(lista().find(x => x.id === d.t), (J.st[d.t].pagina || 1) + 1);
    else if (a === 'modo') { J.modo = d.m; J.res = {}; J.st = {}; J.sel_ia = new Set(); pintarModo(); pintarTribunais(); pintarRes(); }
    else if (a === 'exp') { J.abertos.has(d.k) ? J.abertos.delete(d.k) : J.abertos.add(d.k); pintarRes(); pintarFav(); }
    else if (a === 'fav') { const f = lsGet('favj', {}), r = todos().concat(Object.values(f)).find(x => key(x) === d.k); if (f[d.k]) delete f[d.k]; else if (r) f[d.k] = r; lsSet('favj', f); pintarRes(); pintarFav(); }
    else if (a === 'comp') { const r = todos().concat(Object.values(lsGet('favj', {}))).find(x => key(x) === d.k); if (!r) return; const tx = `${r.tribunal} — ${r.numero_processo}\n${r.ementa || ''}\n${r.inteiro_teor_url || r.url_origem || ''}`; if (navigator.share) navigator.share({ title: r.numero_processo, text: tx }).catch(() => { }); else if (navigator.clipboard) navigator.clipboard.writeText(tx).then(() => alert('Copiado.')); }
    else if (a === 'ia') usarIA(d.tarefa);
    else if (a === 'org') organizar(d.o);
  });
  document.addEventListener('change', e => {
    const t = e.target;
    if (t.matches('[data-jinf]')) { t.checked ? J.selInf.add(t.dataset.jinf) : J.selInf.delete(t.dataset.jinf); document.getElementById('jcont').textContent = '(' + J.selInf.size + ' selecionados)'; }
    if (t.matches('[data-jt]')) { t.checked ? J.sel.add(t.dataset.jt) : J.sel.delete(t.dataset.jt); document.getElementById('jcont').textContent = '(' + J.sel.size + ' selecionados)'; }
    if (t.matches('[data-jia]')) { t.checked ? J.sel_ia.add(t.dataset.jia) : J.sel_ia.delete(t.dataset.jia); pintarIA(); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.id === 'jq') buscar(); });
})();
