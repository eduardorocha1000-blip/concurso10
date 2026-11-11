# Jus Concursos

App (PWA) de estudo para concursos jurídicos: **OAB, Magistratura Estadual SC, Ministério Público SC, Magistratura Federal**.
Funciona offline, instala no Android/iOS ("Adicionar à tela inicial") e não precisa de build.

## Rodar
```bash
python -m http.server 8765
```
Abra http://localhost:8765. (Para instalar no celular, publique a pasta em qualquer hospedagem HTTPS estática: GitHub Pages, Netlify, Cloudflare Pages.)

## O que já existe
Por módulo: visão geral + ranking de artigos mais cobrados · leis com **mapa de calor** (estrelas, cores, nº de editais) · súmulas (STF/STJ/vinculantes) · princípios · enunciados · jurisprudência · doutrina · **mapas mentais** · **fluxogramas interativos** · exemplos resolvidos (família, sucessões, competência) · questões comentadas · **flashcards com repetição espaçada (SM-2)** · discursivas com espelho de autoavaliação · prova oral · backup do progresso.

## Mapa de calor real (a partir das provas)
1. Copie `dados/editais_analise_modelo.csv` para `dados/editais_analise.csv` e **apague as linhas de exemplo**.
2. Para cada prova dos 5 últimos editais, registre uma linha por item cobrado (lei+artigo, súmula, enunciado ou julgado). Colunas e regras estão no topo de `tools/gerar_heat.py`.
3. Rode `python tools/gerar_heat.py`. Ele conta em quantos editais distintos (máx. 5) cada item caiu, valida se o artigo existe nas leis importadas e grava `data/heat.js` (some o aviso "ilustrativo").
Observação: o gerador sobrescreve o `heat.js`; itens sem linha no CSV ficam com 0.

## Súmulas do STF
`python tools/importar_sumulas_stf.py` baixa as Súmulas Vinculantes e as Súmulas do portal do STF para `data/jur_stf.js` (782 de 799 itens na última execução; os demais têm layout diferente na página e continuam só se estiverem na amostra). Os itens da amostra mantêm matéria e frequência; os novos entram como matéria "Geral". Súmulas do STJ: o site bloqueia leitura automática (desafio anti-robô) — copie manualmente para `data/jurisprudencia.js`.

## Leis de Santa Catarina
Constituição Estadual (PDF oficial da ALESC), CODJ (LC 339/2006) e Lei Orgânica do MPSC (LC 738/2019) foram importadas. O servidor da ALESC tem certificado vencido para o Python; baixe com `curl` e passe o arquivo local (`.html` ou `.pdf`) ao `importar_lei.py`.

## ⚠️ O que é amostra e o que falta preencher
O conteúdo em `data/` é uma **amostra pequena** para demonstrar o funcionamento. Ninguém consegue "trazer todo o conteúdo" de cabeça com segurança; o app foi feito para você **encher a base com fontes oficiais**:

| Item | Como completar |
|---|---|
| **Leis completas** | `python tools/importar_lei.py <id> "<nome>" "<matéria>" oab,magsc,mpsc,magfed <url do planalto>` — já testado com o Código Penal (427 artigos). Use os ids `cf`, `cc`, `cpc`, `cp`, `cpp`, `cdc`… para substituir as amostras. |
| **Editais (últimos 5)** | Preencha `editais` de cada módulo em `data/core.js`. |
| **Mapa de calor** | `data/heat.js` hoje é **ilustrativo** (marcado com `ilustrativo: true`). Substitua por contagem real: em quantas das 5 provas o artigo foi cobrado (0–5). Ao colocar `ilustrativo: false` o aviso some. |
| **Súmulas / teses** | Copie dos sites oficiais (STF, STJ, TJSC, TRF4) para `data/jurisprudencia.js`. |
| **Doutrina** | Direitos autorais impedem reproduzir livros. Use sínteses próprias (como as de `data/estudo.js`) com referência à obra. |
| **Questões** | Provas anteriores (FGV, bancas de TJSC/MPSC/TRF4) estão nos sites das bancas; transcreva ou importe com gabarito comentado. |

Todos os textos de amostra devem ser **conferidos** com a fonte oficial antes de estudar por eles.

## Atualização diária, busca e vigência
- `tools/atualizar.py` re-baixa as leis de fonte oficial (Planalto), compara com a versão anterior, atualiza as súmulas do STF, grava `data/changelog.js` (aba 🔔 Novidades; artigos alterados ganham o selo "alterado em …") e faz backup em `backups/` (7 últimos). Se a coleta vier vazia ou muito menor, mantém a versão anterior.
- Tarefa agendada do Windows `JusConcursos-AtualizacaoDiaria` roda `tools/atualizar_diario.bat` todo dia às 03:00 (o PC precisa estar ligado; log em `tools/atualizar.log`). Para remover: `schtasks /Delete /TN JusConcursos-AtualizacaoDiaria /F`.
- O celular só vê a atualização se a pasta for publicada de novo; o app avisa quando a base está há mais de 2 dias sem atualizar.
- 🔎 Pesquisa local (sem IA) nas leis, súmulas, jurisprudência e doutrina, com trecho e link da fonte. Leis exportáveis em TXT, Word e PDF (imprimir).
- Leis de SC (ALESC) vêm de arquivo local e não se atualizam sozinhas.
- Teses do STJ: `python tools/importar_stj.py [meses]` lê os Dados Abertos do STJ (espelhos de acórdãos) e importa os acórdãos que têm tese jurídica ou tema (379 em 12 meses, matéria agrupada por seção/turma). Entra no atualizador diário. Não são todos os acórdãos nem súmulas do STJ.
- Ainda NÃO implementado: súmulas do STJ, LexML, DataJud/TJSC, legislação estadual/municipal em massa, jurisprudência por dispositivo, IA com fontes.
- TJSC / TRF4: o portal do TJSC classifica acesso automatizado como bot e bloqueia ("Bloqueio temporário"); não contornei. Copie as ementas/teses que quiser estudar para `dados/juris_tjsc.csv` (modelo em `dados/juris_modelo.csv`) e rode `python tools/importar_juris_csv.py dados/juris_tjsc.csv tjsc` (para o TRF4 use o nome `trf4`).
