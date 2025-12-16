from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "passtest"  # <-- change this to whatever password you want
hash_value = pwd_ctx.hash(password)
print(hash_value)
