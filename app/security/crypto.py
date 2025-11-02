from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class APIKeyEncryption:
    """Encrypt/Decrypt API keys using Fernet"""
    
    def __init__(self):
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            # Generate new key if not exists
            secret_key = Fernet.generate_key().decode()
            logger.warning(f"Generated new SECRET_KEY: {secret_key}")
            logger.warning("Add this to your .env file!")
        
        if isinstance(secret_key, str):
            secret_key = secret_key.encode()
        
        self.cipher = Fernet(secret_key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt API key"""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt API key"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Example usage
if __name__ == "__main__":
    enc = APIKeyEncryption()
    
    test_key = "test_api_key_12345"
    encrypted = enc.encrypt(test_key)
    decrypted = enc.decrypt(encrypted)
    
    print(f"Original: {test_key}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Match: {test_key == decrypted}")
