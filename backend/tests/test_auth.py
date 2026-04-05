from app.auth import get_password_hash, verify_password

def test_password_hashing():
    password = "minha_senha_segura"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("senha_errada", hashed) == False
