"""
Agente baseado em estado, objetivo e busca heurística para o ambiente
Boxing (PettingZoo Atari).

Estado: posição (x, y) do próprio jogador e do oponente, extraídos da RAM
        (bytes validados no mapeamento: 32/34 para o jogador 1, 33/35 para
        o jogador 2 -- ver src/ambiente/mapeamento_ram.md).

Objetivo: maximizar placar_proprio - placar_oponente, o que na prática
          significa: aproximar-se do oponente e atacar quando estiver ao
          alcance de soco.

Heurística: distância euclidiana até o oponente. É uma heurística
            admissível para o subobjetivo de "alcançar distância de
            ataque", pois nunca superestima o número de passos de
            movimento necessários (cada ação de movimento reduz a
            distância em no máximo ~1.4, para movimentos diagonais).

Busca: a cada passo, o agente faz uma busca gulosa de 1 nível (greedy
       best-first de profundidade 1): simula o efeito de cada ação de
       movimento candidata usando o modelo de transição empírico
       descoberto durante o mapeamento de RAM (cada ação move o sprite em
       torno de +-1 pixel por frame nos eixos x/y) e escolhe a ação que
       minimiza a heurística. Quando a distância já é pequena o
       suficiente, troca para uma ação de ataque na direção do oponente.
"""

import sys
from pathlib import Path

# Garante que "src" seja importável independente de onde o script é chamado
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.ambiente.extrair_estado import extrair_estado  # noqa: E402


ACOES = {
    "NOOP": 0, "FIRE": 1, "UP": 2, "RIGHT": 3, "LEFT": 4, "DOWN": 5,
    "UPRIGHT": 6, "UPLEFT": 7, "DOWNRIGHT": 8, "DOWNLEFT": 9,
    "UPFIRE": 10, "RIGHTFIRE": 11, "LEFTFIRE": 12, "DOWNFIRE": 13,
    "UPRIGHTFIRE": 14, "UPLEFTFIRE": 15, "DOWNRIGHTFIRE": 16, "DOWNLEFTFIRE": 17,
}

# Modelo de transição empírico: ação de movimento -> (dx, dy) aproximado
DELTA_MOVIMENTO = {
    ACOES["RIGHT"]: (1, 0),
    ACOES["LEFT"]: (-1, 0),
    ACOES["UP"]: (0, -1),
    ACOES["DOWN"]: (0, 1),
    ACOES["UPRIGHT"]: (1, -1),
    ACOES["UPLEFT"]: (-1, -1),
    ACOES["DOWNRIGHT"]: (1, 1),
    ACOES["DOWNLEFT"]: (-1, 1),
}


def heuristica_distancia(px, py, ox, oy):
    """h(estado) = distância euclidiana até o oponente."""
    return ((px - ox) ** 2 + (py - oy) ** 2) ** 0.5


class AgenteHeuristico:
    # Tolerância de alinhamento (em pixels) para considerar que o oponente
    # está ao alcance do soco. IMPORTANTE: ações de soco (FIRE) TRAVAM o
    # movimento do boxer -- descoberto empiricamente via debug_heuristico.py,
    # onde o agente ficava preso trocando socos diagonais sem nunca fechar
    # a distância. Por isso o agente só ataca quando já está bem alinhado,
    # e usa SOMENTE movimento puro (sem FIRE) enquanto se aproxima.
    TOLERANCIA_SOCO = 5

    def __init__(self, jogador="first_0"):
        assert jogador in ("first_0", "second_0")
        self.jogador = jogador

    def escolher_acao(self, ram):
        estado = extrair_estado(ram)
        if self.jogador == "first_0":
            px, py, ox, oy = estado["p1_x"], estado["p1_y"], estado["p2_x"], estado["p2_y"]
        else:
            px, py, ox, oy = estado["p2_x"], estado["p2_y"], estado["p1_x"], estado["p1_y"]

        dx, dy = ox - px, oy - py

        # Só ataca quando já está bem alinhado nos dois eixos -- caso
        # contrário, continua se aproximando com movimento puro (sem FIRE),
        # já que socar trava a posição e impede fechar a distância restante.
        if abs(dx) <= self.TOLERANCIA_SOCO and abs(dy) <= self.TOLERANCIA_SOCO:
            return ACOES["FIRE"]

        distancia_atual = heuristica_distancia(px, py, ox, oy)
        return self._busca_gulosa_movimento(px, py, ox, oy, distancia_atual)

    def _busca_gulosa_movimento(self, px, py, ox, oy, distancia_atual):
        """Greedy best-first de profundidade 1 sobre as ações de movimento."""
        melhor_acao = ACOES["NOOP"]
        melhor_h = distancia_atual
        for acao, (dx, dy) in DELTA_MOVIMENTO.items():
            h_simulado = heuristica_distancia(px + dx, py + dy, ox, oy)
            if h_simulado < melhor_h:
                melhor_h = h_simulado
                melhor_acao = acao
        return melhor_acao
