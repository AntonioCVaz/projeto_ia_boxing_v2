"""
Treinamento do agente genético via algoritmo genético simples:
seleção por torneio, cruzamento uniforme, mutação gaussiana e elitismo.

Aptidão (fitness): placar_proprio - placar_oponente ao final de um
episódio contra o agente aleatório (estratégia de referência).
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.genetico.agente_genetico import AgenteGenetico
from src.ambiente.extrair_estado import extrair_estado

TAMANHO_POPULACAO = 20
N_GERACOES = 20
TAXA_MUTACAO = 0.2
DESVIO_MUTACAO = 0.3
TAMANHO_TORNEIO = 3
MAX_PASSOS_EPISODIO = 2000

RNG = np.random.default_rng(42)


def avaliar_fitness(pesos, seed):
    """Roda um episódio completo e retorna placar_p1 - placar_p2."""
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)
    agente = AgenteGenetico(pesos, jogador="first_0")
    agente.reset()

    placar_p1, placar_p2 = 0, 0
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if not (termination or truncation):
            estado = extrair_estado(obs)
            placar_p1, placar_p2 = estado["placar_p1"], estado["placar_p2"]

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs)
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= MAX_PASSOS_EPISODIO or termination or truncation:
            break

    env.close()
    return placar_p1 - placar_p2


def selecao_torneio(populacao, fitnesses):
    indices = RNG.choice(len(populacao), size=TAMANHO_TORNEIO, replace=False)
    melhor = max(indices, key=lambda i: fitnesses[i])
    return populacao[melhor]


def cruzar(pai1, pai2):
    """Cruzamento uniforme: cada peso vem aleatoriamente de um dos pais."""
    mascara = RNG.random(pai1.shape) < 0.5
    return np.where(mascara, pai1, pai2)


def mutar(individuo):
    """Mutação gaussiana aplicada a uma fração dos pesos."""
    mascara = RNG.random(individuo.shape) < TAXA_MUTACAO
    ruido = RNG.normal(0, DESVIO_MUTACAO, size=individuo.shape)
    return individuo + mascara * ruido


def treinar():
    populacao = [AgenteGenetico.pesos_aleatorios(RNG) for _ in range(TAMANHO_POPULACAO)]
    historico_melhor = []
    historico_media = []

    for geracao in range(N_GERACOES):
        seed_geracao = 2000 + geracao  # mesma seed para toda a população nesta geração (comparação justa)
        fitnesses = [avaliar_fitness(ind, seed=seed_geracao) for ind in populacao]

        melhor_idx = int(np.argmax(fitnesses))
        melhor_fitness = fitnesses[melhor_idx]
        media_fitness = float(np.mean(fitnesses))
        historico_melhor.append(melhor_fitness)
        historico_media.append(media_fitness)

        print(f"Geracao {geracao:3d} | melhor={melhor_fitness:+.1f} | media={media_fitness:+.1f}")

        nova_populacao = [populacao[melhor_idx].copy()]  # elitismo: melhor sobrevive direto
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = selecao_torneio(populacao, fitnesses)
            pai2 = selecao_torneio(populacao, fitnesses)
            filho = mutar(cruzar(pai1, pai2))
            nova_populacao.append(filho)

        populacao = nova_populacao

    melhor_final = populacao[0]
    Path("experimentos").mkdir(exist_ok=True)
    np.save("experimentos/melhor_individuo_genetico.npy", melhor_final)
    with open("experimentos/historico_fitness_genetico.json", "w") as f:
        json.dump({"melhor": historico_melhor, "media": historico_media}, f, indent=2)

    print("\nTreinamento concluído.")
    print("Melhor indivíduo salvo em experimentos/melhor_individuo_genetico.npy")
    print("Histórico de fitness salvo em experimentos/historico_fitness_genetico.json")
    return melhor_final, historico_melhor


if __name__ == "__main__":
    treinar()
