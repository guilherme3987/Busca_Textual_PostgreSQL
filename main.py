import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Recupera as credenciais
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")    
port = os.getenv("DB_PORT")    
database = os.getenv("DB_NAME") 

# Cria a conexão com SQLAlchemy para evitar o UserWarning
url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

try:
    engine = create_engine(url)
    print("Conexão estabelecida com sucesso usando variáveis de ambiente!")

    # Exportando os dados
    df_pesquisadores = pd.read_sql("SELECT * FROM public.pesquisadores", engine)
    df_pesquisadores.to_csv("pesquisadores_completo.csv", index=False)
    
    df_producoes = pd.read_sql("SELECT * FROM public.producoes", engine)
    df_producoes.to_csv("producoes_completo.csv", index=False)
    
    print("✓ Arquivos CSV gerados com segurança!")

except Exception as e:
    print(f"Erro ao conectar: {e}")