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
# WEB SCRAPING & CARREGAMENTO DE DADOS ONLINE
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
# MATRIZES DE GRUPOS
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

# -----------------------------------------------------------------------------
# SELEÇÃO DINÂMICA DA MATRIZ NA BARRA LATERAL
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Seleção de Matriz de Grupos")
opcao_matriz = st.sidebar.selectbox(
    "Escolha o conjunto de grupos:",
    ["24 Grupos (19 dezenas)", "56 Grupos (20 dezenas)", "69 Grupos (22 dezenas)"]
)

if "24" in opcao_matriz:
    GRUPOS_ATIVOS = GRUPOS_24
elif "56" in opcao_matriz:
    GRUPOS_ATIVOS = GRUPOS_56
else:
    GRUPOS_ATIVOS = GRUPOS_69

MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
MESTRAS = {1, 2, 3, 5, 9, 10, 11, 13, 20, 25}

# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES DE CÁLCULO
# -----------------------------------------------------------------------------
def seq_max(comb):
    max_c, curr_c = 1, 1
    for i in range(1, 15):
        if comb[i] == comb[i - 1] + 1:
            curr_c += 1
            if curr_c > max_c: max_c = curr_c
        else: curr_c = 1
    return max_c

def calcular_atrasos(resultados_janela):
    atrasos = {}
    for dezena in range(1, 26):
        atraso = 0
        for concurso in resultados_janela:
            if dezena in concurso:
                break
            atraso += 1
        atrasos[dezena] = atraso
    
    dezenas_ordenadas = sorted(atrasos.keys(), key=lambda d: atrasos[d], reverse=True)
    return dezenas_ordenadas, atrasos

def obter_top_trincas_matriz(resultados_janela, dezenas_matriz, top_n=10):
    contador_trincas = Counter()
    dezenas_set = set(dezenas_matriz)
    for concurso in resultados_janela:
        # Considera apenas as dezenas presentas na matriz ativa
        dezenas_filtradas = sorted(list(set(concurso).intersection(dezenas_set)))
        for trinca in itertools.combinations(dezenas_filtradas, 3):
            contador_trincas[trinca] += 1
    return contador_trincas.most_common(top_n)

def validar_jogo_flexivel(comb, prev_draw, 
                           usar_soma, usar_repetidas, usar_moldura, usar_primos, 
                           usar_mestras, usar_impares, usar_sequencia, min_aprovacoes):
    acertos = 0
    j_set = set(comb)
    
    if usar_soma and (160 <= sum(comb) <= 220): acertos += 1
    if usar_repetidas and (len(j_set.intersection(prev_draw)) in [8, 9, 10, 11]): acertos += 1
    if usar_moldura and (len(j_set.intersection(MOLDURA)) in [8, 9, 10, 11]): acertos += 1
    if usar_primos and (len(j_set.intersection(PRIMOS)) in [4, 5, 6, 7]): acertos += 1
    if usar_mestras and (len(j_set.intersection(MESTRAS)) in [5, 6, 7, 8]): acertos += 1
    if usar_impares and (sum(1 for x in comb if x % 2 != 0) in [6, 7, 8, 9]): acertos += 1
    if usar_sequencia and (seq_max(comb) in [3, 4, 5, 6, 7]): acertos += 1

    return acertos >= min_aprovacoes

# -----------------------------------------------------------------------------
# BARRA LATERAL: BASE HISTÓRICA E MODO DE OPERAÇÃO
# -----------------------------------------------------------------------------
st.title("🎲 Gerador Otimizado Lotofácil Analytics Pro")

st.sidebar.markdown("---")
st.sidebar.header("📁 Base Histórica de Dados")

modo_base = st.sidebar.radio(
    "Seletor de Modo:",
    options=["🌐 Conectado Online", "📂 Modo Offline (Planilha Excel / CSV)"],
    index=0
)

df_historico_raw = None

if "Online" in modo_base:
    df_historico_raw = carregar_dados_online()
    if df_historico_raw is not None and not df_historico_raw.empty:
        st.sidebar.success("🌐 Conectado online (`asloterias.com.br`)")
    else:
        st.sidebar.error("⚠️ Falha ao conectar online. Carregue uma planilha no Modo Offline.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload manual de planilha (.xlsx / .csv)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_historico_raw = pd.read_csv(uploaded_file)
            else:
                df_historico_raw = pd.read_excel(uploaded_file, sheet_name='LOTOFÁCIL' if 'LOTOFÁCIL' in pd.ExcelFile(uploaded_file).sheet_names else 0)
            st.sidebar.success("📂 Planilha carregada com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar planilha: {e}")
    else:
        st.sidebar.info("📌 Aguardando envio de arquivo no Modo Offline...")

# -----------------------------------------------------------------------------
# SELEÇÃO DO CONCURSO BASE E FILTRAGEM
# -----------------------------------------------------------------------------
if df_historico_raw is not None and not df_historico_raw.empty:
    col_conc = next((c for c in df_historico_raw.columns if 'concurso' in str(c).lower()), df_historico_raw.columns[0])
    df_historico_raw = df_historico_raw.sort_values(by=col_conc, ascending=True).reset_index(drop=True)
    
    if "Offline" in modo_base:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Seleção do Concurso Alvo (Offline)")
        
        opcoes_concursos = []
        for _, row in df_historico_raw.iterrows():
            c_num = int(row[col_conc])
            c_data = str(row.get('data', ''))
            label_data = f" ({c_data})" if c_data and c_data != 'nan' else ""
            opcoes_concursos.append(f"Concurso: #{c_num}{label_data}")
        
        opcoes_concursos = opcoes_concursos[::-1]
        
        escolha_concurso_str = st.sidebar.selectbox("Escolha o concurso de referência:", options=opcoes_concursos)
        concurso_alvo_num = int(re.search(r'#(\d+)', escolha_concurso_str).group(1))
        
        df_historico = df_historico_raw[df_historico_raw[col_conc].astype(int) <= concurso_alvo_num].copy()
    else:
        df_historico = df_historico_raw.copy()

    col_bolas = [c for c in df_historico.columns if any(t in str(c).lower() for t in ['bola', 'dezena', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14','d15']) and 'data' not in str(c).lower()][:15]

    ultimo_registro = df_historico.iloc[-1]
    last_contest_num = int(ultimo_registro[col_conc])
    data_conc = str(ultimo_registro.get('data', ''))
    data_str = f" ({data_conc})" if data_conc and data_conc != 'nan' else ""

    if len(col_bolas) == 15:
        dezenas_ultimo = [f"{int(ultimo_registro[c]):02d}" for c in col_bolas]
        dezenas_texto = " - ".join(dezenas_ultimo)
        st.sidebar.info(
            f"📌 **Último Concurso Ref.:** #{last_contest_num}{data_str}\n\n"
            f"🎯 **Dezenas:** `{dezenas_texto}`"
        )

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
    
    st.info(f"📊 **Status da Base:** Concurso de referência ativo: **#{last_contest_num}**. Análise calibrada usando os últimos **{qtd_janela}** concursos a partir dessa referência.")

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

    last_janela_df = df_historico.iloc[-qtd_janela:].iloc[::-1]
    janela_concursos = [row[col_bolas].astype(int).tolist() for _, row in last_janela_df.iterrows()]
    prev_draw = set(janela_concursos[0])

    # -------------------------------------------------------------------------
    # PAINEL DE ANÁLISE HISTÓRICA E GERADOR
    # -------------------------------------------------------------------------
    tab_gerador, tab_estatisticas = st.tabs(["🚀 Gerador Otimizado", "📈 Análise Estatística"])

    # Obter universo de dezenas cobertas pela matriz ativa
    dezenas_matriz_ativa = list(set(d for g in GRUPOS_ATIVOS.values() for d in g))

    with tab_estatisticas:
        st.subheader("📊 Frequência e Atraso das Dezenas")
        dezenas_ordenadas_atraso, mapa_atrasos = calcular_atrasos(janela_concursos)
        
        freq_dezenas = Counter(d for conc in janela_concursos for d in conc)
        df_freq = pd.DataFrame([
            {"Dezena": f"{d:02d}", "Frequência": freq_dezenas[d], "Atraso Atual": mapa_atrasos[d]}
            for d in range(1, 26)
        ])
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("**Frequência na Janela Escolhida**")
            st.dataframe(df_freq.sort_values(by="Frequência", ascending=False), use_container_width=True, hide_index=True)
        
        with col_e2:
            st.markdown("**Maiores Atrasos**")
            st.dataframe(df_freq.sort_values(by="Atraso Atual", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader(f"🔥 Top Trincas Mais Frequentes ({opcao_matriz})")
        
        # Ajuste 1: As trincas agora consideram estritamente o universo de dezenas da matriz ativa
        top_trincas = obter_top_trincas_matriz(janela_concursos, dezenas_matriz_ativa)
        df_trincas = pd.DataFrame([
            {"Trinca": f"{t[0]:02d} - {t[1]:02d} - {t[2]:02d}", "Ocorrências": occ}
            for t, occ in top_trincas
        ])
        st.dataframe(df_trincas, use_container_width=True, hide_index=True)

    with tab_gerador:
        st.subheader("🎯 Parâmetros de Geração")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            qtd_jogos = st.number_input("Quantidade de jogos a gerar:", min_value=1, max_value=500, value=10, step=1)
        with col_p2:
            # Ajuste 2: Adicionada opção de gerar via Top Trincas Frequentes
            modo_geracao = st.radio(
                "Método de Seleção dos Grupos / Otimização:",
                [
                    "Melhores Desempenhos no Histórico", 
                    "Otimizado por Top Trincas Frequentes",
                    "Aleatório Controlado"
                ]
            )

        if st.button("✨ Gerar Apostas Otimizadas", type="primary"):
            score_grupos = {}
            for g_nome, g_dezenas in GRUPOS_ATIVOS.items():
                g_set = set(g_dezenas)
                acertos_totais = sum(len(g_set.intersection(conc)) for conc in janela_concursos)
                score_grupos[g_nome] = acertos_totais

            grupos_ordenados = sorted(score_grupos.keys(), key=lambda g: score_grupos[g], reverse=True)
            top_trincas_lista = [t[0] for t in obter_top_trincas_matriz(janela_concursos, dezenas_matriz_ativa, top_n=5)]

            jogos_gerados = []
            info_grupos_origem = []
            tentativas_max = 50000
            tentativa = 0

            while len(jogos_gerados) < qtd_jogos and tentativa < tentativas_max:
                tentativa += 1
                
                if modo_geracao == "Melhores Desempenhos no Histórico":
                    grupo_escolhido = random.choice(grupos_ordenados[:10])
                elif modo_geracao == "Otimizado por Top Trincas Frequentes":
                    # Seleciona grupos que contenham pelo menos uma das trincas mais fortes
                    trinca_alvo = set(random.choice(top_trincas_lista))
                    grupos_com_trinca = [g for g, dezenas in GRUPOS_ATIVOS.items() if trinca_alvo.issubset(set(dezenas))]
                    grupo_escolhido = random.choice(grupos_com_trinca) if grupos_com_trinca else random.choice(grupos_ordenados)
                else:
                    grupo_escolhido = random.choice(list(GRUPOS_ATIVOS.keys()))

                dezenas_grupo = GRUPOS_ATIVOS[grupo_escolhido]
                
                if usar_fixas and dezenas_fixas_selecionadas:
                    if not all(d in dezenas_grupo for d in dezenas_fixas_selecionadas):
                        continue
                    restantes = [d for d in dezenas_grupo if d not in dezenas_fixas_selecionadas]
                    comb_restante = random.sample(restantes, 15 - len(dezenas_fixas_selecionadas))
                    comb = sorted(dezenas_fixas_selecionadas + comb_restante)
                else:
                    comb = sorted(random.sample(dezenas_grupo, 15))

                if comb in jogos_gerados:
                    continue

                if validar_jogo_flexivel(comb, prev_draw, usar_soma, usar_repetidas, 
                                         usar_moldura, usar_primos, usar_mestras, 
                                         usar_impares, usar_sequencia, min_aprovacoes):
                    jogos_gerados.append(comb)
                    info_grupos_origem.append(grupo_escolhido)

            # Salva na sessão para ser consumido na Conferência Histórica
            st.session_state['jogos_gerados_atuais'] = jogos_gerados
            st.session_state['jogos_gerados_grupos'] = info_grupos_origem

            if len(jogos_gerados) < qtd_jogos:
                st.warning(f"⚠️ Foram gerados {len(jogos_gerados)} jogos atendendo aos critérios flexíveis dentro do limite de buscas.")
            else:
                st.success(f"✅ {len(jogos_gerados)} jogos gerados com sucesso!")

        # Exibição dos Jogos Gerados
        if 'jogos_gerados_atuais' in st.session_state and st.session_state['jogos_gerados_atuais']:
            jogos_atuais = st.session_state['jogos_gerados_atuais']
            grupos_atuais = st.session_state.get('jogos_gerados_grupos', ['N/A'] * len(jogos_atuais))

            df_jogos = pd.DataFrame([
                {
                    "Jogo": f"Jogo {i+1:02d}",
                    "Grupo Origem": grupos_atuais[i],  # Ajuste 2: Nome do Grupo adicionado na tabela
                    "Dezenas": " - ".join([f"{d:02d}" for d in jogo]),
                    "Soma": sum(jogo),
                    "Repetidas": len(set(jogo).intersection(prev_draw)),
                    "Moldura": len(set(jogo).intersection(MOLDURA)),
                    "Primos": len(set(jogo).intersection(PRIMOS)),
                    "Ímpares": sum(1 for x in jogo if x % 2 != 0),
                    "Seq. Máx": seq_max(jogo)
                }
                for i, jogo in enumerate(jogos_atuais)
            ])

            st.dataframe(df_jogos, use_container_width=True, hide_index=True)

            texto_exportacao = "\n".join([" ".join([f"{d:02d}" for d in jogo]) for jogo in jogos_atuais])
            st.download_button(
                label="📥 Baixar Jogos (.txt)",
                data=texto_exportacao,
                file_name=f"jogos_lotofacil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        # -----------------------------------------------------------------------------
        # Ajuste 3: CONFERÊNCIA HISTÓRICA DOS JOGOS GERADOS INTEGRADA
        # -----------------------------------------------------------------------------
        if 'jogos_gerados_atuais' in st.session_state and st.session_state['jogos_gerados_atuais']:
            st.markdown("---")
            st.subheader("🔍 Conferência Histórica dos Jogos Gerados")
            
            if st.button("🔎 Verificar Premiações no Histórico Completo"):
                premiacoes_encontradas = []
                
                for idx_jogo, jogo in enumerate(st.session_state['jogos_gerados_atuais'], start=1):
                    set_jogo = set(jogo)
                    for _, row in df_historico.iterrows():
                        sorteio_num = row.get(col_conc, 'N/A')
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
else:
    st.info("👈 Selecione o Modo Conectado Online ou faça o upload de uma planilha no Modo Offline para iniciar.")
