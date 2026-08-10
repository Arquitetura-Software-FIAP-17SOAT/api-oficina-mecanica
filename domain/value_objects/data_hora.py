from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone

FUSO_BRASILIA = timezone(timedelta(hours=-3))


@dataclass(frozen=True, order=True)
class DataHora:
    """Instante no tempo, sempre normalizado para UTC."""

    value: datetime

    def __post_init__(self):
        object.__setattr__(self, "value", self._validar(self.value))

    @staticmethod
    def _validar(valor) -> datetime:
        if valor is None:
            raise ValueError("A data deve ser preenchida.")

        if isinstance(valor, DataHora):
            return valor.value

        if isinstance(valor, str):
            try:
                valor = datetime.fromisoformat(valor)
            except ValueError:
                raise ValueError(
                    "A data informada não está em um formato válido."
                )

        if not isinstance(valor, datetime):
            raise ValueError("A data informada não é válida.")

        if valor.tzinfo is None:
            return valor.replace(tzinfo=UTC)

        return valor.astimezone(UTC)

    @classmethod
    def agora(cls) -> "DataHora":
        return cls(datetime.now(UTC))

    @property
    def naive_utc(self) -> datetime:
        """Formato aceito por colunas TIMESTAMP WITHOUT TIME ZONE."""
        return self.value.replace(tzinfo=None)

    @property
    def em_brasilia(self) -> datetime:
        return self.value.astimezone(FUSO_BRASILIA)

    @property
    def is_passado(self) -> bool:
        return self.value < datetime.now(UTC)

    @property
    def is_futuro(self) -> bool:
        return self.value > datetime.now(UTC)

    def formatado(self) -> str:
        return self.em_brasilia.strftime("%d/%m/%Y %H:%M")

    def data_formatada(self) -> str:
        return self.em_brasilia.strftime("%d/%m/%Y")

    def __str__(self) -> str:
        return self.value.isoformat()
