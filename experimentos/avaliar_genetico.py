"""
Avalia o melhor indivíduo genético treinado (salvo em
experimentos/melhor_individuo_genetico.npy) contra o agente aleatório,
usando o mesmo protocolo do agente heurístico (para comparação justa).
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.genetico.agente_genetico import AgenteGenetico
from src.ambiente.extrair_estado import extrair_estado


def rodar_uma_partida(pesos, seed, max_passos=6000):
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)
    agente = AgenteGenetico(pesos, jogador="first_0")
    agente.reset()

    placar_final = {"placar_p1": 0, "placar_p2": 0}
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if not (termination or truncation):
            estado = extrair_estado(obs)
            placar_final["placar_p1"] = estado["placar_p1"]
            placar_final["placar_p2"] = estado["placar_p2"]

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs)
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= max_passos or termination or truncation:
            break

    env.close()
    return placar_final


def avaliar(n_execucoes=20):
    pesos = np.load("experimentos/melhor_individuo_genetico.npy")

    resultados = []
    for i in range(n_execucoes):
        placar = rodar_uma_partida(pesos, seed=1000 + i)
        resultados.append(placar)
        print(f"execucao {i+1}/{n_execucoes}: "
              f"genetico={placar['placar_p1']} x aleatorio={placar['placar_p2']}")

    vitorias = sum(1 for r in resultados if r["placar_p1"] > r["placar_p2"])
    empates = sum(1 for r in resultados if r["placar_p1"] == r["placar_p2"])
    derrotas = sum(1 for r in resultados if r["placar_p1"] < r["placar_p2"])
    media_p1 = sum(r["placar_p1"] for r in resultados) / n_execucoes
    media_p2 = sum(r["placar_p2"] for r in resultados) / n_execucoes

    print("\n=== Resumo (Genético vs. Aleatório) ===")
    print(f"Execuções: {n_execucoes}")
    print(f"Vitórias: {vitorias} | Empates: {empates} | Derrotas: {derrotas}")
    print(f"Placar médio -- genético: {media_p1:.2f} | aleatório: {media_p2:.2f}")


if __name__ == "__main__":
    avaliar(n_execucoes=20)
