"""
Testes de verificação do diagnóstico de rolamentos.

NÃO EDITE ESTE ARQUIVO. Ele é a referência externa do trabalho do agente.

Três camadas:
  1. contrato   – os arquivos existem e o JSON segue o formato combinado;
  2. física     – os números são consistentes entre si (independe do gabarito);
  3. gabarito   – os números e diagnósticos batem com a referência, dentro de tolerâncias;
  + reprodutibilidade – o results.json precisa sair do script, não da mão de alguém.
"""
from __future__ import annotations

import base64
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
RES = RAIZ / "resultados"
MOTORES = ["M1", "M2", "M3"]
NUMERICOS = ["rotacao_Hz", "BPFO_Hz", "BPFI_Hz"]
CHAVES = NUMERICOS + ["diagnostico", "frequencia_defeito_Hz", "banda_demodulacao_Hz"]
DIAGNOSTICOS = {"saudavel", "pista_externa", "pista_interna"}
FS = 25600.0

# tolerâncias relativas
TOL = {"rotacao_Hz": 0.003, "BPFO_Hz": 0.003, "BPFI_Hz": 0.003}
TOL_DEFEITO = 0.006


def _gabarito():
    txt = (Path(__file__).parent / "gabarito.b64").read_text(encoding="ascii").strip()
    return json.loads(base64.b64decode(txt).decode("utf-8"))


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _mensagem(nome, erro, tol):
    direcao = "ACIMA" if erro > 0 else "ABAIXO"
    faixa = "muito" if abs(erro) > 5 * tol else "um pouco"
    return (f"{nome}: valor {faixa} {direcao} do esperado (tolerância ±{100 * tol:.1f} %). "
            f"Revise o procedimento da skill para esta grandeza.")


@pytest.fixture(scope="session")
def resultados():
    arq = RES / "results.json"
    if not arq.exists():
        pytest.fail("resultados/results.json não existe. Rode: "
                    "python src/analise_vibracao.py --dados dados --saida resultados")
    return json.loads(arq.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- contrato

def test_script_existe():
    assert (RAIZ / "src" / "analise_vibracao.py").exists(), "falta src/analise_vibracao.py"


def test_arquivos_de_saida(resultados):
    assert (RES / "relatorio.md").exists(), "falta resultados/relatorio.md"
    for m in MOTORES:
        assert (RES / f"{m}.png").exists(), f"falta resultados/{m}.png"


@pytest.mark.parametrize("m", MOTORES)
def test_formato_json(resultados, m):
    assert m in resultados, f"{m} ausente em results.json"
    r = resultados[m]
    faltando = [k for k in CHAVES if k not in r]
    assert not faltando, f"{m}: chaves ausentes {faltando}"
    for k in NUMERICOS:
        assert _num(r[k]), f"{m}.{k} não é número finito"
    assert r["diagnostico"] in DIAGNOSTICOS, f"{m}.diagnostico deve ser um de {sorted(DIAGNOSTICOS)}"
    f = r["frequencia_defeito_Hz"]
    assert f is None or _num(f), f"{m}.frequencia_defeito_Hz deve ser número ou null"
    b = r["banda_demodulacao_Hz"]
    assert isinstance(b, list) and len(b) == 2 and all(_num(v) for v in b), \
        f"{m}.banda_demodulacao_Hz deve ser [inferior, superior]"


# ---------------------------------------------------------------- física

@pytest.mark.parametrize("m", MOTORES)
def test_consistencia_fisica(resultados, m):
    r = resultados[m]
    n = _gabarito()[m]["N_elementos"]
    fr, bo, bi = r["rotacao_Hz"], r["BPFO_Hz"], r["BPFI_Hz"]
    assert bo < bi, f"{m}: BPFO deveria ser menor que BPFI"
    assert abs(bo + bi - n * fr) <= 0.002 * n * fr, \
        f"{m}: BPFO + BPFI deveria ser igual a N·f_r (identidade cinemática)"
    lo, hi = r["banda_demodulacao_Hz"]
    assert 0 < lo < hi <= FS / 2, f"{m}: banda de demodulação fora de (0, fs/2]"
    f = r["frequencia_defeito_Hz"]
    if r["diagnostico"] == "saudavel":
        assert f is None, f"{m}: motor saudável não tem frequência de defeito (use null)"
    else:
        ref = bo if r["diagnostico"] == "pista_externa" else bi
        assert f is not None and 0.90 * ref <= f <= 1.05 * ref, \
            f"{m}: frequência de defeito incompatível com a frequência característica do diagnóstico"


# ---------------------------------------------------------------- gabarito

@pytest.mark.parametrize("m", MOTORES)
@pytest.mark.parametrize("grandeza", list(TOL))
def test_gabarito(resultados, m, grandeza):
    esperado = _gabarito()[m][grandeza]
    obtido = resultados[m][grandeza]
    erro = (obtido - esperado) / esperado
    if abs(erro) > TOL[grandeza]:
        pytest.fail(_mensagem(f"{m}.{grandeza}", erro, TOL[grandeza]))


@pytest.mark.parametrize("m", MOTORES)
def test_diagnostico(resultados, m):
    assert resultados[m]["diagnostico"] == _gabarito()[m]["diagnostico"], \
        f"{m}: diagnóstico incorreto"


@pytest.mark.parametrize("m", MOTORES)
def test_frequencia_defeito(resultados, m):
    esperado = _gabarito()[m]["frequencia_defeito_Hz"]
    obtido = resultados[m]["frequencia_defeito_Hz"]
    if esperado is None:
        assert obtido is None, f"{m}: não deveria haver frequência de defeito"
        return
    assert _num(obtido), f"{m}: frequência de defeito ausente"
    erro = (obtido - esperado) / esperado
    if abs(erro) > TOL_DEFEITO:
        pytest.fail(_mensagem(f"{m}.frequencia_defeito_Hz", erro, TOL_DEFEITO))


@pytest.mark.parametrize("m", MOTORES)
def test_banda_demodulacao(resultados, m):
    fn = _gabarito()[m]["ressonancia_Hz"]
    if fn is None:
        return
    lo, hi = resultados[m]["banda_demodulacao_Hz"]
    assert lo <= fn <= hi, f"{m}: a banda escolhida não contém a ressonância excitada pelos impactos"


# ---------------------------------------------------------------- reprodutibilidade

def test_reprodutibilidade(resultados, tmp_path):
    proc = subprocess.run(
        [sys.executable, "src/analise_vibracao.py", "--dados", "dados", "--saida", str(tmp_path)],
        cwd=RAIZ, capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, f"o script falhou:\n{proc.stderr[-2000:]}"
    novo = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    for m in MOTORES:
        for k in NUMERICOS:
            assert math.isclose(novo[m][k], resultados[m][k], rel_tol=1e-6), \
                f"{m}.{k}: results.json não corresponde à saída atual do script"
        assert novo[m]["diagnostico"] == resultados[m]["diagnostico"], \
            f"{m}.diagnostico: results.json não corresponde à saída atual do script"
