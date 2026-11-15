/* Sessão «Redação das peças»: aulas de português jurídico, treino, modelos, esqueletos e verificador de texto.
   O conteúdo fica em data/curso/redacao.js (fora do git); se não existir, a sessão avisa. Rota: #/redacao/<aba>. */
(function () {
  const ABAS = [['aulas', 'Aulas'], ['treino', 'Treino'], ['modelos', 'Modelos'], ['esqueleto', 'Esqueletos'], ['verificador', 'Verificador'], ['checklist', 'Checklist']];
  const R = () => window.REDACAO;
  const lerRD = () => store.get('rd', { t: {}, ck: {} });
  const gravarRD = v => store.set('rd', v);
  const E = s => esc(s);

  function topo(aba) {
    return `<h1>✍️ Redação das peças</h1>
      <p class="mut">Aprenda a escrever a peça e as discursivas da 2ª fase: regras de língua que a banca valoriza, treino, modelos anotados e um verificador que aponta vícios no seu texto.</p>
      <nav class="tabs">${ABAS.map(([k, n]) => `<a href="#/redacao/${k}" class="${k === aba ? 'on' : ''}">${n}</a>`).join('')}</nav>`;
  }

  function aulas() {
    const d = R(), rd = lerRD();
    const lido = rd.lido || {};
    return `<p class="mut">Toque numa aula para abrir. As aulas lidas ficam marcadas neste aparelho.</p>` + d.licoes.map((l, i) => `
      <details class="card" data-item ${i === 0 ? 'open' : ''} data-rd-aula="${E(l.id)}"><summary><b>${i + 1}. ${E(l.t)}</b> ${lido[l.id] ? '<span class="tag">lida</span>' : ''}</summary>
        <ul>${l.r.map(x => `<li>${E(x)}</li>`).join('')}</ul>
        ${l.ex ? `<div class="card" style="border-left:6px solid #b42318"><b>Errado:</b> ${E(l.ex.errado)}</div><div class="card" style="border-left:6px solid #157f3b"><b>Certo:</b> ${E(l.ex.certo)}</div>` : ''}
        <p><a href="#/redacao/treino/${E(l.id)}">Treinar este assunto →</a></p>
      </details>`).join('');
  }

  function treino(filtro) {
    const d = R(), rd = lerRD(), t = rd.t || {};
    const itens = d.treino.map((q, i) => ({ q, i })).filter(x => !filtro || x.q.l === filtro);
    const resp = Object.keys(t).length, ok = d.treino.filter((q, i) => t[i] !== undefined && t[i] === q.g).length;
    const filtros = `<div class="row" style="margin-bottom:8px"><a class="btn sec" href="#/redacao/treino">Todos</a>${d.licoes.map(l => `<a class="btn sec" href="#/redacao/treino/${E(l.id)}">${E(l.t.split(':')[0].slice(0, 22))}</a>`).join('')}</div>`;
    return `<div class="card"><b>Seu desempenho:</b> ${ok} acertos em ${resp} respondidas de ${d.treino.length}. <button class="sec" data-rd="zerar">Zerar treino</button>
      <div class="bar"><i style="width:${Math.round(100 * resp / d.treino.length)}%"></i></div></div>${filtros}` +
      itens.map(({ q, i }) => {
        const p = t[i];
        const alts = q.a.map((x, j) => {
          const bg = p === undefined ? '' : (j === q.g ? 'background:#d7f5dd;' : (j === p ? 'background:#fadbd8;' : ''));
          return `<button class="sec" data-rd="resp" data-i="${i}" data-j="${j}" style="${bg}display:block;text-align:left;width:100%;margin:4px 0">${'ABCD'[j]}) ${E(x)}</button>`;
        }).join('');
        const fb = p === undefined ? '' : `<p>${p === q.g ? '✅ <b>Correto.</b>' : '❌ <b>Errado.</b>'} ${E(q.e)}</p>`;
        return `<div class="card" data-item><p><b>${i + 1}.</b> ${E(q.q)}</p>${alts}${fb}</div>`;
      }).join('');
  }

  function modelos() {
    return `<p class="mut">Respostas discursivas modelo, com a explicação do que cada trecho faz pela nota.</p>` + R().modelos.map(m => `
      <details class="card" data-item><summary><b>${E(m.t)}</b></summary>
        <p class="mut"><b>Enunciado:</b> ${E(m.enun)}</p>
        ${m.resp.map(([txt, nota]) => `<div class="card" style="border-left:6px solid #1e3a5f"><p>${E(txt)}</p><p class="mut">💡 ${E(nota)}</p></div>`).join('')}
      </details>`).join('');
  }

  function esqueleto() {
    return `<p class="mut">Roteiro de cada peça. Para o conteúdo jurídico de cada uma, veja os capítulos de «Peças» em Doutrina e prática.</p>` + R().esqueletos.map(e => `
      <details class="card" data-item><summary><b>${E(e.t)}</b></summary><ol>${e.itens.map(x => `<li>${E(x)}</li>`).join('')}</ol></details>`).join('');
  }

  function checklist() {
    const rd = lerRD(), ck = rd.ck || {};
    return `<p class="mut">Passe por esta lista antes de entregar a peça ou a resposta.</p><div class="card">${R().checklist.map((x, i) => `
      <label style="display:flex;gap:8px;margin:8px 0;align-items:flex-start"><input type="checkbox" data-rd="ck" data-i="${i}" ${ck[i] ? 'checked' : ''} style="margin-top:5px"><span>${E(x)}</span></label>`).join('')}
      <button class="sec" data-rd="zerarck">Limpar marcações</button></div>`;
  }

  function verificador() {
    return `<div class="card"><p>Cole sua resposta ou peça. O verificador aponta expressões a evitar, latinismos sem aspas, citações fora do padrão e erros comuns de regência e pontuação. Ele <b>não corrige o conteúdo jurídico</b>: é só uma revisão de forma.</p>
      <textarea id="rdtxt" rows="12" placeholder="Cole aqui o seu texto..." aria-label="texto a verificar">${E(store.get('rdtxt', ''))}</textarea>
      <div class="row" style="margin-top:8px"><button data-rd="verificar">Verificar</button><button class="sec" data-rd="limpar">Limpar</button><span class="mut" id="rdinfo"></span></div></div><div id="rdres"></div>`;
  }

  function analisar(txt) {
    const d = R(), ach = [];
    d.regras.forEach(([re, msg, sug]) => {
      let m; const rx = new RegExp(re, 'giu');
      while ((m = rx.exec(txt))) {
        if (m[0] === sug) { if (m.index === rx.lastIndex) rx.lastIndex++; continue; }
        const a = Math.max(0, m.index - 28), b = Math.min(txt.length, m.index + m[0].length + 28);
        ach.push({ ini: m.index, trecho: '…' + txt.slice(a, b).replace(/\s+/g, ' ') + '…', achado: m[0], msg, sug });
        if (m.index === rx.lastIndex) rx.lastIndex++;
      }
    });
    d.latinismos.forEach(l => {
      const rx = new RegExp('(^|[^\\p{L}])(' + l.replace(/ /g, '\\s+') + ')(?![\\p{L}])', 'giu'); let m;
      while ((m = rx.exec(txt))) {
        const pos = m.index + m[1].length, antes = txt[pos - 1] || '', depois = txt[pos + m[2].length] || '';
        if (!/["“«']/.test(antes) || !/["”»']/.test(depois)) {
          const a = Math.max(0, pos - 28), b = Math.min(txt.length, pos + m[2].length + 28);
          ach.push({ ini: pos, trecho: '…' + txt.slice(a, b).replace(/\s+/g, ' ') + '…', achado: m[2], msg: 'Latinismo sem aspas (use aspas na prova manuscrita, e não use acento nem hífen).', sug: '«' + m[2] + '» ou o equivalente em português' });
        }
      }
    });
    // letras de item
    const itens = [...txt.matchAll(/^\s*([A-Da-d])\)\s*(\S+)/gm)];
    itens.forEach(m => { if (!/^(sim|n[ãa]o)/i.test(m[2])) ach.push({ ini: m.index, trecho: m[0].trim(), achado: m[0].trim(), msg: 'Em questão de sim ou não, comece a resposta com «Sim» ou «Não».', sug: m[1].toUpperCase() + ') Sim/Não...' }); });
    if (txt.trim().length > 200 && !/\bart(?:igo)?s?\.?\s*\d/i.test(txt)) ach.push({ ini: 0, trecho: '', achado: 'sem dispositivo', msg: 'Não encontrei citação de dispositivo legal. Cite o artigo depois da justificativa.', sug: 'nos termos do art. ..., da ...' });
    ach.sort((x, y) => x.ini - y.ini);
    return ach;
  }

  function stats(txt) {
    const pal = (txt.match(/\S+/g) || []).length;
    return `${pal} palavras · cerca de ${Math.ceil(pal / 11)} linhas manuscritas (a discursiva tem no máximo 30 linhas)`;
  }

  function verificar() {
    const txt = document.getElementById('rdtxt').value; store.set('rdtxt', txt);
    document.getElementById('rdinfo').textContent = stats(txt);
    const out = document.getElementById('rdres');
    if (!txt.trim()) { out.innerHTML = '<p class="mut">Cole um texto para verificar.</p>'; return; }
    const ach = analisar(txt);
    out.innerHTML = ach.length ? `<div class="card"><b>${ach.length} ponto(s) para revisar</b></div>` + ach.map(a => `<div class="card" style="border-left:6px solid #b7791f"><p><b>${E(a.achado)}</b> — ${E(a.msg)}</p>${a.trecho ? `<p class="mut">${E(a.trecho)}</p>` : ''}<p>💡 Sugestão: ${E(a.sug)}</p></div>`).join('')
      : '<div class="card" style="border-left:6px solid #157f3b"><b>Nada encontrado pelas regras.</b> Isso não garante que o texto esteja bom: revise vírgulas, coesão e o conteúdo jurídico.</div>';
  }

  window.redacaoView = function (aba, extra) {
    aba = ABAS.some(a => a[0] === aba) ? aba : 'aulas';
    if (!R()) return topo(aba) + '<div class="card">O conteúdo desta sessão (data/curso/redacao.js) não está disponível neste aparelho. Restaure o backup da doutrina.</div>';
    const corpo = { aulas, treino: () => treino(extra), modelos, esqueleto, checklist, verificador }[aba]();
    return topo(aba) + corpo;
  };
  window.redacaoInit = function (aba) { if (aba === 'verificador' && R()) { const t = document.getElementById('rdtxt'); if (t && t.value) verificar(); } };

  document.addEventListener('click', e => {
    const t = e.target.closest('[data-rd]'); if (!t) return;
    const a = t.dataset.rd, rerender = () => { const y = window.scrollY; route(); window.scrollTo(0, y); };
    if (a === 'resp') { const rd = lerRD(); rd.t = rd.t || {}; rd.t[t.dataset.i] = +t.dataset.j; gravarRD(rd); rerender(); }
    else if (a === 'zerar') { const rd = lerRD(); rd.t = {}; gravarRD(rd); rerender(); }
    else if (a === 'zerarck') { const rd = lerRD(); rd.ck = {}; gravarRD(rd); rerender(); }
    else if (a === 'verificar') verificar();
    else if (a === 'limpar') { store.set('rdtxt', ''); document.getElementById('rdtxt').value = ''; document.getElementById('rdres').innerHTML = ''; document.getElementById('rdinfo').textContent = ''; }
  });
  document.addEventListener('change', e => {
    const t = e.target.closest('[data-rd=ck]'); if (!t) return;
    const rd = lerRD(); rd.ck = rd.ck || {}; rd.ck[t.dataset.i] = t.checked; gravarRD(rd);
  });
  document.addEventListener('toggle', e => {
    const d = e.target; if (!d.matches || !d.matches('details[data-rd-aula]') || !d.open) return;
    const rd = lerRD(); rd.lido = rd.lido || {}; if (!rd.lido[d.dataset.rdAula]) { rd.lido[d.dataset.rdAula] = 1; gravarRD(rd); const s = d.querySelector('summary'); if (s && !s.querySelector('.tag')) s.insertAdjacentHTML('beforeend', ' <span class="tag">lida</span>'); }
  }, true);
})();
