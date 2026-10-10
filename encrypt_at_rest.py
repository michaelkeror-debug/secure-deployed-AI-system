"""Minimal at-rest sketch: a Fernet key from the environment encrypts a secrets blob."""
import os
from pathlib import Path
from cryptography.fernet import Fernet


def load_key() -> bytes:
    raw = os.getenv('LOCAL_FERNET_KEY')
    if not raw:
        raise SystemExit('missing LOCAL_FERNET_KEY (generate with Fernet.generate_key())')
    return raw.encode() if isinstance(raw, str) else raw


def encrypt_blob(plain: bytes, out: Path) -> None:
    token = Fernet(load_key()).encrypt(plain)
    out.write_bytes(token)


def decrypt_blob(path: Path) -> bytes:
    return Fernet(load_key()).decrypt(path.read_bytes())


if __name__ == '__main__':
    Path('secrets').mkdir(exist_ok=True)
    if not os.getenv('LOCAL_FERNET_KEY'):
        key = Fernet.generate_key().decode()
        print('export LOCAL_FERNET_KEY=' + key)
        os.environ['LOCAL_FERNET_KEY'] = key
    encrypt_blob(b'jwt-demo-value', Path('secrets/jwt.enc'))
    assert decrypt_blob(Path('secrets/jwt.enc')) == b'jwt-demo-value'
    print('encrypt_at_rest OK')