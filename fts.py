import logging
from sqlalchemy import Engine, text
 
from steps import STEPS
 
log = logging.getLogger(__name__)
 

"""
Executa todos os passos DDL definidos em steps.STEPS.
Usa AUTOCOMMIT pois comandos DDL não aceitam transação no PostgreSQL.
"""
 
def setup_fts(engine: Engine) -> None:

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for label, query in STEPS:
            log.info("-%s", label)
            try:
                conn.execute(text(query))
                log.info("OK")
            except Exception as exc:
                log.error("Falhou em '%s': %s", label, exc)
                raise
 
    log.info("━" * 55)
    log.info("FTS configurado com sucesso!")
    log.info("    Views  : search_index, unique_lexeme")
    log.info("    Índices: idx_fts_search, idx_lexeme_trgm")
    log.info("━" * 55)
"""
Pesquisa produções científicas pelo termo informado.
 
Args:
    engine: Engine SQLAlchemy já configurado.
    termo:  Palavra ou expressão (ex.: 'dengue', 'inovação').
    fuzzy:  Se True, corrige erros de digitação via pg_trgm antes de buscar.
 
Returns:
    Lista de dicionários com os campos:
    producao_id, nomeartigo, pesquisador_nome, anoartigo, relevancia.
""" 

def buscar(engine: Engine, termo: str, fuzzy: bool = False) -> list[dict]:

    with engine.connect() as conn:
 
        if fuzzy:
            termo = _corrigir_termo(conn, termo)
 
        rows = conn.execute(
            text("""
                SELECT
                    producao_id,
                    nomeartigo,
                    pesquisador_nome,
                    anoartigo,
                    ts_rank(documento, to_tsquery('pt_unaccent', :termo)) AS relevancia
                FROM search_index
                WHERE documento @@ to_tsquery('pt_unaccent', :termo)
                ORDER BY relevancia DESC
                LIMIT 10;
            """),
            {"termo": termo},
        ).mappings().all()
 
    return [dict(r) for r in rows]
 

"""
Atualiza as views materializadas após inserção de novos dados.
Deve ser chamada sempre que houver novos registros em `producoes` ou `pesquisadores`.
""" 
def refresh(engine: Engine) -> None:

    views = ["search_index", "unique_lexeme"]
 
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for view in views:
            log.info("↻  Atualizando %s …", view)
            conn.execute(text(f"REFRESH MATERIALIZED VIEW {view};"))
            log.info("OK")
 
    log.info(" Views atualizadas.")
 
 
"""Usa pg_trgm para encontrar o lexema mais próximo do termo digitado."""
def _corrigir_termo(conn, termo: str) -> str:
    row = conn.execute(
        text("""
            SELECT word FROM unique_lexeme
            WHERE similarity(word, :termo) >= 0.3
            ORDER BY word <-> :termo
            LIMIT 1;
        """),
        {"termo": termo},
    ).fetchone()
 
    if row:
        log.info("Fuzzy: '%s' → '%s'", termo, row[0])
        return row[0]
 
    log.warning("Nenhum lexema similar encontrado para '%s'. Usando original.", termo)
    return termo
 
