# Variáveis para facilitar manutenção
PYTHON = poetry run python
PYTEST = poetry run pytest

.PHONY: help install run test benchmark clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala dependências via Poetry"
	@echo "  make run        - Executa o pipeline principal"
	@echo "  make test       - Executa a suíte de testes unitários"
	@echo "  make benchmark  - Executa a auditoria de performance e gera o gráfico"
	@echo "  make clean      - Remove arquivos temporários e o output silver"

install:
	poetry install

run:
	$(PYTHON) -m rfb_polars_etl.main

test:
	$(PYTEST)

benchmark:
	$(PYTHON) benchmarks/run_benchmark.py

clean:
	@if exist data\silver\*.parquet del /q data\silver\*.parquet
	@if exist benchmarks\*.png del /q benchmarks\*.png
	@echo "Ambiente limpo."