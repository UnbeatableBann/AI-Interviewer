from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Create a PasswordHasher instance (with strong defaults)
pwd_context = PasswordHasher(
    time_cost=3,  # number of iterations
    memory_cost=64 * 1024,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# can use PEPPER to make strong hash password
async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
