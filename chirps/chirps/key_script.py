"""Helper script to generate a fernet key."""
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key.decode())
