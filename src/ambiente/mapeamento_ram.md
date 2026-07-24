# Mapeamento da RAM — Boxing (PettingZoo Atari)

Documentação do processo de engenharia reversa do vetor de 128 bytes de
RAM retornado pelo ambiente `boxing_v2` com `obs_type="ram"`.

## Metodologia

1. Coleta de RAM ao longo de um episódio com ações aleatórias, para
   identificar quais índices variam (script `src/ambiente/mapear_ram.py`).
2. Testes dirigidos, fixando a ação de um jogador, para isolar quais
   índices correspondem à posição/estado de cada agente.
3. Correlação entre mudanças de RAM e o `reward` retornado pelo ambiente,
   para identificar os bytes de placar.
4. Cruzamento com fonte acadêmica -- Anand et al., "Unsupervised State
   Representation Learning in Atari" (mila-iqia/atari-representation-learning,
   https://github.com/mila-iqia/atari-representation-learning) -- que
   documenta o mapeamento de RAM de vários jogos Atari a partir do
   código-fonte original, usado para validar cruzado os achados empíricos.

## Resultados (mapeamento final validado)

| Índice (0-127) | Variável | Evidência |
|---|---|---|
| 17 | relógio (segundos restantes) | variou de forma consistente ao longo do episódio, mudando a cada ~60 frames (1 segundo de jogo); confirmado por inspeção do dataset gerado |
| 18 | placar do jogador 1 (`placar_p1`) | validado diretamente: reward do agente `first_0` mudou de 0 → 1 no EXATO mesmo passo em que o byte 18 mudou de 0 → 1 (teste controlado em `src/ambiente/extrair_estado.py::validar_placar`) |
| 19 | placar do jogador 2 (`placar_p2`) | mudou no evento de `reward=-2` detectado durante o mapeamento inicial; também confirmado pela fonte acadêmica |
| 32 | posição x do jogador 1 (`p1_x`) | variação consistente ao fixar ações de movimento direita/esquerda do `first_0`; confirmado por fonte acadêmica |
| 33 | posição x do jogador 2 (`p2_x`) | variação consistente ao fixar ações de movimento direita/esquerda do `second_0`; confirmado por fonte acadêmica |
| 34 | posição y do jogador 1 (`p1_y`) | variação ao fixar ações CIMA/BAIXO do `first_0` (teste "P1 para CIMA/BAIXO": byte foi de 4 para 3 subindo, e de 4 para 18 descendo) |
| 35 | posição y do jogador 2 (`p2_y`) | variação ao fixar ações CIMA/BAIXO do `second_0` (teste "P2 para CIMA/BAIXO": byte foi de 87 para 73 subindo) |

**Nota sobre codificação:** diferente de alguns outros jogos do Atari, os
bytes de placar e relógio usados aqui **não precisaram de decodificação
BCD** -- a leitura direta como inteiro (`int(ram[byte])`) já bateu
exatamente com os valores reais observados no jogo (por exemplo, o
placar validado foi de 0 para 1, não de `0x00` para `0x01` interpretado
como BCD, que daria o mesmo resultado nesse caso específico, mas os
testes de validação confirmaram que a leitura direta é suficiente dentro
da faixa de placar observada durante os experimentos).

A função `extrair_estado()` em `src/ambiente/extrair_estado.py` implementa
esse mapeamento final e é reutilizada pelos três agentes (heurístico,
genético e RL).

## Índices testados e descartados

Durante a exploração inicial (`mapear_ram.py`), 37 dos 128 índices
variaram com ações aleatórias, e destes, os seguintes também variaram
com ações de movimento fixas, mas **não foram usados** por não terem uma
interpretação clara como variável de estado do jogo:

`0, 14, 15, 20, 24, 26, 28, 30, 49, 51, 57, 59, 63, 64, 65, 66, 67, 68,
69, 70, 71, 72, 75, 77, 99, 101, 103, 105, 109, 111, 119, 122`

Alguns padrões observados nesses índices:
- Os bytes **24, 26, 28 e 30** sempre mudavam para o mesmo valor em
  conjunto (por exemplo, de 16 para 72 simultaneamente) -- consistente
  com bytes de **animação/sprite** (frame da animação do soco ou do
  movimento), não posição.
- O byte **0** teve variações muito grandes (de 75 para 134, por
  exemplo) mesmo em testes de movimento simples -- possivelmente um
  contador interno de frames ou estado de renderização, não usado.
- O byte **14** variou de forma decrescente de forma atípica (255 → 239
  → 127) -- possivelmente relacionado a um contador regressivo interno
  não documentado (talvez de round ou de estado de introdução).

Esses índices foram deixados de fora do mapeamento final por não
agregarem informação necessária para os três agentes implementados
(que dependem apenas de posição, placar e relógio).

## Próximos passos

- [x] Refinar hipóteses com mais testes dirigidos
- [x] Validar mapeamento (posições confirmadas via testes dirigidos +
      fonte acadêmica; placar confirmado via correlação direta com o
      reward do ambiente)
- [x] Usar os índices confirmados como features nos três agentes
      (heurístico, genético e RL, todos via `extrair_estado()`)

## Jornada de depuração do agente heurístico

Registro do processo de descoberta (útil para o vídeo -- itens 5 e 9 do
conteúdo obrigatório):

1. **Primeira versão**: agente nunca pontuava (placar 0 em 20/20 partidas
   contra o aleatório). Diagnóstico revelou que `p1_x` travava sempre no
   mesmo valor durante o "modo ataque" -- ações de soco combinadas com
   direção pareciam não se mover, mas na real o problema era outro.

2. **Descoberta 1 -- distância mínima física**: existe uma distância de
   colisão mínima entre os dois lutadores (~14px) que o modelo de
   movimento não conseguia superar. O limiar de ataque inicial (5px) era
   fisicamente impossível de alcançar. Corrigido para 16px.

3. **Descoberta 2 -- cooldown do soco**: mesmo alinhado e com FIRE sendo
   enviado a cada frame, nenhum soco conectava. Hipótese: segurar o
   soco sem soltar impede a animação do golpe de completar (o jogo
   reinicia a animação a cada novo comando). Corrigido com um cooldown
   de N frames entre socos -- isso fez o agente finalmente pontuar.

4. **Descoberta 3 -- placar "fantasma" (valores como 120 ou 98/99)**:
   ao rodar episódios mais longos, o placar mostrava valores
   impossíveis. Causa: a RAM continuava sendo lida mesmo depois do
   episódio já ter terminado (round decidido por nocaute ou tempo), e
   nesse estado o byte 18 não representa mais o placar real. Corrigido
   parando de atualizar o placar assim que `termination`/`truncation`
   fica `True`.

5. **Resultado final**: com `COOLDOWN_SOCO=8` e episódios de até 6000
   passos, o agente heurístico consegue ficar colado no oponente e
   vencer por nocaute em boa parte das partidas contra o agente
   aleatório -- confirmado visualmente com `render=True`.

**Limitação conhecida**: o desempenho é bimodal -- em algumas partidas o
agente domina (placar alto, nocaute), em outras fica em 0. Hipótese: a
posição/trajetória inicial do oponente aleatório às vezes atrapalha a
fase de aproximação. Fica registrado como possibilidade de melhoria
(item 9 do vídeo).
