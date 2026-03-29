STEPS: list[tuple[str, str]] = [
 
    # ── 1. Extensões ─────────────────────────────────────────────────────────
    (
        "Extensão unaccent",
        "CREATE EXTENSION IF NOT EXISTS unaccent;",
    ),
    (
        "Extensão pg_trgm",
        "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    ),
 
    # ── 2. Configuração de busca pt_unaccent ─────────────────────────────────
    (
        "Text search config pt_unaccent",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_ts_config WHERE cfgname = 'pt_unaccent'
            ) THEN
                EXECUTE 'CREATE TEXT SEARCH CONFIGURATION pt_unaccent (COPY = portuguese)';
            END IF;
        END
        $$;
        """,
    ),
    (
        "Mapping pt_unaccent → unaccent + portuguese_stem",
        """
        ALTER TEXT SEARCH CONFIGURATION pt_unaccent
            ALTER MAPPING FOR hword, hword_part, word
            WITH unaccent, portuguese_stem;
        """,
    ),
 
    # ── 3. View materializada (desnormalizada para FTS) ───────────────────────
    (
        "Drop search_index (se existir)",
        "DROP MATERIALIZED VIEW IF EXISTS search_index CASCADE;",
    ),
    (
        "Materialized view search_index",
        """
        CREATE MATERIALIZED VIEW search_index AS
        SELECT
            ROW_NUMBER() OVER ()  AS producao_id,
            p.pesquisadores_id,
            p.nomeartigo,
            p.anoartigo,
            p.issn,
            res.nome              AS pesquisador_nome,
            res.lattes_id,
            setweight(to_tsvector('pt_unaccent', p.nomeartigo), 'A') ||
            setweight(to_tsvector('simple',      res.nome),     'C') AS documento
        FROM producoes p
        JOIN pesquisadores res
          ON res.pesquisadores_id = p.pesquisadores_id;
        """,
    ),
 
    # ── 4. Índice GIN ─────────────────────────────────────────────────────────
    (
        "Índice GIN idx_fts_search",
        "CREATE INDEX idx_fts_search ON search_index USING gin(documento);",
    ),
 
    # ── 5. View de lexemas únicos (busca fuzzy com pg_trgm) ──────────────────
    (
        "Drop unique_lexeme (se existir)",
        "DROP MATERIALIZED VIEW IF EXISTS unique_lexeme CASCADE;",
    ),
    (
        "Materialized view unique_lexeme",
        """
        CREATE MATERIALIZED VIEW unique_lexeme AS
        SELECT word
        FROM ts_stat(
            $$SELECT to_tsvector('simple', p.nomeartigo) ||
                     to_tsvector('simple', res.nome)
            FROM public.producoes p
            JOIN public.pesquisadores res ON res.pesquisadores_id = p.pesquisadores_id$$
        );
        """,
    ),
    (
        "Índice trigram idx_lexeme_trgm",
        "CREATE INDEX idx_lexeme_trgm ON unique_lexeme USING gin(word gin_trgm_ops);",
    ),
]
