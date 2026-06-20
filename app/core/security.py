# TODO: password hashing with argon2-cffi.
#   - a single PasswordHasher instance
#   - hash_password(plain: str) -> str
#   - verify_password(plain: str, hashed: str) -> bool

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


_hasher = PasswordHasher()

def hash_password(plain: str) -> str:
    return _hasher.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        _hasher.verify(hashed, plain)
        return True
    except VerifyMismatchError:
        return False
