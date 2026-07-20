"""
Extração de estado do Boxing com mapeamento de RAM validado.

Mapeamento confirmado por dois métodos independentes:
1. Testes empíricos da dupla (ações fixas + eventos de recompensa)
2. Cruzamento com fonte acadêmica: Anand et al., "Unsupervised State
   Representation Learning in Atari" (mila-iqia/atari-representation-learning)
   https://github.com/mila-iqia/atari-representation-learning

| Variável       | Byte | Validação                                    |
|----------------|------|-----------------------------------------------|
| p1_x           | 32   | empírico (dupla) + fonte acadêmica            |
| p1_y           | 34   | empírico (dupla) + fonte acadêmica            |
| p2_x (enemy_x) | 33   | empírico (dupla) + fonte acadêmica            |
| p2_y (enemy_y) | 35   | empírico (dupla) + fonte acadêmica            |
| relogio        | 17   | fonte acadêmica (byte estava na lista variável)|
| placar_p1      | 18   | fonte acadêmica -- AINDA NAO TESTADO empiricamente |
| placar_p2      | 19   | fonte acadêmica + evento de reward -2 da dupla|
"""

import numpy as np
from pettingzoo.atari import boxing_v2


def extrair_estado(ram):
    """Lê a RAM bruta e retorna um dicionário com os valores do jogo."""
    return {
        "p1_x": int(ram[32]),
        "p1_y": int(ram[34]),
        "p2_x": int(ram[33]),
        "p2_y": int(ram[35]),
        "relogio": int(ram[17]),
        "placar_p1": int(ram[18]),
        "placar_p2": int(ram[19]),
    }


def validar_placar(max_tentativas=15):
    """
    Roda partidas até detectar reward != 0 e imprime o valor RAW dos
    bytes 18 e 19 antes/depois, para confirmar se batem com o sinal do
    reward e se precisam de decodificação BCD ou não.
    """
    for tentativa in range(max_tentativas):
        env = boxing_v2.env(obs_type="ram")
        env.reset(seed=100 + tentativa)
        ram_anterior = None

        for agent in env.agent_iter():
            obs, reward, term, trunc, info = env.last()

            if reward != 0 and ram_anterior is not None:
                estado_antes = extrair_estado(ram_anterior)
                estado_depois = extrair_estado(obs)
                print(f"[tentativa {tentativa}] agente={agent} reward={reward}")
                print(f"  placar_p1: {estado_antes['placar_p1']} -> {estado_depois['placar_p1']}")
                print(f"  placar_p2: {estado_antes['placar_p2']} -> {estado_depois['placar_p2']}")
                env.close()
                return

            ram_anterior = obs.copy()
            if term or trunc:
                action = None
            else:
                action = np.random.choice([1, 3]) if np.random.rand() < 0.3 else env.action_space(agent).sample()
            env.step(action)

        env.close()
        print(f"Tentativa {tentativa} sem pontuação, tentando de novo...")

    print("Nenhuma pontuação detectada em nenhuma tentativa.")


if __name__ == "__main__":
    validar_placar()
