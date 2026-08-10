from decimal import Decimal


class Valor:
    """Value Object que representa um valor monetário com validações"""
    
    def __init__(self, valor: float | Decimal):
        if isinstance(valor, str):
            valor = Decimal(valor)
        elif isinstance(valor, float):
            valor = Decimal(str(valor))
        
        if not isinstance(valor, Decimal):
            valor = Decimal(valor)
        
        if valor < 0:
            raise ValueError("Valor não pode ser negativo")
        
        # Limita a 2 casas decimais
        self.valor = valor.quantize(Decimal('0.01'))

    def __add__(self, outro):
        if isinstance(outro, Valor):
            return Valor(self.valor + outro.valor)
        return Valor(self.valor + Decimal(str(outro)))

    def __sub__(self, outro):
        if isinstance(outro, Valor):
            return Valor(self.valor - outro.valor)
        return Valor(self.valor - Decimal(str(outro)))

    def __eq__(self, outro):
        if isinstance(outro, Valor):
            return self.valor == outro.valor
        return self.valor == Decimal(str(outro))

    def __lt__(self, outro):
        if isinstance(outro, Valor):
            return self.valor < outro.valor
        return self.valor < Decimal(str(outro))

    def __le__(self, outro):
        if isinstance(outro, Valor):
            return self.valor <= outro.valor
        return self.valor <= Decimal(str(outro))

    def __gt__(self, outro):
        if isinstance(outro, Valor):
            return self.valor > outro.valor
        return self.valor > Decimal(str(outro))

    def __ge__(self, outro):
        if isinstance(outro, Valor):
            return self.valor >= outro.valor
        return self.valor >= Decimal(str(outro))

    def __str__(self):
        return f"R$ {self.valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    
    def __repr__(self):
        return f"Valor({self.valor})"
