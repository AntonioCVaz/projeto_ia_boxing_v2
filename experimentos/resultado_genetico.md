# Resultado final -- Agente Genético

## Histórico: da estratégia degenerada ao sucesso com currículo

**Primeira rodada de treino (sem currículo):** o agente convergiu para
uma estratégia completamente passiva -- nunca se aproximava do
oponente, resultando em 0 vitórias em 20 partidas contra o agente
aleatório (placar médio 0.05 vs. 2.15). Diagnóstico: reward hacking --
o risco de se aproximar de um oponente aleatório era alto demais para um
indivíduo recém-nascido (pesos aleatórios) aprender por tentativa e
erro, então "nunca se aproximar" era a estratégia de menor risco
disponível para a seleção evolutiva.

**Correção -- currículo de treinamento:** nas primeiras metade das
gerações (0 a 11 de 25), o oponente durante o treino ficou PARADO (ação
NOOP constante), removendo o risco de aproximação e permitindo que a
população aprendesse a se aproximar e atacar sem ser punida por isso. Só
a partir da geração 12 o oponente voltou a ser aleatório, testando se a
estratégia aprendida generalizava. Também foi adicionada uma média de 2
seeds por avaliação de fitness, para reduzir o ruído que mascarava o
progresso real entre gerações.

**Resultado:** a mudança de comportamento foi visível já na transição do
currículo -- o fitness de validação (contra seeds fixas) saltou de
valores próximos a zero para +17 a +28 nas gerações finais do currículo,
e se manteve competitivo (positivo na maior parte das gerações seguintes)
mesmo depois de trocar para o oponente aleatório.

## Resultado final -- Agente Genético vs. Agente Aleatório

Protocolo: 30 execuções (via `comparar_agentes.py`, mesmo protocolo
usado para os três agentes).

| Métrica | Valor |
|---|---|
| Vitórias | 27 |
| Empates | 3 |
| Derrotas | 0 |
| Taxa de vitória | 90% |
| Diferença média de placar | +67.93 |

## Comparação final entre os três agentes (vs. agente aleatório, 30 execuções)

| Agente | Dif. média de placar | V/D/E | Taxa de vitória |
|---|---|---|---|
| Heurístico | +103.20 | 17/11/2 | 57% |
| **Genético** | **+67.93** | **27/3/0** | **90%** |
| RL (Q-learning) | -3.93 | 6/23/1 | 20% |

## Interpretação final

O agente genético, após a correção metodológica do currículo, teve a
MAIOR taxa de vitória entre os três agentes (90%), embora com uma
diferença média de placar menor que a do Heurístico -- ou seja, o
Genético vence mais partidas, mas por margens menores; o Heurístico
perde mais partidas, mas quando vence, vence com folga bem maior
(placar mais alto).

Esse contraste ilustra que os dois agentes convergiram para estilos de
jogo diferentes: o Genético parece ter aprendido uma estratégia mais
"segura e consistente" (vence quase sempre, mas sem dominar
completamente), enquanto o Heurístico joga de forma mais "tudo ou nada"
(quando funciona, domina com nocaute; quando não funciona -- ver
limitação bimodal documentada em `src/ambiente/mapeamento_ram.md` --
perde feio).

**Ver também:** `resultado_confrontos_diretos.md` para o resultado do
confronto DIRETO entre Heurístico e Genético (empate, apesar da
diferença nas taxas de vitória contra o aleatório) -- um achado que
reforça que essas duas métricas capturam aspectos diferentes do
desempenho.

## Nota sobre a jornada de depuração

Ver a nota completa de desenvolvimento em `src/genetico/agente_genetico.py`,
que documenta o diagnóstico do reward hacking e a correção por currículo
em detalhe -- mantida como registro histórico do processo de depuração,
conforme pedido pelo edital (itens 5 e 9 do conteúdo obrigatório do
vídeo).
