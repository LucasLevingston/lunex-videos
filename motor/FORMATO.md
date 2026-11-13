# Formato do `episodio.json`

Um episódio é uma lista de cenas. A duração de cada cena sai da fala (voz + 0,65 s), nunca menor que `min`.

```json
{
  "dia": 2, "dias_restantes": 29,
  "chance": 0, "chance_fim": 3,          // a barra anima de chance → chance_fim na cena com "sobe_chance": true
  "resultado": "BANHO",                  // selo "VOCÊS ESCOLHERAM: BANHO" na 1ª cena (null no Dia 1)
  "thumb_ator": "ruan:em_pe:feliz",      // quem aparece na capa
  "thumb_texto": "30 DIAS PRO RUAN",
  "legenda_post": "texto do post com hashtags",
  "cenas": [ ... ]
}
```

## Tipos de cena

| tipo | campos | uso |
|---|---|---|
| `cena` | `fundo` (cenário), `atores`, `tags`, `camera`, `efeitos`, `desfoque_fundo`, `sons`, `legenda_y` | quase tudo |
| `close` | `cor` (vermelho, azul, roxo, verde, amarelo), `id` (cabeça), `escala`, `texto`, `tam` | momento de tensão, close no rosto |
| `story` | `usuario`, `linhas` (a última sai menor), `desenho` ("caixa") ou `imagem` (id de ator), `avatar` | story da Bia ou de alguém |
| `chat` | `contato`, `avatar`, `mensagens`: [{`de`: "bia"/"ruan", `texto`, `t`}] | conversa no celular (azul = Ruan) |
| `cards` | `titulo`, `itens`: [[linha1, linha2], ...], `ator` | listas curtas; cada card entra numa frase da fala (a 1ª frase é a abertura) |
| `votacao` | `fala`, `fim`, `a`/`b`: {`palavra`, `sub`, `id`, `icone`}, `proximo` | SEMPRE a última cena |

Toda cena aceita `fala` (narração), `min` (duração mínima), `sem_legenda`.

## Atores
`{"id": "ruan:correndo:suando", "x": 540, "y": 1680, "escala": 0.95}` — `x` é o centro, `y` é a base (pés). Opções:
- `entra`: `esquerda`, `direita`, `pop`, `baixo` (+ `dur_entrada`); `t`: quando aparece
- `sai`: {`t`, `para`: esquerda/direita, `dur`}
- `troca`: [{`t`, `id`}] troca pose/expressão no meio da cena
- `pula`: [segundos], `balanca`, `treme`, `espelhar`, `centro` (x,y viram o centro da imagem)

IDs (ver `motor/atores.py`): `ruan:<pose>:<expr>` (poses: em_pe, apontando, celular, abacaxi, correndo, comemorando, derrotado, rede, escondido, cabeca; expressões: neutro, sono, susto, apaixonado, suando, confiante, vergonha, feliz), `bia:<pose>:<expr>` (em_pe, acenando, bracos_cruzados, nariz_tapado / sorrindo, desconfiada, enojada, surpresa), `bia_cabeca:<expr>`, `coroa:<julgando|chocado|orgulhoso>`, `zefa:<fofocando|espiando>`, `galo:<cantando|desistindo>`.
Cenários: `banca_abacaxi`, `quarto`, `rua_dona_zefa`, `feira`, `casa_bia`. O chão (pés) fica em y≈1680; escala 0.95 é o tamanho normal; o galo usa ~0.45.
O Ruan sai com os ajustes do `estado.json` automaticamente (sem cheiro depois do banho etc.).

## Tags, câmera, efeitos, sons
- `tags`: [{`texto`, `x`, `y`, `t`, `ate`, `tam`, `cor`, `cor_texto`, `rot`}] — balões/placas que dão "pop". Cores: amarelo, verde, azul, vermelho, rosa, branco, preto, laranja, roxo.
- `camera`: {`zoom`: [ini, fim], `zoom_em`: s (zoom rápido), `foco`: [x, y], `punch`: [t, extra], `tremer`: [[t0, t1]]}
- `efeitos`: `coracoes` (+ `coracoes_pos`), `escurecer`
- `sons`: [[t, nome]] — pop, whoosh, ding, thud, galo, ronco, agua, tada, fail. Entradas, tags, cards, chat e votação já têm som automático.
- Ícones da votação: despertador, chuveiro, coracao, haltere, perfume, flor, abacaxi, ou um texto curto.

## Área segura
Nada importante abaixo de y=1700 nem acima de y=200 (HUD). Legenda em y=1450 (1660 em `close`). Tags grandes entre y=250 e 1400.
