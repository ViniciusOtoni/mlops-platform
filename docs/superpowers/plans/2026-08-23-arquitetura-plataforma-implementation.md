# Arquitetura de Plataforma — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o repositório `mlops-platform` com o reusable workflow de deploy compartilhado (`deploy-bundle.yml`) e a documentação da convenção de repositório de domínio (`platform.yml`), que os quatro repositórios de componente (já emendados em planos separados) e futuros repositórios de domínio vão consumir.

**Architecture:** Sem pacote Python — este repositório é só GitHub Actions (`.github/workflows/deploy-bundle.yml`, com `on: workflow_call`) e documentação. Não há testes automatizados próprios; a verificação real acontece quando um repositório de componente (emendado separadamente) chama o workflow pela primeira vez.

**Tech Stack:** GitHub Actions (reusable workflows), Databricks CLI, Markdown.

---

## Scope Check

Este plano cobre só a criação do `mlops-platform`. As emendas nos quatro repositórios
de componente (rename `dominios/exemplo/` → `examples/`, troca do workflow inline por
um caller deste reusable workflow) são tratadas em planos de emenda próprios, um por
repositório, para não misturar o histórico de mudança de cada um.

## File Structure

```
mlops-platform/
├── README.md
├── .gitignore
├── .github/
│   └── workflows/
│       └── deploy-bundle.yml       # reusable workflow (on: workflow_call)
└── docs/
    ├── superpowers/
    │   ├── specs/2026-08-23-arquitetura-plataforma-design.md   (já commitado)
    │   └── plans/2026-08-23-arquitetura-plataforma-implementation.md (este arquivo)
    └── platform-yml-example/
        └── platform.yml            # exemplo de referência do manifesto de domínio
```

---

## Task 1: Scaffolding do repositório

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Criar `.gitignore`**

```
.DS_Store
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: scaffold mlops-platform repository"
```

---

## Task 2: Reusable workflow de deploy

**Files:**
- Create: `.github/workflows/deploy-bundle.yml`

- [ ] **Step 1: Criar o workflow**

```yaml
# .github/workflows/deploy-bundle.yml
name: Deploy Bundle (reusable)

on:
  workflow_call:
    inputs:
      working-directory:
        description: Caminho do bundle DAB dentro do repositório chamador.
        required: true
        type: string
      bundle-target:
        description: Target do bundle (dev, prod, etc.).
        required: false
        type: string
        default: dev
      python-version:
        required: false
        type: string
        default: "3.11"

jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}

      - name: Install dev dependencies
        run: pip install -r requirements-dev.txt

      - name: Run unit tests
        run: pytest

      - name: Generate resources (if this bundle has a generator)
        run: |
          if [ -f scripts/generate_resources.py ]; then
            python scripts/generate_resources.py
          else
            echo "no scripts/generate_resources.py — skipping"
          fi

      - name: Install Databricks CLI
        uses: databricks/setup-cli@main

      - name: Deploy bundle
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks bundle deploy -t ${{ inputs.bundle-target }} \
            --var="git_commit=${{ github.sha }}" \
            --var="git_branch=${{ github.ref_name }}"
```

- [ ] **Step 2: Validar a sintaxe do YAML localmente**

Run:
```powershell
python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-bundle.yml'))"
```
Expected: sem erro (YAML bem formado). Isto não valida a semântica do
`workflow_call` — essa validação real só acontece na Task 4 deste plano, quando um
repositório de componente o chamar de verdade.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy-bundle.yml
git commit -m "feat: add reusable deploy-bundle workflow"
```

---

## Task 3: Convenção de `platform.yml` e README

**Files:**
- Create: `docs/platform-yml-example/platform.yml`
- Create: `README.md`

- [ ] **Step 1: Criar o exemplo de referência**

```yaml
# docs/platform-yml-example/platform.yml
domain: credito
owner: time-risco-credito
components:
  features:
    package: feature-platform
    version: v0.1.0
  training:
    package: training-platform
    version: v0.1.0
```

- [ ] **Step 2: Escrever o README**

```markdown
# mlops-platform

Repositório guarda-chuva do ecossistema de MLOps no Databricks: hospeda o reusable
workflow de deploy compartilhado e a documentação de arquitetura cross-cutting.

Design completo em
[`docs/superpowers/specs/2026-08-23-arquitetura-plataforma-design.md`](docs/superpowers/specs/2026-08-23-arquitetura-plataforma-design.md).

## Como um repositório usa o reusable workflow

Um repositório com um bundle só:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: ViniciusOtoni/mlops-platform/.github/workflows/deploy-bundle.yml@main
    with:
      working-directory: .
    secrets: inherit
```

Um repositório de domínio com múltiplos bundles (um por componente usado):

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        component: [features, training, serving, monitoring]
    uses: ViniciusOtoni/mlops-platform/.github/workflows/deploy-bundle.yml@main
    with:
      working-directory: ${{ matrix.component }}
    secrets: inherit
```

Cada repositório chamador precisa da sua própria cópia dos secrets
`DATABRICKS_HOST`/`DATABRICKS_TOKEN` — contas pessoais do GitHub não compartilham
secrets entre repositórios automaticamente.

## `platform.yml`

Todo repositório de domínio declara um `platform.yml` na raiz — ver exemplo em
[`docs/platform-yml-example/platform.yml`](docs/platform-yml-example/platform.yml).
Sem enforcement automatizado no v1: é convenção documentada, não validada por CI.

## Versionamento dos pacotes-framework

Manual, via tag semver em cada um dos quatro repositórios de componente
(`feature-platform`, `training-platform`, `serving-platform`,
`monitoring-platform`). Um domínio referencia a tag exata que testou.
```

- [ ] **Step 3: Commit**

```bash
git add docs/platform-yml-example/platform.yml README.md
git commit -m "docs: add platform.yml convention example and usage README"
```

---

## Task 4: Verificação (dependente das emendas nos repositórios de componente)

Este repositório, sozinho, não tem como se autoverificar — um reusable workflow só é
exercitado por quem o chama.

- [ ] **Step 1:** Depois que a emenda do `feature-platform` (plano de emenda próprio)
  trocar seu `.github/workflows/deploy.yml` para chamar
  `ViniciusOtoni/mlops-platform/.github/workflows/deploy-bundle.yml@main`, confirmar
  no GitHub Actions do `feature-platform` que o job de deploy é resolvido corretamente
  (a interface `workflow_call` é reconhecida, os inputs chegam, o secret é herdado).

- [ ] **Step 2:** Se `secrets: inherit` não propagar como documentado na seção 4 do
  spec (risco listado na seção 7), documentar o comportamento real encontrado no spec
  deste repositório e ajustar — por exemplo, passando os secrets explicitamente via
  `secrets:` com mapeamento nomeado, em vez de `inherit`.

---

## Self-Review

**1. Cobertura do spec:** reusable workflow com o contrato exato de inputs/secrets
descrito (Task 2), convenção de `platform.yml` documentada com exemplo (Task 3),
versionamento manual documentado no README (Task 3). O spec também define a
arquitetura de repositório de domínio (seção 5) — isso não gera um artefato de código
neste repositório, é documentação de convenção para quando o primeiro domínio real
existir; coberto pelo README, sem necessidade de uma task adicional.

**2. Placeholders:** nenhum "TBD"/"TODO". A dependência de verificação em outro
repositório (Task 4) está documentada como tal, com um passo de contingência
explícito caso o comportamento assumido de `secrets: inherit` não se confirme.

**3. Consistência:** o contrato de inputs do workflow (`working-directory`,
`bundle-target`, `python-version`) é o mesmo descrito no spec e usado nos dois
exemplos do README — sem divergência de nomes entre os documentos.

---

Plano completo e salvo em
`docs/superpowers/plans/2026-08-23-arquitetura-plataforma-implementation.md`.
