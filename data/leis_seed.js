// Trechos de leis (amostra). Para o texto COMPLETO use: python tools/importar_lei.py (veja README).
(function(){
const L = (id, nome, materia, mods, artigos) => DATA.leis.push({ id, nome, materia, mods, parcial: true, artigos });
const ALL = ['oab','magsc','mpsc','magfed'];

L('cf','Constituição Federal de 1988','Direito Constitucional',ALL,[
 {n:'1º',t:'A República Federativa do Brasil, formada pela união indissolúvel dos Estados e Municípios e do Distrito Federal, constitui-se em Estado Democrático de Direito e tem como fundamentos: I - a soberania; II - a cidadania; III - a dignidade da pessoa humana; IV - os valores sociais do trabalho e da livre iniciativa; V - o pluralismo político.'},
 {n:'2º',t:'São Poderes da União, independentes e harmônicos entre si, o Legislativo, o Executivo e o Judiciário.'},
 {n:'5º',t:'Todos são iguais perante a lei, sem distinção de qualquer natureza, garantindo-se aos brasileiros e aos estrangeiros residentes no País a inviolabilidade do direito à vida, à liberdade, à igualdade, à segurança e à propriedade, nos termos seguintes: [...] XXXV - a lei não excluirá da apreciação do Poder Judiciário lesão ou ameaça a direito; [...] LIV - ninguém será privado da liberdade ou de seus bens sem o devido processo legal; LV - aos litigantes, em processo judicial ou administrativo, e aos acusados em geral são assegurados o contraditório e ampla defesa, com os meios e recursos a ela inerentes; [...] LVII - ninguém será considerado culpado até o trânsito em julgado de sentença penal condenatória; [...] LXVII - não haverá prisão civil por dívida, salvo a do responsável pelo inadimplemento voluntário e inescusável de obrigação alimentícia e a do depositário infiel;'},
 {n:'37',t:'A administração pública direta e indireta de qualquer dos Poderes da União, dos Estados, do Distrito Federal e dos Municípios obedecerá aos princípios de legalidade, impessoalidade, moralidade, publicidade e eficiência e, também, ao seguinte: [...]'},
 {n:'226',t:'§ 3º Para efeito da proteção do Estado, é reconhecida a união estável entre o homem e a mulher como entidade familiar, devendo a lei facilitar sua conversão em casamento.'}
]);

L('cc','Código Civil (Lei 10.406/2002)','Direito Civil',ALL,[
 {n:'186',t:'Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito.'},
 {n:'927',t:'Aquele que, por ato ilícito (arts. 186 e 187), causar dano a outrem, fica obrigado a repará-lo.'},
 {n:'1.694',t:'Podem os parentes, os cônjuges ou companheiros pedir uns aos outros os alimentos de que necessitem para viver de modo compatível com a sua condição social, inclusive para atender às necessidades de sua educação. § 1º Os alimentos devem ser fixados na proporção das necessidades do reclamante e dos recursos da pessoa obrigada.'},
 {n:'1.723',t:'É reconhecida como entidade familiar a união estável entre o homem e a mulher, configurada na convivência pública, contínua e duradoura e estabelecida com o objetivo de constituição de família.'},
 {n:'1.784',t:'Aberta a sucessão, a herança transmite-se, desde logo, aos herdeiros legítimos e testamentários.'},
 {n:'1.789',t:'Havendo herdeiros necessários, o testador só poderá dispor da metade da herança.'},
 {n:'1.829',t:'A sucessão legítima defere-se na ordem seguinte: I - aos descendentes, em concorrência com o cônjuge sobrevivente, salvo se casado este com o falecido no regime da comunhão universal, ou no da separação obrigatória de bens (art. 1.640, parágrafo único); ou se, no regime da comunhão parcial, o autor da herança não houver deixado bens particulares; II - aos ascendentes, em concorrência com o cônjuge; III - ao cônjuge sobrevivente; IV - aos colaterais.  [Nota: o STF (Tema 809) equiparou companheiro e cônjuge para fins sucessórios — art. 1.790 inconstitucional.]'},
 {n:'1.846',t:'Pertence aos herdeiros necessários, de pleno direito, a metade dos bens da herança, constituindo a legítima.'}
]);

L('cpc','Código de Processo Civil (Lei 13.105/2015)','Processo Civil',ALL,[
 {n:'46',t:'A ação fundada em direito pessoal ou em direito real sobre bens móveis será proposta, em regra, no foro de domicílio do réu.'},
 {n:'47',t:'Para ação fundada em direito real sobre imóveis é competente o foro de situação da coisa.'},
 {n:'48',t:'O foro de domicílio do autor da herança, no Brasil, é o competente para o inventário, a partilha, a arrecadação, o cumprimento de disposições de última vontade, a impugnação ou anulação de partilha extrajudicial e para todas as ações em que o espólio for réu, ainda que o óbito tenha ocorrido no estrangeiro.'}
]);

L('cp','Código Penal (Decreto-Lei 2.848/1940)','Direito Penal',ALL,[
 {n:'1º',t:'Não há crime sem lei anterior que o defina. Não há pena sem prévia cominação legal.'},
 {n:'121',t:'Matar alguém: Pena - reclusão, de seis a vinte anos.'},
 {n:'155',t:'Subtrair, para si ou para outrem, coisa alheia móvel: Pena - reclusão, de um a quatro anos, e multa.'}
]);

L('cdc','Código de Defesa do Consumidor (Lei 8.078/1990)','Direito do Consumidor',['oab','magsc','mpsc','magfed'],[
 {n:'14',t:'O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços, bem como por informações insuficientes ou inadequadas sobre sua fruição e riscos.'}
]);

L('eoab','Estatuto da Advocacia (Lei 8.906/1994)','Ética Profissional',['oab'],[
 {n:'1º',t:'São atividades privativas de advocacia: I - a postulação a órgão do Poder Judiciário e aos juizados especiais; II - as atividades de consultoria, assessoria e direção jurídicas.'}
]);
})();
