# Sugestões para tornar o app o mais completo possível

## 1. Conteúdo (o que mais pesa)
1. **Pipeline de leis**: importar do Planalto toda a legislação cobrada (CF, CC, CPC, CP, CPP, CDC, ECA, EOAB, LINDB, LOMAN, Lei 8.625/93, LONMP, CTN, leis esparsas) e **reimportar periodicamente** (as leis mudam; ex.: o CP importado já traz alterações recentes). Agende com `cron`/GitHub Actions.
2. **Análise real dos editais**: para cada carreira, pegue as últimas 5 provas + gabaritos. Para cada questão, registre `lei + artigo`, `súmula`, `tema`. Contar ocorrências gera o mapa de calor de verdade (hoje ilustrativo). Idealmente uma planilha → script que gera `heat.js`.
3. **Jurisprudência oficial**: baixar Súmulas/Vinculantes/Temas do STF e Súmulas/Teses repetitivas do STJ, TJSC, TRF4 e enunciados do CJF, FONAJEF, FPPC, CNJ. Marcar vigência (cancelada/superada) e **data de atualização**.
4. **Informativos**: resumo mensal dos informativos STF/STJ — as bancas de magistratura e MP cobram muito.
5. **Doutrina**: sínteses próprias por tópico do edital + indicação de autores e capítulos; evitar copiar obras protegidas. Incluir **divergências doutrinárias e posição majoritária** (decisivo em discursiva e oral).
6. **Específico de SC**: Código de Divisão e Organização Judiciária (LC 339/2006), Regimento Interno do TJSC, Lei Orgânica do MPSC, Constituição Estadual, jurisprudência do TJSC.
7. **Discursivas e sentenças**: banco de questões com espelho real da banca, **modelo de peça/sentença** e rubrica de correção (ex.: 1 ponto por tese). Magistratura exige sentenças cível e criminal.
8. **Prova oral**: perguntas por ponto do edital + áudio gravado do próprio aluno e cronômetro.
9. **OAB 2ª fase**: modelos de peças por área (petição inicial, contestação, apelação, habeas corpus, etc.), com checklist de pontuação.

## 2. Aprendizado
- **Plano de estudo adaptativo**: data da prova → cronograma diário com peso por matéria (frequência × seu desempenho).
- **Repetição espaçada** também para artigos e súmulas (já há SM-2 nos flashcards).
- **Caderno de erros**: toda questão errada vira flashcard automático.
- **Simulados cronometrados** no formato da banca (nº de questões, tempo, penalização).
- **Estatísticas** por matéria/tema, evolução semanal, mapa de pontos fracos.
- **Grifos e anotações** nos artigos, com busca; "leis secas" com tradução em linguagem simples ao lado.
- **Comparador de artigos** (antes/depois de reforma) e **quadros comparativos** (ex.: dolo x culpa, competência absoluta x relativa).
- Mais **mapas mentais/fluxogramas** (hoje 4 e 4) — gerados a partir do sumário do edital.

## 3. Técnica
- Migrar o armazenamento de `localStorage` para **IndexedDB** (volume grande de leis/anotações) e adicionar **busca global** (FlexSearch/Lunr) em todo o conteúdo.
- **Sincronização entre aparelhos** (conta + backend: Supabase/Firebase) e backup automático.
- Empacotar com **Capacitor** para publicar nas lojas (Android/iOS) — a PWA atual já serve de base.
- Banco de conteúdo em **JSON versionado** + validação automática (script que confere números de artigos e links).
- **Atualizações de conteúdo** por pacotes (modular por carreira) para o app não ficar pesado.
- Acessibilidade (leitor de tela, fonte ajustável), **modo escuro** (já existe) e **áudio** (TTS para ouvir leis no trânsito).
- Testes automatizados do conteúdo e do app.

## 4. Qualidade jurídica e riscos
- **Toda amostra deve ser conferida** com a fonte oficial; revisão por advogado/professor.
- Mostrar **data de atualização** e **fonte** em cada item.
- Atenção a **direitos autorais** (doutrina, questões de bancas, comentários de cursinhos): use apenas conteúdo próprio, licenciado ou domínio público (leis, súmulas e atos oficiais são públicos).
- Não prometer "aprovação"; incluir aviso de que o app é ferramenta de apoio.

## 5. Gamificação e hábito
Metas diárias, sequência de dias (streak), pontos por revisão, ranking opcional, lembretes por notificação (PWA push).

## 6. Ordem sugerida de execução
1. Importar leis completas de todos os módulos → 2. Montar planilha de análise dos editais e gerar `heat.js` real → 3. Importar súmulas/temas → 4. Banco de questões com comentários → 5. Plano de estudo + simulados + caderno de erros → 6. Backend/sincronização e publicação nas lojas.
