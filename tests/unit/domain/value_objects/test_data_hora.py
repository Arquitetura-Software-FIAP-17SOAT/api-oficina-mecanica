import dataclasses
from datetime import UTC, datetime, timedelta, timezone

import pytest

from domain.value_objects.data_hora import FUSO_BRASILIA, DataHora


def test_datetime_naive_e_assumido_como_utc():
    """Testa que a data sem fuso, vinda do banco, é tratada como UTC."""

    data = DataHora(datetime(2026, 8, 9, 15, 30))

    assert data.value == datetime(2026, 8, 9, 15, 30, tzinfo=UTC)
    assert data.value.tzinfo is UTC


def test_datetime_com_fuso_e_convertido_para_utc():
    """Testa a normalização de um horário de Brasília para UTC."""

    data = DataHora(datetime(2026, 8, 9, 12, 0, tzinfo=FUSO_BRASILIA))

    assert data.value == datetime(2026, 8, 9, 15, 0, tzinfo=UTC)


def test_aceita_string_iso():
    """Testa a criação a partir de texto ISO 8601."""

    assert DataHora("2026-08-09T15:30:00").value == datetime(
        2026, 8, 9, 15, 30, tzinfo=UTC
    )


def test_fusos_diferentes_do_mesmo_instante_sao_iguais():
    """Testa a igualdade por instante, não por representação."""

    utc = DataHora(datetime(2026, 8, 9, 15, 0, tzinfo=UTC))
    brasilia = DataHora(datetime(2026, 8, 9, 12, 0, tzinfo=FUSO_BRASILIA))
    tokyo = DataHora(
        datetime(2026, 8, 10, 0, 0, tzinfo=timezone(timedelta(hours=9)))
    )

    assert utc == brasilia == tokyo
    assert len({utc, brasilia, tokyo}) == 1


def test_comparacao_entre_naive_e_aware_nao_quebra():
    """Testa que o VO elimina o TypeError de naive vs aware."""

    do_banco = DataHora(datetime(2026, 8, 9, 15, 0))
    do_token = DataHora(datetime(2026, 8, 9, 16, 0, tzinfo=UTC))

    assert do_banco < do_token
    assert max(do_banco, do_token) == do_token


def test_naive_utc_para_persistencia():
    """Testa o formato entregue à coluna TIMESTAMP."""

    data = DataHora(datetime(2026, 8, 9, 12, 0, tzinfo=FUSO_BRASILIA))

    assert data.naive_utc == datetime(2026, 8, 9, 15, 0)
    assert data.naive_utc.tzinfo is None


def test_em_brasilia():
    """Testa a conversão para o fuso de exibição."""

    data = DataHora(datetime(2026, 8, 9, 15, 0, tzinfo=UTC))

    assert data.em_brasilia.hour == 12


def test_agora_e_aware():
    """Testa que o instante atual nasce com fuso."""

    agora = DataHora.agora()

    assert agora.value.tzinfo is UTC
    assert agora.is_passado is True
    assert agora.is_futuro is False


def test_futuro_e_passado():
    """Testa as checagens de posição no tempo."""

    futuro = DataHora(datetime.now(UTC) + timedelta(days=1))
    passado = DataHora(datetime.now(UTC) - timedelta(days=1))

    assert futuro.is_futuro is True
    assert futuro.is_passado is False
    assert passado.is_passado is True


def test_e_imutavel():
    """Testa que o instante não pode ser alterado após a criação."""

    data = DataHora.agora()

    with pytest.raises(dataclasses.FrozenInstanceError):
        data.value = datetime.now(UTC)


@pytest.mark.parametrize("entrada", [None, "ontem", "2026-13-45", 42, object()])
def test_entradas_invalidas(entrada):
    """Testa a rejeição de entradas que não representam uma data."""

    with pytest.raises(ValueError):
        DataHora(entrada)


def test_formatacao_brasileira():
    """Testa a exibição em horário de Brasília."""

    data = DataHora(datetime(2026, 8, 9, 15, 30, tzinfo=UTC))

    assert data.formatado() == "09/08/2026 12:30"
    assert data.data_formatada() == "09/08/2026"


def test_str_devolve_iso():
    """Testa a serialização técnica em ISO 8601."""

    data = DataHora(datetime(2026, 8, 9, 15, 30, tzinfo=UTC))

    assert str(data) == "2026-08-09T15:30:00+00:00"
