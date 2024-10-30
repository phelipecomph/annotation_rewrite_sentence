import streamlit as st
import pandas as pd
import time
import boto3
import os

s3 = boto3.client('s3',
                  aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"])

bucket_name = 'static.redacaonota1000.com.br'
file_path = 'pares_de_sentenca.csv'
key_name = 'reescrita/pares_de_sentenca.csv'

# Carregar o CSV com as sentenças (substitua 'sentencas.csv' pelo nome do seu arquivo)
s3.download_file(bucket_name, key_name, file_path)
df = pd.read_csv('pares_de_sentenca.csv')

# Filtrar as linhas que ainda não foram anotadas
df_nao_anotadas = df[df['parafrase'].isna()]

# Função para salvar o CSV atualizado


def salvar_csv(df, nome_arquivo='pares_de_sentenca.csv'):
    df.to_csv(nome_arquivo, index=False)
    s3.upload_file(file_path, bucket_name, key_name)


# Variável para acompanhar o progresso
progresso = 1 - len(df_nao_anotadas) / len(df)

# Layout da interface
st.title('Anotação de Parafrase')
st.write(f'Progresso: {int(progresso * 100)}%')


st.session_state.obs = ''
st.session_state.parafrase = ''

# Barra de progresso
st.progress(progresso)

# Mostrar as sentenças para anotar
if not df_nao_anotadas.empty:
    # Selecionar a primeira sentença não anotada
    linha_atual = df_nao_anotadas.iloc[0]
    sentenca1 = linha_atual['sentence1']
    sentenca2 = linha_atual['sentence2']

    st.subheader("Sentença 1")
    st.text_area("Sentença 1", value=sentenca1, height=100,
                 max_chars=None, key="sentenca1")
    st.subheader("Sentença 2")
    st.text_area("Sentença 2", value=sentenca2, height=100,
                 max_chars=None, key="sentenca2")

    st.write("É parafrase?")
    parafrase = st.radio("", ('Sim', 'Não'))

    st.write("Observação")
    obs = st.text_area("Obs", key="obs", value="")

    # Botão para enviar a anotação
    if st.button("Enviar"):
        # Atualizar o DataFrame com a anotação do usuário
        idx = linha_atual.name
        df.at[idx, 'parafrase'] = True if parafrase == 'Sim' else False
        df.at[idx, 'obs'] = obs

        # Salvar o CSV atualizado
        salvar_csv(df)

        st.success("Anotação salva!")
        #time.sleep()
        del st.session_state.obs
        del st.session_state.parafrase
        st.rerun()  # Recarregar a página para mostrar a próxima anotação
else:
    st.write("Todas as sentenças foram anotadas!")
