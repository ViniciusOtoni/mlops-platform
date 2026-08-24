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
