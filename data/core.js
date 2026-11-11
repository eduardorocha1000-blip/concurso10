// Núcleo: módulos, matérias e editais analisados.
// Preencha "editais" com os 5 últimos concursos de cada carreira (banca, ano, link) — veja SUGESTOES.md.
window.DATA = {
  leis: [], sumulas: [], principios: [], enunciados: [], juris: [], doutrina: [],
  mapas: [], fluxos: [], exemplos: [], cards: [], questoes: [], discursivas: [], orais: [],
  modulos: [
    { id: 'oab', nome: 'OAB', cor: '#1e6fb8', icone: '🎓',
      desc: '1ª fase (objetiva) e 2ª fase (peça prático-profissional). Banca: FGV.',
      editais: [ /* {nome:'XXXVIII Exame de Ordem', ano:2023, banca:'FGV', url:''} */ ],
      materias: ['Ética Profissional','Direito Constitucional','Direito Civil','Processo Civil','Direito Penal','Processo Penal','Direito Administrativo','Direito Tributário','Direito do Trabalho','Direito Empresarial','Direito do Consumidor','ECA','Direito Ambiental','Direitos Humanos','Direito Internacional','Filosofia do Direito'] },
    { id: 'magsc', nome: 'Magistratura Estadual SC', cor: '#8a1c3c', icone: '⚖️',
      desc: 'Juiz Substituto do TJSC. Fases: objetiva, discursivas, sentenças, oral, títulos.',
      editais: [],
      materias: ['Direito Constitucional','Direito Civil','Processo Civil','Direito Penal','Processo Penal','Direito Administrativo','Direito Empresarial','Direito do Consumidor','ECA','Direito Tributário','Direito Eleitoral','Direito Previdenciário','Direitos Humanos','Formação Humanística','Organização Judiciária de SC','LOMAN'] },
    { id: 'mpsc', nome: 'Ministério Público SC', cor: '#1f7a4d', icone: '🛡️',
      desc: 'Promotor de Justiça Substituto do MPSC. Objetiva, discursivas, oral.',
      editais: [],
      materias: ['Direito Constitucional','Direito Penal','Processo Penal','Direito Civil','Processo Civil','Tutela Coletiva (ACP, Improbidade)','ECA e Idoso','Direito Ambiental','Direito do Consumidor','Direito Eleitoral','Direito Administrativo','Lei Orgânica do MP (Lei 8.625/93)','Criminologia','Direitos Humanos'] },
    { id: 'magfed', nome: 'Magistratura Federal', cor: '#5b3a9a', icone: '🏛️',
      desc: 'Juiz Federal Substituto (TRF4 para SC). Objetiva, discursivas, sentenças, oral.',
      editais: [],
      materias: ['Direito Constitucional','Direito Administrativo','Direito Civil','Processo Civil','Direito Penal','Processo Penal','Direito Tributário','Direito Previdenciário','Direito Empresarial','Direito Econômico e Financeiro','Direito Internacional','Direitos Humanos','Formação Humanística','LOMAN'] },
    { id: 'enam', nome: 'ENAM – Exame Nacional da Magistratura', cor: '#b45309', icone: '📝',
      desc: 'Prova objetiva nacional (ENFAM/FGV) exigida antes dos concursos de ingresso na magistratura. 80 questões; eliminatória.',
      editais: [],
      materias: ['Direito Constitucional','Direito Civil','Direito Processual Civil','Direito Penal e Processual Penal','Direito Administrativo','Direitos Humanos','Direito Empresarial','Formação humanística e ética'] }
  ]
};
