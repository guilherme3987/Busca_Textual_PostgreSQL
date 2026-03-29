import logging
from config import get_engine
from fts import setup_fts, buscar, refresh
import csv
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)
 
 
def _exibir_resultados(termo: str, resultados: list[dict]) -> None:
    print(f"\n{'─' * 65}")
    print(f"  Resultados para '{termo}' ({len(resultados)} encontrados):")
    print(f"{'─' * 65}")
    for r in resultados:
        print(f"  [{r['relevancia']:.4f}] {r['nomeartigo'][:55]}")
        print(f"           {r['pesquisador_nome']} — {r['anoartigo']}")
    print(f"{'─' * 65}\n")

def _salvar_csv(nome_arquivo: str, resultados: list[dict]) -> None:
    """Salva a lista de dicionários em um arquivo CSV."""
    if not resultados:
        log.warning(f"Nenhum resultado para salvar em '{nome_arquivo}'.")
        return
    
    # Extrai as chaves do primeiro dicionário para usar como cabeçalho
    cabecalhos = resultados[0].keys()
    
    try:
        # encoding='utf-8' garante que os acentos fiquem corretos no Excel/banco
        with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=cabecalhos)
            writer.writeheader()
            writer.writerows(resultados)
        log.info(f"Resultados exportados com sucesso para: {nome_arquivo}")
    except Exception as e:
        log.error(f"Erro ao salvar o arquivo CSV: {e}")
 
 
if __name__ == "__main__":
    try:
        # 1. Conexão
        engine = get_engine()
 
        # 2. Configura FTS (criar views, índices, extensões)
        setup_fts(engine)
 
        # 3. Exemplos de busca e exportação
        termo_1 = "dengue"
        resultados_dengue = buscar(engine, termo_1)
        _exibir_resultados(termo_1, resultados_dengue)
        _salvar_csv("busca_dengue.csv", resultados_dengue)
 
        termo_2 = "inovação"
        resultados_inovacao = buscar(engine, termo_2)
        _exibir_resultados(termo_2, resultados_inovacao)
        _salvar_csv("busca_inovacao.csv", resultados_inovacao)
 
        termo_3 = "dngue"
        resultados_dngue_fuzzy = buscar(engine, termo_3, fuzzy=True)
        _exibir_resultados(f"{termo_3} (fuzzy)", resultados_dngue_fuzzy)
        _salvar_csv("busca_dngue_fuzzy.csv", resultados_dngue_fuzzy)
 
        # 4. Atualizar views após novos dados 
        # refresh(engine)
 
    except EnvironmentError as e:
        log.error("Configuração inválida: %s", e)
    except Exception as e:
        log.error("Erro fatal: %s", e)

"""
# Carrega as variáveis do arquivo .env
load_dotenv()

# Recupera as credenciais
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")    
port = os.getenv("DB_PORT")    
database = os.getenv("DB_NAME") 

# Configurações de logging para evitar mensagens de aviso
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cria a conexão com SQLAlchemy para evitar o UserWarning
url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

try:
    engine = create_engine(url)
    print("Conexão estabelecida com sucesso usando variáveis de ambiente!")
    
except Exception as e:
    print(f"Erro ao conectar: {e}")
"""