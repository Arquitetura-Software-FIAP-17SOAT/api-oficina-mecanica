from datetime import datetime

from domain.value_objects.chassi import Chassi
from domain.value_objects.data_hora import DataHora
from domain.value_objects.placa import Placa


class Veiculo:
    MODELO_MAX_LENGTH = 100
    CHASSI_MAX_LENGTH = 30
    ANO_MINIMO = 1900

    def __init__(
        self,
        cliente_id: int,
        marca_id: int,
        placa: Placa | str,
        modelo: str,
        chassi: Chassi | str | None = None,
        ano_fabricacao: int | None = None,
        id: int | None = None,
        criado_em: DataHora | datetime | str | None = None,
    ):
        self.id = id
        self.cliente_id = self._validar_referencia(cliente_id, "O cliente")
        self.marca_id = self._validar_referencia(marca_id, "A marca")
        self.placa = Placa(placa)
        self.modelo = self._validar_modelo(modelo)
        self.chassi = self._validar_chassi(chassi)
        self.ano_fabricacao = self._validar_ano(ano_fabricacao)
        self.criado_em = DataHora(criado_em) if criado_em is not None else None

    @staticmethod
    def _validar_referencia(valor: int, rotulo: str) -> int:
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValueError(f"{rotulo} deve ser informado.")

        if valor <= 0:
            raise ValueError(f"{rotulo} informado é inválido.")

        return valor

    @classmethod
    def _validar_modelo(cls, modelo: str) -> str:
        if not modelo or not modelo.strip():
            raise ValueError("O modelo deve ser preenchido.")

        modelo = modelo.strip()

        if len(modelo) > cls.MODELO_MAX_LENGTH:
            raise ValueError(
                "O modelo deve possuir no máximo "
                f"{cls.MODELO_MAX_LENGTH} caracteres."
            )

        return modelo

    @staticmethod
    def _validar_chassi(chassi: Chassi | str | None) -> Chassi | None:
        if chassi is None:
            return None

        if isinstance(chassi, str) and not chassi.strip():
            return None

        return Chassi(chassi)

    @classmethod
    def _validar_ano(cls, ano_fabricacao: int | None) -> int | None:
        if ano_fabricacao is None:
            return None

        if not isinstance(ano_fabricacao, int) or isinstance(
            ano_fabricacao, bool
        ):
            raise ValueError("O ano de fabricação deve ser um número inteiro.")

        ano_maximo = DataHora.agora().em_brasilia.year + 1

        if not cls.ANO_MINIMO <= ano_fabricacao <= ano_maximo:
            raise ValueError(
                "O ano de fabricação deve estar entre "
                f"{cls.ANO_MINIMO} e {ano_maximo}."
            )

        return ano_fabricacao

    def change_placa(self, placa: Placa | str) -> None:
        self.placa = Placa(placa)

    def change_modelo(self, modelo: str) -> None:
        self.modelo = self._validar_modelo(modelo)

    def change_chassi(self, chassi: Chassi | str | None) -> None:
        self.chassi = self._validar_chassi(chassi)

    def change_ano_fabricacao(self, ano_fabricacao: int | None) -> None:
        self.ano_fabricacao = self._validar_ano(ano_fabricacao)

    def change_marca(self, marca_id: int) -> None:
        self.marca_id = self._validar_referencia(marca_id, "A marca")
