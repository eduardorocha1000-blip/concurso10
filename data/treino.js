// Flashcards, questões comentadas, discursivas e provas orais (amostra).
(function(){
const ALL=['oab','magsc','mpsc','magfed'];
let ci=0;
const C=(materia,f,v,mods)=>DATA.cards.push({id:'c'+(++ci),materia,f,v,mods:mods||ALL});
C('Constitucional','Quais os fundamentos da República (art. 1º, CF)?','Soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, pluralismo político (mnemônico: SO-CI-DI-VA-PLU).');
C('Constitucional','Há prisão civil por dívida no Brasil?','Só do devedor voluntário e inescusável de alimentos. Depositário infiel: ilícita (SV 25 / Súm. 419 STJ).');
C('Administrativo','Princípios expressos do art. 37, caput, CF?','LIMPE: Legalidade, Impessoalidade, Moralidade, Publicidade, Eficiência.');
C('Administrativo','Qual a SV sobre nepotismo?','SV 13: veda nomeação de cônjuge, companheiro ou parente até 3º grau da autoridade nomeante ou de servidor de direção, chefia ou assessoramento.');
C('Civil (Sucessões)','Em que momento se transmite a herança?','Com a abertura da sucessão (morte) — princípio da saisine (art. 1.784 CC).');
C('Civil (Sucessões)','Quem são herdeiros necessários?','Descendentes, ascendentes e cônjuge (art. 1.845 CC). Companheiro: após o Tema 809 STF, equiparado para fins sucessórios.');
C('Civil (Sucessões)','Qual o tamanho da legítima?','50% da herança (art. 1.846 CC).');
C('Civil (Sucessões)','Cônjuge casado em comunhão parcial concorre com descendentes?','Só se o falecido deixou bens particulares, e apenas sobre eles (STJ REsp 1.368.123).');
C('Civil (Sucessões)','Indignidade x deserdação','Indignidade: exclusão por sentença em ação própria (art. 1.814), vale para sucessão legítima/testamentária. Deserdação: cláusula testamentária, só para herdeiros necessários, com justa causa provada em ação (art. 1.961).');
C('Civil (Família)','Quais regimes de bens existem no CC?','Comunhão parcial (supletivo), comunhão universal, separação (convencional ou obrigatória) e participação final nos aquestos.');
C('Civil (Família)','Prisão civil: quantas parcelas?','As 3 últimas anteriores ao ajuizamento + as que vencerem (Súm. 309 STJ); prazo de 1 a 3 meses, regime fechado.');
C('Civil (Família)','Súmula 301 STJ?','Recusa a exame de DNA em investigação de paternidade gera presunção relativa (juris tantum) de paternidade.');
C('Civil (Família)','Súmula 377 STF?','Na separação legal (obrigatória), comunicam-se os bens adquiridos na constância do casamento (STJ exige prova do esforço comum — EREsp 1.623.858).');
C('Processo Civil','Foro competente para inventário?','Último domicílio do autor da herança (art. 48 CPC).');
C('Processo Civil','Foro das ações de alimentos?','Domicílio ou residência do alimentando (art. 53, II CPC).');
C('Processo Civil','Quando se alega incompetência relativa?','Em preliminar de contestação (art. 64 CPC); se não, prorroga-se.');
C('Processo Civil','Competência absoluta ou relativa: critérios?','Absoluta: matéria, pessoa, função. Relativa: valor e território.');
C('Penal','Quais as fases/elementos do crime (teoria tripartida)?','Fato típico, ilicitude e culpabilidade.');
C('Penal','Dolo eventual x culpa consciente','Dolo eventual: assume o risco. Culpa consciente: prevê, mas acredita sinceramente que não ocorrerá.');
C('Consumidor','Responsabilidade do fornecedor de serviços (art. 14 CDC)?','Objetiva (independe de culpa); do profissional liberal, subjetiva (§4º).');
C('Consumidor','Súmula 479 STJ?','Bancos respondem objetivamente por fortuito interno (fraudes de terceiros em operações bancárias).');
C('Processo Civil','Súmula 7 STJ?','Reexame de prova não cabe em recurso especial.');
C('Ética (OAB)','Atividades privativas da advocacia (art. 1º, EOAB)?','Postulação a órgão do Judiciário e juizados especiais; consultoria, assessoria e direção jurídicas.',['oab']);

let qi=0;
const Q=(materia,banca,ano,enun,alts,gab,coment,mods)=>DATA.questoes.push({id:'q'+(++qi),materia,banca,ano,enun,alts,gab,coment,mods:mods||ALL});
Q('Civil (Sucessões)','Original (estudo)','',
 'Maria, casada em comunhão parcial, é viúva de José, que deixou dois filhos e bens particulares. No tocante a esses bens particulares, Maria:',
 ['Não herda, pois já tem meação.','Concorre com os filhos quanto aos bens particulares.','Herda sozinha, por ser cônjuge.','Herda apenas o usufruto.'],1,
 'Art. 1.829, I, CC e STJ REsp 1.368.123: no regime de comunhão parcial, o cônjuge concorre com descendentes apenas se houver bens particulares, e só quanto a eles. A meação é direito patrimonial distinto, não herança.');
Q('Processo Civil','Original (estudo)','',
 'Para o inventário de pessoa falecida no estrangeiro, com último domicílio no Brasil, é competente:',
 ['O foro da situação dos bens.','O foro do domicílio do inventariante.','O foro do último domicílio do autor da herança no Brasil.','O foro da Justiça Federal da capital.'],2,
 'Art. 48 CPC: foro do domicílio do autor da herança, no Brasil, ainda que o óbito tenha ocorrido no estrangeiro.');
Q('Constitucional','Original (estudo)','',
 'Sobre a prisão civil por dívida, segundo a CF e o STF:',
 ['Admitida para depositário infiel.','Admitida só para devedor voluntário e inescusável de alimentos.','Vedada em qualquer hipótese.','Admitida para devedor de tributos.'],1,
 'Art. 5º, LXVII, CF e Súmula Vinculante 25 do STF: ilícita a prisão do depositário infiel; subsiste a do devedor de alimentos.');
Q('Civil (Família)','Original (estudo)','',
 'Em ação investigatória, a recusa do suposto pai ao exame de DNA:',
 ['Gera presunção absoluta de paternidade.','Gera presunção relativa de paternidade.','Não produz efeitos.','Extingue o processo.'],1,
 'Súmula 301 STJ: presunção juris tantum (relativa), que deve ser avaliada com outras provas.');
Q('Penal','Original (estudo)','',
 'O princípio expresso no art. 1º do Código Penal é o da:',
 ['Culpabilidade.','Legalidade (reserva legal e anterioridade).','Lesividade.','Intervenção mínima.'],1,
 '"Não há crime sem lei anterior que o defina. Não há pena sem prévia cominação legal." Legalidade, previsto também no art. 5º, XXXIX, CF.');
Q('Civil (Sucessões)','Original (estudo)','',
 'Após o julgamento do Tema 809 pelo STF, a sucessão do companheiro:',
 ['Segue o art. 1.790 do CC.','Segue o art. 1.829 do CC, igualando-se ao cônjuge.','Não existe.','Depende de escritura pública de convivência.'],1,
 'RE 878.694: inconstitucional o art. 1.790; aplica-se o art. 1.829 a cônjuges e companheiros.');
Q('Processo Civil','Original (estudo)','',
 'A competência territorial para ação sobre direito real imobiliário (propriedade) é, em regra:',
 ['Do domicílio do réu, relativa.','Do foro da situação da coisa; com impacto absoluto na possessória e nas ações indicadas no art. 47, §1º.','Do domicílio do autor.','Livre por eleição de foro.'],1,
 'Art. 47 CPC. Possessórias imobiliárias: competência absoluta (§2º). Nas ações do §1º, não se admite foro de eleição/domicílio do réu.');
Q('Civil','Original (estudo)','',
 'Aquele que, por ação ou omissão voluntária, negligência ou imprudência, viola direito e causa dano a outrem, ainda que exclusivamente moral:',
 ['Comete ato ilícito (art. 186 CC).','Comete abuso de direito (art. 187).','Comete ato lícito.','Responde apenas penalmente.'],0,
 'É a definição de ato ilícito do art. 186 CC. Seu dever de reparar vem do art. 927.');
Q('Consumidor','Original (estudo)','',
 'Aplica-se o CDC às instituições financeiras?',
 ['Não.','Sim (Súmula 297 STJ).','Só para pessoas físicas.','Apenas para crédito imobiliário.'],1,
 'Súmula 297 STJ. Atenção: a Súmula 479 STJ trata do fortuito interno bancário.');
Q('Processo Civil','Original (estudo)','',
 'Contra acórdão que reexaminou provas, cabe REsp?',
 ['Sim, por violação a lei.','Não, incide a Súmula 7 do STJ.','Sim, por divergência.','Cabe apenas RE.'],1,
 'Súmula 7 STJ: a pretensão de simples reexame de prova não enseja recurso especial.');

// Questões ORIGINAIS (não são de provas reais) — conferir sempre com a lei/súmula citada.
const O='Original (estudo)';
Q('Penal',O,'','O agente esgota os atos executórios, mas, antes da consumação, pratica nova conduta que impede a produção do resultado. Ele responde:',
 ['Por tentativa, com a pena reduzida.','Apenas pelos atos já praticados (arrependimento eficaz).','Pelo crime consumado.','Não responde por nada.'],1,
 'Art. 15 CP. Arrependimento eficaz: esgota os meios, mas impede o resultado. Na desistência voluntária o agente interrompe a execução. Nos dois casos responde só pelos atos já praticados.');
Q('Penal',O,'','Segundo a Súmula 231 do STJ, a incidência de circunstância atenuante:',
 ['Pode reduzir a pena abaixo do mínimo legal.','Não pode conduzir à redução da pena abaixo do mínimo legal.','Só vale na terceira fase.','Obriga o juiz a reduzir em 1/6.'],1,
 'Súmula 231 STJ. Já a agravante também não ultrapassa o máximo. Cuidado: causas de diminuição (3ª fase) podem levar abaixo do mínimo.');
Q('Penal',O,'','Segundo a Súmula 444 do STJ, inquéritos policiais e ações penais em curso:',
 ['Podem agravar a pena-base como maus antecedentes.','Não podem ser usados para agravar a pena-base.','Valem apenas como conduta social.','Geram reincidência.'],1,
 'Súmula 444 STJ: é vedada a utilização de inquéritos e ações penais em curso para agravar a pena-base (presunção de inocência).');
Q('Penal',O,'','Para a Súmula 593 do STJ, o crime de estupro de vulnerável (vítima menor de 14 anos):',
 ['Exige comprovação de violência real.','Configura-se com conjunção carnal ou ato libidinoso, mesmo com consentimento da vítima ou relacionamento anterior.','Depende de representação da vítima.','Admite afastamento pelo consenso familiar.'],1,
 'Súmula 593 STJ (art. 217-A CP): o consentimento, a experiência sexual anterior ou o relacionamento amoroso com o agente não afastam o crime.');
Q('Processo Penal',O,'','Súmula 438 do STJ: é inadmissível extinguir a punibilidade pela prescrição da pretensão punitiva com base em:',
 ['Pena concretamente aplicada.','Pena hipotética ou virtual, com perspectiva de condenação futura.','Pena máxima abstrata.','Decisão do tribunal.'],1,
 'Súmula 438 STJ veda a chamada prescrição em perspectiva (pena hipotética).');
Q('Processo Penal',O,'','A prisão preventiva pode ser decretada, entre outros fundamentos, para:',
 ['Antecipar a pena.','Garantia da ordem pública, da ordem econômica, conveniência da instrução criminal ou assegurar a aplicação da lei penal.','Satisfazer o clamor popular isoladamente.','Qualquer crime, sem prova da materialidade.'],1,
 'Art. 312 CPP: exige prova da existência do crime e indício suficiente de autoria, além de perigo gerado pelo estado de liberdade do imputado. Não é antecipação de pena.');
Q('Constitucional',O,'','O instrumento para assegurar o conhecimento de informações relativas à pessoa do impetrante constantes de bancos de dados de entidades governamentais é:',
 ['Mandado de segurança.','Habeas corpus.','Habeas data.','Mandado de injunção.'],2,
 'Art. 5º, LXXII, CF. HC (LXVIII) protege liberdade de locomoção; MI (LXXI) supre falta de norma regulamentadora; MS (LXIX) protege direito líquido e certo não amparado por HC/HD.');
Q('Constitucional',O,'','O vitaliciamento dos juízes de primeiro grau ocorre:',
 ['Imediatamente após a posse.','Após dois anos de exercício, dependendo a perda do cargo, nesse período, de deliberação do tribunal.','Após cinco anos, por decisão do CNJ.','Após três anos de estágio probatório.'],1,
 'Art. 95, I, CF: vitaliciedade, no primeiro grau, só após dois anos de exercício; depois, a perda do cargo exige sentença judicial transitada em julgado.',['magsc','magfed','oab']);
Q('Constitucional',O,'','São princípios institucionais do Ministério Público, segundo a Constituição:',
 ['Legalidade, moralidade e eficiência.','Unidade, indivisibilidade e independência funcional.','Hierarquia, disciplina e unidade.','Inamovibilidade, vitaliciedade e irredutibilidade.'],1,
 'Art. 127, §1º, CF. Vitaliciedade, inamovibilidade e irredutibilidade de subsídio são garantias (art. 128, §5º, I).',['mpsc','oab']);
Q('Constitucional',O,'','A respeito da competência da Justiça Federal (art. 109, I, CF), uma causa em que é parte sociedade de economia mista federal:',
 ['É da Justiça Federal.','É da Justiça Estadual (Súmulas 556 STF e 42 STJ).','É sempre do STF.','É da Justiça do Trabalho.'],1,
 'Art. 109, I, CF cita União, autarquias e empresas públicas federais; sociedade de economia mista fica de fora e a competência é da Justiça Estadual.',['magfed','oab','magsc']);
Q('Administrativo',O,'','A responsabilidade civil do Estado por danos causados por seus agentes, nessa qualidade, é, em regra:',
 ['Subjetiva.','Objetiva, na modalidade risco administrativo, com direito de regresso contra o agente em caso de dolo ou culpa.','Objetiva integral para toda omissão.','Inexistente se houver culpa de terceiro.'],1,
 'Art. 37, §6º, CF. Pessoas jurídicas de direito público e prestadoras de serviço público respondem objetivamente; regresso contra o agente depende de dolo ou culpa.');
Q('Administrativo',O,'','Súmula 473 do STF: a Administração pode anular seus próprios atos quando eivados de vícios que os tornam ilegais, e revogá-los por motivo de:',
 ['Qualquer motivo, sem limite.','Conveniência ou oportunidade, respeitados os direitos adquiridos, com apreciação judicial sempre possível.','Ordem do Ministério Público.','Decisão do TCU.'],1,
 'Súmula 473 STF (e 346): autotutela. Anulação: ilegalidade. Revogação: conveniência e oportunidade. Direitos adquiridos são respeitados.');
Q('Civil',O,'','Segundo o CC, prescreve em três anos a pretensão de:',
 ['Cobrança de dívidas líquidas constantes de instrumento público ou particular.','Reparação civil.','Pretensão geral dos direitos pessoais.','Alimentos.'],1,
 'Art. 206, §3º, V, CC (3 anos para reparação civil). Dívida líquida em instrumento: 5 anos (§5º, I). Prazo geral: 10 anos (art. 205). Alimentos: 2 anos a partir do vencimento (§2º).');
Q('Civil',O,'','Segundo o STJ, é lícita a cumulação de indenizações de dano estético e dano moral (Súmula 387) e de dano material e moral oriundos do mesmo fato (Súmula 37). Isso significa que:',
 ['O dano estético absorve o moral.','São categorias autônomas e podem ser fixadas cumulativamente.','Só se admite uma por processo.','Dependem de pedido expresso em ação separada.'],1,
 'Súmulas 37 e 387 STJ: verbas autônomas, cumuláveis.');
Q('Civil',O,'','No caso de responsabilidade extracontratual, os juros de mora fluem a partir:',
 ['Da citação.','Do evento danoso (Súmula 54 STJ).','Da sentença.','Do trânsito em julgado.'],1,
 'Súmula 54 STJ. Correção monetária do dano moral: a partir do arbitramento (Súmula 362 STJ).');
Q('Civil (Família)',O,'','O cancelamento de pensão alimentícia de filho que atingiu a maioridade, segundo a Súmula 358 do STJ:',
 ['Ocorre automaticamente aos 18 anos.','Está sujeito a decisão judicial, mediante contraditório, ainda nos próprios autos.','Depende só de pedido extrajudicial.','Nunca é possível.'],1,
 'Súmula 358 STJ: a maioridade não extingue automaticamente o dever; exige-se contraditório (o filho pode necessitar, ex.: estudos).');
Q('Civil (Família)',O,'','A mulher que renunciou aos alimentos na separação judicial:',
 ['Nunca terá pensão previdenciária.','Tem direito à pensão previdenciária por morte do ex-marido se comprovar necessidade econômica superveniente (Súmula 336 STJ).','Terá direito automático.','Só tem direito se houve culpa do ex-marido.'],1,
 'Súmula 336 STJ. Lembrar a diferença: renúncia a alimentos × direito previdenciário.');
Q('Consumidor',O,'','O direito de reclamar de vícios aparentes caduca em:',
 ['30 dias para serviço e produto não duráveis, e 90 dias para duráveis.','5 anos.','7 dias.','1 ano.'],0,
 'Art. 26 CDC (decadência). Art. 27: prescrição de 5 anos para reparação por fato do produto ou serviço. Não confundir vício (art. 18) com fato (art. 12/14).');
Q('Processo Civil',O,'','No procedimento comum, o prazo para contestar é:',
 ['5 dias corridos.','15 dias úteis.','10 dias úteis.','30 dias corridos.'],1,
 'Art. 335 CPC (15 dias) e art. 219 (contagem em dias úteis). Prazo da apelação: 15 dias úteis (art. 1.003, §5º). Embargos de declaração: 5 dias (art. 1.023).');
Q('Processo Civil',O,'','Na condenação, os honorários advocatícios de sucumbência são fixados entre:',
 ['5% e 10% do valor da causa.','10% e 20% sobre o valor da condenação, do proveito econômico ou do valor da causa.','20% e 30%.','Livremente, sem limite.'],1,
 'Art. 85, §2º, CPC. Fazenda Pública tem faixas escalonadas (§3º).');
Q('ECA',O,'','Segundo o ECA, a internação do adolescente em conflito com a lei:',
 ['Pode durar até 10 anos.','Não excede três anos e será reavaliada, no máximo, a cada seis meses.','É indeterminada.','Só se aplica a maiores de 18 anos.'],1,
 'Art. 121, §§2º e 3º, ECA. Criança: até 12 anos incompletos; adolescente: de 12 a 18 (art. 2º). Liberação compulsória aos 21 anos.');
Q('Ética (OAB)',O,'','O prazo de prescrição da pretensão de cobrança de honorários de advogado, segundo o Estatuto da OAB, é de:',
 ['1 ano.','5 anos.','10 anos.','3 anos.'],1,
 'Art. 25 da Lei 8.906/1994: prescreve em 5 anos, contados do vencimento do contrato, do trânsito em julgado da decisão, da ultimação do serviço, da renúncia ou da revogação do mandato.',['oab']);

const Dc=(materia,tema,enun,espelho,mods)=>DATA.discursivas.push({materia,tema,enun,espelho,mods:mods||ALL});
Dc('Civil (Sucessões)','Concorrência sucessória e companheiro',
 'Joana viveu 12 anos em união estável com Paulo, sem contrato. Paulo faleceu deixando um filho de relacionamento anterior, um imóvel comprado durante a convivência e um terreno herdado antes. Quem herda e em qual proporção? Fundamente.',
 ['Identificar o regime: comunhão parcial (art. 1.725 CC)','Meação de Joana sobre o imóvel comum','Tema 809 STF: equiparação a cônjuge; art. 1.829, I','Concorrência com o filho só sobre bens particulares (STJ REsp 1.368.123)','Cálculo da herança e quinhões','Saisine – art. 1.784','Comparar quota do art. 1.832 (se filho comum x exclusivo)']);
Dc('Processo Civil','Competência territorial em ação de divórcio com alimentos',
 'Casal residiu em Chapecó/SC. A esposa mudou-se com o filho de 5 anos para Curitiba/PR. O marido continua em Chapecó. Onde propor divórcio cumulado com alimentos? A competência é absoluta ou relativa?',
 ['Art. 53, I, "a": domicílio do guardião de filho incapaz (Curitiba)','Art. 53, II: alimentos – domicílio do alimentando','Natureza relativa (território) – art. 63 e 64','Proteção ao incapaz (STJ tende a tratar como relativa, mas com interesse de incapaz)','Cumulação e conexão (art. 327 CPC)','Defesa do réu: exceção/preliminar de incompetência']);
Dc('Penal','Dolo eventual no trânsito',
 'Condutor embriagado, em racha, mata dois pedestres. Qual o crime e juízo competente? Justifique.',
 ['Distinção dolo eventual x culpa consciente (art. 18, I CP)','Teoria do consentimento/assunção do risco','Crime: art. 121 (dolo eventual) vs. art. 302 CTB','Competência do Júri (art. 5º, XXXVIII, "d" CF), pronúncia, in dubio pro societate','Análise de elementos objetivos do caso','Jurisprudência STJ/STF']);

const Or=(materia,pergunta,resposta,mods)=>DATA.orais.push({materia,pergunta,resposta,mods:mods||ALL});
Or('Civil (Sucessões)','Explique a saisine e seus efeitos práticos.','Com a abertura da sucessão (morte), a herança transmite-se imediatamente aos herdeiros (art. 1.784 CC). Efeitos: herdeiros ficam legitimados a defender a posse e o domínio (ações possessórias), lei aplicável é a vigente à data da morte (art. 1.787), e o inventário é declaratório quanto à transmissão.');
Or('Processo Civil','Qual a diferença entre competência absoluta e relativa? Exemplos.','Absoluta: matéria, pessoa e função; não pode ser modificada por vontade das partes; pode ser reconhecida de ofício e a qualquer tempo; decisão incompetente pode ser rescindida. Relativa: valor e território; prorrogável; exige alegação em preliminar de contestação (art. 64, §1º CPC). Exemplo: ação possessória imobiliária (absoluta); ação de cobrança contra o domicílio do réu (relativa).');
Or('Constitucional','O que é o princípio da simetria?','Obriga os entes federativos a reproduzirem, nas suas Constituições e leis orgânicas, os princípios básicos do modelo federal, ressalvadas as autonomias locais. Fundamentado nos arts. 25 e 11 ADCT, aplica-se, p.ex., ao processo legislativo e à organização dos poderes; STF julga ADIs contra violações.');
Or('Penal','Diferencie desistência voluntária e arrependimento eficaz.','Desistência voluntária: o agente, podendo prosseguir, interrompe a execução (não esgotou os meios). Arrependimento eficaz: esgota os atos executórios, mas impede o resultado. Em ambos responde apenas pelos atos já praticados (art. 15 CP). Tentativa: execução interrompida por circunstâncias alheias à vontade (art. 14, II).');
Or('Civil (Família)','Quais os requisitos da guarda compartilhada?','Art. 1.583 e 1.584 CC: é a regra, mesmo sem consenso, quando ambos os genitores aptos ao poder familiar; exceção: um deles declarar ao juiz que não deseja a guarda. Tempo de convívio deve ser dividido de forma equilibrada; a cidade-base é a que melhor atenda aos interesses do filho.');
})();
