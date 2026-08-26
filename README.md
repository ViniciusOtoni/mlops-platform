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

## Versionamento do framework

O framework é um pacote só — [`mlplatform`](https://github.com/ViniciusOtoni/platform-libs) —
e tem uma versão só. Os quatro repositórios de componente que existiam antes
(`feature-platform`, `training-platform`, `serving-platform`, `monitoring-platform`)
foram consolidados e removidos; o histórico de todos está preservado no
`platform-libs`.

O versionamento é automatizado pelos reusable workflows deste repositório: o
`ci-validate.yml` bloqueia o merge se a versão do `pyproject.toml` não tiver sido
incrementada em relação à última tag, e o `release-package.yml` publica a tag
`mlplatform-vX.Y.Z` com o wheel anexado ao Release.

Domínios pinam a versão **exata** (`@mlplatform-vX.Y.Z`), nunca um range. Com um
pacote único, é isso que preserva a capacidade de cada bundle subir em momento
diferente — antes esse isolamento vinha de graça, porque cada componente tinha a
sua própria versão.

## Contrato de arquitetura do framework

O `ruff.toml` deste repositório é a configuração de lint compartilhada por todo o
ecossistema, e é também onde mora o contrato de fronteiras do `mlplatform`:

- **Os bounded contexts não se importam entre si.** `features`, `training`,
  `serving` e `monitoring` só compartilham código através do `core/`. Sem isso, a
  consolidação num pacote só reintroduziria em semanas o acoplamento que os quatro
  repositórios separados evitavam por construção.
- **O `core/` não importa contexto nenhum.** É shared kernel: quem depende dele é
  quem está acima, nunca o contrário.

Uma terceira regra — o `core/` não pode importar infraestrutura (`pyspark`,
`mlflow`, `sklearn`, `databricks.*`) — ainda **não** está imposta, porque
`core/audit.py` viola: ele importa `pyspark.sql.functions` dentro de
`get_last_success_checkpoint`. Essa função é infraestrutura morando no kernel, e a
regra entra junto com a extração dela para um adapter.
