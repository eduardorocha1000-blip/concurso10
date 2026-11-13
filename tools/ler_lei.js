#!/usr/bin/env node
// Uso: node tools/ler_lei.js <id_da_lei> <art1,art2,art5-9,...> [max_caracteres_por_artigo]
const fs = require('fs'), vm = require('vm'), path = require('path');
const c = {}; c.window = c; vm.createContext(c); vm.runInContext('var DATA={leis:[]};', c);
const id = process.argv[2], lista = process.argv[3] || '', max = +(process.argv[4] || 700);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'data', 'leis', id + '.js'), 'utf8'), c);
const L = c.DATA.leis[0], num = s => parseInt(String(s).replace(/\./g, ''), 10);
const want = new Set(); lista.split(',').filter(Boolean).forEach(t => { const m = /^(\S+?)-(\d+)$/.exec(t); if (m && !/[A-Z]$/.test(t)) { for (let i = num(m[1]); i <= num(m[2]); i++) want.add(String(i)); } else want.add(t); });
console.log(L.nome, '\n' + L.fonte);
L.artigos.forEach(a => { const k = String(a.n); if (want.has(k) || want.has(k.replace(/\./g, ''))) console.log('Art. ' + a.n + ' — ' + a.t.replace(/\s+/g, ' ').slice(0, max)); });
