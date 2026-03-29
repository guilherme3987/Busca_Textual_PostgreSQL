import os
import logging
from sqlalchemy import create_engine, Engine
from dotenv import load_dotenv
 
# Configurações de logging para evitar mensagens de aviso
log = logging.getLogger(__name__)
 
# Constrói a URL de conexão usando variáveis de ambiente e valida 
def _build_url() -> str:
    
    load_dotenv()
 
    user     = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host     = os.getenv("DB_HOST")
    port     = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
 
    missing = [k for k, v in {
        "DB_USER": user, "DB_PASS": password,
        "DB_HOST": host, "DB_PORT": port, "DB_NAME": database,
    }.items() if not v]
 
    if missing:
        raise EnvironmentError(f"Variáveis de ambiente faltando: {missing}")
 
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
 
# Cria e retorna o engine SQLAlchemy
def get_engine() -> Engine:
    url = _build_url()
    engine = create_engine(url)
    log.info("Engine criado: %s", engine.url.render_as_string(hide_password=True))
    return engine
