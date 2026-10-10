import os
from pathlib import Path
from cryptography.fernet import Fernet
from encrypt_at_rest import encrypt_blob, decrypt_blob

def test_ciphertext_not_plaintext(tmp_path):
    os.environ["LOCAL_FERNET_KEY"] = Fernet.generate_key().decode()
    f = tmp_path / "x.enc"
    encrypt_blob(b"patient: chest pain", f)
    assert b"chest pain" not in f.read_bytes()
    assert decrypt_blob(f) == b"patient: chest pain"