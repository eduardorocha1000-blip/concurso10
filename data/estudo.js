// Princípios, doutrina (sínteses originais), mapas mentais, fluxogramas e exemplos.
(function(){
const ALL=['oab','magsc','mpsc','magfed'];
const P=(materia,nome,desc,mods)=>DATA.principios.push({materia,nome,desc,mods:mods||ALL});
P('Constitucional','Dignidade da pessoa humana','Fundamento da República (art. 1º, III, CF). Vetor interpretativo de todos os direitos fundamentais; veda a coisificação do indivíduo.');
P('Constitucional','Separação dos Poderes','Art. 2º, CF. Independência e harmonia entre Legislativo, Executivo e Judiciário; cláusula pétrea (art. 60, §4º, III).');
P('Administrativo','LIMPE','Art. 37, caput, CF: Legalidade, Impessoalidade, Moralidade, Publicidade e Eficiência. Legalidade para o particular = pode tudo que a lei não proíbe; para o administrador = só o que a lei autoriza.');
P('Processo Civil','Contraditório e ampla defesa','Art. 5º, LV, CF; arts. 9º e 10 do CPC (vedação de decisão-surpresa). Direito de ser ouvido e de influenciar a decisão.');
P('Processo Civil','Cooperação','Art. 6º, CPC: todos os sujeitos do processo devem cooperar para decisão de mérito justa, efetiva e em tempo razoável.');
P('Processo Civil','Inércia e impulso oficial','Arts. 2º e 141 CPC: o processo começa por iniciativa da parte e se desenvolve por impulso oficial; juiz decide nos limites do pedido.');
P('Penal','Legalidade (anterioridade e reserva legal)','Art. 5º, XXXIX, CF; art. 1º, CP. Subprincípios: lei prévia, escrita, estrita e certa.');
P('Penal','Intervenção mínima / fragmentariedade / subsidiariedade','Direito Penal é ultima ratio: só protege bens jurídicos relevantes contra as lesões mais graves, quando outros ramos não bastam.');
P('Penal','Culpabilidade','Não há pena sem culpa (nulla poena sine culpa). Veda responsabilidade penal objetiva.');
P('Processo Penal','Presunção de inocência','Art. 5º, LVII, CF: ninguém é culpado até o trânsito em julgado. Regra probatória (ônus da acusação) e regra de tratamento.');
P('Civil (Família)','Melhor interesse da criança e do adolescente','Art. 227, CF; ECA. Prioridade absoluta; orienta guarda, convivência, adoção e alimentos.');
P('Civil (Família)','Igualdade entre filhos','Art. 227, §6º, CF e art. 1.596 CC: proibidas designações discriminatórias relativas à filiação.');
P('Civil (Sucessões)','Saisine','Art. 1.784 CC: aberta a sucessão, a herança transmite-se imediatamente aos herdeiros, sem solução de continuidade.');
P('Civil (Sucessões)','Intangibilidade da legítima','Arts. 1.789 e 1.846 CC: havendo herdeiros necessários, 50% da herança é reservado a eles.');
P('Civil','Boa-fé objetiva, função social e probidade','Arts. 421 e 422 CC. Boa-fé objetiva: padrão de conduta leal; gera deveres anexos (informação, cooperação, proteção).');
P('Consumidor','Vulnerabilidade e boa-fé','Art. 4º, I e III, CDC. Presunção absoluta de vulnerabilidade do consumidor.');

const D=(materia,titulo,corpo,mods)=>DATA.doutrina.push({materia,titulo,corpo,mods:mods||ALL});
D('Civil (Sucessões)','Sucessão legítima: ordem de vocação hereditária e concorrência',
`<p>Art. 1.829 CC. Ordem: <b>(I) descendentes</b> (com concorrência do cônjuge/companheiro conforme regime), <b>(II) ascendentes</b> (concorrem com cônjuge/companheiro sempre, qualquer regime), <b>(III) cônjuge/companheiro</b> sozinho, <b>(IV) colaterais até o 4º grau</b>.</p>
<h3>Concorrência do cônjuge com descendentes</h3>
<ul><li><b>Comunhão universal:</b> não concorre (já tem meação).</li>
<li><b>Separação obrigatória (art. 1.641):</b> não concorre.</li>
<li><b>Comunhão parcial:</b> concorre <i>apenas</i> se houver bens particulares, e só quanto a eles (STJ, REsp 1.368.123).</li>
<li><b>Separação convencional:</b> concorre (STJ, REsp 992.749).</li>
<li><b>Participação final nos aquestos:</b> concorre, conforme debate doutrinário — revisar posição do STJ.</li></ul>
<h3>Quota</h3><p>Art. 1.832: o cônjuge herda quota igual à dos descendentes que sucederem por cabeça, <b>não podendo a sua quota ser inferior a 1/4 da herança</b> se for ascendente dos herdeiros com quem concorrer.</p>
<h3>Companheiro</h3><p>Após o STF (Tema 809), aplica-se o mesmo regime do art. 1.829 ao companheiro; o art. 1.790 foi declarado inconstitucional.</p>
<p class="mut">Texto de apoio elaborado como síntese de estudo. Aprofunde em Maria Berenice Dias, Flávio Tartuce, Carlos Roberto Gonçalves, Zeno Veloso.</p>`);
D('Processo Civil','Competência: territorial, material e funcional',
`<p><b>Absoluta</b> (matéria, pessoa, função): improrrogável, conhecível de ofício, pode ser alegada a qualquer tempo; gera nulidade de decisão (rescindível). <b>Relativa</b> (valor e território): prorrogável, deve ser alegada em <b>preliminar de contestação</b> (art. 64) sob pena de preclusão.</p>
<h3>Regras de foro (arts. 46–53 CPC)</h3>
<ul><li>Regra geral: domicílio do réu (art. 46).</li><li>Direito real imobiliário: foro da situação da coisa (art. 47); é <b>absoluta</b> nas possessórias imobiliárias (§2º) e, segundo a doutrina majoritária, nas ações sobre propriedade, vizinhança, servidão, divisão/demarcação e nunciação de obra nova (§1º, que veda a opção por foro de eleição/domicílio do réu); relativa nos demais casos.</li>
<li>Inventário/partilha: último domicílio do autor da herança (art. 48).</li>
<li>Alimentos: domicílio ou residência do alimentando (art. 53, II).</li>
<li>Divórcio/união estável: domicílio do guardião do filho incapaz; sem filho, último domicílio do casal; nenhuma das hipóteses, domicílio do réu (art. 53, I).</li>
<li>Reparação de dano por delito/acidente de veículo: domicílio do autor ou local do fato (art. 53, V).</li></ul>
<h3>Conexão e continência</h3><p>Arts. 54–58: reunião de processos para evitar decisões conflitantes; só em competência relativa.</p>
<p class="mut">Síntese de estudo.</p>`);
D('Civil (Família)','Alimentos: natureza, execução e prisão civil',
`<p>Binômio/trinômio <b>necessidade–possibilidade–proporcionalidade</b> (art. 1.694, §1º). Irrepetibilidade; impenhorabilidade; imprescritibilidade do direito (prescrição da pretensão de cobrar parcelas: 2 anos).</p>
<h3>Execução (CPC arts. 528 e ss.)</h3>
<ul><li><b>Rito da prisão:</b> pensão dos <b>3 últimos meses</b> + vincendas (Súm. 309 STJ); prisão de 1 a 3 meses, regime fechado, separado dos presos comuns (art. 528 §§3º, 4º).</li>
<li><b>Rito da penhora:</b> parcelas mais antigas, sem prisão.</li>
<li>Prisão não exime do pagamento das parcelas.</li>
<li>Defesa: só prova de pagamento ou da impossibilidade absoluta de pagar.</li></ul>`);
D('Penal','Teoria do crime (visão analítica tripartida)',
`<p><b>Fato típico</b> (conduta, resultado, nexo causal, tipicidade) → <b>ilicitude</b> (excludentes: legítima defesa, estado de necessidade, estrito cumprimento do dever legal, exercício regular de direito) → <b>culpabilidade</b> (imputabilidade, potencial consciência da ilicitude, exigibilidade de conduta diversa).</p>
<p>Dolo direto/eventual (art. 18, I); culpa consciente x dolo eventual: no eventual o agente assume o risco; na consciente acredita sinceramente que o resultado não ocorrerá.</p>`);

const M=(titulo,materia,arvore)=>DATA.mapas.push({titulo,materia,arvore,mods:ALL});
M('Sucessões','Civil (Sucessões)',{t:'Sucessões',c:[
 {t:'Abertura',c:[{t:'Morte (real/presumida)'},{t:'Saisine – art. 1.784'},{t:'Lei vigente à data da morte'}]},
 {t:'Sucessão legítima',c:[{t:'Ordem do art. 1.829',c:[{t:'Descendentes'},{t:'Ascendentes'},{t:'Cônjuge/companheiro'},{t:'Colaterais até 4º grau'}]},{t:'Herdeiros necessários',c:[{t:'Descendentes'},{t:'Ascendentes'},{t:'Cônjuge'}]},{t:'Legítima = 50%'}]},
 {t:'Sucessão testamentária',c:[{t:'Formas ordinárias: público, cerrado, particular'},{t:'Especiais: marítimo, aeronáutico, militar'},{t:'Capacidade: 16 anos'},{t:'Disponível: 50%'}]},
 {t:'Exclusão',c:[{t:'Indignidade (art. 1.814) – sentença'},{t:'Deserdação (art. 1.961) – testamento'}]},
 {t:'Inventário',c:[{t:'Judicial (art. 610 CPC)'},{t:'Extrajudicial (consenso, capazes, advogado)'},{t:'Foro: art. 48 CPC'},{t:'Prazo: 2 meses abertura / 12 meses fim'}]}]});
M('Competência cível','Processo Civil',{t:'Competência',c:[
 {t:'Absoluta',c:[{t:'Matéria'},{t:'Pessoa'},{t:'Função'},{t:'Conhecível de ofício'}]},
 {t:'Relativa',c:[{t:'Valor'},{t:'Território'},{t:'Prorroga se não arguida (art. 64)'}]},
 {t:'Foros',c:[{t:'Domicílio do réu – art. 46'},{t:'Imóveis – art. 47'},{t:'Herança – art. 48'},{t:'Alimentos – art. 53, II'},{t:'Divórcio – art. 53, I'}]},
 {t:'Modificação',c:[{t:'Conexão / continência'},{t:'Foro de eleição – art. 63'}]}]});
M('Direito de Família','Civil (Família)',{t:'Família',c:[
 {t:'Casamento',c:[{t:'Habilitação e celebração'},{t:'Regimes: comunhão parcial (regra), universal, separação, participação final'},{t:'Dissolução: divórcio (EC 66/10)'}]},
 {t:'União estável',c:[{t:'Art. 1.723 CC'},{t:'Contrato de convivência'},{t:'Regime: comunhão parcial (supletivo)'}]},
 {t:'Filiação',c:[{t:'Biológica, socioafetiva, adoção'},{t:'Presunção pater is est'},{t:'Investigação – Súm. 301 STJ'}]},
 {t:'Poder familiar e guarda',c:[{t:'Compartilhada = regra'},{t:'Unilateral = exceção'}]},
 {t:'Alimentos',c:[{t:'Necessidade x possibilidade'},{t:'Prisão civil – 3 últimas parcelas'}]}]});
M('Teoria do crime','Penal',{t:'Crime',c:[
 {t:'Fato típico',c:[{t:'Conduta'},{t:'Resultado'},{t:'Nexo causal'},{t:'Tipicidade'}]},
 {t:'Ilicitude',c:[{t:'Legítima defesa'},{t:'Estado de necessidade'},{t:'Estrito cumprimento do dever legal'},{t:'Exercício regular de direito'}]},
 {t:'Culpabilidade',c:[{t:'Imputabilidade'},{t:'Potencial consciência da ilicitude'},{t:'Exigibilidade de conduta diversa'}]}]});

// Fluxogramas interativos: tipo q = pergunta, f = fim, p = passo
const F=(titulo,materia,inicio,nos)=>DATA.fluxos.push({titulo,materia,inicio,nos,mods:ALL});
F('Competência territorial cível','Processo Civil','a',{
 a:{tipo:'q',t:'A ação envolve direito real sobre imóvel?',op:[['Sim','b'],['Não','c']]},
 b:{tipo:'q',t:'Versa sobre posse, propriedade, vizinhança, servidão, divisão/demarcação ou nunciação de obra nova?',op:[['Sim','b1'],['Não (ex.: direito real de garantia)','b2']]},
 b1:{tipo:'f',t:'Foro da situação da coisa. Absoluta na possessória (art. 47, §2º); nas demais, o §1º afasta a opção por outro foro (doutrina majoritária: absoluta).'},
 b2:{tipo:'f',t:'Foro de domicílio do réu ou de eleição (art. 47, caput c/c 46) — competência RELATIVA.'},
 c:{tipo:'q',t:'Trata-se de inventário/partilha ou ação contra o espólio?',op:[['Sim','c1'],['Não','d']]},
 c1:{tipo:'f',t:'Último domicílio do autor da herança (art. 48).'},
 d:{tipo:'q',t:'Pedido de alimentos?',op:[['Sim','d1'],['Não','e']]},
 d1:{tipo:'f',t:'Domicílio ou residência do alimentando (art. 53, II).'},
 e:{tipo:'q',t:'Divórcio, separação ou união estável?',op:[['Sim','e1'],['Não','g']]},
 e1:{tipo:'f',t:'1º) domicílio do guardião de filho incapaz; 2º) último domicílio do casal; 3º) domicílio do réu (art. 53, I).'},
 g:{tipo:'f',t:'Regra geral: domicílio do réu (art. 46). Verifique ainda foros especiais do art. 53 (ex.: reparação de dano, consumidor).'}});
F('Sucessão legítima – quem herda?','Civil (Sucessões)','a',{
 a:{tipo:'q',t:'O falecido deixou testamento válido que dispõe de toda a herança?',op:[['Não / só parte','b'],['Sim, havendo herdeiros necessários','a1']]},
 a1:{tipo:'p',t:'Respeite a legítima: 50% pertence aos herdeiros necessários (art. 1.846). Só a metade disponível segue o testamento; o restante segue a ordem legal.',op:[['Continuar','b']]},
 b:{tipo:'q',t:'Deixou descendentes?',op:[['Sim','c'],['Não','d']]},
 c:{tipo:'q',t:'Cônjuge/companheiro é sobrevivente? Qual o regime?',op:[['Comunhão universal ou separação obrigatória','c1'],['Comunhão parcial','c2'],['Separação convencional / outros','c3'],['Não há cônjuge','c4']]},
 c1:{tipo:'f',t:'Só os descendentes herdam (cônjuge tem meação, não herança).'},
 c2:{tipo:'f',t:'Houve bens particulares? SIM: cônjuge concorre com descendentes sobre eles. NÃO: só descendentes herdam.'},
 c3:{tipo:'f',t:'Cônjuge concorre com os descendentes (art. 1.832: não menos que 1/4 se for ascendente de todos os herdeiros com quem concorre).'},
 c4:{tipo:'f',t:'Só os descendentes herdam (grau mais próximo exclui o mais remoto, salvo direito de representação).'},
 d:{tipo:'q',t:'Deixou ascendentes?',op:[['Sim','d1'],['Não','e']]},
 d1:{tipo:'f',t:'Ascendentes herdam em concorrência com cônjuge/companheiro, qualquer que seja o regime (art. 1.836 e 1.837).'},
 e:{tipo:'q',t:'Cônjuge/companheiro sobrevivente?',op:[['Sim','e1'],['Não','e2']]},
 e1:{tipo:'f',t:'Cônjuge/companheiro herda sozinho (art. 1.838).'},
 e2:{tipo:'f',t:'Colaterais até o 4º grau (art. 1.839). Na falta, herança vacante → Município/DF/União (art. 1.844).'}});
F('Estrutura analítica do crime','Penal','a',{
 a:{tipo:'q',t:'Há conduta dolosa/culposa, resultado, nexo causal e tipicidade?',op:[['Sim','b'],['Não','z1']]},
 z1:{tipo:'f',t:'Fato atípico → não há crime (ex.: princípio da insignificância afasta tipicidade material).'},
 b:{tipo:'q',t:'Incide alguma excludente de ilicitude?',op:[['Sim','z2'],['Não','c']]},
 z2:{tipo:'f',t:'Fato típico, mas lícito → não há crime.'},
 c:{tipo:'q',t:'Agente imputável, com potencial consciência da ilicitude e exigibilidade de conduta diversa?',op:[['Sim','z3'],['Não','z4']]},
 z3:{tipo:'f',t:'Crime configurado → dosimetria (art. 68 CP: pena-base, atenuantes/agravantes, causas de aumento/diminuição).'},
 z4:{tipo:'f',t:'Exclui-se a culpabilidade → agente isento de pena (e eventual medida de segurança se inimputável).'}});
F('Prisão civil do devedor de alimentos','Civil (Família)','a',{
 a:{tipo:'q',t:'Débito corresponde às 3 últimas parcelas anteriores ao ajuizamento + vincendas?',op:[['Sim','b'],['Não, parcelas mais antigas','z1']]},
 z1:{tipo:'f',t:'Rito da penhora (art. 523 e ss. c/c 528 §8º) — sem prisão.'},
 b:{tipo:'q',t:'Executado, citado, pagou, provou o pagamento ou justificou a impossibilidade absoluta em 3 dias?',op:[['Sim, justificativa aceita','z2'],['Não','z3']]},
 z2:{tipo:'f',t:'Sem prisão.'},
 z3:{tipo:'f',t:'Decreta-se protesto e prisão de 1 a 3 meses, regime fechado, separado dos presos comuns (art. 528, §§3º e 4º). A prisão não exime do pagamento.'}});

const X=(materia,titulo,caso,solucao)=>DATA.exemplos.push({materia,titulo,caso,solucao,mods:ALL});
X('Civil (Sucessões)','Concorrência do cônjuge — comunhão parcial',
 'João, casado com Maria sob comunhão parcial, falece deixando 2 filhos comuns. Patrimônio: apartamento adquirido na constância do casamento (R$ 600 mil) e um terreno herdado de seu pai antes do casamento (R$ 300 mil).',
 '<b>1)</b> Meação de Maria sobre o apartamento (bem comum): R$ 300 mil; os outros R$ 300 mil integram a herança. <b>2)</b> O terreno é bem particular: integra a herança integral (R$ 300 mil). <b>3)</b> Herança total: R$ 600 mil. <b>4)</b> Como há bens particulares, Maria concorre com os filhos <i>apenas sobre o terreno</i> (STJ, REsp 1.368.123): terreno dividido em 3 partes iguais (R$ 100 mil cada). Sobre o apartamento (parte do falecido, R$ 300 mil), herdam só os filhos (R$ 150 mil cada). <b>Resultado:</b> Maria: R$ 300 mil (meação) + R$ 100 mil; cada filho: R$ 250 mil.');
X('Civil (Sucessões)','Legítima e testamento',
 'Pedro, sem cônjuge, com 1 filho, deixa testamento legando todo o patrimônio (R$ 1 milhão) a uma amiga.',
 'Havendo herdeiro necessário, só 50% é disponível (art. 1.789). O testamento é <b>redutível</b> (ação de redução das disposições testamentárias): amiga recebe R$ 500 mil; o filho recebe R$ 500 mil (legítima, art. 1.846). Não há nulidade total, apenas ineficácia no excesso.');
X('Processo Civil','Competência — inventário e ação de alimentos',
 'Ana mora em Florianópolis/SC, filha de Carlos, falecido com último domicílio em Joinville/SC e imóvel em Curitiba/PR. Ana pretende (a) abrir o inventário e (b) pedir alimentos ao pai de seu filho, que mora em Blumenau/SC.',
 '(a) Inventário: foro de Joinville, último domicílio do autor da herança (art. 48), ainda que o imóvel esteja no PR; (b) alimentos: Ana (ou o filho alimentando) pode ajuizar em seu domicílio — Florianópolis (art. 53, II). Competência territorial relativa: o réu deve arguir a incompetência em preliminar de contestação (art. 64), sob pena de prorrogação.');
X('Civil (Família)','Prisão civil e valor da dívida',
 'Pai deve 10 meses de pensão a filho menor. O credor ajuíza execução.',
 'Pela Súmula 309 do STJ, apenas as <b>3 últimas parcelas anteriores ao ajuizamento + as vencidas no curso</b> autorizam a prisão. As 7 parcelas anteriores seguem pelo rito da penhora (cumprimento de sentença/execução patrimonial), podendo ser cobradas em autos apartados ou no mesmo processo, mas sem prisão.');
X('Penal','Dolo eventual x culpa consciente',
 'Motorista, em alta velocidade e sob efeito de álcool, atropela e mata pedestre.',
 'Se o agente previu o resultado e <b>assumiu o risco</b> (indiferença), há dolo eventual (art. 18, I, CP) → homicídio doloso (art. 121), competência do Júri. Se acreditou sinceramente que evitaria o resultado, culpa consciente → art. 302 CTB. Jurisprudência: embriaguez, velocidade e racha são indícios, mas a análise é do caso concreto.');
})();
