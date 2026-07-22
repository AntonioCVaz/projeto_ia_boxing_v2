# Roteiro de Apresentação -- Estudo Dirigido IA 2026.1

**Duração alvo: 25 minutos** (limite do edital: até 20 min -- ajustar
cortando exemplos se necessário, mas priorizar cobrir todos os itens)
**Formato:** conversa técnica entre os dois integrantes, alternando quem fala
**Convenção:** "P1" e "P2" = Integrante 1 e Integrante 2 (troquem pelos nomes reais)

Antes de gravar: tenham abertos em abas/terminais separados:
- VS Code (ou editor) com o repositório aberto
- Um terminal na raiz do projeto, com o venv ativado
- O ambiente pronto para rodar com `render=True` quando chegar a hora

Ao longo do roteiro, `[MOSTRAR: ...]` indica o que exibir na tela
naquele momento (código, terminal, ou o jogo renderizado).

---

## 0. Abertura (0:00 -- 0:30)

**P1:** "Oi, eu sou [nome], e esse é o [nome do P2]. Esse vídeo é a
apresentação do nosso estudo dirigido de Inteligência Artificial, onde
implementamos três agentes diferentes -- busca heurística, algoritmo
genético e aprendizado por reforço -- competindo no jogo Boxing do Atari."

**P2:** "A gente escolheu o Contexto II do edital, ambiente multiagente
com a biblioteca PettingZoo, usando só a memória RAM do console como
observação -- sem acesso a pixels. Isso trouxe um desafio extra que vocês
vão ver ao longo do vídeo."

---

## 1. Visão geral do ambiente e restrição técnica (0:30 -- 2:30)

*(cobre item 2 e parte do item 3 do edital)*

**P1:** [MOSTRAR: terminal rodando `python src/ambiente/testar_ambiente.py`]
"Esse é o ambiente Boxing da PettingZoo. A restrição do edital pedia
`obs_type='ram'`, ou seja, cada agente recebe, a cada passo, um vetor de
128 bytes -- a memória RAM crua do Atari, valores de 0 a 255. Não tem
posição de jogador, não tem placar pronto -- é tudo memória bruta."

**P2:** "As regras do jogo são simples: dois boxers lutam, socos que
conectam somam pontos, e o round termina por nocaute ou quando o tempo
acaba. O objetivo de cada agente é maximizar a diferença entre o próprio
placar e o do oponente."

**P1:** "O grande desafio aqui foi: como a gente descobre, dentro desses
128 bytes sem documentação nenhuma, quais posições representam a posição
dos jogadores, o placar, o tempo? Foi um trabalho de engenharia reversa."

---

## 2. Mapeamento da RAM: metodologia (2:30 -- 5:00)

*(cobre item 3 e parte do item 1 -- uso de IA generativa)*

**P2:** [MOSTRAR: `src/ambiente/mapear_ram.py`]
"A gente começou rodando o ambiente com ações aleatórias e comparando
quais dos 128 bytes mudavam de valor. Só uns 37 de 128 realmente variavam
-- o resto é memória não usada pelo jogo."

**P1:** [MOSTRAR: `src/ambiente/extrair_estado.py`]
"Depois, fizemos testes dirigidos: fixamos a ação de um jogador (por
exemplo, sempre andar pra direita) e vimos quais bytes mudavam de forma
consistente. Isso isolou os candidatos a posição X e Y de cada jogador."

**P2:** "Pro placar, a gente usou uma estratégia diferente: rodamos o jogo
até acontecer uma pontuação de verdade (reward diferente de zero) e
comparamos a RAM antes e depois desse evento."

**P1:** [MOSTRAR: `src/ambiente/mapeamento_ram.md`]
"E aqui documentamos tudo -- inclusive cruzamos nossos achados com uma
fonte acadêmica, o paper do grupo Mila-IQIA sobre representação de estado
em jogos Atari, que confirmou exatamente as posições que a gente já tinha
encontrado empiricamente: bytes 32, 33, 34 e 35 pras posições, e 18/19
pro placar."

**P2:** "Sobre uso de IA generativa: usamos para nos ajudar a estruturar
os scripts de teste e a organizar a investigação, mas cada hipótese foi
validada com dados reais do ambiente antes de aceitarmos qualquer
mapeamento -- não aceitamos nada só porque a IA sugeriu."

---

## 3. Formato técnico da conexão agente-ambiente (5:00 -- 6:30)

*(cobre item 3 do edital)*

**P1:** [MOSTRAR: `src/ambiente/extrair_estado.py`, função `extrair_estado`]
"Depois de mapeada, a gente centralizou a leitura da RAM numa única
função, `extrair_estado`, que os três agentes reutilizam. Ela devolve um
dicionário com posição X e Y dos dois jogadores, placar de cada um, e o
relógio -- sete valores extraídos dos 128 bytes brutos."

**P2:** "A ação de saída de cada agente é um inteiro de 0 a 17 -- o
espaço de ações padrão do Atari, incluindo direções, socos, e combinações
de direção com soco."

---

## 4. Agente Heurístico (6:30 -- 11:30)

*(cobre itens 4, 5, 6, 7, 9 e 10, focados neste agente)*

**P1:** [MOSTRAR: `src/heuristica/agente_heuristico.py`]
"O primeiro agente usa busca heurística. O estado é a posição relativa
entre os dois jogadores. O objetivo é maximizar a diferença de placar. E
a heurística é a distância euclidiana até o oponente -- quanto menor,
melhor, porque significa que estamos perto o suficiente pra atacar."

**P2:** "A busca em si é gulosa, de profundidade 1: a cada passo, o
agente simula o efeito de cada ação de movimento possível, calcula a
heurística resultante, e escolhe a que minimiza a distância. É repetido a
cada frame, porque o ambiente é dinâmico -- o oponente também está se
mexendo."

**P1:** "Só que a primeira versão desse agente não pontuava NUNCA. Zero
em 20 partidas seguidas contra o oponente aleatório."

**P2:** [MOSTRAR: terminal com a saída antiga de `debug_heuristico.py`,
ou reproduzir ao vivo]
"A gente instrumentou o agente pra registrar distância e ação escolhida
a cada passo, e descobriu três problemas em sequência. Primeiro: existe
uma distância física mínima entre os dois lutadores -- os sprites colidem
e não conseguem se sobrepor, então nosso limiar de 'perto o suficiente
pra atacar' estava fisicamente impossível de alcançar."

**P1:** "Segundo problema: quando corrigimos isso, o agente ficava
socando sem parar, mas nunca conectava. Descobrimos que segurar o botão
de soco todo frame impede a animação do golpe de completar -- é preciso
dar um intervalo entre um soco e outro, como se estivesse soltando o
botão."

**P2:** "E o terceiro problema foi na nossa própria avaliação: em
episódios mais longos, a gente via placares impossíveis, tipo 98 ou 120
pontos. Era porque continuávamos lendo a RAM depois do round já ter
terminado -- nesse estado, os bytes não representam mais o placar real."

**P1:** [MOSTRAR: `python src/heuristica/main.py` com `render=True`, ao
vivo ou gravação]
"Depois dessas três correções, o agente final fica colado no oponente e
vence boa parte das partidas por nocaute. Aqui está ele jogando ao vivo."

**P2:** [MOSTRAR: resultado de `avaliar_heuristico.py`]
"No protocolo de avaliação -- 20 execuções contra o agente aleatório --
o heurístico teve taxa de vitória de [PREENCHER %], com placar médio de
[PREENCHER] contra [PREENCHER] do aleatório."

---

## 5. Agente Genético (11:30 -- 17:00)

*(cobre itens 4, 5, 6, 7, 9 e 10, focados neste agente)*

**P1:** [MOSTRAR: `src/genetico/agente_genetico.py`]
"O segundo agente usa algoritmo genético. O cromossomo é uma matriz de
pesos que, multiplicada por um vetor de features do estado -- posição
relativa do oponente, distância, e tempo desde o último soco -- decide
qual ação tomar."

**P2:** "A aptidão, ou fitness, é a diferença de placar ao final de um
episódio contra o agente aleatório, mais um pequeno bônus por ficar perto
do oponente."

**P1:** [MOSTRAR: `experimentos/treinar_genetico.py`]
"A população tem 20 indivíduos, com seleção por torneio, cruzamento
uniforme, mutação gaussiana e elitismo -- o melhor indivíduo de cada
geração sempre sobrevive direto pra próxima."

**P2:** "Só que na primeira rodada de treino, a evolução convergiu pra
uma estratégia completamente passiva: o indivíduo 'campeão' aprendeu a
nunca se aproximar do oponente, porque só ficar parado já garantia
fitness zero, e tentar atacar carregava risco de apanhar muito."

**P1:** "Isso é um fenômeno conhecido em aprendizado por reforço e
algoritmos evolutivos, chamado reward hacking -- o agente está otimizando
perfeitamente a função que definimos, só que essa função permitia uma
solução de baixo risco que não é o comportamento que a gente queria."

**P2:** [MOSTRAR: gráfico ou tabela do histórico de fitness ANTES do
currículo, se tiverem plotado]
"A solução foi um currículo de treinamento: nas primeiras metade das
gerações, o oponente fica parado, sem se mover -- isso remove o risco de
aproximação e deixa a população aprender a atacar sem medo de apanhar.
Só depois disso a gente troca pro oponente aleatório de verdade, pra
testar se a estratégia aprendida generaliza."

**P1:** [MOSTRAR: saída do treino final, com a transição de
"curriculo(parado)" pra "aleatorio"]
"E funcionou: o agente foi de zero vitórias para uma taxa de [PREENCHER
%] de vitórias depois do currículo."

**P2:** [MOSTRAR: `python src/genetico/main.py` ou script equivalente com
`render=True`]
"Aqui está o agente genético final jogando ao vivo."

---

## 6. Agente de Aprendizado por Reforço (17:00 -- 21:30)

*(cobre itens 4, 5, 6, 7, 9 e 10, focados neste agente)*

**P1:** [MOSTRAR: `src/rl/agente_rl.py`]
"O terceiro agente usa Q-learning tabular. O estado é a posição relativa
até o oponente, discretizada em faixas, mais uma flag indicando se o
cooldown do soco já passou -- reaproveitamos essa mesma lógica de timing
que descobrimos no agente heurístico."

**P2:** "A ação é escolhida por uma política epsilon-greedy: com
probabilidade epsilon, o agente explora uma ação aleatória; caso
contrário, escolhe a ação de maior valor Q conhecido para aquele
estado."

**P1:** [MOSTRAR: `experimentos/treinar_rl.py`]
"No primeiro treino, com 500 episódios, o agente terminou o treinamento
com epsilon ainda em 0.78 -- ou seja, mesmo no final, ele ainda escolhia
ações aleatórias em quase 80% dos passos. O parâmetro de decaimento
estava calibrado pra um treino bem mais longo."

**P2:** "A correção foi calcular o decaimento do epsilon dinamicamente, em
função do número de episódios de treino, garantindo que ele realmente
chegasse perto do mínimo até o fim -- e aumentamos o treino pra
[PREENCHER número] episódios."

**P1:** [MOSTRAR: `python src/rl/main.py` com `render=True`]
"Aqui está o agente de RL jogando com a política já treinada, sem mais
exploração aleatória."

**P2:** [MOSTRAR: resultado da avaliação do RL]
"No protocolo de avaliação, o RL teve taxa de vitória de [PREENCHER %]
contra o agente aleatório -- [comentar se ficou atrás dos outros dois e
por quê: espaço de estados discretizado grosseiramente / poucos episódios
de treino comparado à complexidade do jogo]."

---

## 7. Comparação entre os três agentes (21:30 -- 24:00)

*(cobre item 8 do edital -- protocolo de avaliação e comparação)*

**P1:** [MOSTRAR: tabela de `comparar_agentes.py`, cada agente vs.
aleatório]
"Rodamos os três agentes contra o agente aleatório, 30 execuções cada,
mesmo protocolo pra todos. [Ler a tabela e comentar os números reais]"

**P2:** [MOSTRAR: tabela de `lutar_agentes.py`, os agentes uns contra os
outros, incluindo cada um contra si mesmo]
"E também fizemos os agentes lutarem diretamente entre si -- inclusive
cada um contra si mesmo, pra ver o comportamento em espelho. [Ler a
tabela e comentar: qual agente venceu qual confronto e por quê, ligando
com a lógica de cada paradigma explicada antes]"

**P1:** "Resumindo: o agente heurístico teve o melhor desempenho geral,
porque a heurística foi desenhada diretamente com conhecimento do
domínio. O genético, depois do currículo, chegou perto. O RL foi o mais
limitado, principalmente pela discretização grosseira do espaço de
estados e pelo tempo de treino."

---

## 8. Limitações, uso de IA e reprodutibilidade (24:00 -- 25:00)

*(cobre itens 1 e 9 do edital)*

**P2:** "Sobre limitações: o agente heurístico ainda mostra um
comportamento bimodal -- em algumas partidas domina, em outras fica
travado em zero, dependendo da trajetória inicial do oponente. O genético
tem uma representação bem simples, uma política linear, que poderia ser
trocada por uma rede neural pequena pra capturar padrões mais complexos.
E o RL precisaria de bem mais episódios de treino, ou uma discretização
mais fina do estado, pra competir de igual com os outros dois."

**P1:** "Pra reproduzir o experimento, o repositório tem um README com
instruções de instalação passo a passo, e cada agente tem seu próprio
script de treino e avaliação, documentados."

**P2:** "E sobre uso de ferramentas de IA generativa: usamos pra
acelerar a escrita de código repetitivo e pra nos ajudar a organizar a
investigação e a documentação -- mas todo o código foi testado, revisado
e cada um de nós consegue explicar e modificar qualquer parte dele, como
está pedindo aqui."

---

## Encerramento (25:00)

**P1:** "Isso encerra nossa apresentação. Valeu!"
**P2:** "Até mais!"

---

## Checklist antes de gravar

- [ ] Preencher todos os `[PREENCHER]` com os números reais das
      avaliações finais
- [ ] Testar a renderização (`render=True`) de cada agente antes de
      gravar, pra garantir que a janela abre sem erro
- [ ] Ter os arquivos de código já abertos nas abas certas, pra não
      perder tempo procurando durante a gravação
- [ ] Cronometrar um ensaio -- o roteiro foi pensado para ~25 min, mas
      cortem exemplos se passar muito do limite de 20 min do edital
- [ ] Confirmar que ambos os integrantes participam de fato das
      explicações (edital exige isso explicitamente)
