# Estudo Dirigido — Inteligência Artificial 2026.1

**Disciplina:** Bacharelado em Ciência da Computação — UFAPE
**Professor:** Luis Filipe
**Dupla:** Antônio Carlos da Silva Batista Vaz, Paulo Eduardo Vieira Souza

## Objetivo

Implementar, analisar e comparar três paradigmas de agentes inteligentes
(busca heurística, algoritmo genético e aprendizado por reforço) competindo
em um ambiente multiagente da biblioteca [PettingZoo](https://pettingzoo.farama.org/).

## Contexto escolhido

**Contexto II — Ambiente multiagente.**
Ambiente: `boxing_v2` (família Atari da PettingZoo).
Observação: **exclusivamente RAM** (`obs_type="ram"`), vetor de 128 bytes
(valores inteiros de 0 a 255), conforme restrição do edital.

## Agentes implementados

| Agente | Paradigma | Status | Taxa de vitória vs. aleatório |
|---|---|---|---|
| `src/heuristica/` | Busca heurística (estado, objetivo, heurística de distância) | ✅ concluído | 57% |
| `src/genetico/` | Algoritmo genético (com currículo de treinamento) | ✅ concluído | 90% |
| `src/rl/` | Aprendizado por reforço (Q-learning tabular) | ✅ concluído | 20% |

Resultados completos, incluindo confrontos diretos entre os agentes
(inclusive cada um contra si mesmo), em `experimentos/resultado_genetico.md`
e `experimentos/resultado_confrontos_diretos.md`.

## Estrutura do repositório

```
projeto-ia/
├── README.md
├── requirements.txt
├── src/
│   ├── ambiente/
│   │   ├── testar_ambiente.py       # valida a instalação do ambiente
│   │   ├── mapear_ram.py            # exploração inicial da RAM
│   │   ├── extrair_estado.py        # mapeamento final validado (usado por todos os agentes)
│   │   └── mapeamento_ram.md        # documentação completa do mapeamento
│   ├── heuristica/
│   │   ├── agente_heuristico.py
│   │   └── main.py                  # roda 1 episódio vs. aleatório
│   ├── genetico/
│   │   ├── agente_genetico.py
│   │   └── main.py                  # roda 1 episódio vs. aleatório
│   └── rl/
│       ├── agente_rl.py
│       ├── main.py                  # roda 1 episódio vs. aleatório
│       └── q_table.pkl              # gerado ao treinar
├── experimentos/
│   ├── debug_heuristico.py          # diagnóstico do agente heurístico
│   ├── avaliar_heuristico.py        # avaliação vs. aleatório (20 execuções)
│   ├── treinar_genetico.py          # treino do agente genético (com currículo)
│   ├── avaliar_genetico.py          # avaliação vs. aleatório
│   ├── treinar_rl.py                # treino do agente de RL
│   ├── comparar_agentes.py          # compara os 3 agentes vs. aleatório
│   ├── lutar_agentes.py             # os 3 agentes lutando entre si (+ self-play)
│   ├── renderizar_confronto.py      # renderiza um confronto específico
│   ├── resultado_genetico.md        # resultado final do genético + comparação
│   └── resultado_confrontos_diretos.md  # análise dos confrontos diretos
└── videos/
    └── roteiro_apresentacao.md      # roteiro completo do vídeo (25 min, 2 pessoas)
```

## Instalação

Requer Python 3.10 ou 3.11 (recomendado por compatibilidade com PettingZoo/ALE).

```bash
# 1. Clonar o repositório
git clone https://github.com/AntonioCVaz/projeto_ia_boxing_v2/tree/main
cd projeto-ia

# 2. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar as ROMs do Atari (necessário para o pacote atari da PettingZoo)
AutoROM --accept-license
```

## Execução

### 1. Validar o ambiente e o mapeamento de RAM

```bash
# Confirma que o ambiente PettingZoo está configurado corretamente
python src/ambiente/testar_ambiente.py

# Exploração inicial da RAM (identifica quais bytes variam)
python src/ambiente/mapear_ram.py

# Valida o mapeamento final do placar, correlacionando com o reward do ambiente
python -c "from src.ambiente.extrair_estado import validar_placar; validar_placar()"
```

Documentação completa do mapeamento (metodologia, tabela final de bytes,
jornada de depuração) em `src/ambiente/mapeamento_ram.md`.

### 2. Treinar os agentes

```bash
# Agente genético (currículo: primeiras gerações vs. oponente parado,
# depois vs. aleatório) -- gera experimentos/melhor_individuo_genetico.npy
python experimentos/treinar_genetico.py

# Agente de RL (Q-learning tabular) -- gera src/rl/q_table.pkl
python experimentos/treinar_rl.py
```

O agente heurístico não precisa de treino (é baseado em regras).

### 3. Rodar um agente contra o aleatório (com tela)

```bash
# Heurístico
python -c "from src.heuristica.main import rodar_episodio; rodar_episodio(render=True)"

# Genético
python -c "from src.genetico.main import rodar_episodio; rodar_episodio(render=True)"

# RL
python -c "from src.rl.main import rodar_episodio; rodar_episodio(render=True)"
```

Parâmetros opcionais: `seed=<int>` (fixar uma partida específica) e
`max_passos=<int>` (partidas mais curtas, ex. `max_passos=2000`).

### 4. Avaliar cada agente contra o aleatório (sem tela, várias execuções)

```bash
python experimentos/avaliar_heuristico.py     # 20 execuções
python experimentos/avaliar_genetico.py       # 20 execuções
python experimentos/comparar_agentes.py       # os 3 juntos, 30 execuções cada
```

### 5. Rodar os agentes contra si mesmo e uns contra os outros

```bash
# Round-robin completo: cada agente x si mesmo + x os outros 2 (6 confrontos, sem tela)
python experimentos/lutar_agentes.py
```

Resultado salvo em `experimentos/resultado_confrontos_diretos.json`,
interpretação completa em `experimentos/resultado_confrontos_diretos.md`.

### 6. Renderizar um confronto específico entre dois agentes

Para gravar o vídeo mostrando dois agentes lutando entre si (por
exemplo, Heurístico vs. Genético):

```bash
python experimentos/renderizar_confronto.py
```

Por padrão roda Heurístico vs. Genético. Para trocar o confronto (ex.
Genético vs. RL, ou um agente contra si mesmo), edite as duas linhas
`NOME_A` e `NOME_B` no final do arquivo
`experimentos/renderizar_confronto.py` -- as opções válidas são
`"heuristico"`, `"genetico"` e `"rl"` (pode repetir o mesmo nos dois lados).

## Uso de IA generativa

Ferramentas de IA generativa foram utilizadas como apoio na estruturação
do planejamento, organização do repositório, depuração de bugs e revisão
de código ao longo do desenvolvimento. Todo o código final foi
compreendido, testado e validado pelos dois integrantes da dupla,
conforme exigido pelo edital -- incluindo o diagnóstico e a correção de
bugs reais encontrados durante o desenvolvimento (documentados em
`src/ambiente/mapeamento_ram.md` e `experimentos/resultado_genetico.md`).

## Resultados resumidos

| Agente | Dif. média de placar (vs. aleatório) | V/D/E | Taxa de vitória |
|---|---|---|---|
| Heurístico | +103.20 | 17/11/2 | 57% |
| Genético | +67.93 | 27/3/0 | 90% |
| RL (Q-learning) | -3.93 | 6/23/1 | 20% |

Confrontos diretos entre os agentes (incluindo self-play) em
`experimentos/resultado_confrontos_diretos.md`. Destaque: apesar do
Genético ter maior taxa de vitória contra o aleatório, o confronto direto
Heurístico vs. Genético terminou empatado -- discussão completa no
documento citado.

## Andamento do desenvolvimento

- [x] Definição do contexto, ambiente e planejamento da arquitetura
- [x] Mapeamento das posições relevantes do vetor de RAM do ambiente
- [x] Implementação do agente heurístico (com depuração de 3 bugs reais)
- [x] Implementação do agente genético (com correção de reward hacking via currículo)
- [x] Implementação do agente de RL (com correção de decaimento do epsilon)
- [x] Execução de experimentos comparativos (vs. aleatório e entre os agentes)
- [x] Gravação do vídeo de apresentação (roteiro pronto em `videos/roteiro_apresentacao.md`)
- [x] Entrega final (24/07/2026)
