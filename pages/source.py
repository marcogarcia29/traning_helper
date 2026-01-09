import streamlit as st
import pandas as pd
# Importa o nosso módulo de banco de dados centralizado
import database as db

st.title("Seu registro de treino🏋️")

# Verifica se o usuário está logado, caso contrário, não mostra nada.
# Esta é uma camada extra de segurança para páginas internas.
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

# Pega o ID do usuário da sessão
user_id = st.session_state.user_id

# --- Formulário de Inserção ---
with st.form("workout_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        exercicio = st.text_input("Exercicio", help="Ex: Supino")
    with col2:
        peso = st.number_input("Carga (kg)", min_value=0.0, format="%.2f")
    with col3:
        repeticoes = st.number_input("Repetições", min_value=1, step=1)
    with col4:
        data = st.date_input("Data")
    
    submitted = st.form_submit_button("Adicionar série")

    if submitted and exercicio:
        # Chama a função save_workout, passando o user_id
        db.save_workout(user_id, exercicio.upper(), peso, int(repeticoes), data)
        st.success("Série salva com sucesso! 💪")
    elif submitted:
        st.warning("Por favor, preencha o nome do exercício.")

# --- Exibição dos Dados ---
st.header("Seu treino registrado📒")

# Carrega os treinos passando o user_id do usuário logado
df = db.load_workouts(user_id)

if not df.empty:
    # Renomeia as colunas para exibição
    df.columns = ["Exercício", "Carga (kg)", "Repetições", "Data"]
    st.dataframe(df, width='stretch')
else:
    st.info("Nenhum treino registrado ainda. Use o formulário acima para começar.")
