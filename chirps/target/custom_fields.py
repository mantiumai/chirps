# custom_fields.py  
  
from fernet_fields import EncryptedCharField  
from cryptography.fernet import Fernet  
  
class CustomEncryptedCharField(EncryptedCharField):  
    def from_db_value(self, value, expression, connection):  
        if value is not None:  
            value = super().from_db_value(value, expression, connection)  
            if isinstance(value, bytes):  
                return value.decode('utf-8')  
            else:  
                return value  
        return None  
