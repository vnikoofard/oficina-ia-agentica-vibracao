"""Prepara uma cópia isolada de uma etapa, fora do repositório.

Por quê: aberto dentro do repositório, o agente pode "espiar" as pastas
vizinhas (por exemplo, ler a skill da etapa 2 enquanto roda a etapa 1) e o
experimento perde o sentido. Na cópia isolada as outras etapas não estão ao lado.

Uso:
    python preparar_etapa.py 1                 # cria ~/oficina-isolada/etapa-1/
    python preparar_etapa.py 3 --substituir    # apaga a cópia anterior e cria de novo
    python preparar_etapa.py 2 --destino D:/oficina-isolada

Estrutura criada (o AGENTS.md procura o Python em ../../.venv):
    <destino>/etapa-N/
    ├── .venv  -> ambiente virtual do repositório (atalho)
    └── etapas/N-nome/   cópia limpa da etapa (sem src/, resultados/ nem notas antigas)
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
IGNORAR = shutil.ignore_patterns("src", "resultados", "__pycache__", ".pytest_cache", "*.pyc")


def achar_etapa(n: str) -> Path:
    candidatas = sorted((REPO / "etapas").glob(f"{n}-*"))
    if len(candidatas) != 1:
        sys.exit(f"Etapa '{n}' não encontrada em {REPO / 'etapas'} (use 0, 1, 2 ou 3).")
    return candidatas[0]


def achar_venv(indicado: str | None) -> Path | None:
    if indicado:
        return Path(indicado).expanduser().resolve()
    if (REPO / ".venv").exists():
        return (REPO / ".venv").resolve()
    if sys.prefix != sys.base_prefix:          # rodando de dentro de um ambiente virtual
        return Path(sys.prefix).resolve()
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("etapa", help="0, 1, 2 ou 3")
    ap.add_argument("--destino", default="~/oficina-isolada", help="pasta-base (padrão: ~/oficina-isolada)")
    ap.add_argument("--venv", help="ambiente virtual a usar (padrão: .venv do repositório)")
    ap.add_argument("--substituir", action="store_true", help="apaga uma cópia anterior desta etapa")
    a = ap.parse_args()

    origem = achar_etapa(a.etapa)
    raiz = Path(a.destino).expanduser().resolve() / f"etapa-{a.etapa}"
    if REPO == raiz or REPO in raiz.parents:
        sys.exit("O destino precisa ficar fora do repositório.")
    if raiz.exists():
        if not a.substituir:
            sys.exit(f"{raiz} já existe. Use --substituir para recriar a cópia.")
        shutil.rmtree(raiz)

    destino_etapa = raiz / "etapas" / origem.name
    shutil.copytree(origem, destino_etapa, ignore=IGNORAR)
    for velho in (destino_etapa / "notas").glob("*.md") if (destino_etapa / "notas").exists() else []:
        if velho.name != "LEIA-ME.md":
            velho.unlink()

    venv = achar_venv(a.venv)
    aviso_venv = ""
    if venv is None:
        aviso_venv = ("\nAtenção: nenhum ambiente virtual encontrado. Crie o .venv na raiz do "
                      "repositório (veja o README) e rode este script de novo.")
    else:
        try:
            os.symlink(venv, raiz / ".venv", target_is_directory=True)
        except OSError:
            aviso_venv = (f"\nAtenção: não deu para criar o atalho .venv (no Windows isso exige o modo "
                          f"de desenvolvedor). Antes de abrir o agente, ative o ambiente:\n"
                          f"  {venv / 'Scripts' / 'Activate.ps1'}")

    print(f"Cópia isolada pronta: {destino_etapa}")
    print(f"Ambiente virtual: {venv if venv else '—'}{aviso_venv}")
    print("\nPróximos passos:")
    print(f"  cd \"{destino_etapa}\"")
    print("  claude      (ou: opencode / agy)")
    print("e cole o pedido padrão do README.")


if __name__ == "__main__":
    main()
