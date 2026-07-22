"""
Faz os três agentes lutarem entre si -- cada um contra si mesmo e contra
os outros dois (round-robin completo, 6 confrontos únicos) -- em vez de
cada um só contra o agente aleatório.

Para cada par, roda metade das partidas com A como first_0/B como
second_0 e a outra metade invertida, para cancelar qualquer vantagem
posicional do ambiente.

Uso:
    python experimentos/lutar_agentes.py
"""

import json
import sys
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico
from src.genetico.agente_genetico import AgenteGenetico
from src.rl.agente_rl import AgenteRL

N_EPISODIOS_POR_CONFRONTO = 20  # total; metade em cada posição
MAX_PASSOS_POR_EPISODIO = 6000
SEED_INICIAL = 500


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
    "Heuristico": criar_heuristico,
    "Genetico": criar_genetico,
    "RL": criar_rl,
}


def escolher_acao(agente, obs):
    if isinstance(agente, AgenteRL):
        return agente.escolher_acao(obs, treinando=False)
    return agente.escolher_acao(obs)


def rodar_confronto(fabrica_a, fabrica_b, seed, max_passos=MAX_PASSOS_POR_EPISODIO):
    """A joga como first_0, B como second_0. Retorna (placar_a, placar_b)."""
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    agente_a = fabrica_a("first_0")
    agente_b = fabrica_b("second_0")
    placar = {"first_0": 0, "second_0": 0}
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        placar[agent] += reward

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = escolher_acao(agente_a, obs)
        else:
            action = escolher_acao(agente_b, obs)

        env.step(action)
        passo += 1
        if passo >= max_passos:
            break

    env.close()
    return placar["first_0"], placar["second_0"]


def avaliar_confronto(nome_a, nome_b, n_episodios=N_EPISODIOS_POR_CONFRONTO):
    fabrica_a = FABRICAS[nome_a]
    fabrica_b = FABRICAS[nome_b]

    vitorias_a, vitorias_b, empates = 0, 0, 0
    diferencas_a = []
    metade = n_episodios // 2

    print(f"\n{nome_a} vs {nome_b} ({n_episodios} partidas, posicoes alternadas)...")

    for i in range(metade):
        seed = SEED_INICIAL + i
        p_a, p_b = rodar_confronto(fabrica_a, fabrica_b, seed)
        diferencas_a.append(p_a - p_b)
        if p_a > p_b:
            vitorias_a += 1
        elif p_b > p_a:
            vitorias_b += 1
        else:
            empates += 1

    for i in range(metade):
        seed = SEED_INICIAL + 1000 + i
        p_b, p_a = rodar_confronto(fabrica_b, fabrica_a, seed)  # B como first_0 desta vez
        diferencas_a.append(p_a - p_b)
        if p_a > p_b:
            vitorias_a += 1
        elif p_b > p_a:
            vitorias_b += 1
        else:
            empates += 1

    media_diferenca_a = float(np.mean(diferencas_a))
    resultado = {
        "confronto": f"{nome_a} vs {nome_b}",
        "vitorias_a": vitorias_a,
        "vitorias_b": vitorias_b,
        "empates": empates,
        "media_diferenca_placar_a": media_diferenca_a,
    }
    print(f"  {nome_a}: {vitorias_a} vitorias | {nome_b}: {vitorias_b} vitorias | "
          f"Empates: {empates} | Diferenca media ({nome_a} - {nome_b}): {media_diferenca_a:+.2f}")
    return resultado


def main():
    nomes = list(FABRICAS.keys())
    # combinations_with_replacement inclui os confrontos de cada agente
    # contra si mesmo (ex: Heuristico vs Heuristico) e contra os outros
    # dois -- round-robin completo com 6 confrontos únicos no total.
    pares = list(combinations_with_replacement(nomes, 2))

    resultados = []
    for nome_a, nome_b in pares:
        r = avaliar_confronto(nome_a, nome_b)
        resultados.append(r)

    print("\n" + "=" * 78)
    print("RESUMO -- confrontos diretos entre agentes (incluindo cada um contra si mesmo)")
    print("=" * 78)
    print(f"{'Confronto':<28}{'V(A)':>8}{'V(B)':>8}{'Empates':>10}{'Dif. media (A-B)':>20}")
    print("-" * 78)
    for r in resultados:
        print(f"{r['confronto']:<28}{r['vitorias_a']:>8}{r['vitorias_b']:>8}"
              f"{r['empates']:>10}{r['media_diferenca_placar_a']:>20.2f}")
    print("=" * 78)

    Path("experimentos").mkdir(exist_ok=True)
    with open("experimentos/resultado_confrontos_diretos.json", "w") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print("\nResultado salvo em experimentos/resultado_confrontos_diretos.json")


if __name__ == "__main__":
    main()
