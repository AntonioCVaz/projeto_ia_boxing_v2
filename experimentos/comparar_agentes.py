"""
Roda N episódios de cada agente (heurístico, genético, RL) contra um
oponente de ação aleatória, e compara o desempenho entre os três.

Uso:
    python experimentos/comparar_agentes.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico
from src.rl.agente_rl import AgenteRL

try:
    from src.genetico.agente_genetico import AgenteGenetico
    GENETICO_DISPONIVEL = Path("experimentos/melhor_individuo_genetico.npy").exists()
except ImportError:
    GENETICO_DISPONIVEL = False


N_EPISODIOS = 30
MAX_PASSOS_POR_EPISODIO = 6000
SEED_INICIAL = 100


def rodar_episodio(fabrica_agente, seed, max_passos=MAX_PASSOS_POR_EPISODIO):
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    agente = fabrica_agente()
    placar_final = {"first_0": 0, "second_0": 0}
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        placar_final[agent] += reward

        if termination or truncation:
            action = None
        elif agent == "first_0":
            if isinstance(agente, AgenteRL):
                action = agente.escolher_acao(obs, treinando=False)
            else:
                action = agente.escolher_acao(obs)
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= max_passos:
            break

    env.close()
    return placar_final["first_0"], placar_final["second_0"]


def avaliar_agente(nome, fabrica_agente, n_episodios=N_EPISODIOS):
    diferencas = []
    vitorias = 0
    derrotas = 0
    empates = 0

    print(f"\nAvaliando agente: {nome} ({n_episodios} episódios)...")
    for i in range(n_episodios):
        seed = SEED_INICIAL + i
        placar_p1, placar_p2 = rodar_episodio(fabrica_agente, seed)
        diferenca = placar_p1 - placar_p2
        diferencas.append(diferenca)

        if diferenca > 0:
            vitorias += 1
        elif diferenca < 0:
            derrotas += 1
        else:
            empates += 1

    media_diferenca = sum(diferencas) / len(diferencas)
    taxa_vitoria = vitorias / n_episodios

    return {
        "agente": nome,
        "media_diferenca_placar": media_diferenca,
        "vitorias": vitorias,
        "derrotas": derrotas,
        "empates": empates,
        "taxa_vitoria": taxa_vitoria,
    }


def imprimir_tabela_resultados(resultados):
    print("\n" + "=" * 72)
    print(f"{'Agente':<15}{'Dif. média placar':>20}{'V/D/E':>15}{'Taxa de vitória':>20}")
    print("-" * 72)
    for r in resultados:
        vde = f"{r['vitorias']}/{r['derrotas']}/{r['empates']}"
        print(f"{r['agente']:<15}{r['media_diferenca_placar']:>20.2f}"
              f"{vde:>15}{r['taxa_vitoria']:>19.0%}")
    print("=" * 72)


def main():
    resultados = []

    resultados.append(
        avaliar_agente("Heurístico", lambda: AgenteHeuristico(jogador="first_0"))
    )

    if GENETICO_DISPONIVEL:
        pesos_geneticos = np.load("experimentos/melhor_individuo_genetico.npy")
        resultados.append(
            avaliar_agente("Genético", lambda: AgenteGenetico(pesos_geneticos, jogador="first_0"))
        )
    else:
        print("\n[aviso] Pesos do agente genético não encontrados em "
              "experimentos/melhor_individuo_genetico.npy — pulando da comparação.")

    def criar_agente_rl():
        agente = AgenteRL(jogador="first_0")
        agente.carregar("src/rl/q_table.pkl")
        return agente

    resultados.append(avaliar_agente("RL (Q-learning)", criar_agente_rl))

    imprimir_tabela_resultados(resultados)


if __name__ == "__main__":
    main()
