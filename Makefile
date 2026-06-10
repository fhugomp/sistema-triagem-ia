.PHONY: test format lint typecheck run setup

# Roda a nossa suite de testes obrigatória
test:
	poetry run pytest -v

# Formata o código matematicamente
format:
	poetry run ruff format .

# Checa e corrige erros de sintaxe ou variáveis não usadas
lint:
	poetry run ruff check --fix .

# Garante a tipagem estática rigorosa das nossas variáveis
typecheck:
	poetry run mypy src/

# Roda o sistema final no navegador
run:
	poetry run streamlit run main.py

# Roda todas as verificações de qualidade de uma vez antes de um "git commit"
check-all: format lint typecheck test