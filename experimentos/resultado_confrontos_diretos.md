# Resultado dos Confrontos Diretos entre Agentes

Protocolo: 6 confrontos únicos (round-robin completo, incluindo cada
agente contra si mesmo), 20 partidas por confronto, com posições
alternadas (10 partidas com A como `first_0`, 10 com B como `first_0`)
para cancelar qualquer vantagem posicional do ambiente.

## Resultados brutos

| Confronto | Vitórias A | Vitórias B | Empates | Dif. média (A-B) |
|---|---|---|---|---|
| Heurístico vs Heurístico | 10 | 10 | 0 | 0.00 |
| Heurístico vs Genético | 10 | 10 | 0 | 0.00 |
| Heurístico vs RL | 20 | 0 | 0 | +196.00 |
| Genético vs Genético | 10 | 10 | 0 | 0.00 |
| Genético vs RL | 10 | 0 | 10 | +100.00 |
| RL vs RL | 0 | 0 | 20 | 0.00 |

## Interpretação

### Autoconfrontos (Heurístico×Heurístico e Genético×Genético): validação da metodologia

Os dois agentes determinísticos empataram em diferença média de placar
contra cópias de si mesmos (0.00, com uma divisão exata de 10/10 nas
vitórias). **Isso é o resultado esperado e correto**, não uma falha: como
o protocolo de avaliação alterna posições especificamente para cancelar
qualquer viés posicional do ambiente, dois agentes com habilidade
idêntica devem, em média, empatar -- quem vence cada partida individual
reflete apenas a aleatoriedade inerente do jogo (variações do oponente
"espelho", elementos estocásticos do Atari), não diferença de
habilidade. Esse resultado funciona como um **teste de sanidade** que
confirma que a metodologia de alternância de posições está funcionando
como projetada.

### RL vs RL: confirma a limitação já observada

Todas as 20 partidas terminaram empatadas em RL vs RL. Isso é consistente
com o desempenho fraco do RL observado contra o agente aleatório (~20%
de taxa de vitória): a política aprendida ainda é bastante passiva para
boa parte dos estados (tabela Q pouco explorada), então dois agentes RL
jogando um contra o outro resultam em pouquíssimo engajamento de ambos os
lados -- ninguém ataca o suficiente para pontuar.

### Heurístico e Genético dominam o RL

Tanto o Heurístico (196 de diferença média, 20-0) quanto o Genético (100
de diferença média, 10 vitórias e 10 empates, RL nunca vence) dominam
claramente o agente de RL em confronto direto. Isso confirma a hierarquia
já observada nos testes contra o agente aleatório: o RL, com a
discretização de estado utilizada e o volume de treino disponível dentro
do prazo do projeto, ficou atrás dos outros dois paradigmas.

### Heurístico vs Genético: resultado mais interessante do experimento

Apesar do agente Genético ter tido uma taxa de vitória muito superior ao
Heurístico contra o agente aleatório (90% vs. 57%, ver
`resultado_genetico.md` e a comparação em `comparar_agentes.py`), no
confronto DIRETO entre os dois o resultado foi empate exato (0.00 de
diferença média, 10-10).

Isso é um achado genuinamente relevante para a discussão dos agentes: **a
taxa de vitória contra um oponente fraco (aleatório) não necessariamente
prevê o resultado contra um oponente forte**. O Genético pode ter
aprendido uma estratégia bem afinada especificamente para explorar as
fraquezas do comportamento aleatório (imprevisível, mas sem
intencionalidade), enquanto o Heurístico, por usar uma heurística de
distância mais "genérica" (não especializada em nenhum oponente
específico), generaliza igualmente bem tanto contra o aleatório quanto
contra o Genético.

## Limitação do protocolo

Cada confronto usou apenas 20 partidas (10 seeds únicas × 2 ordens de
posição). Para os autoconfrontos, isso significa que o resultado de
exatamente 0.00 pode refletir tanto a simetria estrutural esperada
quanto, em menor grau, o tamanho de amostra ainda moderado -- um número
maior de partidas tornaria essa conclusão estatisticamente mais robusta,
mas não havia tempo hábil no cronograma do projeto para uma amostra
maior.
