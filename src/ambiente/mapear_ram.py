"""
Ferramenta exploratória para mapear os 128 bytes da RAM do ambiente
Boxing (PettingZoo Atari), identificando quais índices variam durante
o jogo e são, portanto, candidatos a representar posição, placar, tempo etc.

Metodologia:
1. Roda um episódio com ações aleatórias, guardando a RAM a cada passo.
2. Identifica quais índices do vetor NUNCA mudam (provavelmente irrelevantes).
3. Identifica quais índices mudam MUITO pouco (bons candidatos a posição/estado).
4. Roda um teste dirigido: um agente sempre anda pra direita, outro fica
   parado, e comparamos a RAM antes/depois para achar candidatos a
   posição de cada jogador.
"""

import numpy as np
from pettingzoo.atari import boxing_v2


def coletar_ram_episodio(n_passos=200, seed=42):
    """Roda um episódio com ações aleatórias e retorna todas as RAMs coletadas."""
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    historico = {agent: [] for agent in env.possible_agents}

    passo = 0
    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        historico[agent].append(obs.copy())

        if termination or truncation:
            action = None
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        passo += 1
        if passo >= n_passos:
            break

    env.close()
    return historico


def encontrar_bytes_variaveis(historico):
    """Para cada agente, identifica quais índices de RAM mudaram de valor."""
    resultado = {}
    for agent, frames in historico.items():
        if len(frames) < 2:
            continue
        matriz = np.stack(frames)  # shape (n_passos, 128)
        variacao = matriz.max(axis=0).astype(int) - matriz.min(axis=0).astype(int)
        indices_variaveis = np.where(variacao > 0)[0]
        resultado[agent] = {
            "indices_variaveis": indices_variaveis.tolist(),
            "variacao_por_indice": {int(i): int(variacao[i]) for i in indices_variaveis},
        }
    return resultado


def teste_dirigido_acao_fixa(acao_p1, acao_p2, n_passos=60, seed=42):
    """
    Roda o ambiente forçando ações fixas para os dois jogadores
    (ex: sempre mover pra direita) e retorna a RAM inicial e final,
    útil para isolar qual byte corresponde à posição de cada um.
    """
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)

    acoes = {"first_0": acao_p1, "second_0": acao_p2}
    ram_inicial, ram_final = None, None
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        if ram_inicial is None:
            ram_inicial = obs.copy()

        if termination or truncation:
            action = None
        else:
            action = acoes.get(agent, 0)

        env.step(action)
        ram_final = obs.copy()
        passo += 1
        if passo >= n_passos * len(env.possible_agents):
            break

    env.close()
    return ram_inicial, ram_final


if __name__ == "__main__":
    print("=== Etapa 1: coletando RAM com ações aleatórias ===")
    historico = coletar_ram_episodio(n_passos=200)
    resultado = encontrar_bytes_variaveis(historico)

    for agent, dados in resultado.items():
        print(f"\nAgente: {agent}")
        print(f"Total de índices que variaram: {len(dados['indices_variaveis'])} de 128")
        print(f"Índices: {dados['indices_variaveis']}")

    print("\n=== Etapa 2: teste dirigido (ação fixa) ===")
    # Consultar env.action_space(agent) para saber os códigos de ação do Boxing
    # (tipicamente: 0=NOOP, e ações de movimento/soco variam por índice)
    ram_i, ram_f = teste_dirigido_acao_fixa(acao_p1=2, acao_p2=0, n_passos=60)
    diferenca = np.abs(ram_f.astype(int) - ram_i.astype(int))
    indices_mudaram = np.where(diferenca > 0)[0]
    print(f"Índices que mudaram com ação fixa do jogador 1: {indices_mudaram.tolist()}")
    for i in indices_mudaram:
        print(f"  byte[{i}]: {ram_i[i]} -> {ram_f[i]} (diff={diferenca[i]})")
