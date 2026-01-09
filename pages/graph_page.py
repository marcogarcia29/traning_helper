import streamlit as st
import pandas as pd
from db_functions import load_workouts

import altair as alt
# Importa o nosso módulo de banco de dados centralizado
import database as db

st.title("Sua evolução de treino📈")
try:
    df = load_workouts()
except:
    st.info("Nenhum treino registrado ainda. Vá para a página de 'Seus treinos' para começar.")

# Verifica se o usuário está logado, caso contrário, não mostra nada.
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

# Pega o ID do usuário da sessão e carrega seus treinos
user_id = st.session_state.user_id
df = db.load_workouts(user_id)

if not df.empty:
    # --- Limpeza e Preparação dos Dados ---
    # Converte a coluna de data para o formato datetime para manipulação
    df['date'] = pd.to_datetime(df['date'])
    # Garante que a coluna de peso seja numérica
    df['weight'] = pd.to_numeric(df['weight'])

    # Extrai o valor numérico da coluna 'carga' (ex: '10kg' -> 10.0)
    # O 'coerce' transforma erros em 'NaN' (Not a Number)
    df['carga'] = pd.to_numeric(df['weight'], errors='coerce')
    df.dropna(subset=['carga'], inplace=True) # Remove linhas onde a carga não era um número

    # --- Interface do Usuário ---
    #lista_exercicios = df['exercicio'].unique()
    lista_exercicios = df['exercise'].unique()
    exercicio_selecionado = st.selectbox("Selecione um exercício para ver a evolução:", options=lista_exercicios)

    if exercicio_selecionado:
        # Filtra o DataFrame para o exercício escolhido
        #df_exercicio = df[df['exercicio'] == exercicio_selecionado]
        df_exercicio = df[df['exercise'] == exercicio_selecionado].copy()

        if not df_exercicio.empty:
            st.subheader(f"Evolução de Carga para: {exercicio_selecionado}")
            #st.subheader(f"Evolução de Carga Máxima para: {exercicio_selecionado}")

            # --- Prepara os dados para o gráfico de evolução geral ---
            # 1. Normaliza a data para ignorar horas/minutos/segundos
            df_agrupado_dia = df_exercicio.copy()
            df_agrupado_dia['dia_registro'] = df_agrupado_dia['date'].dt.normalize()
            # Agrupa por dia e pega a carga máxima levantada naquele dia
            df_evolucao = df_exercicio.groupby(df_exercicio['date'].dt.date)['weight'].max().reset_index()
            df_evolucao.rename(columns={'date': 'Data', 'weight': 'Carga Máxima (kg)'}, inplace=True)

            # 2. Agrupa por dia e pega a carga máxima daquele dia
            # df_evolucao = df_agrupado_dia.groupby('dia_registro')['weight'].max().reset_index()
            # df_evolucao.rename(columns={'dia_registro': 'Data', 'carga': 'Carga Máxima (kg)'}, inplace=True)

            # --- Cria o gráfico de evolução com Altair ---
            chart_evolucao = alt.Chart(df_evolucao).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Data:T', title='Data do Registro', axis=alt.Axis(labelAngle=0, format='%d/%m')),
                y=alt.Y('Carga Máxima (kg):Q', title='Carga Máxima (kg)'),
                tooltip=[alt.Tooltip('Data:T', format='%d/%m/%Y'), alt.Tooltip('Carga Máxima (kg):Q')]
                #tooltip=[alt.Tooltip('Data:T', format='%d/%m/%Y'), 'Carga Máxima (kg):Q']
            ).interactive()
            st.altair_chart(chart_evolucao, width='stretch')
            #st.altair_chart(chart_evolucao, use_container_width=True)

            st.divider()

            # --- SEÇÃO DE COMPARAÇÃO DE TREINOS ---
            st.header("Análise Detalhada por Dia de Treino")
            # --- SEÇÃO DE ANÁLISE DETALHADA ---
            st.header("Histórico Detalhado do Exercício")
            
            # Pega as datas únicas para o exercício selecionado
            datas_disponiveis = sorted(df_exercicio['date'].dt.date.unique(), reverse=True)
            
            if datas_disponiveis:
                data_selecionada = st.selectbox(
                    "Selecione uma data para analisar:",
                    options=datas_disponiveis,
                    format_func=lambda date: date.strftime('%d/%m/%Y')
                )
            # Adiciona um número de série para cada registro dentro de um dia de treino
            # Isso nos ajuda a visualizar as séries em ordem no gráfico
            df_exercicio['serie_num'] = df_exercicio.groupby(df_exercicio['date'].dt.date).cumcount() + 1

            # Encontra o próximo dia de treino
            proxima_data = next((d for d in sorted(datas_disponiveis, reverse=False) if d > data_selecionada), None)
            # Prepara os dados para o gráfico de barras detalhado
            df_melted = df_exercicio.melt(
                id_vars=['date', 'serie_num'], 
                value_vars=['weight', 'reps'],
                var_name='Grandeza',
                value_name='Valor'
            )
            # Mapeia os nomes para português para o gráfico
            df_melted['Grandeza'] = df_melted['Grandeza'].map({'weight': 'Carga (kg)', 'reps': 'Repetições'})

            col1, col2 = st.columns(2)
            # --- Cria o gráfico de barras detalhado com Altair ---
            chart_detalhado = alt.Chart(df_melted).mark_bar().encode(
                x=alt.X('date:T', title='Data', axis=alt.Axis(labelAngle=-45, format='%d/%m/%y')),
                y=alt.Y('Valor:Q', title='Valor'),
                color=alt.Color('Grandeza:N', title='Grandeza'),
                column=alt.Column('serie_num:N', title='Série'), # Cria uma coluna para cada série
                tooltip=['date:T', 'serie_num:N', 'Grandeza:N', 'Valor:Q']
            ).properties(
                width=30 # Largura de cada gráfico de série
            )
            st.altair_chart(chart_detalhado)

            def criar_grafico_dia(df_dia, data_ref, titulo):
                """Função para criar o gráfico de barras para um dia específico."""
                if df_dia.empty:
                    st.info(f"Não há dados para {titulo}.")
                    return

                st.subheader(titulo)
                st.write(f"Data: {data_ref.strftime('%d/%m/%Y')}")

                # Transforma os dados para o formato 'long' para o Altair
                df_melted = df_dia.melt(
                    id_vars=['serie'], 
                    value_vars=['carga', 'repeticoes'],
                    var_name='Grandeza',
                    value_name='Valor'
                )
                df_melted['serie'] = 'Série ' + df_melted['serie'].astype(str)

                chart = alt.Chart(df_melted).mark_bar().encode(
                    x=alt.X('serie:N', title='Série', sort=None),
                    y=alt.Y('Valor:Q', title='Valor'),
                    color=alt.Color('Grandeza:N', title='Grandeza'),
                    xOffset='Grandeza:N',
                    tooltip=['serie', 'Grandeza', 'Valor']
                ).properties(
                    width=alt.Step(40) # Controla a largura das barras
                )
                st.altair_chart(chart, width='stretch')

                # Gráfico para a data selecionada
                with col1:
                    df_data_selecionada = df_exercicio[df_exercicio['date'].dt.date == data_selecionada]
                    criar_grafico_dia(df_data_selecionada, data_selecionada, "Treino Selecionado")

                # Gráfico para a próxima data de treino
                with col2:
                    if proxima_data:
                        df_proxima_data = df_exercicio[df_exercicio['date'].dt.date == proxima_data]
                        criar_grafico_dia(df_proxima_data, proxima_data, "Próximo Treino")
                    else:
                        st.subheader("Próximo Treino")
                        st.info("Não há um registro de treino futuro para comparação.")

            st.subheader("Histórico de Treinos")
            # Renomeando colunas para exibição na tabela
            st.dataframe(df_exercicio.rename(columns={'exercicio': 'Exercício', 'serie': 'Série', 'repeticoes': 'Repetições', 'carga': 'Carga', 'data_registro': 'Data'}), width='stretch')
        else:
            st.warning("Não há dados de carga válidos para este exercício.")
            st.warning("Não há dados válidos para este exercício.")
else:
    st.info("Nenhum treino registrado ainda. Vá para a página de 'Seus treinos' para começar.")