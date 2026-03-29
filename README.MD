# Motor de Busca Full-Text (FTS) com PostgreSQL e Python

Este projeto implementa uma solução de busca textual avançada (Full-Text Search) utilizando PostgreSQL e Python. O sistema é capaz de realizar buscas exatas, por prefixo e buscas aproximadas (fuzzy) com tolerância a erros de digitação, otimizado através de Materialized Views e índices GIN/Trigram.

---

## Estrutura do Projeto e Lógica dos Arquivos

A arquitetura do projeto foi dividida em módulos para separar as responsabilidades de configuração, definição de dados (DDL), lógica de busca (DML) e execução.

### 1. `config.py` (Gerenciamento de Conexão)
Este arquivo é o ponto de entrada para a comunicação com o banco de dados.

* **Lógica implementada:** Utiliza a biblioteca `dotenv` para carregar credenciais de segurança a partir de um arquivo `.env`, evitando que senhas sejam expostas no código.
* **ORM/Engine:** Constrói dinamicamente a string de conexão e utiliza o SQLAlchemy para criar a Engine, que gerencia o pool de conexões com o PostgreSQL de forma otimizada.

### 2. `init.sql` / `docker-compose.yml` (Infraestrutura)
Define a infraestrutura do banco de dados via Docker.

* **Configuração:** Configura um contêiner rodando a imagem `postgres:15`, mapeando a porta `5432` interna para a `5437` na máquina host.
* **Persistência:** Estabelece um volume local para garantir a persistência dos dados entre as execuções.

### 3. `steps.py` (Definição da Estrutura FTS - DDL)
Este arquivo armazena as instruções SQL brutas necessárias para preparar o PostgreSQL para a busca textual avançada.

* **Extensões:** Ativa a extensão `unaccent` (para ignorar acentuação nas buscas) e `pg_trgm` (para habilitar a busca fuzzy por similaridade de trigramas).
* **Dicionário Customizado:** Cria uma configuração de texto (`pt_unaccent`) que une a remoção de acentos com o dicionário `portuguese_stem`, responsável por reduzir palavras ao seu radical (ex: "computação" vira "comput").
* **Materialized View `search_index`:** Cria uma tabela física temporária que pré-calcula o documento de busca (`tsvector`) concatenando o nome do artigo e o nome do pesquisador. Isso evita que o banco tenha que processar o texto a cada nova consulta, garantindo alta performance. Utiliza um índice GIN para buscas rápidas.
* **Materialized View `unique_lexeme`:** Extrai todas as palavras únicas (lexemas) da base de dados usando a função `ts_stat` e aplica um índice de trigramas (`gist`). Esta view é o "dicionário de correção" usado para resolver erros de digitação.

### 4. `fts.py` (Motor de Busca e Correção - DML)
É o núcleo lógico da aplicação, responsável por interagir com a estrutura criada no banco.

* **Setup e Refresh:** Automatizam a execução dos scripts do `steps.py` e a atualização dos dados nas Materialized Views, respectivamente.
* **Lógica de Correção (`_corrigir_termo`):** Se o usuário digitar algo errado (ex: "dngue"), a função cruza o termo com a view `unique_lexeme` usando o operador de distância trigrâmica (`<->`). Ela retorna a palavra correta do banco de dados caso a similaridade (`similarity()`) seja maior que um limite pré-definido (ex: 0.5).
* **Tratamento de Strings:** Transforma strings simples (ex: "dengue bahia") em uma query válida para o PostgreSQL (`dengue & bahia:*`), onde o `&` exige que ambos os termos existam e o `:*` permite a busca por prefixo (encontrando palavras incompletas).
* **Busca e Comparação:** Consulta a view `search_index` comparando o documento (`tsvector`) com a query (`tsquery`) usando o operador `@@`.
* **Ranqueamento:** Ordena os resultados matematicamente pela relevância usando a função `ts_rank` e limita a resposta aos 10 melhores resultados.

### 5. `main.py` (Execução e Apresentação)
Arquivo principal que orquestra o fluxo da aplicação.

* **Lógica implementada:** Instancia a conexão com o banco, aciona a configuração do FTS (`setup_fts`) e executa cenários de teste pré-definidos (buscas exatas e buscas fuzzy).
* **Interface:** Formata o retorno do banco em uma interface de texto limpa no terminal para facilitar a visualização dos pesos de relevância (`ts_rank`).