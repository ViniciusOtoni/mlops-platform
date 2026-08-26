#!/usr/bin/env python3
"""Falha se a tag '<nome-do-pacote>-v<versao>' do pyproject.toml já existir no
repositório — pré-requisito pro release automático (CD) conseguir criar uma
tag nova a cada merge: sem isso, todo PR precisa vir com bump de versão."""

import subprocess
import sys
import tomllib
from pathlib import Path


def main() -> int:
    working_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    pyproject_path = working_dir / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    name = data["project"]["name"]
    version = data["project"]["version"]
    tag = f"{name}-v{version}"

    subprocess.run(["git", "fetch", "--tags", "--quiet"], check=True)
    existing = subprocess.run(
        ["git", "tag", "-l", tag], capture_output=True, text=True, check=True
    ).stdout.strip()

    if existing == tag:
        print(
            f"::error::A tag '{tag}' já existe. Faça bump da versão em "
            f'{pyproject_path} antes de mergear (version = "{version}" já foi lançada).'
        )
        return 1

    print(f"OK: '{tag}' ainda não existe, pronto para release em '{name}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
