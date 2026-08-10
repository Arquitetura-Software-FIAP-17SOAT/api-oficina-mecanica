class Email:
    def __init__(self, value: str):
        if "@" not in value:
            raise ValueError("E-mail inválido")

        self.value = value.lower()

    def __str__(self):
        return self.value