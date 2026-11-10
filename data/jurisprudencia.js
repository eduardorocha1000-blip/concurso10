// Súmulas, enunciados e jurisprudência (amostra). f = frequência nos 5 últimos editais (ILUSTRATIVA).
(function(){
const ALL=['oab','magsc','mpsc','magfed'];
const S=(tribunal,n,materia,texto,f,extra)=>DATA.sumulas.push(Object.assign({tribunal,n,materia,texto,mods:ALL,f:f||{}},extra||{}));
S('STF-SV','11','Penal/Processo Penal','Só é lícito o uso de algemas em casos de resistência e de fundado receio de fuga ou de perigo à integridade física própria ou alheia, por parte do preso ou de terceiros, justificada a excepcionalidade por escrito, sob pena de responsabilidade disciplinar, civil e penal do agente ou da autoridade e de nulidade da prisão ou do ato processual a que se refere, sem prejuízo da responsabilidade civil do Estado.',{oab:5,magsc:4,mpsc:5,magfed:4},{vinculante:true});
S('STF-SV','13','Administrativo','A nomeação de cônjuge, companheiro ou parente em linha reta, colateral ou por afinidade, até o terceiro grau, inclusive, da autoridade nomeante ou de servidor da mesma pessoa jurídica investido em cargo de direção, chefia ou assessoramento, para o exercício de cargo em comissão ou de confiança ou, ainda, de função gratificada na administração pública direta e indireta em qualquer dos poderes da União, dos Estados, do Distrito Federal e dos Municípios, compreendido o ajuste mediante designações recíprocas, viola a Constituição Federal.',{oab:5,magsc:5,mpsc:5,magfed:5},{vinculante:true});
S('STF-SV','14','Processo Penal','É direito do defensor, no interesse do representado, ter acesso amplo aos elementos de prova que, já documentados em procedimento investigatório realizado por órgão com competência de polícia judiciária, digam respeito ao exercício do direito de defesa.',{oab:5,magsc:4,mpsc:5,magfed:4},{vinculante:true});
S('STF-SV','25','Constitucional/Civil','É ilícita a prisão civil de depositário infiel, qualquer que seja a modalidade do depósito.',{oab:5,magsc:5,mpsc:4,magfed:4},{vinculante:true});
S('STF','377','Civil (Família)','No regime de separação legal de bens, comunicam-se os adquiridos na constância do casamento.',{oab:3,magsc:5,mpsc:2,magfed:2});
S('STF','380','Civil (Família)','Comprovada a existência de sociedade de fato entre os concubinos, é cabível a sua dissolução judicial, com a partilha do patrimônio adquirido pelo esforço comum.',{oab:2,magsc:3,mpsc:1,magfed:1});
S('STJ','7','Processo Civil','A pretensão de simples reexame de prova não enseja recurso especial.',{oab:4,magsc:5,mpsc:5,magfed:5});
S('STJ','54','Civil (Responsabilidade)','Os juros moratórios fluem a partir do evento danoso, em caso de responsabilidade extracontratual.',{oab:4,magsc:5,mpsc:3,magfed:4});
S('STJ','297','Consumidor','O Código de Defesa do Consumidor é aplicável às instituições financeiras.',{oab:5,magsc:5,mpsc:4,magfed:4});
S('STJ','301','Civil (Família)','Em ação investigatória, a recusa do suposto pai a submeter-se ao exame de DNA induz presunção juris tantum de paternidade.',{oab:4,magsc:5,mpsc:4,magfed:2});
S('STJ','309','Civil (Família)','O débito alimentar que autoriza a prisão civil do alimentante é o que compreende as três prestações anteriores ao ajuizamento da execução e as que vencerem no curso do processo.',{oab:5,magsc:5,mpsc:4,magfed:2});
S('STJ','358','Civil (Família)','O cancelamento de pensão alimentícia de filho que atingiu a maioridade está sujeito à decisão judicial, mediante contraditório, ainda que nos próprios autos.',{oab:4,magsc:5,mpsc:4,magfed:2});
S('STJ','364','Civil (Bem de família)','O conceito de impenhorabilidade de bem de família abrange também o imóvel pertencente a pessoas solteiras, separadas e viúvas.',{oab:4,magsc:5,mpsc:3,magfed:3});
S('STJ','479','Consumidor/Civil','As instituições financeiras respondem objetivamente pelos danos gerados por fortuito interno relativo a fraudes e delitos praticados por terceiros no âmbito de operações bancárias.',{oab:5,magsc:5,mpsc:4,magfed:4});

const E=(fonte,n,materia,texto,f)=>DATA.enunciados.push({fonte,n,materia,texto,mods:ALL,f:f||{}});
E('CJF – Jornada de Direito Civil','274','Civil','Os direitos da personalidade, regulados de maneira não-exaustiva pelo Código Civil, são expressões da cláusula geral de tutela da pessoa humana, contida no art. 1º, III, da Constituição (princípio da dignidade da pessoa humana).',{magsc:4,magfed:3,oab:2,mpsc:2});

const J=(tribunal,ref,materia,tese,mods,f)=>DATA.juris.push({tribunal,ref,materia,tese,mods:mods||ALL,f:f||{}});
J('STF','RE 878.694 (Tema 809) – repercussão geral','Civil (Sucessões)','É inconstitucional a distinção de regimes sucessórios entre cônjuges e companheiros, devendo ser aplicado, em ambos os casos, o regime do art. 1.829 do Código Civil.',ALL,{oab:4,magsc:5,mpsc:3,magfed:4});
J('STF','ADPF 132 e ADI 4.277','Constitucional/Família','Reconhecida a união estável entre pessoas do mesmo sexo como entidade familiar, com as mesmas regras e consequências da união estável heteroafetiva.',ALL,{oab:4,magsc:5,mpsc:4,magfed:5});
J('STJ','REsp 1.368.123/SP (2ª Seção, 2015)','Civil (Sucessões)','No regime de comunhão parcial, o cônjuge sobrevivente concorre com os descendentes apenas quanto aos bens particulares deixados pelo falecido (art. 1.829, I, CC).',ALL,{oab:3,magsc:5,mpsc:2,magfed:2});
J('STJ','Tese – bem de família','Civil/Processo','O bem de família do fiador em contrato de locação é penhorável (Lei 8.009/90, art. 3º, VII); STF confirmou em RE 1.307.334 (Tema 1127), inclusive para locação comercial.',ALL,{oab:4,magsc:4,mpsc:2,magfed:3});
})();
