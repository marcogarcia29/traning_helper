import streamlit as st
import database as db # Importa nosso novo módulo de banco de dados

# Move page config to the very top as recommended by Streamlit
st.set_page_config(
    page_title="Assistente de treinos",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Inicialização do Banco de Dados ---
db.create_tables()

# --- Inicialização do Estado da Sessão ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "Login" # Controla entre 'Login' e 'Cadastro'

# 1. Inicializar o estado da sidebar se não existir
if 'sidebar_oculta' not in st.session_state:
    st.session_state.sidebar_oculta = False

# Função para alterar o estado
def alternar_sidebar():
    st.session_state.sidebar_oculta = not st.session_state.sidebar_oculta

# 2. Lógica para esconder a Sidebar usando CSS
if st.session_state.sidebar_oculta:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- Funções de Callback para mudar de página ---
def go_to_signup():
    st.session_state.page = "Cadastro"

def go_to_login():
    st.session_state.page = "Login"

# --- Lógica de Login/Cadastro/Logout ---
if not st.session_state.logged_in:
    st.title("Bem-vindo ao seu Assistente de Treino! 🏋️")

    if st.session_state.page == "Login":
        st.subheader("Faça login para continuar")
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Entrar")

            if login_button:
                user_id = db.check_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.success("Login realizado com sucesso!")
                    if st.session_state.sidebar_oculta == True:
                        alternar_sidebar()
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        
        st.write("Não tem uma conta?")
        st.button("Criar Conta", on_click=go_to_signup)

    elif st.session_state.page == "Cadastro":
        st.subheader("Crie sua conta")
        with st.form("signup_form"):
            new_username = st.text_input("Escolha um nome de usuário")
            new_password = st.text_input("Escolha uma senha", type="password")
            signup_button = st.form_submit_button("Cadastrar")

            if signup_button:
                if db.add_user(new_username, new_password):
                    st.success("Conta criada com sucesso! Você já pode fazer o login.")
                    st.balloons()
                else:
                    st.error("Este nome de usuário já existe. Por favor, escolha outro.")
        
        st.button("Voltar para o Login", on_click=go_to_login)

else:
    # Usuário está logado
    st.title("Bem-vindo ao seu Assistente de Treino! 🏋️")

    if st.sidebar.button("Sair", on_click=alternar_sidebar):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.page = "Login"
        st.rerun()

    st.write("Bem-vindo!")
    # --- Navigation and Content for Logged-in Users ---
    pages = {
        "Sua evolução": [
            st.Page('pages/graph_page.py', title="Sua evolução", icon="📈")
        ],
        "Seus treinos": [
            st.Page('pages/source.py', title="Seus treinos", icon="🏋️")
        ]
    }

    pg = st.navigation(pages=pages, position="sidebar")
    pg.run()

    st.sidebar.success("Selecione uma página acima.")
    st.write("Use o menu na barra lateral para navegar entre as páginas de registro e visualização de gráficos.")
