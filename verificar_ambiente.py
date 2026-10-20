#!/usr/bin/env python3
"""Confere se o seu computador está pronto para a oficina.

Rode, com o ambiente virtual ativado:
    python verificar_ambiente.py
"""
import importlib
import shutil
import sys
from pathlib import Path

OK, FALHA, AVISO = "[ OK ]", "[FALHA]", "[AVISO]"
problemas = 0

print(f"Python {sys.version.split()[0]} em {sys.executable}")
if sys.version_info < (3, 10):
    print(f"{FALHA} use Python 3.10 ou mais recente")
    problemas += 1
else:
    print(f"{OK} versão do Python")

if sys.prefix == sys.base_prefix:
    print(f"{AVISO} o ambiente virtual não parece ativado (veja o README, passo 3)")
else:
    print(f"{OK} ambiente virtual ativado")

for mod in ("numpy", "pandas", "scipy", "matplotlib", "pytest"):
    try:
        m = importlib.import_module(mod)
        print(f"{OK} {mod} {getattr(m, '__version__', '')}")
    except ImportError:
        print(f"{FALHA} {mod} não instalado -> pip install -r requirements.txt")
        problemas += 1

dados = Path(__file__).parent / "etapas" / "0-sem-harness" / "dados"
csvs = sorted(dados.glob("*.csv"))
if len(csvs) == 3:
    print(f"{OK} dados da oficina encontrados ({', '.join(c.name for c in csvs)})")
else:
    print(f"{FALHA} dados não encontrados em {dados}")
    problemas += 1

agentes = {"opencode": "OpenCode", "agy": "Antigravity CLI", "antigravity": "Antigravity",
           "claude": "Claude Code"}
achados = [nome for cmd, nome in agentes.items() if shutil.which(cmd)]
if achados:
    print(f"{OK} agente(s) encontrado(s) no PATH: {', '.join(achados)}")
else:
    print(f"{AVISO} nenhum agente de terminal no PATH. Se for usar o Antigravity (app), "
          "tudo bem; se for usar o OpenCode, veja o README, passo 4.")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.close(fig)
    print(f"{OK} matplotlib consegue gerar figuras")
except Exception as exc:  # noqa: BLE001
    print(f"{FALHA} matplotlib: {exc}")
    problemas += 1

print()
print("Tudo pronto para a oficina!" if problemas == 0
      else f"{problemas} problema(s) encontrado(s). Veja o README ou traga o notebook para a oficina "
           "que resolvemos no início.")
