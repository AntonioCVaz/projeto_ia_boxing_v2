# Estudo Dirigido — Inteligência Artificial 2026.1

**Disciplina:** Bacharelado em Ciência da Computação — UFAPE
**Professor:** Luis Filipe
**Dupla:** NOME_1, NOME_2

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

| Agente | Paradigma | Status |
|---|---|---|
| `src/heuristica/` | Busca heurística (estado, objetivo, heurística) | 🚧 em desenvolvimento |
| `src/genetico/` | Algoritmo genético | 🚧 em desenvolvimento |
| `src/rl/` | Aprendizado por reforço | 🚧 em desenvolvimento |

## Estrutura do repositório

```
projeto-ia/
├── README.md
├── requirements.txt
├── src/
│   ├── ambiente/       # wrapper/configuração do ambiente PettingZoo
│   ├── heuristica/      # agente de busca heurística
│   ├── genetico/        # agente de algoritmo genético
│   └── rl/              # agente de aprendizado por reforço
├── experimentos/        # scripts de avaliação e comparação entre agentes
└── videos/              # link/registro do vídeo de apresentação
```

## Instalação

Requer Python 3.10 ou 3.11 (recomendado por compatibilidade com PettingZoo/ALE).

```bash
# 1. Clonar o repositório
git clone <URL_DO_REPOSITORIO>
cd projeto-ia

# 2. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar as ROMs do Atari (necessário para o pacote atari da PettingZoo)
AutoROM --accept-license
```

## Execução

> Instruções serão detalhadas conforme cada agente for implementado.

```bash
# Testar se o ambiente está configurado corretamente
python src/ambiente/testar_ambiente.py

# Executar o agente heurístico
python src/heuristica/main.py

# Executar o agente genético (treino)
python src/genetico/treinar.py

# Executar o agente de RL (treino)
python src/rl/treinar.py

# Rodar comparação entre os agentes
python experimentos/comparar_agentes.py
```

## Uso de IA generativa

Ferramentas de IA generativa foram utilizadas como apoio na estruturação do
planejamento, organização do repositório e revisão de código. Todo o código
final foi/será compreendido, testado e validado pelos dois integrantes da
dupla, conforme exigido pelo edital.

## Andamento do desenvolvimento

As principais etapas de desenvolvimento estão registradas no ambiente
virtual da disciplina, conforme cronograma do estudo dirigido. Resumo:

- [x] 17/07/2026 — Definição do contexto, ambiente e planejamento da arquitetura
- [ ] Mapeamento das posições relevantes do vetor de RAM do ambiente
- [ ] Implementação do agente heurístico
- [ ] Implementação do agente genético
- [ ] Implementação do agente de RL
- [ ] Execução de experimentos comparativos
- [ ] Gravação do vídeo de apresentação
- [ ] 24/07/2026 — Entrega final

## Licença

Trabalho acadêmico desenvolvido para a disciplina de Inteligência Artificial (UFAPE).
