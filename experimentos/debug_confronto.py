"""
Diagnóstico de um confronto entre dois agentes: registra a cada passo a
distância entre eles, a ação escolhida por cada um, e o placar --
para descobrir por que um agente pode não estar pontuando contra o
outro mesmo "colado" nele.
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico, ACOES
from src.genetico.agente_genetico import AgenteGenetico
from src.rl.agente_rl import AgenteRL
from src.ambiente.extrair_estado import extrair_estado

NOME_ACAO = {v: k for k, v in ACOES.items()}


def criar_heuristico(jogador):
    return AgenteHeuristico(jogador=jogador)


def criar_genetico(jogador):
    pesos = np.load("experimentos/melhor_individuo_genetico.npy")
    return AgenteGenetico(pesos, jogador=jogador)


def criar_rl(jogador):
    agente = AgenteRL(jogador=jogador)
    agente.carregar("src/rl/q_table.pkl")
    return agente


FABRICAS = {"heuristico": criar_heuristico, "genetico": criar_genetico, "rl": criar_rl}


def escolher_acao(agente, obs):
    if isinstance(agente, AgenteRL):
        return agente.escolher_acao(obs, treinando=False)
    return agente.escolher_acao(obs)


def diagnosticar(nome_a="heuristico", nome_b="genetico", seed=42, max_passos=3000):
    agente_a = FABRICAS[nome_a]("first_0")
    agente_b = FABRICAS[nome_b]("second_0")

    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    contagem_a = Counter()
    contagem_b = Counter()
    distancias = []
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = escolher_acao(agente_a, obs)
            contagem_a[NOME_ACAO.get(action, str(action))] += 1
        else:
            action = escolher_acao(agente_b, obs)
            contagem_b[NOME_ACAO.get(action, str(action))] += 1

        env.step(action)

        if agent == "first_0":
            estado = extrair_estado(obs)
            dx = estado["p2_x"] - estado["p1_x"]
            dy = estado["p2_y"] - estado["p1_y"]
            dist = (dx ** 2 + dy ** 2) ** 0.5
            distancias.append(dist)
            if passo % 200 == 0:
                print(f"passo={passo:5d} dist={dist:6.1f} dx={dx:4d} dy={dy:4d} "
                      f"placar={estado['placar_p1']}x{estado['placar_p2']}")

        passo += 1
        if passo >= max_passos:
            break

    env.close()

    print(f"\n=== Resumo: {nome_a} (first_0) vs {nome_b} (second_0) ===")
    print(f"Distância mínima: {min(distancias):.1f} | média: {sum(distancias)/len(distancias):.1f}")
    print(f"\nAções de {nome_a}:")
    for acao, n in contagem_a.most_common():
        print(f"  {acao:16s}: {n:5d} ({100*n/sum(contagem_a.values()):.1f}%)")
    print(f"\nAções de {nome_b}:")
    for acao, n in contagem_b.most_common():
        print(f"  {acao:16s}: {n:5d} ({100*n/sum(contagem_b.values()):.1f}%)")


if __name__ == "__main__":
    diagnosticar(nome_a="heuristico", nome_b="genetico")
