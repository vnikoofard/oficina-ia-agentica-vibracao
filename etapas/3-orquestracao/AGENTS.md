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
  não crie outro nem procure um pelo computador: pare e avise.
- Frequências em Hz; aceleração em g.
- Nunca altere nada em `dados/`.
- Bibliotecas disponíveis: `numpy`, `pandas`, `scipy`, `matplotlib`. Não instale pacotes.
- Use o Python do ambiente virtual do repositório (`.venv` na raiz). Se o terminal
  não estiver com o ambiente ativado, chame-o diretamente:
  Windows `..\..\.venv\Scripts\python.exe`, Linux/macOS `../../.venv/bin/python`.

## Como trabalhar: você é o orquestrador

> Se você é um subagente (`inspetor`, `implementador` ou `revisor`), ignore esta
> seção e siga o seu arquivo em `agentes/`.

Nesta pasta o trabalho é feito por uma **equipe de agentes**. Você planeja e
coordena; quem lê os dados, programa e revisa são subagentes, cada um com o seu papel
descrito em `agentes/`:

| Subagente | Papel | Pode editar arquivos? |
|---|---|---|
| `inspetor` | descreve os dados brutos (`agentes/inspetor.md`) | não |
| `implementador` | escreve e roda `src/analise_vibracao.py` seguindo a skill (`agentes/implementador.md`) | sim |
| `revisor` | verifica o código contra a skill e roda os testes (`agentes/revisor.md`) | não |

Fluxo obrigatório:

1. Delegue ao **inspetor** a inspeção de `dados/`. Salve o relatório dele em
   `notas/inspecao.md`.
2. **Planeje e espere aprovação.** Com base em `notas/inspecao.md` e na skill,
   escreva `notas/plano.md` com:
   - o pedido, entendido em até três linhas;
   - o que cada subagente vai receber e entregar;
   - os critérios de aceite: o contrato de saída e os testes;
   - as armadilhas dos dados que a inspeção encontrou e como cada uma será
     tratada;
   - dúvidas, se houver.

   Mostre um resumo do plano e **pare**. Não delegue a implementação até a
   pessoa responder aprovando. Se ela pedir mudanças, revise `notas/plano.md`
   e pergunte de novo.
3. Delegue ao **implementador** a implementação. Diga a ele para ler
   `notas/plano.md`, `notas/inspecao.md` e a skill.
4. Delegue ao **revisor** a revisão. Salve o relatório dele em `notas/revisao.md`.
5. Se o veredito for `REPROVADO`, delegue de novo ao implementador, pedindo que
   corrija os problemas de `notas/revisao.md`, e depois ao revisor. No máximo
   3 rodadas; se ainda houver falhas, pare e explique.
6. Quando o veredito for `APROVADO`, apresente um resumo final: os resultados
   por motor, quantas rodadas foram necessárias, o que cada subagente fez e se
   algo saiu diferente do plano aprovado.

Regras do orquestrador:

- Você **não** escreve nem corrige o código de análise: isso é do implementador.
  Você só escreve em `notas/`.
- Ao delegar, passe ao subagente só o que ele precisa (o papel dele e os arquivos
  a ler). Cada subagente começa sem o histórico desta conversa — de propósito.
- Se a sua ferramenta não carregar os subagentes de `.claude/agents/` ou
  `.opencode/agents/`, crie subagentes com as instruções de `agentes/*.md`.
  Se ela não oferecer subagentes, execute os papéis em sequência, relendo o
  arquivo do papel antes de cada um e sem reaproveitar conclusões do papel
  anterior; diga no resumo final que foi assim.

## Conhecimento de domínio (skill)

Antes de qualquer análise de vibração, **leia e siga**
`skills/vibracao-rolamentos/SKILL.md`. Ela define o procedimento e as
armadilhas conhecidas destes arquivos.

- Em caso de conflito entre a sua intuição e a skill, a skill vence.
- Se achar que a skill está errada ou incompleta para algum caso, diga isso
  explicitamente no relatório em vez de desviar dela em silêncio.

## Regras invioláveis (valem para todos os agentes)

- **Não** edite, apague, renomeie nem leia o conteúdo de nada em `tests/`.
  Os testes e o gabarito são a referência externa; ajustar a referência para
  passar no teste invalida todo o trabalho.
- **Não** escreva números à mão em `resultados/results.json`: ele precisa sair
  do script. Um dos testes executa o script de novo e compara as saídas.
- Não relaxe critérios da skill só para acertar um teste; se um teste parecer
  incompatível com a skill, relate a contradição.
