"""
Diagnóstico do AgenteHeuristico: registra a distância até o oponente e a
ação escolhida a cada passo, para descobrir por que o agente não está
conseguindo pontuar.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico, heuristica_distancia, ACOES
from src.ambiente.extrair_estado import extrair_estado

NOME_ACAO = {v: k for k, v in ACOES.items()}


def diagnosticar(max_passos=1500, seed=42):
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)
    agente = AgenteHeuristico(jogador="first_0")

    distancias = []
    contagem_acoes = Counter()
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs)
            estado = extrair_estado(obs)
            d = heuristica_distancia(estado["p1_x"], estado["p1_y"],
                                      estado["p2_x"], estado["p2_y"])
            distancias.append(d)
            contagem_acoes[NOME_ACAO[action]] += 1

            if passo % 200 == 0:
                print(f"passo={passo:5d} dist={d:6.1f} "
                      f"acao={NOME_ACAO[action]:14s} "
                      f"p1=({estado['p1_x']},{estado['p1_y']}) "
                      f"p2=({estado['p2_x']},{estado['p2_y']}) "
                      f"placar={estado['placar_p1']}x{estado['placar_p2']}")
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= max_passos:
            break

    env.close()

    print("\n=== Resumo do diagnóstico ===")
    print(f"Distância inicial: {distancias[0]:.1f}")
    print(f"Distância mínima atingida: {min(distancias):.1f}")
    print(f"Distância média: {sum(distancias)/len(distancias):.1f}")
    print(f"Distância final: {distancias[-1]:.1f}")
    print(f"\nDistribuição de ações escolhidas:")
    for acao, contagem in contagem_acoes.most_common():
        print(f"  {acao:14s}: {contagem:5d} ({100*contagem/sum(contagem_acoes.values()):.1f}%)")


if __name__ == "__main__":
    diagnosticar()
