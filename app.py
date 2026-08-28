import streamlit as st
import pandas as pd

# ==========================================
# 0. AUTENTICAÇÃO E SEGURANÇA DE ACESSO
# ==========================================
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔒 Acesso Restrito")
        senha_input = st.text_input("Digite a senha de acesso:", type="password")
        
        if st.button("Entrar"):
            # Verifica a senha configurada no secrets do Streamlit (.streamlit/secrets.toml)
            if "senha" in st.secrets and senha_input == st.secrets["senha"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("🔑 Senha incorreta. Tente novamente.")
        return False
    return True

# Bloqueia a execução do aplicativo caso o usuário não esteja autenticado
if not verificar_senha():
    st.stop()

# ==========================================
# 1. MATRIZ DE GRUPOS E CONJUNTOS NUMÉRICOS
# ==========================================
GRUPOS_56 = [
    [1, 2, 3, 4, 18, 19, 20, 21, 22, 23], [1, 2, 3, 4, 18, 19, 22, 23, 24, 25],
    [1, 2, 3, 5, 18, 19, 20, 21, 24, 25], [1, 2, 4, 5, 18, 19, 20, 21, 22, 24],
    [1, 2, 4, 5, 18, 19, 21, 23, 24, 25], [1, 3, 4, 5, 18, 19, 20, 22, 23, 25],
    [1, 3, 4, 5, 18, 19, 21, 22, 24, 25], [2, 3, 4, 5, 18, 19, 20, 23, 24, 25],
    [6, 7, 8, 9, 18, 19, 20, 21, 22, 23], [6, 7, 8, 9, 18, 19, 22, 23, 24, 25],
    [6, 7, 8, 10, 18, 19, 20, 21, 24, 25], [6, 7, 9, 10, 18, 19, 20, 21, 22, 24],
    [6, 7, 9, 10, 18, 19, 21, 23, 24, 25], [6, 8, 9, 10, 18, 19, 20, 22, 23, 25],
    [6, 8, 9, 10, 18, 19, 21, 22, 24, 25], [7, 8, 9, 10, 18, 19, 20, 23, 24, 25],
    [11, 12, 13, 14, 18, 19, 20, 21, 22, 23], [11, 12, 13, 14, 18, 19, 22, 23, 24, 25],
    [11, 12, 13, 15, 18, 19, 20, 21, 24, 25], [11, 12, 14, 15, 18, 19, 20, 21, 22, 24],
    [11, 12, 14, 15, 18, 19, 21, 23, 24, 25], [11, 13, 14, 15, 18, 19, 20, 22, 23, 25],
    [11, 13, 14, 15, 18, 19, 21, 22, 24, 25], [12, 13, 14, 15, 18, 19, 20, 23, 24, 25],
    [16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [1, 2, 6, 7, 11, 12, 16, 17, 18, 19],
    [1, 2, 6, 7, 13, 14, 16, 17, 20, 21], [1, 2, 8, 9, 11, 12, 16, 17, 22, 23],
    [1, 2, 8, 9, 13, 14, 16, 17, 24, 25], [3, 4, 6, 7, 11, 12, 16, 17, 24, 25],
    [3, 4, 6, 7, 13, 14, 16, 17, 22, 23], [3, 4, 8, 9, 11, 12, 16, 17, 20, 21],
    [3, 4, 8, 9, 13, 14, 16, 17, 18, 19], [1, 3, 6, 8, 11, 13, 16, 18, 20, 22],
    [1, 3, 6, 8, 12, 14, 17, 19, 21, 23], [1, 3, 7, 9, 11, 13, 17, 19, 24, 25],
    [1, 3, 7, 9, 12, 14, 16, 18, 22, 23], [2, 4, 6, 8, 11, 13, 17, 19, 23, 25],
    [2, 4, 6, 8, 12, 14, 16, 18, 21, 24], [2, 4, 7, 9, 11, 13, 16, 18, 20, 22],
    [2, 4, 7, 9, 12, 14, 17, 19, 21, 25], [1, 5, 6, 10, 11, 15, 16, 20, 24, 25],
    [1, 5, 6, 10, 12, 13, 17, 18, 21, 22], [1, 5, 7, 8, 11, 15, 17, 19, 22, 23],
    [1, 5, 7, 8, 12, 13, 16, 20, 21, 25], [2, 3, 6, 10, 11, 15, 17, 19, 21, 23],
    [2, 3, 6, 10, 12, 13, 16, 20, 22, 24], [2, 3, 7, 8, 11, 15, 16, 18, 24, 25],
    [2, 3, 7, 8, 12, 13, 17, 19, 20, 22], [4, 5, 8, 10, 13, 15, 16, 18, 21, 25],
    [4, 5, 8, 10, 12, 14, 17, 19, 20, 23], [4, 5, 9, 10, 11, 14, 16, 20, 22, 24],
    [4, 5, 9, 10, 12, 15, 17, 18, 21, 23], [2, 5, 7, 10, 13, 14, 16, 19, 21, 25],
    [2, 5, 7, 10, 11, 12, 17, 18, 22, 24], [3, 5, 6, 9, 13, 14, 17, 18, 20, 23]
]

PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
PARES = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24}

# ==========================================
# 2. FUNÇÃO DE RANKING DE GRUPOS
# ==========================================
def calcular_ranking_grupos(jogos):
    contagem_grupos = {i: 0 for i in range(len(GRUPOS_56))}
    for jogo in jogos:
        set_jogo = set(jogo)
        for idx, grupo in enumerate(GRUPOS_56):
            if len(set_jogo.intersection(grupo)) >= 6:
                contagem_grupos[idx] += 1
    
    ranking = sorted(contagem_grupos.items(), key=lambda x: x[1], reverse=True)
    return ranking

# ==========================================
# 3. INTERFACE PRINCIPAL DO STREAMLIT
# ==========================================
st.title("🎯 Validador e Filtrador de Jogos - Lotofácil")
st.markdown("---")

# Barra Lateral - Configuração dos 7 Filtros Flexíveis
st.sidebar.header("⚙️ Configuração dos Filtros")

usar_obrig = st.sidebar.checkbox("Dezena 18 Obrigatória", value=True)
usar_primos = st.sidebar.checkbox("Primos (5 a 7)", value=True)
usar_fibo = st.sidebar.checkbox("Fibonacci (3 a 5)", value=True)
usar_moldura = st.sidebar.checkbox("Moldura (8 a 11)", value=True)
usar_pares = st.sidebar.checkbox("Pares (6 a 8)", value=True)
usar_soma = st.sidebar.checkbox("Soma Total (180 a 220)", value=True)
usar_grupos = st.sidebar.checkbox("Ranking de Grupos (Min. 6 acertos)", value=True)

# Contagem dinâmica de filtros ativos
filtros_ativos = sum([
    usar_obrig, usar_primos, usar_fibo, 
    usar_moldura, usar_pares, usar_soma, usar_grupos
])

st.sidebar.markdown("---")

if filtros_ativos > 0:
    min_filtros = st.sidebar.slider(
        "Mínimo de Filtros Exigidos:", 
        min_value=1, 
        max_value=filtros_ativos, 
        value=filtros_ativos
    )
else:
    min_filtros = 0
    st.sidebar.warning("Nenhum filtro está ativo.")

# ==========================================
# 4. CARREGAMENTO E PROCESSAMENTO DO ARQUIVO
# ==========================================
arquivo = st.file_uploader("Envie sua planilha Excel (.xlsx)", type=["xlsx"])

if arquivo is not None:
    # TRATAMENTO DE ERROS AMIGÁVEL (TRY / EXCEPT)
    try:
        df = pd.read_excel(arquivo, header=None)
        jogos_raw = df.values.tolist()
        
        jogos_validos = []
        for linha in jogos_raw:
            jogo = [int(x) for x in linha if pd.notna(x) and str(x).isdigit()]
            if len(jogo) == 15:
                jogos_validos.append(jogo)

        if not jogos_validos:
            st.error("❌ Nenhum jogo válido com 15 dezenas foi encontrado na planilha.")
        else:
            st.success(f"📊 Total de jogos identificados na planilha: **{len(jogos_validos)}**")
            
            # Pré-calcula ranking de grupos se o filtro estiver ativo
            top_grupos_indices = set()
            if usar_grupos:
                ranking = calcular_ranking_grupos(jogos_validos)
                top_grupos_indices = {idx for idx, count in ranking if count > 0}

            # FUNÇÃO DE VALIDAÇÃO COM PONTUAÇÃO FLEXÍVEL NOS 7 CRITÉRIOS
            def validar_jogo(jogo):
                score = 0
                set_jogo = set(jogo)

                # 1. Dezena Obrigatória (Integrada ao score tolerável)
                if usar_obrig:
                    if 18 in set_jogo:
                        score += 1

                # 2. Primos (5 a 7)
                if usar_primos:
                    if 5 <= len(set_jogo.intersection(PRIMOS)) <= 7:
                        score += 1

                # 3. Fibonacci (3 a 5)
                if usar_fibo:
                    if 3 <= len(set_jogo.intersection(FIBONACCI)) <= 5:
                        score += 1

                # 4. Moldura (8 a 11)
                if usar_moldura:
                    if 8 <= len(set_jogo.intersection(MOLDURA)) <= 11:
                        score += 1

                # 5. Pares (6 a 8)
                if usar_pares:
                    if 6 <= len(set_jogo.intersection(PARES)) <= 8:
                        score += 1

                # 6. Soma Total (180 a 220)
                if usar_soma:
                    if 180 <= sum(jogo) <= 220:
                        score += 1

                # 7. Grupos
                if usar_grupos:
                    passou_grupo = False
                    for g_idx in top_grupos_indices:
                        if len(set_jogo.intersection(GRUPOS_56[g_idx])) >= 6:
                            passou_grupo = True
                            break
                    if passou_grupo:
                        score += 1

                return score >= min_filtros

            # Executa a filtragem dos jogos
            jogos_aprovados = [jogo for jogo in jogos_validos if validar_jogo(jogo)]

            st.markdown("---")
            st.subheader("📈 Resultados da Análise")
            col1, col2 = st.columns(2)
            col1.metric("Jogos Analisados", len(jogos_validos))
            col2.metric("Jogos Aprovados", len(jogos_aprovados))

            # Exibe tabela com jogos aprovados
            if jogos_aprovados:
                df_aprovados = pd.DataFrame(
                    jogos_aprovados, 
                    columns=[f"D{i}" for i in range(1, 16)]
                )
                st.dataframe(df_aprovados, use_container_width=True)

                # Botão de Download dos resultados
                csv = df_aprovados.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Jogos Aprovados (CSV)",
                    data=csv,
                    file_name="jogos_filtrados.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Nenhum jogo atendeu aos critérios de tolerância selecionados.")

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo Excel: {str(e)}")
        st.info("💡 Verifique se o arquivo enviado está no formato correto (.xlsx) e possui apenas números nas dezenas.")