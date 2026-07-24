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
    # movimento do boxer -- descoberto empiricamente via debug_heuristico.py.
    # Também descobrimos que existe uma distância mínima FÍSICA de ~14px
    # entre os dois lutadores (colisão dos sprites -- eles não conseguem
    # se sobrepor), então o limiar precisa ser >= 14, senão o agente nunca
    # sai do modo de movimento (ficava preso tentando chegar mais perto
    # do que é fisicamente possível).
    TOLERANCIA_SOCO = 16

    # Nº mínimo de frames entre um soco e outro. Descoberto empiricamente:
    # segurando FIRE em todo frame (sem soltar), o golpe nunca conectava --
    # o jogo parece reiniciar a animação do soco a cada novo comando, sem
    # deixá-la completar. O agente aleatório pontuava porque, por sorte,
    # intercalava FIRE com outras ações, "soltando o botão" sem querer.
    COOLDOWN_SOCO = 12

    # Detecção de "travamento no canto do ringue": um comportamento real
    # do Boxing original do Atari em que dois jogadores presos no canto,
    # empurrando contra a parede, têm dificuldade de se acertar --
    # descoberto empiricamente via debug_confronto.py (heurístico x
    # genético ficou com distância travada em exatos 15px por 2400+
    # frames seguidos, socando repetidamente sem nunca conectar). Se a
    # posição do oponente não mudar por muitos frames seguidos mesmo
    # tentando atacar, o agente recua um pouco para se reposicionar,
    # em vez de insistir preso no mesmo lugar.
    LIMIAR_TRAVAMENTO = 40  # frames sem a posição relativa mudar
    FRAMES_RECUO = 10

    def __init__(self, jogador="first_0"):
        assert jogador in ("first_0", "second_0")
        self.jogador = jogador
        self.frames_desde_ultimo_soco = self.COOLDOWN_SOCO
        self._ultima_posicao_relativa = None
        self._frames_parado = 0
        self._frames_recuando = 0

    def escolher_acao(self, ram):
        estado = extrair_estado(ram)
        if self.jogador == "first_0":
            px, py, ox, oy = estado["p1_x"], estado["p1_y"], estado["p2_x"], estado["p2_y"]
        else:
            px, py, ox, oy = estado["p2_x"], estado["p2_y"], estado["p1_x"], estado["p1_y"]

        dx, dy = ox - px, oy - py
        self.frames_desde_ultimo_soco += 1

        posicao_relativa = (dx, dy)
        if posicao_relativa == self._ultima_posicao_relativa:
            self._frames_parado += 1
        else:
            self._frames_parado = 0
        self._ultima_posicao_relativa = posicao_relativa

        # Se está travado (posição sem mudar por muitos frames) enquanto
        # ao alcance de ataque, recua um pouco antes de tentar de novo --
        # quebra o "impasse de canto" em vez de insistir preso no lugar.
        if self._frames_parado >= self.LIMIAR_TRAVAMENTO:
            self._frames_recuando = self.FRAMES_RECUO
            self._frames_parado = 0

        if self._frames_recuando > 0:
            self._frames_recuando -= 1
            return self._acao_de_recuo(dx, dy)

        # Só ataca quando já está bem alinhado nos dois eixos -- caso
        # contrário, continua se aproximando com movimento puro (sem FIRE),
        # já que a distância horizontal mínima é limitada pela colisão
        # física entre os lutadores.
        if abs(dx) <= self.TOLERANCIA_SOCO and abs(dy) <= self.TOLERANCIA_SOCO:
            if self.frames_desde_ultimo_soco >= self.COOLDOWN_SOCO:
                self.frames_desde_ultimo_soco = 0
                return self._acao_de_ataque(dy)
            return ACOES["NOOP"]  # espera a animação do soco anterior terminar

        distancia_atual = heuristica_distancia(px, py, ox, oy)
        return self._busca_gulosa_movimento(px, py, ox, oy, distancia_atual)

    def _acao_de_recuo(self, dx, dy):
        """Move na direção OPOSTA ao oponente, para sair do canto travado."""
        if dx > 0:
            return ACOES["LEFT"]
        if dx < 0:
            return ACOES["RIGHT"]
        return ACOES["UP"] if dy > 0 else ACOES["DOWN"]

    def _acao_de_ataque(self, dy):
        """
        Soco mirado verticalmente no oponente. Hipótese testada: FIRE puro
        (sem direção) sempre soca "reto" e erra quando o oponente está
        um pouco acima/abaixo -- por isso miramos o soco no eixo vertical
        (dy), já que o eixo horizontal já está no limite físico de colisão.
        """
        MARGEM_ALINHAMENTO_VERTICAL = 3
        if dy > MARGEM_ALINHAMENTO_VERTICAL:
            return ACOES["DOWNRIGHTFIRE"]
        if dy < -MARGEM_ALINHAMENTO_VERTICAL:
            return ACOES["UPRIGHTFIRE"]
        return ACOES["FIRE"]

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
