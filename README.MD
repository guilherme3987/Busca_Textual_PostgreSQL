# Projeto: Full-Text Search em PostgreSQL 

Este projeto implementa uma solução de busca textual avançada para o banco de dados **BD\_PESQUISADOR**, permitindo pesquisas rápidas, rankeadas e tolerantes a erros em registros de produções acadêmicas.

## 1\. Mapeamento de Estrutura

Para aplicar a lógica de busca de um blog acadêmico à nossa realidade institucional, utilizamos o seguinte depara:

| Conceito (Blog) | Sua Base de Dados | Colunas Relacionadas |
| :--- | :--- | :--- |
| **Author** | `public.pesquisadores` | [cite_start]`nome` [cite: 12, 13] |
| **Post** | `public.producoes` | [cite_start]`nomeartigo` [cite: 12, 13] |
| **Tag** | (Não há equivalente) | [cite_start]`issn` ou `área` [cite: 12] |
| **Idioma** | Inglês | **Português** |

-----

## 2\. Configuração do Ambiente e Ingestão

A base de dados opera em **PostgreSQL 17.9 (Debian)**. O processo de carga inicial segue estas etapas:

1.  **Criação de Tabelas:** Estrutura espelhada aos arquivos CSV gerados via Python.
2.  **Importação:** Uso do comando `COPY` para alta performance na carga de dados.
3.  **Extensões Necessárias:**
      * `unaccent`: Para ignorar acentos nas buscas (ex: "Saúde" vs "Saude").
      * `pg_trgm`: Habilita o algoritmo de *Trigramas* para busca fuzzy (aproximada).

### Configuração de Texto Personalizada (`pt_unaccent`)

Diferente do padrão, criamos uma configuração que combina o dicionário de português (`portuguese_stem`) com a remoção de acentos. Isso garante que a busca por "produção" encontre "producao" ou "produções".

-----

## 3\. Motor de Busca e Indexação

### Construção do Documento

O "documento" de busca é gerado pela concatenação do título do artigo com o nome do pesquisador. Aplicamos pesos diferenciados para priorizar resultados:

  * **Peso A:** Título do Artigo (`nomeartigo`).
  * **Peso B:** Nome do Pesquisador (`nome`).

### Performance com Materialized Views

Para garantir que a busca não onere o servidor `127.0.0.1`, utilizamos uma **View Materializada**:

  * **`search_index`**: Uma tabela física que armazena o documento já processado (`tsvector`).
  * **Índice GIN**: Aplicado sobre a view, é o tipo de índice ideal para dados que não mudam a todo segundo (produções científicas).
  * **Manutenção:** Comando `REFRESH MATERIALIZED VIEW` deve ser executado após inserções de novos artigos.

-----

## 4\. Funcionalidades de Pesquisa

### Operadores Suportados

A busca utiliza `to_tsquery` com os seguintes operadores lógicos:

  * `&` (AND): Ambos os termos.
  * `|` (OR): Qualquer um dos termos.
  * `!` (NOT): Exclui um termo.
  * `:*` (Prefixo): Busca por termos incompletos (ex: `comput:*` encontra "computação").

### Ranking e Headline (Bônus)

  * **`ts_rank()`**: Ordena os resultados por relevância.
  * **`ts_headline()`**: Retorna um trecho do título destacando em **\<b\>negrito\</b\>** os termos encontrados.

### Busca Fuzzy (Tolerância a Erros)

Utilizamos a função `similarity()` para lidar com erros de digitação.

> **Exemplo:** Uma busca por "dngue" retornará resultados para "dengue" com base no índice de similaridade de caracteres.

-----

## 5\. Como Executar

1.  Garanta que o PostgreSQL esteja rodando na porta `5437`.
2.  Execute o script SQL de criação de extensões.
3.  Rode a criação da Materialized View.
4.  Realize consultas utilizando a função de busca rankeada.

-----
