# 30 dias pro Ruan — série "você decide" (canal LUNEX)

Animação 2D vertical (1080x1920). O Ruan, vendedor de abacaxi que não toma banho e acorda meio-dia, tem 30 dias para conquistar a Bia, médica do posto, antes dela se mudar pra São Paulo. Cada episódio termina com duas opções; o próximo episódio mostra a escolhida. 3 episódios por dia: 11h, 15h e 19h.

| pasta/arquivo | o que é |
|---|---|
| `setup.sh` | instala voz (Kokoro pm_santa), fonte e dependências |
| `motor/episodio.py` | monta voz, quadros de teste e o vídeo a partir de `episodios/diaNN/episodio.json` |
| `motor/FORMATO.md` | como escrever um episódio (cenas, atores, tags, câmera, votação) |
| `kit/` | personagens e cenários em SVG gerados por código (`ruan.py`, `elenco.py`) |
| `estado.json` | onde a história está: dia, chance, ajustes do Ruan, histórico, fatos, ganchos |
| `fila.json` | episódios prontos e agendados (links dos vídeos nas branches `upload-*`) |
| `config.json` | marca do Metricool (`metricool_blogId`), redes e horários |
| `arvore.md` | **trilha da história**: votações dos Dias 1–3 e banco de votações de cada ato até o Dia 30 (siga ao escolher e escrever) |
| `referencia/` | estudo do formato e storyboard original |

Os vídeos sobem em branches temporárias `upload-diaNN` só até o Metricool copiar.
