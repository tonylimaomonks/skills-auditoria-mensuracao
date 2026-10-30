#!/bin/bash
# Regressão das skills: gera a auditoria BR (exemplo), a auditoria MX e a execução BR da Smart Fit numa pasta
# temporária e compara byte a byte com base-smartfit.sha (saída aprovada antes da generalização, 29/10/2026).
# Não escreve nada no vault: usa links simbólicos e grava só na pasta temporária.
# Uso: testes/regressao.sh [pasta-Smart-Fit]
set -u
K="$(cd "$(dirname "$0")/.." && pwd)"
R="${1:-$HOME/Documents/obsidian/Dia-a-dia/clients/Smart-Fit}"
P="$(mktemp -d)"
[ -f "$R/cliente.json" ] || { echo "Smart-Fit não encontrado em $R"; exit 2; }
for p in brasil mexico; do
  mkdir -p "$P/$p/entregas"
  for c in "$R/$p"/*; do n=$(basename "$c"); [ "$n" = entregas ] || ln -sfn "$c" "$P/$p/$n"; done
  for c in "$R/$p/entregas"/*; do n=$(basename "$c"); case "$n" in *.html) ;; *) ln -sfn "$c" "$P/$p/entregas/$n";; esac; done
done
mkdir -p "$P/brx/entregas/_fonte"
for c in "$R/brasil"/*; do n=$(basename "$c"); [ "$n" = entregas ] || ln -sfn "$c" "$P/brx/$n"; done
for c in "$R/brasil/entregas/_fonte"/*; do ln -sfn "$c" "$P/brx/entregas/_fonte/"; done
rm "$P/brx/entregas/_fonte/conteudo.json"
cp "$K/auditoria-mensuracao-pais/assets/exemplo-conteudo-br.json" "$P/brx/entregas/_fonte/conteudo.json"
ln -sfn "$R/design-system" "$P/design-system"; ln -sfn "$R/cliente.json" "$P/cliente.json"
cd "$P"
python3 "$K/auditoria-mensuracao-pais/scripts/motor/build.py" brx > log_br.txt 2>&1 || { echo "FALHOU auditoria BR"; tail log_br.txt; exit 1; }
python3 "$K/auditoria-mensuracao-pais/scripts/motor/build.py" mexico > log_mx.txt 2>&1 || { echo "FALHOU auditoria MX"; tail log_mx.txt; exit 1; }
mkdir -p ex && python3 "$K/relatorios-execucao-pais/scripts/build.py" brasil --saida ex > log_ex.txt 2>&1 || { echo "FALHOU execução BR"; tail log_ex.txt; exit 1; }
find . -name "*.html" -type f | grep -v "/_fonte/" | sed 's#^\./##' | xargs shasum | sort -k2 > atual.sha
find "$K" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
if diff "$K/testes/base-smartfit.sha" atual.sha; then
  echo "OK: $(wc -l < atual.sha | tr -d ' ') HTMLs idênticos à base"; rm -rf "$P"
else
  echo "DIFERENTE da base. Saídas em $P (compare com uma build da versão anterior)"; exit 1
fi
