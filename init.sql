version: '3.8'

services:
  db:
    image: postgres:15
    container_name: postgres_lattes
    restart: always
    environment:
      - POSTGRES_DB=BD_PESQUISADOR_BUSCA_TEXTUAL
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5437:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - lattes_network

networks:
  lattes_network:
    driver: bridge