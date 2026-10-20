---
name: vibracao-rolamentos
description: Procedimento para diagnosticar defeitos de pista externa e pista interna em rolamentos a partir de sinais brutos de aceleração e tacômetro, pela análise de envelope (demodulação) com banda escolhida por curtose.
---

# Skill: diagnóstico de rolamentos por análise de envelope

Siga os passos na ordem. Cada passo traz uma **armadilha** conhecida destes arquivos.

## 1. Leitura do arquivo

- Codificação **Windows-1252** (`encoding="cp1252"`); separador `;`; decimal `,`.
- O arquivo começa com linhas de **metadados** `chave;valor`. A tabela começa
  na linha que inicia com `Aceleração`.
- Canal 1: aceleração em g. Canal 2: tacômetro em V (1 pulso por volta).
- Não há coluna de tempo: `t = n / fs`.

> Armadilha: a **taxa de amostragem está em kHz** (`25,6` = 25 600 Hz).
> Lida como Hz, todas as frequências ficam 1000 vezes erradas.

## 2. Rotação real do eixo (tacômetro)

- Detecte as bordas de subida do tacômetro (cruzamento de 2,5 V de baixo para cima).
- `f_r = (n_bordas − 1) / (t_última − t_primeira)` em Hz.

> Armadilha: **nunca use a rotação de placa**. Motor de indução gira com
> escorregamento que depende da carga; a rotação real difere da de placa em 1–2 %.

## 3. Frequências características do rolamento

Com `N` elementos rolantes, diâmetro do elemento `d`, diâmetro primitivo `D` e
ângulo de contato `φ`:

```
r    = d · cos(φ) / D
BPFO = (N/2) · f_r · (1 − r)      # passagem de elementos pela pista externa
BPFI = (N/2) · f_r · (1 + r)      # passagem de elementos pela pista interna
FTF  = (f_r/2) · (1 − r)          # gaiola
BSF  = (D / 2d) · f_r · (1 − r²)  # rotação do elemento
```

Verificação obrigatória: `BPFO + BPFI = N · f_r`.

> Armadilha: **φ está em graus**. `np.cos(15)` usa radianos e inverte o sinal de r,
> o que praticamente troca BPFO e BPFI.

## 4. Por que não diagnosticar pelo espectro bruto

O defeito gera impactos curtos que excitam uma **ressonância estrutural** de
alguns kHz. No espectro bruto, a energia dos impactos aparece em kHz, não em BPFO.
Na faixa de BPFO/BPFI o espectro bruto mostra harmônicos da rotação (1×–4×) e a
componente elétrica de 120 Hz, que podem cair perto das frequências de defeito.

> Armadilha: procurar um pico em BPFO/BPFI no espectro bruto produz falsos
> alarmes e deixa passar defeitos reais. Use o espectro bruto só como referência.

## 5. Escolha da banda de demodulação (curtose)

- Remova a média do sinal.
- Para bandas de 1000 Hz de largura com centros de 1500 Hz a 10 000 Hz, a cada 500 Hz:
  filtre com Butterworth passa-banda de ordem 4 aplicado sem defasagem
  (`scipy.signal.butter(..., output="sos")` + `sosfiltfilt`) e calcule a
  **curtose** do sinal filtrado (`scipy.stats.kurtosis(..., fisher=False)`; ruído
  gaussiano dá ≈ 3, impactos dão > 3).
- Use a banda de **maior curtose**.

> Armadilha: **não escolha a banda pela energia**. Há uma ressonância de ruído em
> torno de 7–8 kHz com muita energia e nenhum impacto (curtose ≈ 3); demodular ali
> esconde o defeito.

## 6. Envelope e espectro do envelope

- Sinal analítico do sinal filtrado: `z = scipy.signal.hilbert(x_filtrado)`;
  envelope `e = |z|`; remova a média.
- Espectro de amplitude do envelope com janela de Hann:
  `A = 2·|rfft(e·w)| / Σw`, `f = rfftfreq(n, 1/fs)`.
- Resolução: `Δf = fs / n` (com 4 s de sinal, 0,25 Hz).

> Armadilha: tirar o envelope **sem** filtrar antes: os harmônicos de rotação de
> baixa frequência dominam o envelope e mascaram o defeito.

## 7. Detecção e classificação

- Nível de referência: `ref = mediana(A)` na faixa `[0,5·BPFO, 1,5·BPFI]`.
- Para cada candidata (BPFO → pista externa; BPFI → pista interna), procure o
  maior pico de `A` na janela `[0,95, 1,02] × frequência teórica`
  (o escorregamento dos elementos faz a frequência real ficar ligeiramente
  **abaixo** da teórica) e calcule `razão = pico / ref`.
- A candidata de maior razão é o diagnóstico se `razão ≥ 8`; caso contrário, `saudavel`.
- Frequência do defeito: refine o pico por **interpolação parabólica** dos
  logaritmos das amplitudes nos três bins em torno do máximo.

> Armadilha: reportar a frequência **teórica** como medida. A diferença
> (1–2 %) é informação de diagnóstico e precisa ser medida.

Confirmações (para o relatório): harmônico 2× do defeito; na pista interna,
bandas laterais em `BPFI ± f_r` (o defeito gira com o eixo e entra e sai da zona
de carga a cada volta).

## 8. Gráficos e conferência final

Para cada motor: trecho do sinal bruto; espectro bruto até 1 kHz com 1×–4×,
BPFO e BPFI marcados; espectro do envelope até ~3·BPFI com k·BPFO e k·BPFI
marcados e o pico detectado destacado.

Conferências antes de concluir: `BPFO + BPFI = N·f_r`; BPFO < BPFI; banda
abaixo de fs/2; frequência medida dentro da janela da teórica; `null` para
motores saudáveis.
