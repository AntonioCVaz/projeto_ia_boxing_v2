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

## Resultados (preencher após rodar o script)

| Índice (0-127) | Hipótese | Evidência |
|---|---|---|
| _preencher_ | posição jogador 1 (eixo x?) | mudou de forma consistente ao fixar ação de movimento |
| _preencher_ | placar jogador 1 | mudou apenas quando reward > 0 |
| ... | ... | ... |

## Índices testados e descartados

_Bytes que variaram mas não foi possível associar a nenhuma variável
interpretável (podem ser contadores internos do jogo, RNG, etc.)_

## Próximos passos

- [ ] Refinar hipóteses com mais testes dirigidos
- [ ] Validar mapeamento visualmente (comparar screenshot com valores de RAM)
- [ ] Usar os índices confirmados como features nos três agentes

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
   enviado a cada frame, nenhum soco conectava. Hipótese: seguravam o
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
