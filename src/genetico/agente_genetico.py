"""
Agente baseado em algoritmo genético para o ambiente Boxing (PettingZoo Atari).

Cromossomo: matriz de pesos W (N_FEATURES x N_ACOES) que mapeia um vetor
            de features do estado relativo (posição do oponente em
            relação ao próprio agente, distância euclidiana e tempo desde
            o último soco) para uma pontuação por ação disponível.
            A ação escolhida é argmax(features . W).

Aptidão (fitness): placar_proprio - placar_oponente ao final de um
                    episódio contra um oponente de referência.

As features reaproveitam o mapeamento de RAM e a lógica de "cooldown do
soco" descobertos durante o desenvolvimento do agente heurístico (ver
src/ambiente/mapeamento_ram.md) -- sem essa informação de tempo desde o
último soco, a política não teria como aprender a evitar martelar FIRE
sem soltar o botão, que é o mesmo problema que travava o heurístico.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.ambiente.extrair_estado import extrair_estado  # noqa: E402
from src.heuristica.agente_heuristico import ACOES  # noqa: E402

N_ACOES = len(ACOES)
N_FEATURES = 5  # dx, dy, distancia, frames_desde_soco, bias

ACOES_DE_SOCO = {v for k, v in ACOES.items() if "FIRE" in k}


def extrair_features(estado, jogador, frames_desde_soco):
    """Vetor de features relativas, normalizado, com termo de bias."""
    if jogador == "first_0":
        px, py, ox, oy = estado["p1_x"], estado["p1_y"], estado["p2_x"], estado["p2_y"]
    else:
        px, py, ox, oy = estado["p2_x"], estado["p2_y"], estado["p1_x"], estado["p1_y"]

    dx = ox - px
    dy = oy - py
    dist = (dx ** 2 + dy ** 2) ** 0.5
    tempo_normalizado = min(frames_desde_soco, 20) / 20.0

    return np.array([dx / 160.0, dy / 210.0, dist / 260.0, tempo_normalizado, 1.0])


class AgenteGenetico:
    def __init__(self, pesos, jogador="first_0"):
        assert pesos.shape == (N_FEATURES, N_ACOES)
        self.pesos = pesos
        self.jogador = jogador
        self.frames_desde_soco = 999

    def reset(self):
        """Chamar no início de cada episódio (o indivíduo não tem memória entre partidas)."""
        self.frames_desde_soco = 999

    def escolher_acao(self, ram):
        estado = extrair_estado(ram)
        features = extrair_features(estado, self.jogador, self.frames_desde_soco)
        scores = features @ self.pesos
        acao = int(np.argmax(scores))

        self.frames_desde_soco += 1
        if acao in ACOES_DE_SOCO:
            self.frames_desde_soco = 0

        return acao

    @staticmethod
    def pesos_aleatorios(rng):
        return rng.normal(0, 0.5, size=(N_FEATURES, N_ACOES))
