import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os

# Função para carregar os dados de um arquivo CSV
def carregar_dados(nome_arquivo, colunas):
    if os.path.exists(nome_arquivo):
        return pd.read_csv(nome_arquivo)
    else:
        return pd.DataFrame(columns=colunas)

# Função para salvar os dados em um arquivo CSV
def salvar_dados(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

# Variáveis globais para manter os dados
bandejas_compradas = carregar_dados('bandejas_compradas.csv', ['Código', 'Nome Variedade', 'Quantidade'])
semeio = carregar_dados('semeio.csv', ['Data', 'Código Variedade', 'Nome Variedade', 'Quantidade Semeada', 'Bandejas para Plantio'])
plantios = carregar_dados('plantios.csv', ['Data', 'Código Variedade', 'Nome Variedade', 'Quantidade Vasos Plantados', 'Bandejas Usadas'])
descartes = carregar_dados('descartes.csv', ['Data', 'Tipo', 'Código Variedade', 'Nome Variedade', 'Quantidade Descartada'])

# Título do App
st.title('Gerenciamento de Comércio de Plantas')

# Menu na Sidebar
st.sidebar.title("Menu de Controle")
menu = st.sidebar.radio("Selecione uma opção:", 
                        ('Controle de Bandejas Compradas', 
                         'Controle de Semeio', 
                         'Controle de Plantio', 
                         'Controle de Descarte'))

# Função para controlar bandejas compradas
def controle_bandejas():
    st.header("Controle de Bandejas Compradas")
    
    # Inputs para adicionar nova bandeja
    codigo = st.text_input('Código da Bandeja (6 números)', max_chars=6)
    nome_variedade = st.text_input('Nome da Variedade')
    quantidade = st.number_input('Quantidade de Bandejas', min_value=1)
    
    if st.button('Adicionar Bandeja'):
        global bandejas_compradas
        nova_bandeja = pd.DataFrame({'Código': [codigo], 'Nome Variedade': [nome_variedade], 'Quantidade': [quantidade]})
        bandejas_compradas = pd.concat([bandejas_compradas, nova_bandeja], ignore_index=True)
        salvar_dados(bandejas_compradas, 'bandejas_compradas.csv')
        st.success(f'Bandeja de código {codigo} adicionada com sucesso!')
    
    st.subheader("Bandejas Compradas")
    st.dataframe(bandejas_compradas)

# Função para controlar o semeio
def controle_semeio():
    st.header("Controle de Semeio")
    
    # Inputs para adicionar semeio
    data_semeio = st.date_input('Data do Semeio', value=date.today())
    codigo_variedade = st.text_input('Código da Variedade (CF seguido de 4 dígitos)')
    nome_variedade = st.text_input('Nome da Variedade')
    quantidade_semeada = st.number_input('Quantidade Semeada (em bandejas)', min_value=1)
    
    if st.button('Adicionar Registro de Semeio'):
        global semeio
        novo_semeio = pd.DataFrame({'Data': [data_semeio], 'Código Variedade': [codigo_variedade], 'Nome Variedade': [nome_variedade], 'Quantidade Semeada': [quantidade_semeada], 'Bandejas para Plantio': [0]})
        semeio = pd.concat([semeio, novo_semeio], ignore_index=True)
        salvar_dados(semeio, 'semeio.csv')
        st.success(f'Registro de semeio para a variedade {nome_variedade} adicionado com sucesso!')
    
    st.subheader("Histórico de Semeio")
    st.dataframe(semeio)

# Função para controlar plantios
def controle_plantios():
    global bandejas_compradas, plantios

    st.header("Controle de Plantio")
    
    if bandejas_compradas.empty:
        st.warning("Nenhuma bandeja registrada. Por favor, registre bandejas primeiro no controle de bandejas compradas.")
        return

    nomes_variedades = bandejas_compradas['Nome Variedade'].unique().tolist()
    nome_variedade_plantio = st.selectbox('Nome da Variedade', nomes_variedades)
    
    if nome_variedade_plantio:
        codigos_variedade = bandejas_compradas[bandejas_compradas['Nome Variedade'] == nome_variedade_plantio]['Código'].tolist()
    else:
        codigos_variedade = []
    
    codigo_variedade_plantio = st.selectbox('Código da Variedade', codigos_variedade)
    quantidade_vasos_plantados = st.number_input('Quantidade de Vasos Plantados', min_value=1)
    quantidade_bandejas_usadas = st.number_input('Quantidade de Bandejas Usadas', min_value=1)
    
    if st.button('Adicionar Plantio'):
        if codigo_variedade_plantio and nome_variedade_plantio:
            novo_plantio = pd.DataFrame({'Data': [date.today()], 'Código Variedade': [codigo_variedade_plantio], 'Nome Variedade': [nome_variedade_plantio], 'Quantidade Vasos Plantados': [quantidade_vasos_plantados], 'Bandejas Usadas': [quantidade_bandejas_usadas]})
            plantios = pd.concat([plantios, novo_plantio], ignore_index=True)

            index = bandejas_compradas[(bandejas_compradas['Código'] == codigo_variedade_plantio) & (bandejas_compradas['Nome Variedade'] == nome_variedade_plantio)].index
            if not index.empty:
                bandejas_compradas.loc[index, 'Quantidade'] -= quantidade_bandejas_usadas
                bandejas_compradas = bandejas_compradas[bandejas_compradas['Quantidade'] > 0]

            salvar_dados(plantios, 'plantios.csv')
            salvar_dados(bandejas_compradas, 'bandejas_compradas.csv')
            st.success(f'Plantio registrado: {quantidade_vasos_plantados} vasos da variedade {nome_variedade_plantio}!')
        else:
            st.error("Por favor, selecione corretamente a variedade e o código.")

    st.subheader("Histórico de Plantios")
    st.dataframe(plantios)

# Função para controlar descarte
def controle_descarte():
    global descartes

    st.header("Controle de Descarte")
    data_descarte = st.date_input('Data do Descarte', value=date.today())
    tipo_descarte = st.selectbox('Tipo de Descarte', ['Bandejas', 'Vasos'])
    codigo_variedade = st.text_input('Código da Variedade')
    nome_variedade = st.text_input('Nome da Variedade')
    quantidade_descartada = st.number_input('Quantidade de Descarte', min_value=1)

    if st.button('Adicionar Descarte'):
        novo_descarte = pd.DataFrame({'Data': [data_descarte], 'Tipo': [tipo_descarte], 'Código Variedade': [codigo_variedade], 'Nome Variedade': [nome_variedade], 'Quantidade Descartada': [quantidade_descartada]})
        descartes = pd.concat([descartes, novo_descarte], ignore_index=True)
        salvar_dados(descartes, 'descartes.csv')
        st.success(f'{quantidade_descartada} {tipo_descarte} descartados da variedade {nome_variedade}!')

    st.subheader("Histórico de Descarte")
    st.dataframe(descartes)

# Navegação no menu
if menu == 'Controle de Bandejas Compradas':
    controle_bandejas()
elif menu == 'Controle de Semeio':
    controle_semeio()
elif menu == 'Controle de Plantio':
    controle_plantios()
elif menu == 'Controle de Descarte':
    controle_descarte()
