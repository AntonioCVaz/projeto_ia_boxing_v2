"""
Renderiza AO VIVO um confronto entre dois agentes específicos -- qualquer
combinação entre Heurístico, Genético e RL, incluindo um agente contra
si mesmo. Útil para gravar o vídeo mostrando os agentes lutando entre si
(não apenas contra o agente aleatório).

Para trocar quem luta contra quem, edite as duas linhas indicadas em
`if __name__ == "__main__":`, no final do arquivo.

Uso:
    python experimentos/renderizar_confronto.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico
from src.genetico.agente_genetico import AgenteGenetico
from src.rl.agente_rl import AgenteRL
from src.ambiente.extrair_estado import extrair_estado


def criar_heuristico(jogador):
    return AgenteHeuristico(jogador=jogador)


def criar_genetico(jogador):
    pesos = np.load("experimentos/melhor_individuo_genetico.npy")
    return AgenteGenetico(pesos, jogador=jogador)


def criar_rl(jogador):
    agente = AgenteRL(jogador=jogador)
    agente.carregar("src/rl/q_table.pkl")
    return agente


FABRICAS = {
    "heuristico": criar_heuristico,
    "genetico": criar_genetico,
    "rl": criar_rl,
}


def escolher_acao(agente, obs):
    if isinstance(agente, AgenteRL):
        return agente.escolher_acao(obs, treinando=False)
    return agente.escolher_acao(obs)


def renderizar_confronto(nome_a, nome_b, seed=42, max_passos=6000, render=True):
    """nome_a joga como first_0, nome_b como second_0.
    nome_a e nome_b devem ser uma das chaves de FABRICAS:
    'heuristico', 'genetico' ou 'rl' (pode repetir o mesmo nos dois lados)."""
    agente_a = FABRICAS[nome_a]("first_0")
    agente_b = FABRICAS[nome_b]("second_0")

    env = boxing_v2.env(obs_type="ram", render_mode="human" if render else None)
    env.reset(seed=seed)

    passo = 0
    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = escolher_acao(agente_a, obs)
        else:
            action = escolher_acao(agente_b, obs)

        env.step(action)
        passo += 1
        if passo % 500 == 0:
            estado = extrair_estado(obs)
            print(f"passo={passo} | {nome_a}={estado['placar_p1']} "
                  f"x {estado['placar_p2']}={nome_b} | relogio={estado['relogio']}")
        if passo >= max_passos:
            break

    env.close()


if __name__ == "__main__":
    # <<< TROQUE AQUI para escolher quem luta contra quem >>>
    # Opções válidas: "heuristico", "genetico", "rl"
    # (pode repetir o mesmo nos dois lados, ex: "heuristico" vs "heuristico")
    NOME_A = "heuristico"
    NOME_B = "genetico"

    renderizar_confronto(NOME_A, NOME_B, render=True)
