import random
import string
import uuid

class EncryptionService:
    CHARACTERS = string.ascii_letters + string.digits

    @classmethod
    def generate_code(cls, length=20):
        code = ''.join(random.choice(cls.CHARACTERS) for i in range(length))
        return code
    
    @classmethod
    def generate_uuid(cls):
        return str(uuid.uuid4())
