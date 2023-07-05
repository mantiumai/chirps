from cryptography.fernet import Fernet  
  
key = Fernet.generate_key()  
print(key.decode())  
