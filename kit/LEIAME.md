# Kit da série "30 dias pro Ruan"

- `poses/`: 9 poses do Ruan (SVG + PNG). `expressoes/`: 8 rostos. `ajustes/`: como ele fica depois de cada voto.
- `elenco/`: Bia, médica loira de jaleco e estetoscópio (5 poses/expressões, inclusive tapando o nariz por causa do cheiro), Seu Coroa (o abacaxi velho e ranzinza: julgando, chocado, orgulhoso), Dona Zefa na janela (espiando, fofocando), Galo (cantando, desistindo).
- `cenarios/`: banca de abacaxi, quarto (relógio 12:07), rua da Dona Zefa, feira, casa da Bia (caixas de mudança). Tamanho do vídeo: 1080x1920. `_teste_escala` mostra Ruan e Bia na banca na escala certa (0,95, pés na linha da calçada).
- `FOLHA_MODELO_RUAN.png`: tudo junto, para conferir.
- `ruan.py` e `elenco.py` geram tudo de novo: `python ruan.py kit` e `python elenco.py kit`. As cores ficam no topo dos arquivos.

## Animar (HyperFrames/CSS)
Cada parte é um `<g>` com id e gira em torno da junta:
| id | junta (x, y) |
|---|---|
| braco_L / braco_R | 252,458 / 348,458 |
| antebraco_L / antebraco_R | cotovelo (a 105 px do ombro) |
| coxa_L / coxa_R | 276,660 / 324,660 |
| canela_L / canela_R | joelho (a 125 px do quadril) |
| cabeca | 300,410 (pescoço) |
| camada_cheiro | some quando o voto do banho vencer |

Para trocar a expressão sem trocar a pose: `character(pose, expr)` em `ruan.py`.
Os ajustes (`dirty`, `bags`, `stubble`, `messy_hair`, `muscle`) ficam ligados ou desligados para sempre, conforme os votos.
