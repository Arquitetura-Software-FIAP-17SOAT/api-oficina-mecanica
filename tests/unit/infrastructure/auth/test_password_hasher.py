from infrastructure.auth.password_hasher import BCryptPasswordHasher


def test_hash_gera_valor_diferente_da_senha_original():
    hasher = BCryptPasswordHasher()

    hashed = hasher.hash("minha-senha-secreta")

    assert hashed != "minha-senha-secreta"
    assert isinstance(hashed, str)


def test_verify_aceita_senha_correta():
    hasher = BCryptPasswordHasher()
    hashed = hasher.hash("minha-senha-secreta")

    assert hasher.verify("minha-senha-secreta", hashed) is True


def test_verify_rejeita_senha_incorreta():
    hasher = BCryptPasswordHasher()
    hashed = hasher.hash("minha-senha-secreta")

    assert hasher.verify("senha-errada", hashed) is False
