---
name: ruan-30-dias
description: Produz e agenda os episódios da série animada "30 dias pro Ruan" (você decide) do canal LUNEX, 3 por dia no Metricool. Use para criar o próximo episódio do Ruan e da Bia.
---

# 30 dias pro Ruan — produzir o próximo episódio

Série animada 2D vertical no formato "você decide": cada episódio termina com duas opções e o seguinte mostra a escolhida. **Não leia comentários para decidir:** escolha você a opção que rende o melhor episódio. O canal publica 3 episódios por dia (11:00, 15:00 e 19:00, America/Sao_Paulo). Cada execução produz **1 episódio**, o próximo da história.

Tudo mora no repositório `LucasLevingston/lunex-videos` (público). Leia lá `README.md` e `motor/FORMATO.md`.

## 0. Preparar
1. `add_repo` LucasLevingston/lunex-videos (push) e `git clone --depth 1` em `/home/claude/lunex-videos`. Antes de começar, `git pull`.
2. `bash setup.sh` (instala a voz Kokoro pm_santa, fonte e dependências; baixa ~350 MB de modelo do GitHub).
3. Leia `config.json`, `estado.json`, `fila.json` e os `episodio.json` dos 2 últimos dias (são o modelo de tom e de cena).

## 1. Ver se precisa produzir
- Itens da `fila.json` com status `pronto` ainda não agendados: se já houver **3 ou mais**, não produza; vá direto ao passo 7 e encerre.
- Se existir pasta em `episodios/` sem item na fila (ex.: o Dia 1), renderize essa pasta (passos 5 e 6) antes de criar outra.

## 2. Decidir a opção vencedora do episódio anterior
`estado.json > ultima_votacao` tem as duas palavras. Escolha a que rende a melhor história agora:
- alterne avanços (o Ruan melhora) e desastres engraçados; não deixe a mesma área (higiene, coragem, trabalho, aparência) vencer duas vezes seguidas;
- de vez em quando, escolha a opção "errada" e faça o narrador zoar quem votou nela, como nas referências;
- a opção que perdeu pode voltar numa votação futura ("Quem votou em DENTES? Ainda não.").
Registre em `historico[-1].vencedora`.

## 3. Escrever o episódio (`episodios/diaNN/episodio.json`, NN = dia com 2 dígitos)
Formato em `motor/FORMATO.md`. Duração alvo **60 a 100 s** (~150 a 220 palavras de fala). Molde, medido nas referências (`referencia/ESTUDO.md`):

| bloco | tempo | o que acontece |
|---|---|---|
| Resultado | 0–8 s | `"resultado": "PALAVRA"` (selo automático) + o narrador comenta a escolha e zoa os dois lados ("Finalmente gente com bom senso." / "Vocês são cruéis.") |
| Situação | 8–18 s | lembra 1 problema fixo ou piada antiga (Seu Coroa, Dona Zefa, Galo Desistente, cheiro, cartão recusado) |
| Execução | 18–70 s | o Ruan tenta cumprir a escolha em 3–4 cenas/cenários; uma piada a cada 3–5 s; pelo menos um "ficou pior do que parecia" |
| Vitória | 70–85 s | o ajuste fica (`sobe_chance: true` na cena, `chance_fim` maior) ou dá errado e a chance cai |
| Bia | 85–98 s | `chat`, `story` ou encontro: a reação dela expõe o próximo defeito, que vira a votação |
| Votação | final | cena `votacao`: `fala` com a pergunta e `fim` "Comenta uma palavra. Daqui a pouco tem o dia N+1." |

Regras:
- **Fala:** narrador debochado que fala com o público ("vocês", "você"); frases curtas; evite vírgulas desnecessárias (a voz trava nelas); números na fala por extenso ("trinta dias"); nunca mais de 2 frases seguidas sem mudar algo na tela.
- **Personagens fixos:** Ruan (bem magro, vende abacaxi, não toma banho, acorda meio-dia, apaixonado pela Bia há 5 anos); Bia (loira, médica do posto, se muda pra São Paulo no dia 30); Seu Coroa (abacaxi velho de bigode que julga em silêncio); Dona Zefa (vizinha fofoqueira na janela); Galo Desistente. Pode criar coadjuvantes só com o que o kit desenha.
- **Continuidade:** o que foi conquistado fica (`estado.json > ajustes` e `fatos`); use `ganchos_abertos` e callbacks de episódios anteriores.
- **Votação:** palavras curtas (≤ 7 letras), em maiúsculas, bem diferentes entre si; `sub` com 2–3 palavras; `id` = cabeça do Ruan com expressão que combine; `icone` do FORMATO.md.
- **Contadores:** `dia` = N; `dias_restantes` = 31 − N; `chance` = chance atual; `chance_fim` = nova chance (sobe 2 a 6 num acerto, cai 2 a 5 num desastre; nunca passa de 100).
- **Tom:** humor leve para todas as idades; a Bia é respeitada (o alvo da piada é o Ruan); nada de conteúdo sexual, palavrão, marcas ou pessoas reais.
- `legenda_post`: 2–4 linhas no estilo do Dia 1 + "Comenta UMA palavra: A ou B." + hashtags `#30diaspororuan #vocedecide #animacao #historinha #humor`.
- `thumb_ator` e `thumb_texto` (ex.: "O BANHO DO RUAN").

**Dia 30 (final da temporada):** sem votação de ajuste; se a chance ≥ 60 a Bia fica (ou chama o Ruan pra ir junto), senão ela vai e ele promete ir atrás. A votação final é "TEMPORADA 2?" com duas direções. Depois, `estado.json` ganha `temporada` + 1, novo objetivo de 30 dias, `dia_atual` volta a 0 (o Dia 1 da nova temporada recomeça a contagem), e ajustes conquistados continuam.

## 4. Atualizar o kit, se precisar
Se a história pedir pose, expressão, cenário ou ícone que não existe, acrescente no `kit/ruan.py`, `kit/elenco.py` ou `motor/episodio.py` seguindo o mesmo traço (contorno preto grosso, cores chapadas) e confira numa imagem. Não troque o visual dos personagens existentes.

## 5. Voz e quadros de teste
```bash
python3 motor/episodio.py episodios/diaNN/episodio.json voz
python3 motor/episodio.py episodios/diaNN/episodio.json quadros <6 a 8 tempos, nos momentos mais cheios>
```
Abra os quadros em `episodios/diaNN/teste/` com Read. Corrija texto sobreposto, ator fora do quadro, legenda em cima de tag e qualquer coisa abaixo de y=1700. Repita só os quadros que mudaram.

## 6. Vídeo e upload
```bash
python3 motor/episodio.py episodios/diaNN/episodio.json video   # video.mp4, thumb.jpg, legenda.txt
```
- Confira com `ffprobe` que tem vídeo e áudio e dura 40–110 s.
- Branch temporária: `git checkout -b upload-diaNN && git add -f episodios/diaNN/video.mp4 episodios/diaNN/thumb.jpg && git commit && git push -u origin upload-diaNN`, depois volte para a main.
- Confira com curl que respondem 200: `https://raw.githubusercontent.com/LucasLevingston/lunex-videos/upload-diaNN/episodios/diaNN/video.mp4` e `.../thumb.jpg`.
- Na main: acrescente em `fila.json > itens` {`dia`, `titulo` ("30 dias pro Ruan · Dia N"), `texto` (legenda_post), `video_url`, `thumb_url`, `branch`, `criado_em`, `status`: "pronto", `agendado_para`: null, `plannerUrl`: null, `ultimo_erro`: null}; atualize `estado.json` (`dia_atual`, `dias_restantes`, `chance`, `ajustes`, `fatos`, `ganchos_abertos`, novo item em `historico` com resumo e votação, `ultima_votacao`); commit e push (se recusado: `git pull --rebase` e push de novo).

## 7. Agendar no Metricool
- Se `config.json > metricool_blogId` for null: não agende. Encerre com a mensagem final dizendo que o episódio ficou na fila.
- Senão: `getBrandSettings` (confira que a marca existe), `getScheduledPosts` dos próximos 7 dias. Os episódios saem **em ordem**: agende o item `pronto` de menor `dia` no primeiro horário livre (11:00, 15:00 ou 19:00) depois do último episódio já agendado. Rascunhos (draft) não ocupam horário.
- `createScheduledPost` com: `providers` instagram (`instagramData.type` REEL), tiktok e youtube (`youtubeData`: type short, title = titulo, madeForKids false, category COMEDY) — só as redes de `config.json > metricool_redes` que a marca tiver; `text` = texto; `media` = [video_url]; `videoThumbnailUrl` = thumb_url; `publicationDate` no fuso America/Sao_Paulo.
- Se recusar a capa: tente com `videoCoverMilliseconds` 1000 no lugar. Se recusar outra coisa: deixe `pronto`, grave o erro em `ultimo_erro` e avise.
- Agendou: confira que a mídia aponta para static.metricool.com; `fila.json` → status `agendado`, `agendado_para`, `plannerUrl`; commit e push; apague a branch `upload-diaNN` (`git push origin --delete upload-diaNN`).
- Agende os outros itens `pronto` que couberem na mesma execução, sempre em ordem.

## 8. Mensagem final
Uma mensagem curta: dia produzido, opção que você escolheu e por quê (1 linha), votação nova, chance, duração, horário agendado ou "ficou na fila" e o motivo, e qualquer pendência.
