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
N_GERACOES = 25
TAXA_MUTACAO = 0.2
DESVIO_MUTACAO = 0.3
TAMANHO_TORNEIO = 3
MAX_PASSOS_EPISODIO = 3000
N_SEEDS_POR_AVALIACAO = 2  # media de N partidas por individuo, para reduzir ruido

# CURRÍCULO: nas primeiras metade das gerações, o oponente fica PARADO
# (NOOP o tempo todo). Isso remove o risco de apanhar muito ao se
# aproximar, permitindo que a população aprenda a "buscar e atacar" sem
# ser punida por isso -- só depois disso aprendido é que trocamos para o
# oponente aleatório, para testar generalização. Diagnóstico anterior:
# sem currículo, a evolução convergia para "nunca se aproximar", pois
# aproximar-se de um oponente aleatório é arriscado demais para um
# indivíduo recém-nascido (pesos aleatórios) aprender por tentativa e erro.
GERACOES_COM_CURRICULO = N_GERACOES // 2

# Seeds FIXAS usadas só para medir a evolução real do melhor indivíduo ao
# longo das gerações (não usadas na seleção, para não termos "trapaça" --
# a seleção continua usando uma seed por geração, o que ajuda a evitar
# overfitting a um único cenário; mas isso torna o "melhor" de cada
# geração incomparável entre si, já que cada um foi avaliado num cenário
# diferente. As seeds de validação resolvem isso: o mesmo cenário é usado
# para medir o progresso do campeão a cada geração.)
SEEDS_VALIDACAO = [9001, 9002, 9003]

RNG = np.random.default_rng(42)


def avaliar_fitness(pesos, seed, oponente_parado=False, retornar_detalhes=False):
    """
    Roda um episódio completo e retorna o fitness combinando:
      1. placar_p1 - placar_p2 (o objetivo real)
      2. um pequeno bônus por proximidade média ao oponente ao longo do
         episódio (reward shaping)

    oponente_parado=True faz o oponente (second_0) ficar em NOOP o tempo
    todo -- usado nas gerações de currículo, para reduzir o risco de
    aproximação nas primeiras gerações.
    """
    from src.genetico.agente_genetico import extrair_features

    PESO_PROXIMIDADE = 0.02

    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)
    agente = AgenteGenetico(pesos, jogador="first_0")
    agente.reset()

    placar_p1, placar_p2 = 0, 0
    distancias = []
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if not (termination or truncation):
            estado = extrair_estado(obs)
            placar_p1, placar_p2 = estado["placar_p1"], estado["placar_p2"]
            if agent == "first_0":
                features = extrair_features(estado, "first_0", agente.frames_desde_soco)
                dx_norm, dy_norm = features[0], features[1]
                dist_norm = (dx_norm ** 2 + dy_norm ** 2) ** 0.5
                distancias.append(dist_norm)

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs)
        elif oponente_parado:
            action = 0  # NOOP
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= MAX_PASSOS_EPISODIO or termination or truncation:
            break

    env.close()

    resultado_partida = placar_p1 - placar_p2
    distancia_media = float(np.mean(distancias)) if distancias else 1.0
    bonus_proximidade = PESO_PROXIMIDADE * (1.0 - distancia_media)  # quanto menor a distância, maior o bônus
    fitness = resultado_partida + bonus_proximidade

    if retornar_detalhes:
        return fitness, resultado_partida, distancia_media
    return fitness


def avaliar_fitness_medio(pesos, seed_base, oponente_parado=False):
    """Roda N_SEEDS_POR_AVALIACAO partidas (seeds diferentes) e retorna a
    média do fitness, para reduzir o ruído de uma única partida (fonte da
    alta variância observada na validação: resultados de -13 a 0)."""
    valores = [
        avaliar_fitness(pesos, seed=seed_base + i, oponente_parado=oponente_parado)
        for i in range(N_SEEDS_POR_AVALIACAO)
    ]
    return float(np.mean(valores))


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


def avaliar_validacao(pesos):
    """
    Avalia um indivíduo nas seeds FIXAS de validação e retorna a média do
    RESULTADO REAL DA PARTIDA (placar_p1 - placar_p2, sem o bônus de
    proximidade usado só para guiar a seleção). Usado para medir o
    progresso real do campeão entre gerações, sem o ruído de trocar de
    cenário a cada geração.
    """
    resultados = [avaliar_fitness(pesos, seed=s, retornar_detalhes=True)[1] for s in SEEDS_VALIDACAO]
    return float(np.mean(resultados))


def treinar():
    populacao = [AgenteGenetico.pesos_aleatorios(RNG) for _ in range(TAMANHO_POPULACAO)]
    historico_treino_melhor = []
    historico_treino_media = []
    historico_validacao = []
    melhor_individuo_global = populacao[0].copy()
    melhor_validacao_global = -float("inf")

    for geracao in range(N_GERACOES):
        seed_geracao = 2000 + geracao * 10  # espaçadas para não colidir com N_SEEDS_POR_AVALIACAO
        usar_curriculo = geracao < GERACOES_COM_CURRICULO
        fitnesses = [
            avaliar_fitness_medio(ind, seed_base=seed_geracao, oponente_parado=usar_curriculo)
            for ind in populacao
        ]

        melhor_idx = int(np.argmax(fitnesses))
        melhor_fitness_treino = fitnesses[melhor_idx]
        media_fitness_treino = float(np.mean(fitnesses))

        # Avalia o campeão desta geração num cenário fixo, para termos uma
        # curva de evolução comparável entre gerações (métrica reportável).
        fitness_validacao = avaliar_validacao(populacao[melhor_idx])

        # Mantém registro do melhor indivíduo JÁ VISTO em qualquer geração
        # (não necessariamente o elite da última geração).
        if fitness_validacao > melhor_validacao_global:
            melhor_validacao_global = fitness_validacao
            melhor_individuo_global = populacao[melhor_idx].copy()

        historico_treino_melhor.append(melhor_fitness_treino)
        historico_treino_media.append(media_fitness_treino)
        historico_validacao.append(fitness_validacao)

        print(f"Geracao {geracao:3d} | melhor(treino)={melhor_fitness_treino:+.1f} | "
              f"media(treino)={media_fitness_treino:+.1f} | validacao={fitness_validacao:+.2f} | "
              f"{'curriculo(parado)' if usar_curriculo else 'aleatorio'}")

        nova_populacao = [populacao[melhor_idx].copy()]  # elitismo: melhor sobrevive direto
        while len(nova_populacao) < TAMANHO_POPULACAO:
            pai1 = selecao_torneio(populacao, fitnesses)
            pai2 = selecao_torneio(populacao, fitnesses)
            filho = mutar(cruzar(pai1, pai2))
            nova_populacao.append(filho)

        populacao = nova_populacao

    print(f"\nMelhor validacao encontrada: {melhor_validacao_global:+.2f}")

    Path("experimentos").mkdir(exist_ok=True)
    np.save("experimentos/melhor_individuo_genetico.npy", melhor_individuo_global)
    with open("experimentos/historico_fitness_genetico.json", "w") as f:
        json.dump({
            "melhor_treino": historico_treino_melhor,
            "media_treino": historico_treino_media,
            "validacao": historico_validacao,
            "melhor_validacao_global": melhor_validacao_global,
        }, f, indent=2)

    print("\nTreinamento concluído.")
    print("Melhor indivíduo (por validação) salvo em experimentos/melhor_individuo_genetico.npy")
    print("Histórico de fitness salvo em experimentos/historico_fitness_genetico.json")
    return melhor_individuo_global, historico_validacao


if __name__ == "__main__":
    treinar()
