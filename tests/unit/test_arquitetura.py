import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]

CAMADAS = ("domain", "application", "adapters", "presentation")
FRAMEWORKS = ("sqlalchemy", "fastapi", "pydantic", "passlib", "jose")

# Camada -> pacotes que ela NÃO pode importar (regra de dependência: de fora para dentro).
PROIBIDOS = {
    "domain": ("application", "adapters", "presentation") + FRAMEWORKS,
    "application": ("adapters", "presentation") + FRAMEWORKS,
    "adapters": ("presentation",),
}

# Apenas a composição das dependências conhece os adaptadores. A autenticação
# (auth_dependencies.py) fica de fora de propósito: usa a porta TokenDecoder.
PRESENTATION_PODE_IMPORTAR_ADAPTERS = {
    "presentation/dependencies/dependencies.py",
    "presentation/dependencies/cliente_dependencies.py",
    "presentation/dependencies/insumo_dependencies.py",
    "presentation/dependencies/servico_dependencies.py",
    "presentation/dependencies/veiculo_dependencies.py",
    "presentation/dependencies/integracao_dependencies.py",
}


def _imports(arquivo: Path) -> set[str]:
    modulos = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            modulos.add(no.module.split(".")[0])
    return modulos


def _arquivos(camada: str):
    return sorted((RAIZ / camada).rglob("*.py"))


@pytest.mark.parametrize("camada", PROIBIDOS)
def test_camada_nao_importa_camadas_externas(camada):
    violacoes = [
        f"{arquivo.relative_to(RAIZ)} importa {modulo}"
        for arquivo in _arquivos(camada)
        for modulo in _imports(arquivo) & set(PROIBIDOS[camada])
    ]

    assert not violacoes, "\n".join(violacoes)


def test_presentation_so_acessa_adapters_na_composicao_de_dependencias():
    violacoes = [
        f"{arquivo.relative_to(RAIZ)} importa adapters"
        for arquivo in _arquivos("presentation")
        if "adapters" in _imports(arquivo)
        and arquivo.relative_to(RAIZ).as_posix()
        not in PRESENTATION_PODE_IMPORTAR_ADAPTERS
    ]

    assert not violacoes, "\n".join(violacoes)


def test_presentation_nao_depende_da_biblioteca_de_jwt():
    violacoes = [
        f"{arquivo.relative_to(RAIZ)} importa jose"
        for arquivo in _arquivos("presentation")
        if "jose" in _imports(arquivo)
    ]

    assert not violacoes, "\n".join(violacoes)


def test_rotas_nao_definem_schemas_pydantic():
    """Requests/responses ficam em presentation/api/schemas, não nos endpoints."""
    violacoes = []
    for arquivo in _arquivos("presentation/api/routes"):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.ClassDef) and any(
                isinstance(base, ast.Name) and base.id == "BaseModel"
                for base in no.bases
            ):
                violacoes.append(f"{arquivo.relative_to(RAIZ)} define {no.name}")

    assert not violacoes, "\n".join(violacoes)

