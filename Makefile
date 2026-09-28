# Atalhos (Linux/macOS). No Windows use diretamente: python estudos.py ...
PY ?= python3

.PHONY: todos listar limpar verificar overleaf
todos:            ## compila todos os cadernos e copia os PDFs para saida/
	$(PY) estudos.py compilar --todos
listar:
	$(PY) estudos.py listar
limpar:
	$(PY) estudos.py limpar --todos
verificar:
	$(PY) estudos.py verificar
overleaf:         ## make overleaf C=cadernos/livros/lff
	$(PY) estudos.py overleaf $(C)
