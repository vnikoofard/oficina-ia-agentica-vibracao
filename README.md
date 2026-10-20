# Oficina: IA agêntica para resolver problemas de engenharia

Pós-graduação em Engenharia — FEG/UNESP · Prof. Dr. Vahid Nikoofard (FAT/UERJ)

Nesta oficina vamos usar um **agente de IA** (um modelo de linguagem que lê arquivos,
escreve e executa código e verifica o próprio trabalho) para diagnosticar, a partir
de medições brutas de vibração, o estado dos rolamentos de três motores elétricos.
O foco não é a IA "acertar sozinha", e sim o **harness**: a especificação, o
conhecimento de domínio e os testes que transformam um agente genérico em uma
ferramenta de engenharia confiável.

> **Prepare o computador antes do evento (≈ 30 min).** Quem não conseguir instalar
> acompanha a demonstração no telão normalmente.

---

## Antes da oficina

### 1. Python 3.10 ou mais recente

- **Windows:** instale pelo [python.org](https://www.python.org/downloads/) e marque
  **"Add python.exe to PATH"** na primeira tela do instalador.
- **macOS:** `brew install python` ou o instalador do python.org.
- **Linux:** normalmente já vem instalado (`python3 --version`).

### 2. Baixe este repositório

Com Git:

```bash
git clone https://github.com/vnikoofard/oficina-ia-agentica-vibracao
cd oficina-ia-agentica-vibracao
```

Sem Git: em [github.com/vnikoofard/oficina-ia-agentica-vibracao](https://github.com/vnikoofard/oficina-ia-agentica-vibracao), botão **Code → Download ZIP**, e descompacte.

### 3. Crie o ambiente virtual e instale as dependências

Abra um terminal **na pasta do repositório**:

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
> Se o PowerShell bloquear o script de ativação, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Escolha **um** agente de IA (gratuito)

Os dois funcionam com este repositório: ambos leem o arquivo `AGENTS.md`.

**Opção A — OpenCode (terminal, código aberto)**
1. Instale: `npm install -g opencode-ai` (requer Node.js) ou veja outras formas em
   [opencode.ai](https://opencode.ai). No Windows ele roda diretamente, mas a
   documentação recomenda o WSL para a melhor experiência; se o terminal der
   trabalho, prefira a opção B.
2. Rode `opencode`, digite `/models` e escolha um modelo marcado como **Free**.
   Se pedir autenticação, use `/connect` → *OpenCode Zen* e cole a chave criada em
   [opencode.ai/auth](https://opencode.ai/auth).
3. Os modelos gratuitos são promocionais e mudam com frequência. **Vários deles podem
   usar seus prompts para treinamento** — não envie dados confidenciais. Prefira os que
   a página do [OpenCode Zen](https://opencode.ai/docs/zen/) descreve como de retenção
   zero (em outubro de 2026: Space Bunny Free, LongCat 2.5 Preview Free, Step 5 Preview Free).

**Opção B — Google Antigravity (aplicativo com editor + agente)**
1. Baixe em [antigravity.google](https://antigravity.google) (Windows, macOS e Linux)
   e entre com uma conta Google. O uso individual é gratuito, com cotas de uso.
2. Opcional: estudantes universitários podem ativar o plano estudante do Gemini
   ([gemini.google/br/students](https://gemini.google/br/students/?hl=pt-BR)) — atualmente
   12 meses do Google AI Plus sem custo, com verificação de matrícula. **Atenção:** é
   preciso cadastrar forma de pagamento e o plano é renovado automaticamente com cobrança
   ao final do período se não for cancelado. Não é necessário para a oficina.

### 5. Confira se está tudo pronto

```bash
python verificar_ambiente.py
```

---

## Durante a oficina

O mesmo problema é resolvido quatro vezes, **com o mesmo pedido ao agente**. Só o
harness muda de uma etapa para a outra — é um experimento controlado. Na última
etapa, o agente principal vira um **orquestrador** que delega o trabalho a uma
equipe de subagentes.

| Pasta | O que o agente recebe |
|---|---|
| `etapas/0-sem-harness` | só os dados |
| `etapas/1-instrucoes` | + `AGENTS.md` (contexto, contrato de saída, convenções) |
| `etapas/2-skill` | + `skills/vibracao-rolamentos/SKILL.md` (procedimento de engenharia) |
| `etapas/3-orquestracao` | + `tests/`, um plano aprovado por você e uma equipe de subagentes: inspetor, implementador e revisor independente |

**Como rodar cada etapa:** abra o agente **dentro da pasta da etapa**
(ex.: `cd etapas/1-instrucoes` e depois `opencode`; no Antigravity, *Open Folder* nessa pasta)
e envie o pedido abaixo:

```
Analise as medições de vibração da pasta dados/ e diga, para cada motor, se o
rolamento está saudável ou com defeito e, havendo defeito, se ele está na pista
externa ou na pista interna. Informe também a rotação do eixo e as frequências
características do rolamento.
```

Na etapa 3 você mesmo pode conferir: `python -m pytest`.

### Etapa 3: orquestração multi-agente

```
orquestrador ──► inspetor ──► plano ──► você aprova ──► implementador ──► revisor ──► APROVADO
                                                             ▲               │
                                                             └── REPROVADO ──┘
```

- Depois da inspeção, o orquestrador escreve `notas/plano.md` e **para**. Leia o
  plano e responda (por exemplo, `Aprovado, pode seguir.`) ou peça mudanças. Só
  então ele delega a implementação.
- Os papéis estão em `agentes/*.md` (texto comum, vale para qualquer ferramenta).
- **Claude Code** carrega os subagentes de `.claude/agents/`; **OpenCode**, de
  `.opencode/agents/`. Os dois apenas apontam para `agentes/*.md`.
- **Antigravity** cria subagentes dinamicamente: o `AGENTS.md` instrui o
  orquestrador a criá-los a partir de `agentes/*.md`.
- O inspetor e o revisor **não podem editar arquivos** (restrição imposta pela
  ferramenta). Os relatórios deles e o plano ficam em `notas/`.

---

## Estrutura

```
├── requirements.txt
├── verificar_ambiente.py
└── etapas/
    ├── 0-sem-harness/   dados/
    ├── 1-instrucoes/    dados/  AGENTS.md  CLAUDE.md
    ├── 2-skill/         dados/  AGENTS.md  CLAUDE.md  skills/
    └── 3-orquestracao/  dados/  AGENTS.md  CLAUDE.md  skills/  tests/  agentes/  notas/
                         .claude/agents/  .opencode/agents/
```

`CLAUDE.md` apenas importa o `AGENTS.md` (para quem usa Claude Code). O
`.claude/settings.json` da etapa 3 bloqueia, no Claude Code, a edição dos testes e a leitura
do gabarito — um exemplo de regra **imposta pelo harness**, e não apenas pedida ao modelo.

Os dados são **sintéticos**: foram gerados a partir de um modelo físico do
rolamento (impactos que excitam uma ressonância estrutural, harmônicos da rotação
e ruído realista), para que exista um gabarito exato.
