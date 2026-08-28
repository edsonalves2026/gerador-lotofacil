import streamlit as st
import pandas as pd
import numpy as np
import itertools
from datetime import datetime
import random

# Configuração da página web
st.set_page_config(page_title="Gerador Lotofácil", page_icon="🎲", layout="wide")

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
# TÍTULO E INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
st.title("🎲 Gerador Otimizado Lotofácil")
st.write("Faça o upload da planilha atualizada para recalibrar os grupos estatísticos com base nos últimos 25 concursos reais.")

# Constantes e Grupos Originais
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

def seq_max(comb):
    max_c, curr_c = 1, 1
    for i in range(1, 15):
        if comb[i] == comb[i - 1] + 1:
            curr_c += 1
            if curr_c > max_c: max_c = curr_c
        else: curr_c = 1
    return max_c

def calcular_atrasos(resultados_25):
    atrasos = {}
    for dezena in range(1, 26):
        atraso = 0
        for concurso in resultados_25:
            if dezena in concurso:
                break
            atraso += 1
        atrasos[dezena] = atraso
    
    dezenas_ordenadas = sorted(atrasos.keys(), key=lambda d: atrasos[d], reverse=True)
    return dezenas_ordenadas, atrasos

# -----------------------------------------------------------------------------
# VALIDAÇÃO FLEXÍVEL CORRIGIDA
# -----------------------------------------------------------------------------
def validar_jogo_flexivel(comb, prev_draw, 
                          usar_soma, usar_repetidas, usar_moldura, usar_primos, 
                          usar_mestras, usar_impares, usar_sequencia, min_aprovacoes):
    acertos = 0
    j_set = set(comb)
    
    # 1. Soma
    if usar_soma and (160 <= sum(comb) <= 220):
        acertos += 1
        
    # 2. Repetidas
    if usar_repetidas and (len(j_set.intersection(prev_draw)) in [8, 9, 10, 11]):
        acertos += 1
        
    # 3. Moldura
    if usar_moldura and (len(j_set.intersection(MOLDURA)) in [8, 9, 10, 11]):
        acertos += 1
        
    # 4. Primos
    if usar_primos and (len(j_set.intersection(PRIMOS)) in [4, 5, 6, 7]):
        acertos += 1
        
    # 5. Mestras
    if usar_mestras and (len(j_set.intersection(MESTRAS)) in [5, 6, 7, 8]):
        acertos += 1
        
    # 6. Ímpares
    if usar_impares and (sum(1 for x in comb if x % 2 != 0) in [6, 7, 8, 9]):
        acertos += 1
        
    # 7. Sequência Máxima
    if usar_sequencia and (seq_max(comb) in [3, 4, 5, 6, 7]):
        acertos += 1

    return acertos >= min_aprovacoes

# -----------------------------------------------------------------------------
# UPLOAD DA PLANILHA E BARRA LATERAL
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("📂 Faça o upload da planilha Excel atualizada (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name='LOTOFÁCIL')
    col_bolas = [f'Bola{i}' for i in range(1, 16)]

    last_contest_row = df.iloc[-1]
    last_contest_num = int(last_contest_row.iloc[0]) if 'Concurso' in df.columns or len(df.columns) > 0 else len(df)
    
    st.info(f"📊 **Status da Planilha:** Último concurso registrado na base: **Concurso {last_contest_num}**. Análise calibrada usando os últimos 25 concursos do arquivo.")

    st.sidebar.header("⚙️ Configuração de Filtros Estatísticos")
    st.sidebar.write("Ative os filtros desejados e defina o rigor:")
    
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

    total_filtros_possiveis = 7
    min_aprovacoes = st.sidebar.slider("Mínimo de regras estatísticas atendidas:", min_value=1, max_value=total_filtros_possiveis, value=5)

    last_25_df = df.iloc[-25:].iloc[::-1] 
    ultimos_25_concursos = []
    for _, row in last_25_df.iterrows():
        concurso_lista = row[col_bolas].astype(int).tolist()
        ultimos_25_concursos.append(concurso_lista)

    dezenas_mais_atrasadas, mapa_atrasos = calcular_atrasos(ultimos_25_concursos)

    st.subheader("Filtro: Dezenas Obrigatórias (Devem estar em 100% dos jogos)")
    modo_selecao = st.radio(
        "Como deseja escolher as dezenas obrigatórias?",
        ["Escolher manualmente", "Sugestão por atraso (últimos 25 concursos da planilha)"],
        horizontal=True
    )

    if modo_selecao == "Escolher manualmente":
        dezenas_selecionadas = st.multiselect(
            "Selecione a(s) dezena(s) que DEVE(M) obrigatoriamente estar em todos os jogos gerados:",
            options=list(range(1, 26)),
            default=[]
        )
    else:
        opcoes_formatadas = [f"Dezena {d} ({mapa_atrasos[d]} concursos sem sair nos últimos 25)" for d in dezenas_mais_atrasadas]
        
        selecao_formatada = st.multiselect(
            "Dezenas ordenadas pelo maior atraso:",
            options=opcoes_formatadas,
            default=opcoes_formatadas[:2]
        )
        
        dezenas_selecionadas = [int(item.split()[1]) for item in selecao_formatada]

    st.write(f"Dezenas Obrigatórias selecionadas: **{dezenas_selecionadas}**")
    if usar_fixas and dezenas_fixas_selecionadas:
        st.write(f"🔒 **Dezenas Fixas Extras:** {dezenas_fixas_selecionadas}")

    dezenas_obrigatorias_set = set(dezenas_selecionadas)
    dezenas_fixas_set = set(dezenas_fixas_selecionadas) if usar_fixas else set()
    
    # Junta todas as dezenas que são obrigatórias/fixas de forma absoluta
    todas_obrigatorias_absolutas = dezenas_obrigatorias_set.union(dezenas_fixas_set)

    if st.button("Gerar Palpites"):
        # Validação preventiva
        if len(todas_obrigatorias_absolutas) > 15:
            st.error(f"⚠️ Você selecionou {len(todas_obrigatorias_absolutas)} dezenas obrigatórias/fixas no total, mas um jogo da Lotofácil tem no máximo 15 dezenas! Reduza a quantidade.")
        elif usar_fixas and not dezenas_fixas_selecionadas:
            st.error("⚠️ Você ativou a opção de Dezenas Fixas na barra lateral, mas não selecionou nenhuma!")
        else:
            prev_draw = set(last_contest_row[col_bolas].astype(int).values)

            # 1. Avalia os Top 5 Grupos baseados nos últimos 25 concursos
            scores = {}
            last_25_score_df = df.iloc[-25:]
            for g_name, nums in GRUPOS_56.items():
                set_g = set(nums)
                c_14_15, c_13, total_hits = 0, 0, 0
                for _, row in last_25_score_df.iterrows():
                    draw = set(row[col_bolas].astype(int).values)
                    hits = len(set_g.intersection(draw))
                    total_hits += hits
                    if hits >= 14: c_14_15 += 1
                    elif hits == 13: c_13 += 1
                media = total_hits / 25
                score = (c_14_15 * 50) + (c_13 * 10) + (media * 5)
                scores[g_name] = (score, c_14_15, c_13, media)

            top_5_groups = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)[:5]
            top_5_names = [g[0] for g in top_5_groups]

            jogos_gerados = []
            
            # 2. Gera as combinações dentro dos melhores grupos garantindo as regras obrigatórias na raiz
            for g_name in top_5_names:
                nums = GRUPOS_56[g_name]
                set_g = set(nums)
                
                # VERIFICAÇÃO DE SEGURANÇA: As dezenas obrigatórias precisam pertencer aos 20 números do grupo
                if not todas_obrigatorias_absolutas.issubset(set_g):
                    # Se o grupo não contiver todas as dezenas obrigatórias escolhidas, ele pula este grupo para evitar jogos vazios
                    continue

                # Remove as obrigatórias da lista de escolha e calcula quantas faltam para completar 15
                dezenas_disponiveis = sorted(list(set_g - todas_obrigatorias_absolutas))
                vagas_restantes = 15 - len(todas_obrigatorias_absolutas)
                
                if vagas_restantes < 0:
                    continue

                # Cria combinações apenas com as vagas restantes somadas às dezenas obrigatórias fixas
                for comb_parcial in itertools.combinations(dezenas_disponiveis, vagas_restantes):
                    jogo_completo = sorted(list(comb_parcial) + list(todas_obrigatorias_absolutas))
                    
                    # Valida se o jogo atende aos filtros estatísticos selecionados no slider
                    if validar_jogo_flexivel(
                        jogo_completo, prev_draw, 
                        usar_soma, usar_repetidas, usar_moldura, usar_primos, 
                        usar_mestras, usar_impares, usar_sequencia, min_aprovacoes
                    ):
                        jogos_gerados.append(jogo_completo)

            # Remove duplicadas caso apareçam em grupos diferentes
            jogos_unicos = []
            vistos = set()
            for j in jogos_gerados:
                t = tuple(j)
                if t not in vistos:
                    vistos.add(t)
                    jogos_unicos.append(j)

            if jogos_unicos:
                # Seleciona até 20 jogos aleatórios dos válidos encontrados
                amostra_jogos = random.sample(jogos_unicos, min(len(jogos_unicos), 20))
                
                st.success(f"Grupos Quentes identificados na planilha: {', '.join(top_5_names)}")
                st.write(f"Total de jogos válidos encontrados respeitando suas dezenas obrigatórias: **{len(jogos_unicos)}**")

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
                st.error("⚠️ Nenhum jogo foi gerado. Isso ocorre porque a quantidade de dezenas obrigatórias/fixas selecionadas é muito alta ou restritiva demais para os Top 5 Grupos estatísticos atuais. Tente desmarcar algumas dezenas ou flexibilizar os filtros.")
else:
    st.warning("⚠️ Por favor, faça o upload da sua planilha Excel (.xlsx) da Lotofácil para habilitar a geração de palpites e o cálculo estatístico.")
