# =============================================================================
# Gerador Lotofácil Analytics Pro — Versão integrada
# =============================================================================
from collections import Counter
from datetime import datetime
import itertools
import random
import re

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gerador Lotofácil Analytics Pro",
    page_icon="🎲",
    layout="wide",
)

# -----------------------------------------------------------------------------
# CONSTANTES GLOBAIS
# -----------------------------------------------------------------------------
MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
PRIMOS  = {2, 3, 5, 7, 11, 13, 17, 19, 23}
MESTRAS = {1, 2, 3, 5, 9, 10, 11, 13, 20, 25}
BAIXAS  = set(range(1, 13))

MAPA_PREMIOS = {
    11: "Onze (11 pts)",
    12: "Doze (12 pts)",
    13: "Treze (13 pts)",
    14: "QUATORZE (14 pts)",
    15: "QUINZE (15 pts)",
}

PRECO_JOGO = 3.50
VALORES_PREMIO = {
    11: 6.00,
    12: 12.00,
    13: 30.00,
    14: 1_500.00,
    15: 1_500_000.00,
}

TENTATIVAS_MIN   = 50_000
FATOR_TENTATIVAS = 5_000

# =============================================================================
# ⬇️⬇️ COLE AQUI AS MATRIZES (GRUPOS_24, GRUPOS_56, GRUPOS_69) ⬇️⬇️
# =============================================================================
# Copie do seu arquivo original (do início de GRUPOS_24 até o fim de GRUPOS_69).
# Exemplo do formato esperado:

# GRUPOS_24 = {"Grupo 01": [...], "Grupo 02": [...], ...}
# GRUPOS_56 = {"Grupo 01": [...], "Grupo 02": [...], ...}
# GRUPOS_69 = {"Grupo 01": [...], "Grupo 02": [...], ...}

GRUPOS_24 = {
    "Grupo 01": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 23, 24],
    "Grupo 02": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 23, 24, 25],
    "Grupo 03": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 20, 22, 23, 24],
    "Grupo 04": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 22, 23, 24, 25],
    "Grupo 05": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 21, 22, 23, 24],
    "Grupo 06": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20],
    "Grupo 07": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 21, 22, 25],
    "Grupo 08": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 19, 20, 21, 22, 25],
    "Grupo 09": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 19, 20, 21, 22, 25],
    "Grupo 10": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21, 23, 24, 25],
    "Grupo 11": [1, 2, 3, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 12": [1, 2, 4, 7, 8, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 13": [1, 2, 5, 6, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 14": [1, 3, 4, 6, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 15": [1, 3, 5, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 16": [1, 4, 5, 7, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 17": [1, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 18": [2, 3, 4, 5, 8, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 19": [2, 3, 4, 5, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 20": [2, 3, 6, 7, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 21": [2, 4, 6, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 22": [3, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 23": [4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "Grupo 24": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
}


GRUPOS_56 = {
    "GRUPO 01": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 23, 24],
    "GRUPO 02": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 23],
    "GRUPO 03": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 24],
    "GRUPO 04": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 25],
    "GRUPO 05": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 21, 24, 25],
    "GRUPO 06": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 21, 22, 23, 24, 25],
    "GRUPO 07": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 24, 25],
    "GRUPO 08": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 20, 23, 25],
    "GRUPO 09": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 20, 21, 22, 23, 24, 25],
    "GRUPO 10": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24],
    "GRUPO 11": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 25],
    "GRUPO 12": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 21, 23, 24],
    "GRUPO 13": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 21, 22, 25],
    "GRUPO 14": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 20, 23, 24, 25],
    "GRUPO 15": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 19, 20, 22, 23, 25],
    "GRUPO 16": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23],
    "GRUPO 17": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19, 20, 22, 24, 25],
    "GRUPO 18": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 17, 18, 19, 20, 21, 22, 24],
    "GRUPO 19": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 20, 21, 22, 24],
    "GRUPO 20": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 18, 19, 22, 23, 24, 25],
    "GRUPO 21": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 21, 22, 23, 24, 25],
    "GRUPO 22": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22],
    "GRUPO 23": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 20, 21, 23, 25],
    "GRUPO 24": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 21, 22, 24, 25],
    "GRUPO 25": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 18, 20, 22, 23, 24, 25],
    "GRUPO 26": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19, 22, 23, 25],
    "GRUPO 27": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 20, 21, 22, 23, 24],
    "GRUPO 28": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 17, 18, 19, 20, 21, 24, 25],
    "GRUPO 29": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 19, 20, 23, 24, 25],
    "GRUPO 30": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 18, 19, 21, 22, 23, 24],
    "GRUPO 31": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 18, 20, 21, 22, 23, 25],
    "GRUPO 32": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 18, 19, 21, 22, 23, 24],
    "GRUPO 33": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 34": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 35": [1, 2, 3, 4, 5, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 36": [1, 2, 3, 6, 7, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 37": [1, 2, 3, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 38": [1, 2, 4, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 39": [1, 2, 4, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 40": [1, 2, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 41": [1, 3, 4, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 42": [1, 3, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 43": [1, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 44": [1, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 45": [1, 4, 5, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 46": [1, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 47": [2, 3, 4, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 48": [2, 3, 5, 6, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 49": [2, 3, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 50": [2, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 51": [2, 4, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 52": [2, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 53": [3, 4, 5, 6, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 54": [3, 4, 5, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 55": [3, 4, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 56": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
}



GRUPOS_69 = {
    "GRUPO 01": [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 02": [3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 03": [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 04": [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 05": [2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 06": [2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 07": [2, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 08": [2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 09": [1, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 10": [1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 11": [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 12": [1, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 13": [1, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 14": [1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 15": [1, 2, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 16": [1, 2, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 17": [1, 2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 18": [1, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 19": [1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 20": [1, 2, 3, 4, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 21": [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 22": [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25],
    "GRUPO 23": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 24": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25],
    "GRUPO 25": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25],
    "GRUPO 26": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25],
    "GRUPO 27": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25],
    "GRUPO 28": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25],
    "GRUPO 29": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24],
    "GRUPO 30": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 31": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25],
    "GRUPO 32": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25],
    "GRUPO 33": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24],
    "GRUPO 34": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25],
    "GRUPO 35": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24],
    "GRUPO 36": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 37": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 38": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 39": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 40": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 41": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 42": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 43": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 44": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 45": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25],
    "GRUPO 46": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 21, 22, 23, 24, 25],
    "GRUPO 47": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25],
    "GRUPO 48": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24],
    "GRUPO 49": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25],
    "GRUPO 50": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24],
    "GRUPO 51": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 21, 22, 23, 24, 25],
    "GRUPO 52": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25],
    "GRUPO 53": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25],
    "GRUPO 54": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 24, 25],
    "GRUPO 55": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    "GRUPO 56": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 57": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 58": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 59": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 60": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 23, 25],
    "GRUPO 61": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 23, 24, 25],
    "GRUPO 62": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 25],
    "GRUPO 63": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 23, 25],
    "GRUPO 64": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 25],
    "GRUPO 65": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25],
    "GRUPO 66": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 25],
    "GRUPO 67": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 22, 24, 25],
    "GRUPO 68": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24],
    "GRUPO 69": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24]
}


# =============================================================================
# ⬆️⬆️ FIM DAS MATRIZES ⬆️⬆️
# =============================================================================


# -----------------------------------------------------------------------------
# AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    st.title("🔒 Acesso Restrito")
    st.subheader("Digite a senha para acessar o gerador da Lotofácil")
    senha_digitada = st.text_input("Senha:", type="password")

    if st.button("Entrar"):
        try:
            senha_correta = st.secrets.get("APP_PASSWORD")
            if not senha_correta:
                st.error("⚠️ Configuração ausente: defina `APP_PASSWORD` no arquivo `.streamlit/secrets.toml`.")
                return False

            if senha_digitada == senha_correta:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        except Exception:
            st.error("⚠️ O arquivo `.streamlit/secrets.toml` não foi encontrado ou está mal formatado.")
            return False

    return False

if not verificar_senha():
    st.stop()


# -----------------------------------------------------------------------------
# SCRAPING ONLINE
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def carregar_dados_online():
    url = "https://asloterias.com.br/lista-de-resultados-da-lotofacil"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            st.warning(f"⚠️ Scraping retornou status {r.status_code}.")
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        container = soup.find("div", class_="col-md-8") or soup
        texto = container.get_text(separator=" ")

        padrao = re.compile(
            r"(\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})\s*-\s*"
            + r"\s+".join([r"(\d{2})"] * 15)
        )
        matches = padrao.findall(texto)

        dados = []
        for match in matches:
            conc = int(match[0])
            data = match[1]
            dezenas = [int(x) for x in match[2:]]
            if not all(1 <= d <= 25 for d in dezenas) or len(set(dezenas)) != 15:
                continue
            row = {"concurso": conc, "data": data}
            for i, d in enumerate(dezenas, 1):
                row[f"Bola{i}"] = d
            dados.append(row)

        if dados:
            df = pd.DataFrame(dados)
            df = df.drop_duplicates(subset="concurso", keep="last")
            return df.sort_values(by="concurso", ascending=True).reset_index(drop=True)
    except Exception as e:
        st.warning(f"⚠️ Falha no scraping: {e}")
    return None


# -----------------------------------------------------------------------------
# MÉTRICAS UNIFICADAS
# -----------------------------------------------------------------------------
def _seq_max(comb):
    mx, cur = 1, 1
    for i in range(1, len(comb)):
        if comb[i] == comb[i - 1] + 1:
            cur += 1
            mx = max(mx, cur)
        else:
            cur = 1
    return mx


def _seq_total(comb):
    return sum(1 for i in range(1, len(comb)) if comb[i] == comb[i - 1] + 1)


def _soma_digitos(comb):
    return sum(int(ch) for x in comb for ch in str(x))


def _n_espelhos(comb):
    s = set(comb)
    return sum(1 for x in s if (26 - x) in s and x != 13) // 2


def _metricas(comb, ctx):
    s = set(comb)
    prev = ctx.get("prev_draw", set())
    linhas = Counter((x - 1) // 5 for x in comb)
    colunas = Counter((x - 1) % 5 for x in comb)
    termos = Counter(x % 10 for x in comb)
    return {
        "soma":         sum(comb),
        "soma_digitos": _soma_digitos(comb),
        "repetidas":    len(s & prev),
        "moldura":      len(s & MOLDURA),
        "primos":       len(s & PRIMOS),
        "mestras":      len(s & MESTRAS),
        "impares":      sum(1 for x in comb if x % 2),
        "baixas":       len(s & BAIXAS),
        "seq_max":      _seq_max(comb),
        "seq_total":    _seq_total(comb),
        "espelhos":     _n_espelhos(comb),
        "gemeas_max":   max(termos.values()) if termos else 0,
        "linha_min":    min(linhas.values()),
        "linha_max":    max(linhas.values()),
        "coluna_min":   min(colunas.values()),
        "coluna_max":   max(colunas.values()),
    }


# -----------------------------------------------------------------------------
# FILTROS (dict: nome -> (função, faixa clássica))
# -----------------------------------------------------------------------------
FILTROS = {
    "Soma (160-220)":           (lambda m: 160 <= m["soma"] <= 220,           ("soma", 160, 220)),
    "Repetidas (8-11)":         (lambda m: 8 <= m["repetidas"] <= 11,         ("repetidas", 8, 11)),
    "Moldura (8-11)":           (lambda m: 8 <= m["moldura"] <= 11,           ("moldura", 8, 11)),
    "Primos (4-7)":             (lambda m: 4 <= m["primos"] <= 7,             ("primos", 4, 7)),
    "Mestras (5-8)":            (lambda m: 5 <= m["mestras"] <= 8,            ("mestras", 5, 8)),
    "Ímpares (6-9)":            (lambda m: 6 <= m["impares"] <= 9,            ("impares", 6, 9)),
    "Seq. Máx (3-7)":           (lambda m: 3 <= m["seq_max"] <= 7,            ("seq_max", 3, 7)),
    "Soma dígitos (60-95)":     (lambda m: 60 <= m["soma_digitos"] <= 95,     ("soma_digitos", 60, 95)),
    "Baixas 1-12 (6-9)":        (lambda m: 6 <= m["baixas"] <= 9,             ("baixas", 6, 9)),
    "Seq. total (3-7)":         (lambda m: 3 <= m["seq_total"] <= 7,          ("seq_total", 3, 7)),
    "Espelhos (≤ 3)":           (lambda m: m["espelhos"] <= 3,                ("espelhos", 0, 3)),
    "Gêmeas (≤ 4)":             (lambda m: m["gemeas_max"] <= 4,              ("gemeas_max", 0, 4)),
    "Linhas do volante (1-5)":  (lambda m: 1 <= m["linha_min"] and m["linha_max"] <= 5,
                                                                            ("linha_max", 1, 5)),
    "Colunas do volante (1-5)": (lambda m: 1 <= m["coluna_min"] and m["coluna_max"] <= 5,
                                                                            ("coluna_max", 1, 5)),
}

FILTROS_CLASSICOS = list(FILTROS.keys())[:7]
FILTROS_AVANCADOS = list(FILTROS.keys())[7:]


def _percentile(vals, p):
    if not vals:
        return None
    idx = int(round(p / 100 * (len(vals) - 1)))
    return vals[idx]


def calcular_ranges_adaptativos(janela_concursos, p_low=15, p_high=85):
    amostras = {}
    n = len(janela_concursos)
    for i, conc in enumerate(janela_concursos):
        prev = set(janela_concursos[i + 1]) if i + 1 < n else set()
        m = _metricas(conc, {"prev_draw": prev})
        for k, v in m.items():
            amostras.setdefault(k, []).append(v)
    ranges = {}
    for k, vals in amostras.items():
        vals = sorted(vals)
        lo, hi = _percentile(vals, p_low), _percentile(vals, p_high)
        if lo is not None and hi is not None:
            ranges[k] = (lo, hi)
    return ranges


def validar_jogo(comb, ctx, filtros_ativos, ranges_adaptativos=None):
    m = _metricas(comb, ctx)
    aprov = 0
    detalhes = {}
    for nome in filtros_ativos:
        fn, (metric, lo_c, hi_c) = FILTROS[nome]
        if (ranges_adaptativos and metric in ranges_adaptativos
                and nome != "Repetidas (8-11)"):
            lo, hi = ranges_adaptativos[metric]
            val = m[metric]
            ok = (val <= hi) if metric in ("espelhos", "gemeas_max") else (lo <= val <= hi)
        else:
            ok = fn(m)
        detalhes[nome] = ok
        aprov += int(ok)
    return aprov, m, detalhes


# -----------------------------------------------------------------------------
# ANALYTICS AVANÇADOS
# -----------------------------------------------------------------------------
def calcular_atrasos(janela):
    atrasos = {}
    for d in range(1, 26):
        a = 0
        for conc in janela:
            if d in conc:
                break
            a += 1
        atrasos[d] = a
    return sorted(atrasos, key=atrasos.get, reverse=True), atrasos


def obter_top_trincas_matriz(janela, dezenas_matriz, top_n=10):
    c = Counter()
    dz = set(dezenas_matriz)
    for conc in janela:
        f = sorted(list(set(conc) & dz))
        for t in itertools.combinations(f, 3):
            c[t] += 1
    return c.most_common(top_n)


def obter_top_duplas(janela, dezenas_matriz, top_n=15):
    c = Counter()
    dz = set(dezenas_matriz)
    for conc in janela:
        f = sorted(set(conc) & dz)
        for d in itertools.combinations(f, 2):
            c[d] += 1
    return c.most_common(top_n)


def obter_top_quadras(janela, dezenas_matriz, top_n=10):
    c = Counter()
    dz = set(dezenas_matriz)
    for conc in janela:
        f = sorted(set(conc) & dz)
        for q in itertools.combinations(f, 4):
            c[q] += 1
    return c.most_common(top_n)


def matriz_markov(janela):
    M = np.zeros((26, 26))
    for i in range(1, len(janela)):
        for a in janela[i - 1]:
            for b in janela[i]:
                M[a][b] += 1
    for a in range(1, 26):
        s = M[a].sum()
        if s > 0:
            M[a] /= s
    return M


def score_bayesiano(janela):
    freq = Counter(d for c in janela for d in c)
    N = len(janela)
    return {d: (freq[d] + 1) / (N + 25) for d in range(1, 26)}


# =============================================================================
# INTERFACE
# =============================================================================
st.title("🎲 Gerador Otimizado Lotofácil Analytics Pro")

# ------------------------ Sidebar: matriz -------------------------
st.sidebar.header("⚙️ Seleção de Matriz de Grupos")
opcao_matriz = st.sidebar.selectbox(
    "Escolha o conjunto de grupos:",
    [
        "24 Grupos (19 dezenas)",
        "56 Grupos (20 dezenas)",
        "69 Grupos (22 dezenas)",
        "🎯 Digitar Dezenas Manualmente",
    ],
)

if "24" in opcao_matriz:
    GRUPOS_ATIVOS = GRUPOS_24
elif "56" in opcao_matriz:
    GRUPOS_ATIVOS = GRUPOS_56
elif "69" in opcao_matriz:
    GRUPOS_ATIVOS = GRUPOS_69
else:
    st.sidebar.markdown("---")
    dezenas_manuais = st.sidebar.multiselect(
        "Selecione de 15 a 24 dezenas para a sua matriz:",
        options=list(range(1, 26)),
        default=list(range(1, 20)),
    )
    if len(dezenas_manuais) < 15:
        st.sidebar.warning("⚠️ Selecione pelo menos 15 dezenas.")
    GRUPOS_ATIVOS = {"Grupo Manual": sorted(dezenas_manuais)}

# ------------------------ Sidebar: base histórica -------------------------
st.sidebar.markdown("---")
st.sidebar.header("📁 Base Histórica de Dados")

modo_base = st.sidebar.radio(
    "Seletor de Modo:",
    options=["🌐 Conectado Online", "📂 Modo Offline (Planilha Excel / CSV)"],
    index=0,
)

df_historico_raw = None

if "Online" in modo_base:
    df_historico_raw = carregar_dados_online()
    if df_historico_raw is not None and not df_historico_raw.empty:
        st.sidebar.success("🌐 Conectado online")
    else:
        st.sidebar.error("⚠️ Falha online. Use o Modo Offline.")
else:
    uploaded = st.sidebar.file_uploader(
        "Upload manual de planilha (.xlsx / .csv)", type=["xlsx", "csv"]
    )
    if uploaded is not None:
        try:
            if uploaded.name.endswith(".csv"):
                df_historico_raw = pd.read_csv(uploaded)
            else:
                xls = pd.ExcelFile(uploaded)
                sheet = "LOTOFÁCIL" if "LOTOFÁCIL" in xls.sheet_names else 0
                df_historico_raw = pd.read_excel(uploaded, sheet_name=sheet)
            if df_historico_raw is None or df_historico_raw.empty:
                st.sidebar.error("❌ Planilha vazia.")
                df_historico_raw = None
            else:
                st.sidebar.success(f"📂 {len(df_historico_raw)} linhas carregadas.")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar: {e}")
            df_historico_raw = None
    else:
        st.sidebar.info("📌 Aguardando arquivo...")


# =============================================================================
# PROCESSAMENTO
# =============================================================================
if df_historico_raw is not None and not df_historico_raw.empty:
    col_conc = next(
        (c for c in df_historico_raw.columns if "concurso" in str(c).lower()),
        df_historico_raw.columns[0],
    )
    df_historico_raw = df_historico_raw.sort_values(
        by=col_conc, ascending=True
    ).reset_index(drop=True)

    if "Offline" in modo_base:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Concurso Alvo (Offline)")
        opcoes = []
        for _, row in df_historico_raw.iterrows():
            c_num = int(row[col_conc])
            c_data = str(row.get("data", ""))
            lbl = f" ({c_data})" if c_data and c_data != "nan" else ""
            opcoes.append(f"Concurso: #{c_num}{lbl}")
        opcoes = opcoes[::-1]
        escolha = st.sidebar.selectbox("Referência:", options=opcoes)
        concurso_alvo = int(re.search(r"#(\d+)", escolha).group(1))
        df_historico = df_historico_raw[
            df_historico_raw[col_conc].astype(int) <= concurso_alvo
        ].copy()
    else:
        df_historico = df_historico_raw.copy()

    col_bolas = [
        c for c in df_historico.columns
        if any(t in str(c).lower() for t in [
            "bola", "dezena", "d1", "d2", "d3", "d4", "d5", "d6",
            "d7", "d8", "d9", "d10", "d11", "d12", "d13", "d14", "d15",
        ]) and "data" not in str(c).lower()
    ][:15]

    ultimo = df_historico.iloc[-1]
    last_contest_num = int(ultimo[col_conc])
    data_c = str(ultimo.get("data", ""))
    data_str = f" ({data_c})" if data_c and data_c != "nan" else ""

    if len(col_bolas) == 15:
        dez_txt = " - ".join(f"{int(ultimo[c]):02d}" for c in col_bolas)
        st.sidebar.info(
            f"📌 **Último Concurso:** #{last_contest_num}{data_str}\n\n"
            f"🎯 **Dezenas:** `{dez_txt}`"
        )
    else:
        st.sidebar.warning(f"⚠️ Detectadas apenas {len(col_bolas)} colunas.")

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Escopo da Análise")
    total_base = len(df_historico)
    qtd_janela = st.sidebar.number_input(
        "Concursos para recalibragem:",
        min_value=10, max_value=total_base,
        value=min(25, total_base), step=5,
    )

    st.info(
        f"📊 **Base:** #{last_contest_num}. "
        f"Análise calibrada nos últimos **{qtd_janela}** concursos."
    )

    # ---------------- Filtros clássicos ----------------
    st.sidebar.header("⚙️ Filtros Estatísticos (clássicos)")
    usar_soma      = st.sidebar.checkbox("Soma (160-220)", value=True)
    usar_repetidas = st.sidebar.checkbox("Repetidas (8-11)", value=True)
    usar_moldura   = st.sidebar.checkbox("Moldura (8-11)", value=True)
    usar_primos    = st.sidebar.checkbox("Primos (4-7)", value=True)
    usar_mestras   = st.sidebar.checkbox("Mestras (5-8)", value=True)
    usar_impares   = st.sidebar.checkbox("Ímpares (6-9)", value=True)
    usar_sequencia = st.sidebar.checkbox("Seq. Máx (3-7)", value=True)

    # ---------------- Filtros avançados ----------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 Filtros Avançados")
    filtros_avancados_ativos = []
    for nome in FILTROS_AVANCADOS:
        if st.sidebar.checkbox(nome, value=False, key=f"adv_{nome}"):
            filtros_avancados_ativos.append(nome)

    # ---------------- Modo de faixas ----------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Modo de Faixas")
    modo_ranges = st.sidebar.radio(
        "Limites:",
        ["Clássico (hardcoded)", "Adaptativo (P15–P85)"],
        index=0,
    )
    usar_adaptativo = modo_ranges.startswith("Adaptativo")

    # ---------------- Dezenas fixas ----------------
    st.sidebar.markdown("---")
    usar_fixas = st.sidebar.checkbox(
        "🔒 Ativar Dezenas Fixas", value=False
    )
    dezenas_fixas_selecionadas = []
    if usar_fixas:
        dezenas_fixas_selecionadas = st.sidebar.multiselect(
            "Selecione 1 ou 2 dezenas fixas:",
            options=list(range(1, 26)),
            max_selections=2,
            default=[],
        )

    # ---------------- Janela ----------------
    last_janela = df_historico.iloc[-qtd_janela:].iloc[::-1]
    janela_concursos = [
        row[col_bolas].astype(int).tolist() for _, row in last_janela.iterrows()
    ]
    prev_draw = set(janela_concursos[0])

    filtros_classicos_ativos = [
        nome for nome, chk in [
            ("Soma (160-220)", usar_soma),
            ("Repetidas (8-11)", usar_repetidas),
            ("Moldura (8-11)", usar_moldura),
            ("Primos (4-7)", usar_primos),
            ("Mestras (5-8)", usar_mestras),
            ("Ímpares (6-9)", usar_impares),
            ("Seq. Máx (3-7)", usar_sequencia),
        ] if chk
    ]
    filtros_ativos = filtros_classicos_ativos + filtros_avancados_ativos

    if usar_adaptativo:
        ranges_adap = calcular_ranges_adaptativos(janela_concursos)
    else:
        ranges_adap = None

    min_aprovacoes = st.sidebar.slider(
        "Mínimo de regras atendidas:",
        min_value=1,
        max_value=max(1, len(filtros_ativos)),
        value=min(len(filtros_ativos), max(1, len(filtros_classicos_ativos))),
    )

    dezenas_matriz_ativa = sorted(set(d for g in GRUPOS_ATIVOS.values() for d in g))

    # =========================================================================
    # ABAS
    # =========================================================================
    tab_gerador, tab_estat, tab_backtest, tab_metodo = st.tabs(
        ["🚀 Gerador", "📈 Estatísticas", "🧪 Backtest", "📚 Metodologia"]
    )

    # -------------------------------------------------------------------------
    # ABA ESTATÍSTICAS
    # -------------------------------------------------------------------------
    with tab_estat:
        st.subheader("📊 Frequência e Atraso")
        _, mapa_atrasos = calcular_atrasos(janela_concursos)
        freq_dez = Counter(d for c in janela_concursos for d in c)
        df_freq = pd.DataFrame([{
            "Dezena": f"{d:02d}",
            "Frequência": freq_dez[d],
            "Atraso": mapa_atrasos[d],
        } for d in range(1, 26)])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Frequência**")
            st.dataframe(
                df_freq.sort_values("Frequência", ascending=False),
                use_container_width=True, hide_index=True,
            )
        with c2:
            st.markdown("**Maiores Atrasos**")
            st.dataframe(
                df_freq.sort_values("Atraso", ascending=False),
                use_container_width=True, hide_index=True,
            )

        st.markdown("---")
        st.subheader(f"🔥 Top Trincas ({opcao_matriz})")
        trincas = obter_top_trincas_matriz(janela_concursos, dezenas_matriz_ativa)
        st.dataframe(pd.DataFrame([
            {"Trinca": f"{t[0]:02d} - {t[1]:02d} - {t[2]:02d}", "Ocorrências": occ}
            for t, occ in trincas
        ]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔗 Top Duplas e Quadras")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Top Duplas**")
            st.dataframe(pd.DataFrame([
                {"Dupla": f"{d[0]:02d}-{d[1]:02d}", "Ocorrências": o}
                for d, o in obter_top_duplas(janela_concursos, dezenas_matriz_ativa)
            ]), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Top Quadras**")
            st.dataframe(pd.DataFrame([
                {"Quadra": " ".join(f"{x:02d}" for x in q), "Ocorrências": o}
                for q, o in obter_top_quadras(janela_concursos, dezenas_matriz_ativa)
            ]), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # ABA GERADOR
    # -------------------------------------------------------------------------
    with tab_gerador:
        st.subheader("🎯 Parâmetros de Geração")

        c1, c2 = st.columns(2)
        with c1:
            qtd_jogos = st.number_input(
                "Quantidade de jogos:", min_value=1, max_value=500, value=10,
            )
        with c2:
            modo_geracao = st.radio(
                "Método:",
                [
                    "Melhores Desempenhos no Histórico",
                    "Otimizado por Top Trincas Frequentes",
                    "Otimizado por Duplas + Quadras",
                    "Aleatório Controlado",
                    "🎯 Usar Dezenas Manuais",
                ],
            )

        if st.button("✨ Gerar Apostas", type="primary"):
            if len(dezenas_matriz_ativa) < 15:
                st.error("❌ Selecione pelo menos 15 dezenas.")
            elif not filtros_ativos:
                st.error("❌ Ative pelo menos um filtro.")
            else:
                with st.spinner("Gerando..."):
                    score_grupos = {
                       g: sum(len(set(gd) & set(c)) for c in janela_concursos)
                        for g, gd in GRUPOS_ATIVOS.items()
                    }
                    grupos_ord = sorted(score_grupos, key=score_grupos.get, reverse=True)
                    top_t = [
                        t[0] for t in obter_top_trincas_matriz(
                            janela_concursos, dezenas_matriz_ativa, top_n=5
                        )
                    ]
                    top_d = dict(obter_top_duplas(
                        janela_concursos, dezenas_matriz_ativa, top_n=30
                    ))
                    top_q = dict(obter_top_quadras(
                        janela_concursos, dezenas_matriz_ativa, top_n=20
                    ))

                    jogos, infos = [], []
                    tent_max = max(TENTATIVAS_MIN, qtd_jogos * FATOR_TENTATIVAS)
                    tent = 0
                    prog = st.progress(0.0)

                    while len(jogos) < qtd_jogos and tent < tent_max:
                        tent += 1
                        if tent % 500 == 0:
                            prog.progress(min(len(jogos) / qtd_jogos, 1.0))

                        if "Manual" in opcao_matriz or modo_geracao.endswith("Manual"):
                            grupo = "Grupo Manual"
                        elif modo_geracao == "Melhores Desempenhos no Histórico":
                            grupo = random.choice(grupos_ord[:10])
                        elif modo_geracao == "Otimizado por Top Trincas Frequentes":
                            t_alvo = set(random.choice(top_t)) if top_t else set()
                            cands = [g for g, d in GRUPOS_ATIVOS.items() if t_alvo <= set(d)]
                            grupo = random.choice(cands) if cands else random.choice(grupos_ord)
                        elif modo_geracao == "Otimizado por Duplas + Quadras":
                            ranked = sorted(
                                GRUPOS_ATIVOS,
                                key=lambda g: (
                                    sum(top_d.get(d, 0) for d in itertools.combinations(
                                        sorted(GRUPOS_ATIVOS[g]), 2
                                    ))
                                    + 3 * sum(top_q.get(q, 0) for q in itertools.combinations(
                                        sorted(GRUPOS_ATIVOS[g]), 4
                                    ))
                                ),
                                reverse=True,
                            )
                            grupo = random.choice(ranked[:10])
                        else:
                            grupo = random.choice(list(GRUPOS_ATIVOS))

                        dg = GRUPOS_ATIVOS[grupo]

                        if usar_fixas and dezenas_fixas_selecionadas:
                            if not all(d in dg for d in dezenas_fixas_selecionadas):
                                continue
                            rest = [d for d in dg if d not in dezenas_fixas_selecionadas]
                            comb = sorted(
                                dezenas_fixas_selecionadas
                                + random.sample(rest, 15 - len(dezenas_fixas_selecionadas))
                            )
                        else:
                            comb = sorted(random.sample(dg, 15))

                        if comb in jogos:
                            continue

                        aprov, metricas, detalhes = validar_jogo(
                            comb, {"prev_draw": prev_draw},
                            filtros_ativos, ranges_adap,
                        )
                        if aprov >= min_aprovacoes:
                            jogos.append(comb)
                            infos.append({
                                "grupo": grupo,
                                "metricas": metricas,
                                "detalhes": detalhes,
                                "aprovacoes": aprov,
                            })

                    prog.empty()
                    st.session_state["jogos"] = jogos
                    st.session_state["infos"] = infos
                    st.session_state["filtros_usados"] = filtros_ativos

                    if len(jogos) < qtd_jogos:
                        st.warning(
                            f"⚠️ Gerados {len(jogos)}/{qtd_jogos} jogos "
                            f"em {tent_max} tentativas."
                        )
                    else:
                        st.success(f"✅ {len(jogos)} jogos gerados!")

        # ---------- Exibição ----------
        if st.session_state.get("jogos"):
            jogos = st.session_state["jogos"]
            infos = st.session_state.get("infos", [{}] * len(jogos))
            nfilt = len(st.session_state.get("filtros_usados", []))

            df_j = pd.DataFrame([{
                "Jogo": f"Jogo {i+1:02d}",
                "Grupo Origem": infos[i].get("grupo", "—"),
                "Dezenas": " - ".join(f"{d:02d}" for d in j),
                "Soma": infos[i]["metricas"]["soma"],
                "Repet.": infos[i]["metricas"]["repetidas"],
                "Moldura": infos[i]["metricas"]["moldura"],
                "Primos": infos[i]["metricas"]["primos"],
                "Ímpares": infos[i]["metricas"]["impares"],
                "Seq.Máx": infos[i]["metricas"]["seq_max"],
                "Aprov.": f"{infos[i]['aprovacoes']}/{nfilt}",
            } for i, j in enumerate(jogos)])

            st.dataframe(df_j, use_container_width=True, hide_index=True)

            with st.expander("🔍 Explicador por jogo"):
                idx = st.selectbox(
                    "Escolha:",
                    options=range(len(jogos)),
                    format_func=lambda i: (
                        f"Jogo {i+1:02d} — "
                        + " ".join(f"{d:02d}" for d in jogos[i])
                    ),
                )
                det = infos[idx].get("detalhes", {})
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Filtros**")
                    for nome, ok in det.items():
                        st.markdown(f"{'✅' if ok else '❌'} {nome}")
                with c2:
                    st.markdown("**Métricas**")
                    st.json(infos[idx].get("metricas", {}))

            texto = "\n".join(" ".join(f"{d:02d}" for d in j) for j in jogos)
            st.download_button(
                "📥 Baixar Jogos (.txt)", data=texto,
                file_name=f"jogos_lotofacil_{datetime.now():%Y%m%d_%H%M%S}.txt",
                mime="text/plain",
            )

            st.markdown("---")
            st.subheader("🔍 Conferência Histórica Completa")
            if st.button("🔎 Verificar Premiações"):
                achados = []
                for idx_j, jogo in enumerate(jogos, 1):
                    sj = set(jogo)
                    for _, row in df_historico.iterrows():
                        s_dez = set(row[col_bolas].astype(int).values)
                        a = len(sj & s_dez)
                        if a >= 11:
                            achados.append({
                                "Jogo Nº": idx_j,
                                "Dezenas do Jogo": ", ".join(map(str, jogo)),
                                "Tipo": MAPA_PREMIOS.get(a, ""),
                                "Concurso": row.get(col_conc, "—"),
                                "Dezenas Sorteadas": ", ".join(map(str, sorted(s_dez))),
                            })
                if achados:
                    dfp = pd.DataFrame(achados)
                    dfp.index += 1
                    st.success(f"🎉 {len(achados)} premiações encontradas.")
                    st.dataframe(dfp, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhuma premiação no histórico consultado.")

    # -------------------------------------------------------------------------
    # ABA BACKTEST WALK-FORWARD
    # -------------------------------------------------------------------------
    def _gerar_jogos_core(treino_df, grupos, qtd, filtros, min_aprov, prev, fixas):
        if len(treino_df) < 10:
            return []
        cols = [c for c in treino_df.columns if c in col_bolas][:15]
        jan = treino_df.iloc[-min(25, len(treino_df)):].iloc[::-1]
        jl = [row[cols].astype(int).tolist() for _, row in jan.iterrows()]
        dz = sorted(set(d for g in grupos.values() for d in g))
        score = {g: sum(len(set(gd) & c) for c in jl) for g, gd in grupos.items()}
        ranked = sorted(score, key=score.get, reverse=True)
        trincas = [t[0] for t in obter_top_trincas_matriz(jl, dz, top_n=5)]
        rad = calcular_ranges_adaptativos(jl) if usar_adaptativo else None

        jogos, tent, tmax = [], 0, max(TENTATIVAS_MIN, qtd * FATOR_TENTATIVAS)
        while len(jogos) < qtd and tent < tmax:
            tent += 1
            if random.random() < 0.5:
                grupo = random.choice(ranked[:10])
            else:
                t_alvo = set(random.choice(trincas)) if trincas else set()
                cands = [g for g, d in grupos.items() if t_alvo <= set(d)]
                grupo = random.choice(cands) if cands else random.choice(list(grupos))
            dg = grupos[grupo]
            if fixas and not all(d in dg for d in fixas):
                continue
            if fixas:
                rest = [d for d in dg if d not in fixas]
                comb = sorted(fixas + random.sample(rest, 15 - len(fixas)))
            else:
                comb = sorted(random.sample(dg, 15))
            if comb in jogos:
                continue
            aprov, _, _ = validar_jogo(comb, {"prev_draw": prev}, filtros, rad)
            if aprov >= min_aprov:
                jogos.append(comb)
        return jogos

    with tab_backtest:
        st.subheader("🧪 Backtest Walk-Forward")
        st.markdown(
            "Para cada concurso alvo, gera jogos usando **apenas** dados anteriores "
            "(sem look-ahead). Mede a performance real."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            n_test = st.number_input(
                "Concursos para testar:",
                min_value=5,
                max_value=max(5, min(200, len(df_historico) - 10)),
                value=min(30, max(5, len(df_historico) - 10)),
            )
        with c2:
            qtd_back = st.number_input(
                "Jogos por concurso:", min_value=1, max_value=50, value=5,
            )
        with c3:
            comparar = st.checkbox("Comparar com aleatório", value=True)

        if st.button("▶️ Rodar Backtest", type="primary"):
            if not filtros_ativos:
                st.error("Ative ao menos um filtro.")
            else:
                res = []
                prog = st.progress(0.0)
                stt = st.empty()
                for k in range(n_test):
                    idx = len(df_historico) - n_test + k
                    treino = df_historico.iloc[:idx]
                    alvo = df_historico.iloc[idx]
                    dez_alvo = set(alvo[col_bolas].astype(int).values)
                    prev = (
                        set(df_historico.iloc[idx - 1][col_bolas].astype(int).values)
                        if idx > 0 else set()
                    )
                    jogos = _gerar_jogos_core(
                        treino, GRUPOS_ATIVOS, qtd_back, filtros_ativos,
                        min_aprovacoes, prev,
                        dezenas_fixas_selecionadas if usar_fixas else [],
                    )
                    acertos = [len(set(j) & dez_alvo) for j in jogos]
                    premios = [VALORES_PREMIO.get(a, 0) for a in acertos]
                    base_p = []
                    if comparar:
                        for _ in range(qtd_back):
                            c = random.sample(range(1, 26), 15)
                            base_p.append(VALORES_PREMIO.get(len(set(c) & dez_alvo), 0))
                    res.append({
                        "Concurso": int(alvo[col_conc]),
                        "Jogos": len(jogos),
                        "Custo (R$)": len(jogos) * PRECO_JOGO,
                        "Prêmio (R$)": sum(premios),
                        "Melhor acerto": max(acertos) if acertos else 0,
                        "Prêmio base (R$)": sum(base_p),
                        "Custo base (R$)": len(base_p) * PRECO_JOGO,
                    })
                    prog.progress((k + 1) / n_test)
                    stt.caption(f"Testando #{int(alvo[col_conc])}...")

                prog.empty(); stt.empty()
                df_bt = pd.DataFrame(res)

                ct = df_bt["Custo (R$)"].sum()
                pt = df_bt["Prêmio (R$)"].sum()
                roi = (pt - ct) / ct * 100 if ct else 0
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Custo", f"R$ {ct:,.2f}")
                m2.metric("Prêmio", f"R$ {pt:,.2f}")
                m3.metric("ROI", f"{roi:+.1f}%")
                m4.metric("Melhor acerto", f"{df_bt['Melhor acerto'].max()} pts")

                if comparar:
                    cb = df_bt["Custo base (R$)"].sum()
                    pb = df_bt["Prêmio base (R$)"].sum()
                    roib = (pb - cb) / cb * 100 if cb else 0
                    st.markdown(
                        f"**Baseline aleatório:** ROI {roib:+.1f}% | "
                        f"Prêmio R$ {pb:,.2f} | "
                        f"Delta: **{roi - roib:+.1f} p.p.**"
                    )

                st.markdown("---")
                st.subheader("📈 Evolução")
                st.line_chart(
                    df_bt.set_index("Concurso")[["Prêmio (R$)", "Custo (R$)"]],
                    use_container_width=True,
                )
                st.bar_chart(
                    df_bt.set_index("Concurso")[["Melhor acerto"]],
                    use_container_width=True,
                )
                st.dataframe(df_bt, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # ABA METODOLOGIA
    # -------------------------------------------------------------------------
    with tab_metodo:
        st.subheader("📚 Metodologia e Limitações")
        st.markdown("""
### Como funciona
1. Histórico da Lotofácil é carregado (online ou planilha)
2. Matrizes (24/56/69 grupos) restringem o espaço amostral
3. Filtros estatísticos validam cada jogo candidato
4. Apenas jogos que atendem a **N filtros** são aceitos

### Filtros disponíveis
- **Clássicos:** Soma, Repetidas, Moldura, Primos, Mestras, Ímpares, Seq. Máx
- **Avançados:** Soma dígitos, Baixas, Seq. total, Espelhos, Gêmeas, Linhas, Colunas

### Modo Adaptativo (P15–P85)
Os limites dos filtros são recalculados como os percentis 15 e 85 da
distribuição empírica dos últimos `N` concursos — filtros **dinâmicos**.

### Backtest Walk-Forward
Para cada concurso `N`, treina com `1..N-1`, gera jogos e confere em `N`.
Elimina **look-ahead bias**.

---

### ⚠️ Aviso estatístico
A Lotofácil é um sorteio **independente**. Filtros históricos **não aumentam**
a probabilidade individual de acerto — o espaço amostral é fixo (3.268.760
combinações). O que eles **fazem**:
- Reduzem combinações candidatas
- Evitam padrões populares → melhor **rateio**
- Organizam a aposta com métricas objetivas

O que eles **não fazem**:
- Prever o próximo sorteio
- Aumentar chance de 15 pontos
- Garantir lucro

**Jogue com responsabilidade.**
        """)

else:
    st.info(
        "👈 Selecione o Modo Online ou carregue uma planilha no Modo Offline."
    )
