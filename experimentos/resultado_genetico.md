# Resultado final -- Agente Genético vs. Agente Aleatório

Protocolo: 20 execuções, mesmo formato de avaliação usado no agente
heurístico (`avaliar_heuristico.py`), para comparação justa.

## Resultado

| Métrica | Valor |
|---|---|
| Vitórias | 0 |
| Empates | 11 |
| Derrotas | 9 |
| Placar médio -- genético | 0.05 |
| Placar médio -- aleatório | 2.15 |

## Interpretação

O agente genético não venceu nenhuma partida e empatou em 0x0 na maioria
das execuções (11 de 20) -- consistente com a estratégia degenerada
identificada durante o treinamento (ver nota de desenvolvimento em
`src/genetico/agente_genetico.py`): o indivíduo "campeão" aprendeu a
evitar risco ficando a uma distância seguraum, sem nunca de fato
engajar em combate, já que o risco esperado de atacar (dado o alto
placar que o oponente aleatório consegue por sorte) supera o ganho
esperado.

Esse resultado confirma empiricamente o diagnóstico de reward hacking:
o agente não é "ruim" por falha de implementação -- ele está otimizando
corretamente a função de fitness que definimos, só que essa função
permitia uma solução de baixo risco/baixo retorno que não corresponde
ao comportamento desejado (vencer lutas).

## Comparação com o agente heurístico (referência)

| Agente | Vitórias/20 | Placar médio próprio | Placar médio adversário |
|---|---|---|---|
| Heurístico | (ver avaliar_heuristico.py) | ~24-42 (varia com hiperparâmetros) | ~1.5-3.5 |
| Genético | 0 | 0.05 | 2.15 |

O contraste é didático para o vídeo: o heurístico teve sucesso porque a
função objetivo (heurística de distância + regras de ataque) foi
desenhada diretamente a partir do conhecimento do domínio, enquanto o
genético teve que *descobrir* uma boa estratégia a partir de um sinal
de fitness esparso e arriscado -- e não teve gerações/população
suficientes para escapar do ótimo local passivo.
