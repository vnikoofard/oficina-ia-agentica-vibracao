# Projeto: diagnóstico de rolamentos por vibração

## Contexto

Você atua como assistente de uma equipe de manutenção preditiva industrial.
A pasta `dados/` contém medições brutas de vibração de três motores elétricos
(`M1`, `M2`, `M3`), exportadas por um coletor de dados: um canal de aceleração
medido no mancal dianteiro e um canal de tacômetro.

## Objetivo

Para cada motor, determinar:

- a rotação real do eixo;
- as frequências características de defeito do rolamento: pista externa (BPFO)
  e pista interna (BPFI);
- o diagnóstico do rolamento: saudável, defeito na pista externa ou defeito na
  pista interna;
- quando houver defeito, a frequência de defeito efetivamente medida no sinal.

## Contrato de saída (obrigatório)

1. Todo o cálculo fica em `src/analise_vibracao.py`, executável assim:

   ```
   python src/analise_vibracao.py --dados dados --saida resultados
   ```

2. `resultados/results.json`, exatamente neste formato (uma chave por motor):

   ```json
   {
     "M1": {
       "rotacao_Hz": 0.0,
       "BPFO_Hz": 0.0,
       "BPFI_Hz": 0.0,
       "diagnostico": "saudavel | pista_externa | pista_interna",
       "frequencia_defeito_Hz": null,
       "faixa_analise_Hz": [0.0, 0.0]
     }
   }
   ```

   - `frequencia_defeito_Hz` é `null` quando o diagnóstico é `saudavel`.
   - `faixa_analise_Hz` é a faixa de frequências do sinal de aceleração em que
     você baseou a detecção do defeito, `[inferior, superior]`, em Hz.

3. `resultados/<motor>.png`: para cada motor, um trecho do sinal no tempo, o
   espectro e o gráfico em que o diagnóstico se baseia, com as frequências
   características marcadas.

4. `resultados/relatorio.md`: tabela com os resultados e um parágrafo curto
   por motor justificando o diagnóstico.

## Convenções

- **Trabalhe só com os arquivos desta pasta.** Não leia, liste nem altere nada
  fora dela (pastas vizinhas, pasta-mãe, outros projetos). A única exceção é
  usar o Python do ambiente virtual indicado abaixo. Se o ambiente não existir,
  não crie outro nem procure um pelo computador: pare e avise que é preciso
  criar o `.venv` na raiz do repositório (passo 3 do README).
- Frequências em Hz; aceleração em g.
- Nunca altere nada em `dados/`.
- Bibliotecas disponíveis: `numpy`, `pandas`, `scipy`, `matplotlib`. Não instale pacotes.
- Use o Python do ambiente virtual do repositório (`.venv` na raiz). Se o terminal
  não estiver com o ambiente ativado, chame-o diretamente:
  Windows `..\..\.venv\Scripts\python.exe`, Linux/macOS `../../.venv/bin/python`.

## Como trabalhar

1. Antes de escrever código, abra os arquivos de dados e descreva o que encontrou
   (formato, canais, unidades, metadados, anomalias).
2. Apresente um plano curto e só então implemente.
3. Rode o script, abra os gráficos gerados e confira se os resultados fazem
   sentido fisicamente antes de declarar a tarefa concluída.
4. No final, liste as hipóteses e decisões que você tomou.
