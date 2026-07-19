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
