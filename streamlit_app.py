import streamlit as st
import pandas as pd
import numpy as np
import itertools
import random

# Configuração da página web
st.set_page_config(page_title="Gerador Lotofácil Otimizado", page_icon="🎲", layout="wide")

st.title("🎲 Gerador Otimizado Lotofácil")
st.write("Faça o upload da planilha atualizada, ajuste os filtros na barra lateral e gere os palpites otimizados.")

# --- CONSTANTES E GRUPOS ---
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

MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
MESTRAS = {1, 2, 3, 5, 9, 10, 11, 13, 20, 25}
DEZENAS_OBRIGATORIAS = {18}

# --- PAINEL LATERAL (CONFIGURAÇÃO DE FILTROS) ---
st.sidebar.header("⚙️ Painel de Controle dos Filtros")

usar_soma = st.sidebar.checkbox("Filtro: Soma Total (180 a 210)", value=True)
usar_repetidas = st.sidebar.checkbox("Filtro: Repetidas Concurso Anterior (9 ou 10)", value=True)
usar_moldura = st.sidebar.checkbox("Filtro: Dezenas na Moldura (9 ou 10)", value=True)
usar_primos = st.sidebar.checkbox("Filtro: Dezenas Primas (5 ou 6)", value=True)
usar_impares = st.sidebar.checkbox("Filtro: Dezenas Ímpares (7 ou 8)", value=True)
usar_sequencia = st.sidebar.checkbox("Filtro: Sequência Máxima (4 ou 5)", value=True)
usar_obrig = st.sidebar.checkbox("Filtro: Dezena Obrigatória (18)", value=True)

# Total de filtros ativos
filtros_ativos = sum([usar_soma, usar_repetidas, usar_moldura, usar_primos, usar_impares, usar_sequencia, usar_obrig])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Tolerância a Falhas")

# Define o mínimo de aprovações aceitáveis
min_aprovacoes = st.sidebar.slider(
    "Mínimo de Filtros Exigidos:",
    min_value=1,
    max_value=max(1, filtros_ativos),
    value=max(1, filtros_ativos)
)

# --- FUNÇÕES DE LÓGICA OTIMIZADAS ---
def seq_max(comb):
    max_c, curr_c = 1, 1
    for i in range(1, 15):
        if comb[i] == comb[i - 1] + 1:
            curr_c += 1
            if curr_c > max_c:
                max_c = curr_c
        else:
            curr_c = 1
    return max_c

def validar_jogo_flexivel(comb, prev_draw, set_grupo):
    acertos = 0
    j_set = set(comb)
    
    # Check 1: Soma
    if usar_soma and (180 <= sum(comb) <= 210):
        acertos += 1
        
    # Check 2: Repetidas
    if usar_repetidas and (len(j_set.intersection(prev_draw)) in [9, 10]):
        acertos += 1
        
    # Check 3: Moldura
    if usar_moldura and (len(j_set.intersection(MOLDURA)) in [9, 10]):
        acertos += 1
        
    # Check 4: Primos
    if usar_primos and (len(j_set.intersection(PRIMOS)) in [5, 6]):
        acertos += 1
        
    # Check 5: Ímpares
    if usar_impares and (sum(1 for x in comb if x % 2 != 0) in [7, 8]):
        acertos += 1
        
    # Check 6: Sequência Máxima
    if usar_sequencia and (seq_max(comb) in [4, 5]):
        acertos += 1
        
    # Check 7: Dezena Obrigatória
    if usar_obrig:
        obrig = DEZENAS_OBRIGATORIAS.intersection(set_grupo)
        if not obrig or obrig.issubset(j_set):
            acertos += 1

    return acertos >= min_aprovacoes

# --- INTERFACE E PROCESSAMENTO ---
uploaded_file = st.file_uploader("Selecione a planilha Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Gerar Palpites Otimizados"):
        try:
            df = pd.read_excel(uploaded_file, sheet_name='LOTOFÁCIL')
            col_bolas = [f'Bola{i}' for i in range(1, 16)]

            last_25 = df.iloc[-25:]
            last_contest_row = df.iloc[-1]
            last_contest_num = int(last_contest_row.iloc[0]) if 'Concurso' in df.columns else len(df)
            prev_draw = set(last_contest_row[col_bolas].astype(int).values)

            scores = {}
            for g_name, nums in GRUPOS_56.items():
                set_g = set(nums)
                c_14_15, c_13, total_hits = 0, 0, 0
                for _, row in last_25.iterrows():
                    draw = set(row[col_bolas].astype(int).values)
                    hits = len(set_g.intersection(draw))
                    total_hits += hits
                    if hits >= 14:
                        c_14_15 += 1
                    elif hits == 13:
                        c_13 += 1
                media = total_hits / 25
                score = (c_14_15 * 50) + (c_13 * 10) + (media * 5)
                scores[g_name] = (score, c_14_15, c_13, media)

            top_5_groups = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)[:5]
            top_5_names = [g[0] for g in top_5_groups]

            jogos_gerados = []
            for g_name in top_5_names:
                nums = GRUPOS_56[g_name]
                set_g = set(nums)
                sorted_g = sorted(nums)
                
                validos = [c for c in itertools.combinations(sorted_g, 15) if validar_jogo_flexivel(c, prev_draw, set_g)]
                
                if validos:
                    jogos_gerados.extend(random.sample(validos, min(len(validos), 4)))

            st.success(f"Grupos Quentes Selecionados: {', '.join(top_5_names)}")

            if jogos_gerados:
                conteudo_txt = f"=== PALPITES CONCURSO {last_contest_num + 1} ===\n\n"
                for idx, jogo in enumerate(jogos_gerados, 1):
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
                st.warning("⚠️ Nenhum jogo atendeu aos critérios mínimos solicitados. Tente reduzir o 'Mínimo de Filtros Exigidos' na barra lateral.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
