"""
Treinamento do AgenteRL (Q-learning tabular) no ambiente Boxing.

Detalhe importante sobre o ambiente AEC (turn-based) da PettingZoo:
env.last() retorna, a cada turno de um agente, a recompensa ACUMULADA
desde a ÚLTIMA VEZ que esse MESMO agente agiu -- não a recompensa do
passo anterior de qualquer agente. Por isso o aprendizado (chamada de
`agente.aprender(...)`) acontece sempre que é a vez do first_0 jogar de
novo, usando a recompensa relativa à sua última ação.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.rl.agente_rl import AgenteRL
from src.ambiente.extrair_estado import extrair_estado

N_EPISODIOS = 500
MAX_PASSOS_POR_EPISODIO = 3000
SALVAR_A_CADA = 50


def rodar_episodio_treino(agente, seed):
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    tem_transicao_pendente = False
    placar_p1, placar_p2 = 0, 0
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        terminou = termination or truncation

        if not terminou:
            estado = extrair_estado(obs)
            placar_p1, placar_p2 = estado["placar_p1"], estado["placar_p2"]

        if agent == "first_0":
            # `reward` aqui é a recompensa acumulada desde a última ação
            # do first_0 -- exatamente o que precisamos para atualizar a
            # transição (estado anterior, ação anterior) -> este estado.
            if tem_transicao_pendente:
                agente.aprender(reward, obs, terminou)

            if terminou:
                action = None
                tem_transicao_pendente = False
            else:
                action = agente.escolher_acao(obs, treinando=True)
                tem_transicao_pendente = True
        else:
            action = None if terminou else env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= MAX_PASSOS_POR_EPISODIO:
            break

    env.close()
    return placar_p1 - placar_p2


def treinar():
    agente = AgenteRL(jogador="first_0")
    historico_diferenca = []
    historico_epsilon = []

    for episodio in range(N_EPISODIOS):
        seed = 3000 + episodio
        diferenca = rodar_episodio_treino(agente, seed)
        agente.decair_epsilon()

        historico_diferenca.append(diferenca)
        historico_epsilon.append(agente.epsilon)

        if episodio % 10 == 0:
            media_recente = sum(historico_diferenca[-20:]) / len(historico_diferenca[-20:])
            print(f"episodio {episodio:4d} | diferenca={diferenca:+4d} | "
                  f"media_ultimos_20={media_recente:+.2f} | epsilon={agente.epsilon:.3f} | "
                  f"estados_conhecidos={len(agente.q_table)}")

        if episodio % SALVAR_A_CADA == 0 and episodio > 0:
            agente.salvar("src/rl/q_table.pkl")

    agente.salvar("src/rl/q_table.pkl")
    with open("experimentos/historico_treino_rl.json", "w") as f:
        json.dump({
            "diferenca_placar": historico_diferenca,
            "epsilon": historico_epsilon,
        }, f, indent=2)

    print("\nTreinamento concluído.")
    print(f"Tabela Q salva em src/rl/q_table.pkl ({len(agente.q_table)} estados conhecidos)")
    print("Histórico salvo em experimentos/historico_treino_rl.json")


if __name__ == "__main__":
    treinar()
