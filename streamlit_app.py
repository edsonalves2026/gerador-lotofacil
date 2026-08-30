import streamlit as st
import pandas as pd
import numpy as np
import itertools
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

st.set_page_config(page_title="Gerador Lotofácil Analytics Pro", page_icon="🎲", layout="wide")

# -----------------------------------------------------------------------------
# AUTENTICAÇÃO / TELA DE LOGIN
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
        senha_correta = st.secrets.get("APP_PASSWORD", "123456")
        
        if senha_digitada == senha_correta:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
            
    return False

if not verificar_senha():
    st.stop()

# -----------------------------------------------------------------------------
# WEB SCRAPING & CARREGAMENTO DE DADOS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def carregar_dados_online():
    url = "https://asloterias.com.br/lista-de-resultados-da-lotofacil"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            container = soup.find('div', class_='col-md-8') or soup
            texto = container.get_text(separator=' ')
            
            padrao = re.compile(r'(\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})\s*-\s*' + r'\s+'.join([r'(\d{2})']*15))
            matches = padrao.findall(texto)
            
            dados = []
            for match in matches:
                conc = int(match[0])
                data = match[1]
                dezenas = [int(x) for x in match[2:]]
                row = {"concurso": conc, "data": data}
                for i, d in enumerate(dezenas, 1):
                    row[f"Bola{i}"] = d
                dados.append(row)
            
            if dados:
                df = pd.DataFrame(dados)
                return df.sort_values(by="concurso", ascending=True).reset_index(drop=True)
    except Exception:
        pass
    return None

# -----------------------------------------------------------------------------
# DEFINIÇÃO DAS MATRIZES DE GRUPOS
# -----------------------------------------------------------------------------
GRUPOS_24 = {
    'GRUPO 01': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 23, 24],
    'GRUPO 02': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 23, 24, 25],
    'GRUPO 03': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 20, 22, 23, 24],
    'GRUPO 04': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 22, 23, 24, 25],
    'GRUPO 05': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 21, 22, 23, 24],
    'GRUPO 06': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20],
    'GRUPO 07': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 21, 22, 25],
    'GRUPO 08': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 19, 20, 21, 22, 25],
    'GRUPO 09': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 19, 20, 21, 22, 25],
    'GRUPO 10': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 11': [1, 2, 3, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 12': [1, 2, 4, 7, 8, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 13': [1, 2, 5, 6, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 14': [1, 3, 4, 6, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 15': [1, 3, 5, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 16': [1, 4, 5, 7, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 17': [1, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 18': [2, 3, 4, 5, 8, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 19': [2, 3, 4, 5, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 20': [2, 3, 6, 7, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 21': [2, 4, 6, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 22': [3, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 23': [4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 24': [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
}

GRUPOS_56 = {
    'GRUPO 01': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 23, 24],
    'GRUPO 02': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 23],
    'GRUPO 03': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 24],
    'GRUPO 04': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 20, 22, 25],
    'GRUPO 05': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 21, 24, 25],
    'GRUPO 06': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 21, 22, 23, 24, 25],
    'GRUPO 07': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 24, 25],
    'GRUPO 08': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19, 20, 23, 25],
    'GRUPO 09': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 20, 21, 22, 23, 24, 25],
    'GRUPO 10': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24],
    'GRUPO 11': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 19, 20, 21, 22, 25],
    'GRUPO 12': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 21, 23, 24],
    'GRUPO 13': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 21, 22, 25],
    'GRUPO 14': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 18, 20, 23, 24, 25],
    'GRUPO 15': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 19, 20, 22, 23, 25],
    'GRUPO 16': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23],
    'GRUPO 17': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19, 20, 22, 24, 25],
    'GRUPO 18': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 17, 18, 19, 20, 21, 22, 24],
    'GRUPO 19': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 20, 21, 22, 24],
    'GRUPO 20': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 18, 19, 22, 23, 24, 25],
    'GRUPO 21': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 21, 22, 23, 24, 25],
    'GRUPO 22': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22],
    'GRUPO 23': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 20, 21, 23, 25],
    'GRUPO 24': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 21, 22, 24, 25],
    'GRUPO 25': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 18, 20, 22, 23, 24, 25],
    'GRUPO 26': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19, 22, 23, 25],
    'GRUPO 27': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 20, 21, 22, 23, 24],
    'GRUPO 28': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 17, 18, 19, 20, 21, 24, 25],
    'GRUPO 29': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 17, 19, 20, 23, 24, 25],
    'GRUPO 30': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 18, 19, 21, 22, 23, 24],
    'GRUPO 31': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 18, 20, 21, 22, 23, 25],
    'GRUPO 32': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 18, 19, 21, 22, 23, 24],
    'GRUPO 33': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 34': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 35': [1, 2, 3, 4, 5, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 36': [1, 2, 3, 6, 7, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 37': [1, 2, 3, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 38': [1, 2, 4, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 39': [1, 2, 4, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 40': [1, 2, 5, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 41': [1, 3, 4, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 42': [1, 3, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 43': [1, 3, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 44': [1, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 45': [1, 4, 5, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 46': [1, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 47': [2, 3, 4, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 48': [2, 3, 5, 6, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 49': [2, 3, 5, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 50': [2, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 51': [2, 4, 6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 52': [2, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 53': [3, 4, 5, 6, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 54': [3, 4, 5, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 55': [3, 4, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 56': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
}

GRUPOS_69 = {
    'GRUPO 01': [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 02': [3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 03': [3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 04': [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 05': [2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 06': [2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 07': [2, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 08': [2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 09': [1, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 10': [1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 11': [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 12': [1, 3, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 13': [1, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 14': [1, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 15': [1, 2, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 16': [1, 2, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 17': [1, 2, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 18': [1, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 19': [1, 2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 20': [1, 2, 3, 4, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 21': [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 22': [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25],
    'GRUPO 23': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 24': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25],
    'GRUPO 25': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25],
    'GRUPO 26': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25],
    'GRUPO 27': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25],
    'GRUPO 28': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25],
    'GRUPO 29': [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24],
    'GRUPO 30': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 31': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25],
    'GRUPO 32': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25],
    'GRUPO 33': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24],
    'GRUPO 34': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25],
    'GRUPO 35': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24],
    'GRUPO 36': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 37': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 38': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 39': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 40': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 41': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 42': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 43': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 44': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 45': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25],
    'GRUPO 46': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 21, 22, 23, 24, 25],
    'GRUPO 47': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25],
    'GRUPO 48': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24],
    'GRUPO 49': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 25],
    'GRUPO 50': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24],
    'GRUPO 51': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 21, 22, 23, 24, 25],
    'GRUPO 52': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 24, 25],
    'GRUPO 53': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25],
    'GRUPO 54': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 22, 24, 25],
    'GRUPO 55': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'GRUPO 56': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 57': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 58': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 59': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 60': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 23, 25],
    'GRUPO 61': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 23, 24, 25],
    'GRUPO 62': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 25],
    'GRUPO 63': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 23, 25],
    'GRUPO 64': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 25],
    'GRUPO 65': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25],
    'GRUPO 66': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 25],
    'GRUPO 67': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 22, 24, 25],
    'GRUPO 68': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 24],
    'GRUPO 69': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24]
}

# =============================================================================
# SEÇÃO DA BARRA LATERAL (MODO ONLINE/OFFLINE E MATRIZES)
# =============================================================================
st.sidebar.header("📁 Base Histórica")

# Opção de escolha entre Online e Offline
modo_operacao = st.sidebar.radio(
    "Modo de Operação:",
    ["🌐 Conectado Online", "📂 Modo Offline (Planilha Excel)"],
    index=0
)

df_historico_raw = None

if modo_operacao == "🌐 Conectado Online":
    # Sua função existente de carregamento online
    df_historico_raw = carregar_dados()
    if df_historico_raw is not None and not df_historico_raw.empty:
        st.sidebar.success("🌐 Conectado online (`asloterias`)")
    else:
        st.sidebar.warning("Não foi possível carregar online. Tente o modo offline.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload manual da planilha", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            df_historico_raw = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
            st.sidebar.success("Base carregada via Upload!")
        except Exception as e:
            st.sidebar.error(f"Erro no upload: {e}")
    else:
        st.sidebar.info("Carregue uma planilha Excel ou CSV para iniciar no modo offline.")

# Extração dos sorteios completos
sorteios_historico_completos_bruto = extrair_sorteios_historicos(df_historico_raw) if df_historico_raw is not None and not df_historico_raw.empty else []

# SELETOR INTERATIVO DE CONCURSO (CORTE DE REFERÊNCIA)
df_historico = None
sorteios_historico_completos = []

if df_historico_raw is not None and not df_historico_raw.empty and sorteios_historico_completos_bruto:
    lista_concursos_disponiveis = []
    for idx_c, _ in enumerate(sorteios_historico_completos_bruto):
        conc_num = df_historico_raw.iloc[idx_c].get('concurso', idx_c + 1)
        data_conc = df_historico_raw.iloc[idx_c].get('data', '')
        label_c = f"Concurso #{conc_num}" + (f" ({data_conc})" if data_conc else "")
        lista_concursos_disponiveis.append((conc_num, idx_c, label_c))
    
    labels_opcoes = [item[2] for item in lista_concursos_disponiveis]
    escolha_concurso_str = st.sidebar.selectbox(
        "🎯 Definir Concurso de Referência (Corte):",
        options=labels_opcoes,
        index=len(labels_opcoes) - 1 # Padrão é sempre o mais recente
    )
    
    indice_selecionado = next(item[1] for item in lista_concursos_disponiveis if item[2] == escolha_concurso_str)
    
    # Corta o dataframe e os sorteios até a escolha do usuário
    df_historico = df_historico_raw.iloc[:indice_selecionado + 1].copy()
    sorteios_historico_completos = sorteios_historico_completos_bruto[:indice_selecionado + 1]
    
    ultimo_registro = df_historico.iloc[-1]
    conc_num = ultimo_registro.get('concurso', 'N/A')
    data_conc = ultimo_registro.get('data', '')
    data_str = f" ({data_conc})" if data_conc else ""
    last_contest_num = conc_num
    
    cols_dezenas = [c for c in df_historico.columns if any(t in str(c).lower() for t in ['bola', 'dezena', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14', 'd15']) and 'data' not in str(c).lower()][:15]
    col_bolas = cols_dezenas # Define a referência das colunas de dezenas para o resto do script
    
    if len(cols_dezenas) == 15:
        dezenas_ultimo = [f"{int(ultimo_registro[c]):02d}" for c in cols_dezenas]
        dezenas_texto = " - ".join(dezenas_ultimo)
        st.sidebar.info(
            f"📌 **Concurso Referência:** #{conc_num}{data_str}\n\n"
            f"🎯 **Dezenas:** `{dezenas_texto}`"
        )
    else:
        st.sidebar.info(f"📌 **Concurso Referência:** #{conc_num}{data_str}")

ultimo_sorteio = sorteios_historico_completos[-1] if sorteios_historico_completos else []

# =============================================================================
# CONFIGURAÇÃO DE FILTROS E JANELA (CORPO PRINCIPAL)
# =============================================================================
if df_historico is None or df_historico.empty:
    st.warning("⚠️ Aguardando carregamento dos dados para iniciar as análises.")
else:
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Escopo da Análise")
    total_concursos_base = len(df_historico)
    
    qtd_janela = st.sidebar.number_input(
        "Quantidade de concursos para recalibragem dos grupos:", 
        min_value=10, 
        max_value=total_concursos_base, 
        value=min(25, total_concursos_base), 
        step=5
    )
    
    st.info(f"📊 **Status da Base:** Concurso mais recente: **{last_contest_num}**. Análise calibrada usando os últimos **{qtd_janela}** concursos do histórico.")

    st.sidebar.header("⚙️ Configuração de Filtros Estatísticos")
    usar_soma = st.sidebar.checkbox("Filtro de Soma (160 - 220)", value=True)
    usar_repetidas = st.sidebar.checkbox("Filtro de Repetidas (8 a 11)", value=True)
    usar_moldura = st.sidebar.checkbox("Filtro de Moldura (8 a 11)", value=True)
    usar_primos = st.sidebar.checkbox("Filtro de Primos (4 a 7)", value=True)
    usar_mestras = st.sidebar.checkbox("Filtro de Mestras (5 a 8)", value=True)
    usar_impares = st.sidebar.checkbox("Filtro de Ímpares (6 a 9)", value=True)
    usar_sequencia = st.sidebar.checkbox("Filtro de Sequência Máx (3 a 7)", value=True)
    
    st.sidebar.markdown("---")
    usar_fixas = st.sidebar.checkbox("🔒 Ativar Dezenas Fixas (Obrigatórias em todos os jogos)", value=False)
    
    dezenas_fixas_selecionadas = []
    if usar_fixas:
        dezenas_fixas_selecionadas = st.sidebar.multiselect(
            "Selecione 1 ou 2 dezenas fixas absolutas (1 a 25):",
            options=list(range(1, 26)),
            max_selections=2,
            default=[]
        )

    min_aprovacoes = st.sidebar.slider("Mínimo de regras estatísticas atendidas:", min_value=1, max_value=7, value=5)

    # Dados da janela cortada
    last_janela_df = df_historico.iloc[-qtd_janela:].iloc[::-1]
    janela_concursos = [row[col_bolas].astype(int).tolist() for _, row in last_janela_df.iterrows()]

    # -----------------------------------------------------------------------------
    # SEÇÃO 1: RANKING DOS MELHORES GRUPOS
    # -----------------------------------------------------------------------------
    st.subheader("🏆 Ranking dos Melhores Grupos na Janela Selecionada")
    
    scores = {}
    last_janela_score_df = df_historico.iloc[-qtd_janela:]
    for g_name, nums in GRUPOS_ATIVOS.items():
        set_g = set(nums)
        c_14_15, c_13, total_hits = 0, 0, 0
        for _, row in last_janela_score_df.iterrows():
            draw = set(row[col_bolas].astype(int).values)
            hits = len(set_g.intersection(draw))
            total_hits += hits
            if hits >= 14: c_14_15 += 1
            elif hits == 13: c_13 += 1
        media = total_hits / qtd_janela
        score = (c_14_15 * 50) + (c_13 * 10) + (media * 5)
        scores[g_name] = {
            "Pontuação": round(score, 2),
            "Média Acertos": round(media, 2),
            "Acertos 14-15 pts": c_14_15,
            "Acertos 13 pts": c_13
        }

    df_ranking = pd.DataFrame.from_dict(scores, orient='index').sort_values(by="Pontuação", ascending=False)
    st.dataframe(df_ranking.head(10), use_container_width=True)

    top_5_names = df_ranking.head(5).index.tolist()

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # SEÇÃO 2: SELEÇÃO DE TRINCAS QUENTES & DEZENAS OBRIGATÓRIAS
    # -----------------------------------------------------------------------------
    st.subheader("🔥 Análise de Trincas Quentes (Conjuntos de 3 Dezenas Frequentes)")
    top_trincas_list = obter_top_trincas(janela_concursos, top_n=10)
    
    opcoes_trincas = ["Nenhuma trinca selecionada"] + [
        f"Trinca {list(t[0])} - Apareceu em {t[1]} dos últimos {qtd_janela} concursos" 
        for t in top_trincas_list
    ]
    
    trinca_escolhida_str = st.selectbox("Selecione uma Trinca para incluir obrigatoriamente nos palpites:", opcoes_trincas)
    
    dezenas_trinca = []
    if trinca_escolhida_str != "Nenhuma trinca selecionada":
        match_trinca = re.search(r'\[(\d+),\s*(\d+),\s*(\d+)\]', trinca_escolhida_str)
        if match_trinca:
            dezenas_trinca = [int(match_trinca.group(1)), int(match_trinca.group(2)), int(match_trinca.group(3))]

    dezenas_mais_atrasadas, mapa_atrasos = calcular_atrasos(janela_concursos)

    st.subheader("📌 Filtro: Dezenas Obrigatórias")
    modo_selecao = st.radio(
        "Como deseja escolher as dezenas obrigatórias?",
        ["Escolher manualmente", f"Sugestão por atraso (últimos {qtd_janela} concursos)"],
        horizontal=True
    )

    if modo_selecao == "Escolher manualmente":
        dezenas_selecionadas = st.multiselect(
            "Selecione a(s) dezena(s) que DEVE(M) estar nos jogos:",
            options=list(range(1, 26)),
            default=[]
        )
    else:
        opcoes_formatadas = [f"Dezena {d} ({mapa_atrasos[d]} concursos sem sair)" for d in dezenas_mais_atrasadas]
        selecao_formatada = st.multiselect(
            "Dezenas ordenadas pelo maior atraso:",
            options=opcoes_formatadas,
            default=opcoes_formatadas[:2]
        )
        dezenas_selecionadas = [int(item.split()[1]) for item in selecao_formatada]

    dezenas_obrigatorias_set = set(dezenas_selecionadas)
    dezenas_fixas_set = set(dezenas_fixas_selecionadas) if usar_fixas else set()
    dezenas_trinca_set = set(dezenas_trinca)
    
    todas_obrigatorias_absolutas = dezenas_obrigatorias_set.union(dezenas_fixas_set).union(dezenas_trinca_set)

    st.write(f"Dezenas Obrigatórias Finais (Incluindo Trinca/Fixas/Manuais): **{sorted(list(todas_obrigatorias_absolutas))}**")

    # -----------------------------------------------------------------------------
    # GERAÇÃO DE PALPITES
    # -----------------------------------------------------------------------------
    if st.button("Gerar Palpites", type="primary"):
        if len(todas_obrigatorias_absolutas) > 15:
            st.error(f"⚠️ Você selecionou {len(todas_obrigatorias_absolutas)} dezenas obrigatórias no total (unindo manuais, fixas e trinca), mas um jogo da Lotofácil tem no máximo 15 dezenas!")
        elif usar_fixas and not dezenas_fixas_selecionadas:
            st.error("⚠️ Você ativou a opção de Dezenas Fixas na barra lateral, mas não selecionou nenhuma!")
        else:
            prev_draw = set(df_historico.iloc[-1][col_bolas].astype(int).values)
            jogos_gerados = []
            
            for g_name in top_5_names:
                nums = GRUPOS_ATIVOS[g_name]
                set_g = set(nums)
                
                if not todas_obrigatorias_absolutas.issubset(set_g):
                    continue

                dezenas_disponiveis = sorted(list(set_g - todas_obrigatorias_absolutas))
                vagas_restantes = 15 - len(todas_obrigatorias_absolutas)
                
                if vagas_restantes < 0:
                    continue

                for comb_parcial in itertools.combinations(dezenas_disponiveis, vagas_restantes):
                    jogo_completo = sorted(list(comb_parcial) + list(todas_obrigatorias_absolutas))
                    
                    if validar_jogo_flexivel(
                        jogo_completo, prev_draw, 
                        usar_soma, usar_repetidas, usar_moldura, usar_primos, 
                        usar_mestras, usar_impares, usar_sequencia, min_aprovacoes
                    ):
                        jogos_gerados.append(jogo_completo)

            jogos_unicos = []
            vistos = set()
            for j in jogos_gerados:
                t = tuple(j)
                if t not in vistos:
                    vistos.add(t)
                    jogos_unicos.append(j)

            if jogos_unicos:
                amostra_jogos = random.sample(jogos_unicos, min(len(jogos_unicos), 20))
                st.session_state['jogos_gerados_atuais'] = amostra_jogos
                
                st.success(f"Grupos Quentes identificados na janela: {', '.join(top_5_names)}")
                st.write(f"Total de jogos válidos encontrados respeitando suas dezenas obrigatórias/trinca: **{len(jogos_unicos)}**")

                conteudo_txt = f"=== PALPITES CONCURSO {last_contest_num + 1} ===\n\n"
                for idx, jogo in enumerate(amostra_jogos, 1):
                    jogo_str = " ".join([f"{x:02d}" for x in jogo])
                    conteudo_txt += f"Jogo {idx:02d}: {jogo_str}\n"

                st.text_area("Jogos Gerados:", conteudo_txt, height=300)

                st.download_button(
                    label="Baixar TXT dos Jogos",
                    data=conteudo_txt,
                    file_name=f"palpites_concurso_{last_contest_num + 1}.txt",
                    mime="text/plain"
                )
            else:
                st.session_state['jogos_gerados_atuais'] = []
                st.error("⚠️ Nenhum jogo foi gerado. A quantidade de dezenas obrigatórias/trincas é muito restritiva para os Top 5 Grupos e filtros configurados.")

    # -----------------------------------------------------------------------------
    # CONFERÊNCIA HISTÓRICA
    # -----------------------------------------------------------------------------
    if 'jogos_gerados_atuais' in st.session_state and st.session_state['jogos_gerados_atuais']:
        st.markdown("---")
        st.subheader("🔍 Conferência Histórica dos Jogos Gerados")
        
        if st.button("🔎 Verificar Premiações no Histórico Completo"):
            premiacoes_encontradas = []
            
            for idx_jogo, jogo in enumerate(st.session_state['jogos_gerados_atuais'], start=1):
                set_jogo = set(jogo)
                for _, row in df_historico.iterrows():
                    sorteio_num = row.get('concurso', 'N/A')
                    sorteio_dezenas = set(row[col_bolas].astype(int).values)
                    acertos = len(set_jogo.intersection(sorteio_dezenas))
                    
                    if acertos >= 12:
                        tipo = "Doze (12 pts)" if acertos == 12 else ("Treze (13 pts)" if acertos == 13 else ("QUATORZE (14 pts)" if acertos == 14 else "QUINZE (15 pts)"))
                        premiacoes_encontradas.append({
                            "Jogo Gerado Nº": idx_jogo,
                            "Dezenas do Jogo": ", ".join(map(str, jogo)),
                            "Tipo de Prêmio": tipo,
                            "Concurso": sorteio_num,
                            "Dezenas Sorteadas": ", ".join(map(str, sorted(list(sorteio_dezenas))))
                        })

            if premiacoes_encontradas:
                df_premios = pd.DataFrame(premiacoes_encontradas)
                df_premios.index = df_premios.index + 1
                st.success(f"🎉 Foram encontradas **{len(premiacoes_encontradas)}** ocorrências de premiações históricas para os jogos gerados!")
                st.dataframe(df_premios, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum dos jogos gerados nesta rodada obteve 12, 13, 14 ou 15 acertos no histórico consultado.")
