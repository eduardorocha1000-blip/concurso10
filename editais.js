// Módulo "Editais": matéria (conteúdo programático) dos últimos editais de cada grande grupo.
// O texto vem dos editais publicados (data/editais.js, gerado por tools/editais_extrair.py), sem resumo.
(function () {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const GRUPOS = [['oab', '🎓 OAB', 'Exame de Ordem Unificado (FGV). A 1ª fase cobra o currículo do curso de Direito; o edital detalha o programa da 2ª fase (prova prático-profissional).'],
    ['magsc', '⚖️ Magistratura Estadual SC', 'Juiz Substituto do TJSC (FGV). Programa conforme a Resolução CNJ 75/2009.'],
    ['mpsc', '🛡️ Ministério Público SC', 'Promotor de Justiça Substituto do MPSC.'],
    ['magfed', '🏛️ Magistratura Federal', 'Juiz Federal Substituto. Não localizei edital recente do TRF4 (SC); estão os editais mais recentes de outros TRFs, que seguem o mesmo programa nacional (Res. CNJ 75/2009).'],
    ['enam', '📝 ENAM', 'Exame Nacional da Magistratura (ENFAM/FGV).']];
  let carregando = null;
  function carrega() {
    if (window.EDITAIS) return Promise.resolve();
    return carregando || (carregando = new Promise(r => { const s = document.createElement('script'); s.src = 'data/editais.js'; s.onload = s.onerror = () => r(); document.head.appendChild(s); }));
  }
  const norm = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const chave = d => norm(d).replace(/^direito (do |da |de |dos |das )?/, '').replace(/\s+/g, ' ').replace(/^[a-z]\) /, '').trim();

  function edital(e) {
    const nPts = e.programa.reduce((a, d) => a + d.pontos.length, 0);
    return `<details class="card" data-item data-ed="${esc(e.id)}"><summary><b>${esc(e.nome)}</b> <span class="tag">${esc(e.ano)}</span>${e.banca ? `<span class="tag">banca: ${esc(e.banca)}</span>` : ''}<span class="tag">${e.programa.length} disciplinas · ${nPts} pontos</span></summary>
      <p class="mut">${esc(e.orgao)} · <a href="${esc(e.fonte)}" target="_blank" rel="noopener">edital / página oficial</a>${e.nota ? ' · ' + esc(e.nota) : ''}</p>
      ${e.fase1 ? `<div class="card"><b>1ª fase (prova objetiva)</b><p>${esc(e.fase1)}</p><b>2ª fase (prático-profissional)</b><p>${esc(e.fase2 || '')}</p>${e.prova ? `<p class="mut">${esc(e.prova)}</p>` : ''}</div>` : ''}
      ${e.quadro ? `<details class="card"><summary>📊 Distribuição das questões da prova objetiva (transcrição do edital)</summary><pre style="white-space:pre-wrap;font-family:inherit">${esc(e.quadro.join('\n'))}</pre></details>` : ''}
      ${e.intro ? `<p class="mut">${esc(e.intro)}</p>` : ''}
      ${e.programa.length ? e.programa.map(d => `<details class="card"><summary><b>${esc(d.disc)}</b> ${d.bloco ? `<span class="tag">${esc(d.bloco)}</span>` : ''}<span class="tag">${d.pontos.length} pontos</span></summary><ol style="padding-left:1.2em">${d.pontos.map(p => `<li>${esc(p.replace(/^\d+\s?\.?\s+/, ''))}</li>`).join('')}</ol></details>`).join('') : '<p class="mut">Programa não extraído automaticamente deste edital; use o link oficial.</p>'}
    </details>`;
  }

  function matriz(eds) {
    const ordenados = eds.slice().sort((a, b) => b.ano - a.ano), linhas = new Map();
    ordenados.forEach(e => e.programa.forEach(d => { const k = chave(d.disc), l = linhas.get(k) || { nome: d.disc, n: {} }; l.n[e.id] = (l.n[e.id] || 0) + d.pontos.length; linhas.set(k, l); }));
    const rows = [...linhas.values()].sort((a, b) => Object.keys(b.n).length - Object.keys(a.n).length || a.nome.localeCompare(b.nome));
    if (rows.length < 2) return '';
    return `<details class="card"><summary>🔎 Comparativo: disciplinas e nº de pontos por edital</summary><div style="overflow-x:auto"><table style="border-collapse:collapse;font-size:13px"><thead><tr><th style="text-align:left;padding:4px">Disciplina</th>${ordenados.map(e => `<th style="padding:4px" title="${esc(e.nome)}">${esc(e.id.toUpperCase())}</th>`).join('')}</tr></thead><tbody>
      ${rows.map(l => `<tr><td style="padding:4px;border-top:1px solid #ddd">${esc(l.nome.replace(/^[A-Z]\)\s*/, ''))} <span class="tag">${Object.keys(l.n).length}/${ordenados.length}</span></td>${ordenados.map(e => `<td style="text-align:center;padding:4px;border-top:1px solid #ddd">${l.n[e.id] ? '✓ ' + l.n[e.id] : '—'}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
      <p class="mut">✓ N = quantidade de pontos do programa dessa disciplina no edital. "—" = a disciplina não consta com esse nome (pode estar embutida em outra). Os nomes são normalizados automaticamente; confira no edital.</p></details>`;
  }

  window.editaisView = function (grupo) {
    const g = GRUPOS.find(x => x[0] === grupo);
    if (!g) return `<h1>📋 Editais — matéria dos últimos concursos</h1><p class="mut">Conteúdo programático copiado dos editais publicados, sem resumo. Escolha um grupo.</p>
      <div class="grid">${GRUPOS.map(([id, nome, desc]) => `<a class="card mod" href="#/editais/${id}"><h2>${nome}</h2><div class="mut">${esc(desc)}</div></a>`).join('')}</div>
      <div class="card"><input id="edq" type="search" placeholder="Buscar um tema em todos os editais (ex.: improbidade, tutela provisória)" style="width:100%"><div id="edres"></div></div><p><a href="#/">Voltar</a></p>`;
    return `<h1>${g[1]}</h1><p class="mut">${esc(g[2])}</p><div id="edbox">Carregando editais…</div>
      <p><a href="#/editais">← Todos os grupos</a> · <a href="#/m/${grupo}/visao">Abrir o módulo ${g[1]}</a></p>`;
  };

  window.editaisInit = async function (grupo) {
    await carrega();
    const all = window.EDITAIS || [];
    if (!grupo) return;
    const box = document.getElementById('edbox'); if (!box) return;
    const eds = all.filter(e => e.grupo === grupo).sort((a, b) => b.ano - a.ano || (a.id < b.id ? 1 : -1));
    box.innerHTML = eds.length ? `<div class="banner">Texto extraído automaticamente dos PDFs dos editais. Pode haver quebras de formatação; <b>confira no edital oficial</b> antes de decidir o que estudar. ${eds.length} edital(is) neste grupo.</div>${matriz(eds)}${eds.map(edital).join('')}` : '<p class="mut">Nenhum edital cadastrado para este grupo.</p>';
  };

  document.addEventListener('input', e => {
    if (!e.target.matches || !e.target.matches('#edq')) return;
    clearTimeout(window._edt); window._edt = setTimeout(async () => {
      await carrega(); const q = norm(e.target.value.trim()), out = document.getElementById('edres'); if (!out) return;
      if (q.length < 3) { out.innerHTML = ''; return; }
      const hits = [];
      (window.EDITAIS || []).forEach(ed => ed.programa.forEach(d => d.pontos.forEach(p => { if (norm(p).includes(q) || norm(d.disc).includes(q)) hits.push({ ed, d, p }); })));
      const porEd = {}; hits.forEach(h => (porEd[h.ed.id] = porEd[h.ed.id] || []).push(h));
      out.innerHTML = `<p class="mut">${hits.length} ponto(s) em ${Object.keys(porEd).length} edital(is)</p>` + Object.entries(porEd).map(([id, hs]) => { const ed = hs[0].ed; return `<details class="card"><summary>${esc(ed.nome)} <span class="tag">${hs.length}</span></summary>${hs.slice(0, 25).map(h => `<p><b>${esc(h.d.disc)}</b> — ${esc(h.p.slice(0, 400))}</p>`).join('')}</details>`; }).join('');
    }, 250);
  });
})();
