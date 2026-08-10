class Descricao:
    """Value Object que representa uma descrição com validações"""
    
    COMPRIMENTO_MINIMO = 3
    COMPRIMENTO_MAXIMO = 1000

    def __init__(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("Descrição não pode ser vazia")
        
        if len(valor) < self.COMPRIMENTO_MINIMO:
            raise ValueError(
                f"Descrição deve ter no mínimo {self.COMPRIMENTO_MINIMO} caracteres"
            )
        
        if len(valor) > self.COMPRIMENTO_MAXIMO:
            raise ValueError(
                f"Descrição não pode exceder {self.COMPRIMENTO_MAXIMO} caracteres"
            )
        
        self.valor = valor.strip()

    def __str__(self):
        return self.valor
    
    def __eq__(self, outro):
        if not isinstance(outro, Descricao):
            return False
        return self.valor == outro.valor
    
    def __repr__(self):
        return f"Descricao('{self.valor}')"
