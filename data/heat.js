// Mapa de calor: quantos dos 5 últimos editais cobraram o artigo (0 a 5), por módulo.
// ATENÇÃO: valores abaixo são ILUSTRATIVOS (estimativa), NÃO resultado de análise real de provas.
// Substitua pela análise real. Formato: HEAT.<idLei>["<artigo sem pontos>"] = {oab:n, magsc:n, mpsc:n, magfed:n}
window.HEAT = { ilustrativo: true,
  cf: { '1': {oab:4,magsc:4,mpsc:4,magfed:5}, '2': {oab:3,magsc:3,mpsc:3,magfed:4}, '5': {oab:5,magsc:5,mpsc:5,magfed:5},
        '37': {oab:5,magsc:5,mpsc:4,magfed:5}, '226': {oab:4,magsc:4,mpsc:4,magfed:3} },
  cc: { '186': {oab:5,magsc:5,mpsc:4,magfed:4}, '927': {oab:5,magsc:5,mpsc:4,magfed:4}, '1694': {oab:4,magsc:5,mpsc:4,magfed:2},
        '1723': {oab:4,magsc:5,mpsc:3,magfed:3}, '1784': {oab:4,magsc:5,mpsc:3,magfed:3}, '1789': {oab:3,magsc:4,mpsc:2,magfed:2},
        '1829': {oab:5,magsc:5,mpsc:4,magfed:4}, '1845': {oab:3,magsc:4,mpsc:2,magfed:2}, '1846': {oab:3,magsc:4,mpsc:2,magfed:2} },
  cpc: { '42': {oab:2,magsc:3,mpsc:3,magfed:3}, '46': {oab:5,magsc:5,mpsc:4,magfed:4}, '47': {oab:5,magsc:5,mpsc:4,magfed:4},
         '48': {oab:4,magsc:5,mpsc:3,magfed:3}, '53': {oab:4,magsc:5,mpsc:4,magfed:3} },
  cp: { '1': {oab:5,magsc:5,mpsc:5,magfed:5}, '121': {oab:5,magsc:5,mpsc:5,magfed:5}, '155': {oab:5,magsc:5,mpsc:5,magfed:5} },
  cdc: { '14': {oab:5,magsc:4,mpsc:4,magfed:3} },
  eoab: { '1': {oab:5,magsc:0,mpsc:0,magfed:0} }
};
