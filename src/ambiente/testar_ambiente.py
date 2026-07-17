"""
Script simples para validar a instalação do ambiente PettingZoo Atari
com observação RAM, conforme restrição do Contexto II do estudo dirigido.
"""

from pettingzoo.atari import boxing_v2


def testar_ambiente():
    env = boxing_v2.env(obs_type="ram")
    env.reset(seed=42)

    print(f"Agentes no ambiente: {env.agents}")

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()
        print(f"Agente: {agent} | shape da observação: {obs.shape} | "
              f"dtype: {obs.dtype} | min: {obs.min()} | max: {obs.max()}")

        if termination or truncation:
            action = None
        else:
            action = env.action_space(agent).sample()

        env.step(action)
        break  # só testamos o primeiro passo

    env.close()
    print("\nAmbiente configurado corretamente!")


if __name__ == "__main__":
    testar_ambiente()
