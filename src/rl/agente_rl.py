"""
Agente de aprendizado por reforço (Q-learning tabular) para o ambiente
Boxing (PettingZoo Atari).

Estado: posição relativa (dx, dy) até o oponente, discretizada em bins,
        mais uma flag indicando se o cooldown do soco já passou.
        Reaproveita o mesmo mapeamento de RAM usado no agente heurístico
        (ver src/ambiente/mapeamento_ram.md e extrair_estado.py).

Ação: mesmo espaço de ações do ambiente (Discrete(18)).

Algoritmo: Q-learning tabular com política epsilon-greedy.
"""

import pickle
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.ambiente.extrair_estado import extrair_estado  # noqa: E402

N_ACOES = 18
BIN_SIZE = 8          # tamanho da faixa de discretização da posição relativa
COOLDOWN_SOCO = 8      # mesmo valor usado no agente heurístico

# Ações que envolvem soco (FIRE puro e as combinações direcionais com FIRE)
ACOES_DE_SOCO = {1, 10, 11, 12, 13, 14, 15, 16, 17}


def discretizar_estado(px, py, ox, oy, frames_desde_soco):
    """Reduz o estado contínuo (posições) a um estado discreto compacto,
    o suficiente para caber numa tabela Q sem explodir em tamanho."""
    dx = int((ox - px) // BIN_SIZE)
    dy = int((oy - py) // BIN_SIZE)
    pronto = 1 if frames_desde_soco >= COOLDOWN_SOCO else 0
    return (dx, dy, pronto)


class AgenteRL:
    def __init__(self, jogador="first_0", alpha=0.1, gamma=0.95,
                 epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.9995):
        assert jogador in ("first_0", "second_0")
        self.jogador = jogador
        self.alpha = alpha            # taxa de aprendizado
        self.gamma = gamma            # fator de desconto
        self.epsilon = epsilon        # taxa de exploração inicial
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Tabela Q: estado -> vetor de valores por ação
        self.q_table = defaultdict(lambda: np.zeros(N_ACOES))

        self.frames_desde_ultimo_soco = COOLDOWN_SOCO
        self._ultimo_estado = None
        self._ultima_acao = None

    def _ler_posicoes(self, ram):
        estado = extrair_estado(ram)
        if self.jogador == "first_0":
            return estado["p1_x"], estado["p1_y"], estado["p2_x"], estado["p2_y"]
        return estado["p2_x"], estado["p2_y"], estado["p1_x"], estado["p1_y"]

    def escolher_acao(self, ram, treinando=False):
        """Escolhe uma ação a partir da RAM atual.
        treinando=True usa epsilon-greedy; treinando=False é greedy puro
        (usado na avaliação/gravação do vídeo, com a política já aprendida).
        """
        px, py, ox, oy = self._ler_posicoes(ram)
        self.frames_desde_ultimo_soco += 1
        estado = discretizar_estado(px, py, ox, oy, self.frames_desde_ultimo_soco)

        if treinando and random.random() < self.epsilon:
            acao = random.randrange(N_ACOES)
        else:
            acao = int(np.argmax(self.q_table[estado]))

        if acao in ACOES_DE_SOCO:
            self.frames_desde_ultimo_soco = 0

        self._ultimo_estado = estado
        self._ultima_acao = acao
        return acao

    def aprender(self, recompensa, ram_proximo, terminou):
        """Atualiza a tabela Q com a transição (estado, ação, recompensa, próximo estado)."""
        if self._ultimo_estado is None:
            return

        if terminou:
            alvo = recompensa
        else:
            px, py, ox, oy = self._ler_posicoes(ram_proximo)
            proximo_estado = discretizar_estado(px, py, ox, oy, self.frames_desde_ultimo_soco)
            alvo = recompensa + self.gamma * np.max(self.q_table[proximo_estado])

        erro_td = alvo - self.q_table[self._ultimo_estado][self._ultima_acao]
        self.q_table[self._ultimo_estado][self._ultima_acao] += self.alpha * erro_td

    def decair_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def salvar(self, caminho="src/rl/q_table.pkl"):
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "wb") as f:
            pickle.dump(dict(self.q_table), f)

    def carregar(self, caminho="src/rl/q_table.pkl"):
        with open(caminho, "rb") as f:
            tabela = pickle.load(f)
        self.q_table = defaultdict(lambda: np.zeros(N_ACOES), tabela)
