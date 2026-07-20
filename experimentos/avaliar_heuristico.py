"""
Protocolo de avaliação: roda N episódios do AgenteHeuristico (first_0)
contra um oponente de ação aleatória (second_0) e reporta métricas
agregadas, servindo de comparação com a estratégia de referência
(agente aleatório), conforme item 8 do conteúdo obrigatório do vídeo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pettingzoo.atari import boxing_v2
from src.heuristica.agente_heuristico import AgenteHeuristico
from src.ambiente.extrair_estado import extrair_estado


def rodar_uma_partida(seed, max_passos=3000):
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=seed)
    agente = AgenteHeuristico(jogador="first_0")

    placar_final = {"placar_p1": 0, "placar_p2": 0}
    passo = 0

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs)
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        estado = extrair_estado(obs)
        placar_final["placar_p1"] = estado["placar_p1"]
        placar_final["placar_p2"] = estado["placar_p2"]

        passo += 1
        if passo >= max_passos:
            break

    env.close()
    return placar_final


def avaliar(n_execucoes=20):
    resultados = []
    for i in range(n_execucoes):
        placar = rodar_uma_partida(seed=1000 + i)
        resultados.append(placar)
        print(f"execucao {i+1}/{n_execucoes}: "
              f"heuristico={placar['placar_p1']} x aleatorio={placar['placar_p2']}")

    vitorias = sum(1 for r in resultados if r["placar_p1"] > r["placar_p2"])
    empates = sum(1 for r in resultados if r["placar_p1"] == r["placar_p2"])
    derrotas = sum(1 for r in resultados if r["placar_p1"] < r["placar_p2"])
    media_p1 = sum(r["placar_p1"] for r in resultados) / n_execucoes
    media_p2 = sum(r["placar_p2"] for r in resultados) / n_execucoes

    print("\n=== Resumo (Heurístico vs. Aleatório) ===")
    print(f"Execuções: {n_execucoes}")
    print(f"Vitórias: {vitorias} | Empates: {empates} | Derrotas: {derrotas}")
    print(f"Placar médio -- heurístico: {media_p1:.2f} | aleatório: {media_p2:.2f}")


if __name__ == "__main__":
    avaliar(n_execucoes=20)
