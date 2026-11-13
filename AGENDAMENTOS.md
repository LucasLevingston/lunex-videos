# Tarefas agendadas da série (a criar, desativadas até o canal entrar no Metricool)

| tarefa | horário (America/Sao_Paulo) | cron |
|---|---|---|
| 30 dias pro Ruan — episódio A | 05:23 | `CRON_TZ=America/Sao_Paulo 23 5 * * *` |
| 30 dias pro Ruan — episódio B | 07:37 | `CRON_TZ=America/Sao_Paulo 37 7 * * *` |
| 30 dias pro Ruan — episódio C | 09:47 | `CRON_TZ=America/Sao_Paulo 47 9 * * *` |

Cada uma produz 1 episódio e agenda no primeiro horário livre (11:00, 15:00, 19:00). Ficam fora das sessões noturnas do Outra Realidade (23:37–04:11).

## Texto de cada tarefa (troque A/05:23 pela letra e hora da tarefa)

Execução agendada da série animada "30 dias pro Ruan" (canal LUNEX): produzir o PRÓXIMO episódio e agendar no Metricool. O canal publica 3 episódios por dia (11:00, 15:00 e 19:00, America/Sao_Paulo). Esta é a sessão A (05:23); as outras sessões rodam separadas, cada uma faz 1 episódio. Não há ninguém acompanhando, então não faça perguntas.

1. Carregue a skill /ruan-30-dias e siga-a inteira. Se a skill não estiver disponível, anexe o repositório LucasLevingston/lunex-videos com add_repo (acesso push), clone com --depth 1 e siga o arquivo COMO_PRODUZIR.md do repositório.
2. Antes de decidir qualquer coisa, faça git pull: outra sessão pode ter acabado de produzir um episódio. Produza só 1 episódio nesta execução.
3. NÃO leia comentários para decidir a votação anterior: você escolhe a opção que rende o melhor episódio (seção 2 da skill).
4. Se config.json > metricool_blogId estiver null, produza, deixe o episódio na fila (status pronto) e não agende. Se já houver 3 ou mais episódios pronto sem agendar, não produza: só tente agendar e encerre.
5. Se a voz, o render ou o upload falhar, não agende nada quebrado; registre o erro em fila.json (ultimo_erro) e avise com PushNotification.
6. No fim, mande uma mensagem curta: dia produzido, opção escolhida e por quê, votação nova, chance, duração, horário agendado (ou "ficou na fila" e o motivo) e pendências.
