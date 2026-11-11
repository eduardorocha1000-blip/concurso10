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

## Pesquisa de jurisprudência ao vivo (sem armazenar)
Rode `tools/iniciar_app.bat` (ou `python tools/servidor.py`): o servidor local serve o app e consulta os tribunais na hora, sem guardar as decisões (só os favoritos, neste aparelho). Tela ⚖️ no topo do app.
- **Texto completo:** STF (API pública do portal; ementa, relator, órgão, datas, legislação citada, precedente qualificado, link do inteiro teor).
- **Metadados (DataJud/CNJ):** STJ, TST, TSE, STM, 27 TJs + TJDFT, 6 TRFs, 24 TRTs, 27 TREs, 3 TJMs — número, classe, órgão julgador, assuntos, data de ajuizamento. O DataJud não fornece ementa nem inteiro teor, e cada consulta leva ~30–50 s. Cada tribunal tem o botão "pesquisar no site oficial".
- **Bloqueados para robôs:** STJ (pesquisa de jurisprudência), TJSC, TSE, LexML, TJSP (captcha) — não são contornados; use o link para o site oficial.
- Campos que a fonte não fornece ficam nulos. Cada resultado traz fonte e data da verificação.
- **Organização sem IA:** marque decisões e use "Comparar lado a lado", "Legislação citada (consolidada)", "Palavras-chave em comum" ou "Copiar lista" (não resume nem interpreta).
- **IA (opcional, desligada por padrão):** defina `ANTHROPIC_API_KEY` no ambiente deste PC e reinicie o servidor. A IA só recebe as decisões que você marcar ("usar na IA"), deve citar processos e não inventar precedentes. A chave fica só no servidor.
- Só funciona com o servidor local ligado (no GitHub Pages/celular fora do PC não há pesquisa ao vivo).

## Leis e súmulas
- 79 leis completas (`tools/lote_leis.py` importa um lote do Planalto; o atualizador diário as renova).
- Súmulas: STF (782 de 799) e STJ (649, do PDF oficial `SumulasSTJ.pdf`; súmulas posteriores a esse PDF não estão incluídas — `python tools/importar_sumulas_stj.py`).

## ENAM, súmulas por grupo, mapas em imagem e prática dentro da doutrina
- **Módulo ENAM** (📝): guia com estrutura da prova (80 questões, FGV/ENFAM — dados de fontes secundárias: **confira o edital**), distribuição por disciplina, horas semanais proporcionais e progresso de leitura da doutrina. Usa os mesmos conteúdos da magistratura (leis, súmulas, jurisprudência, doutrina, prática).
- **Súmulas por grupo:** abaixo do filtro, escolha STF, Vinculantes, STJ etc. TST/TSE/STM ficam vazios (sites bloqueiam robôs): copie para um CSV e rode `python tools/importar_sumulas_csv.py dados/sumulas_tst.csv tst`.
- **Mapas mentais em imagem (SVG):** os 4 mapas de exemplo (`python tools/gerar_mapas.py`) e um mapa por capítulo da doutrina, gerado dos títulos do capítulo (`tools/importar_doutrina.py`; ficam em `data/doutrina/mapas/`, fora do repositório público).
- **Prática dentro da doutrina:** aba "Doutrina e prática". Em cada disciplina (e em Sucessões/Família) há o bloco "Prática" com mapas, fluxogramas, exemplos, questões, flashcards, discursivas e prova oral. A revisão do dia com repetição espaçada continua em `#/m/<módulo>/cards`.
- `tools/servidor.py` agora envia `Cache-Control: no-cache` (o navegador revalida os arquivos).

## Editais: a matéria dos últimos concursos (📋)
Tela `#/editais` (e o botão em "Visão geral" de cada módulo): conteúdo programático **copiado dos editais**, por grupo — OAB (47º e 46º Exame; programa da 2ª fase + descrição da 1ª), Magistratura SC (TJSC 2026 e 2024), MPSC (45º/2025, 2023 ×2, 2020), Magistratura Federal (TRF5 2026, TRF6 2025, TRF2 2025, TRF1 2025 — não achei edital recente do TRF4) e ENAM (2026.1 e 2026.2). Cada edital traz o link oficial, a banca, o quadro de distribuição de questões (quando o PDF permitiu extrair), as disciplinas com os pontos numerados, um comparativo de disciplinas entre editais e busca de tema.
- Gerado por `python tools/editais_extrair.py <pasta com os PDFs>` (lista de editais no topo do script). A extração é automática: confira no edital oficial.
- Para acrescentar um edital novo: baixe o PDF, extraia o texto (`.txt` com o mesmo nome) e inclua uma linha em `EDITAIS`.

## Informativos e súmulas organizadas
- **Informativos (🔎 em ⚖️ › botão "Informativos"):** pesquisa ao vivo, sem armazenar, nos informativos do **STF** (base `informativos` do portal; mostra trechos da edição) e do **STJ** (Informativo de Jurisprudência: processo, ramo, tema, destaque, legislação). Os demais tribunais não têm busca pública utilizável aqui (bloqueiam robôs, captcha ou não publicam): aparece o link do site oficial. Endpoints `/api/informativos` do `tools/servidor.py`.
- **Súmulas STF (CSV do portal):** `python tools/importar_sumulas_stf_csv.py export1.csv export2.csv ...` → `data/jur_stf_sumulas.js` (736 súmulas, com situação — cancelada/alterada/superada —, ramo do direito, órgão, data, publicação e observação).
- **Súmulas STJ (lista oficial em PDF):** `python tools/importar_verbetes_stj.py VerbetesSTJ.pdf` atualiza `data/jur_stj_sumulas.js` (676 súmulas até a 676; 29 canceladas; textos com acentuação). Atenção: `tools/importar_sumulas_stj.py` regenera esse arquivo a partir do PDF antigo e apaga as atualizações — rode o de verbetes depois.
- **Organização na aba Súmulas:** grupos (Vinculantes, STF, STJ), **ramo do direito**, situação (vigentes/canceladas…) e ordem (número, mais novas, por ramo, mais cobradas). Onde a fonte não informa o ramo (Súmulas Vinculantes, STJ a partir da 650), a classificação é automática por palavras-chave, marcada "auto".
