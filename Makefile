# Variáveis para facilitar manutenção
PYTHON = poetry run python
PYTEST = poetry run pytest -v

.PHONY: help install run query test benchmark clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala dependências via Poetry"
	@echo "  make run        - Executa o pipeline principal"
	@echo "  make query      - Executa a consulta de municípios (requer silver)"
	@echo "  make test       - Executa a suíte de testes unitários"
	@echo "  make benchmark  - Executa a auditoria de performance e gera o gráfico"
	@echo "  make clean      - Remove arquivos temporários e o output silver"

install:
	poetry install

run:
	$(PYTHON) -m rfb_polars_etl.main

grupos:
	$(PYTHON) -m rfb_polars_etl.grupos_cidades.pipeline_grupos

query:
	$(PYTHON) -m rfb_polars_etl.query_municipios

test:
	$(PYTEST)

benchmark:
	$(PYTHON) benchmarks/run_benchmark.py

clean:
	rm -f data/silver/*.parquet
	rm -f benchmarks/*.png
	@echo "Ambiente limpo."
