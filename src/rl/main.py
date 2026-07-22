"""
Roda um único episódio: AgenteRL (first_0, já treinado) vs. ação aleatória (second_0).
Útil para visualizar o comportamento do agente e para gravar o vídeo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pettingzoo.atari import boxing_v2
from src.rl.agente_rl import AgenteRL
from src.ambiente.extrair_estado import extrair_estado


def rodar_episodio(render=False, seed=42, max_passos=6000,
                    caminho_q_table="src/rl/q_table.pkl"):
    env = boxing_v2.env(obs_type="ram", render_mode="human" if render else None)
    env.reset(seed=seed)
    agente = AgenteRL(jogador="first_0")
    agente.carregar(caminho_q_table)
    passo = 0
    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        if termination or truncation:
            action = None
        elif agent == "first_0":
            action = agente.escolher_acao(obs, treinando=False)
        else:
            action = env.action_space(agent).sample()
        env.step(action)
        passo += 1
        if passo % 500 == 0:
            estado = extrair_estado(obs)
            print(f"passo={passo} placar_p1={estado['placar_p1']} "
                  f"placar_p2={estado['placar_p2']} relogio={estado['relogio']}")
        if passo >= max_passos:
            break
    env.close()


if __name__ == "__main__":
    # render=True abre uma janela mostrando o jogo (útil para debug visual,
    # mas deixe False para rodar mais rápido)
    rodar_episodio(render=False)
