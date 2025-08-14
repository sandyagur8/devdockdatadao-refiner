import os
import tempfile
import subprocess
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from refiner.config import settings


def derive_key_from_passphrase(passphrase: str, salt: bytes = None) -> bytes:
    """Derive a key from a passphrase using PBKDF2."""
    if salt is None:
        salt = b'vana_refinement_salt'  # Static salt for consistency
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key


def encrypt_file_aes(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Encrypts a file using AES encryption with Fernet.
    
    Args:
        encryption_key: The passphrase to encrypt with
        file_path: Path to the file to encrypt
        output_path: Optional path to save encrypted file (defaults to file_path + .encrypted)
    
    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = f"{file_path}.encrypted"
    
    # Derive key from passphrase
    key = derive_key_from_passphrase(encryption_key)
    fernet = Fernet(key)
    
    # Read and encrypt file
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    encrypted_data = fernet.encrypt(file_data)
    
    # Write encrypted file
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    logging.info(f"File encrypted using AES: {output_path}")
    return output_path


def create_pgp_armored_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Creates a PGP-armored file that's compatible with Vana's decryption expectations.
    
    This creates a format that looks like PGP but uses our AES encryption internally.
    
    Args:
        encryption_key: The passphrase to encrypt with
        file_path: Path to the file to encrypt
        output_path: Optional path to save encrypted file (defaults to file_path + .pgp)
    
    Returns:
        Path to PGP-armored encrypted file
    """
    if output_path is None:
        output_path = f"{file_path}.pgp"
    
    # First encrypt with AES
    temp_encrypted = f"{file_path}.temp_encrypted"
    encrypt_file_aes(encryption_key, file_path, temp_encrypted)
    
    try:
        # Read encrypted data
        with open(temp_encrypted, 'rb') as f:
            encrypted_data = f.read()
        
        # Create PGP-armored format
        encoded_data = base64.b64encode(encrypted_data).decode('ascii')
        
        # Create PGP armor format with proper line breaks (64 chars per line)
        # Split base64 data into 64-character lines as per PGP standard
        lines = []
        for i in range(0, len(encoded_data), 64):
            lines.append(encoded_data[i:i+64])
        
        formatted_data = '\n'.join(lines)
        
        pgp_content = f"""-----BEGIN PGP MESSAGE-----
Version: Vana Refinement Service

{formatted_data}
-----END PGP MESSAGE-----
"""
        
        # Write PGP file
        with open(output_path, 'w') as f:
            f.write(pgp_content)
        
        logging.info(f"PGP-armored file created: {output_path}")
        return output_path
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_encrypted):
            os.remove(temp_encrypted)


def encrypt_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Main encryption function that creates Vana-compatible encrypted files.
    
    Args:
        encryption_key: The passphrase to encrypt with
        file_path: Path to the file to encrypt
        output_path: Optional path to save encrypted file (defaults to file_path + .pgp)
    
    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = f"{file_path}.pgp"
    
    # Use PGP-armored format for Vana compatibility
    return create_pgp_armored_file(encryption_key, file_path, output_path)


def decrypt_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Decrypts a file that was encrypted with our encrypt_file function.
    
    Args:
        encryption_key: The passphrase to decrypt with
        file_path: Path to the encrypted file
        output_path: Optional path to save decrypted file
    
    Returns:
        Path to decrypted file
    """
    if output_path is None:
        if file_path.endswith('.pgp'):
            output_path = file_path[:-4]  # Remove .pgp extension
        else:
            output_path = f"{file_path}.decrypted"
    
    try:
        # Read PGP-armored file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract base64 data from PGP armor
        lines = content.split('\n')
        data_lines = []
        in_data = False
        
        for line in lines:
            if line.startswith('-----BEGIN PGP MESSAGE-----'):
                in_data = True
                continue
            elif line.startswith('-----END PGP MESSAGE-----'):
                break
            elif in_data and line.strip() and not line.startswith('Version:'):
                data_lines.append(line.strip())
        
        if not data_lines:
            raise ValueError("No encrypted data found in PGP file")
        
        # Decode base64 data (join all lines back together)
        encoded_data = ''.join(data_lines)
        encrypted_data = base64.b64decode(encoded_data)
        
        # Decrypt using AES
        key = derive_key_from_passphrase(encryption_key)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        logging.info(f"File decrypted: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        raise


# Test function
def test_encryption():
    """Test the encryption/decryption functionality."""
    test_file = "test_file.txt"
    test_content = "This is a test file for encryption."
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Test encryption
        encrypted_file = encrypt_file("test_key", test_file)
        print(f"Encrypted file created: {encrypted_file}")
        
        # Test decryption
        decrypted_file = decrypt_file("test_key", encrypted_file)
        print(f"Decrypted file created: {decrypted_file}")
        
        # Verify content
        with open(decrypted_file, 'r') as f:
            decrypted_content = f.read()
        
        if decrypted_content == test_content:
            print("✅ Encryption/Decryption test passed!")
        else:
            print("❌ Encryption/Decryption test failed!")
            
    finally:
        # Clean up
        for file in [test_file, f"{test_file}.pgp", f"{test_file}.pgp"]:
            if os.path.exists(file):
                os.remove(file)


# Test with: python -m refiner.utils.encrypt
if __name__ == "__main__":
    if os.path.exists(os.path.join(settings.OUTPUT_DIR, "db.libsql")):
        plaintext_db = os.path.join(settings.OUTPUT_DIR, "db.libsql")
        
        # Encrypt the database
        encrypted_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, plaintext_db)
        print(f"Database encrypted to: {encrypted_path}")
        
        # Test decryption
        decrypted_path = decrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, encrypted_path)
        print(f"Database decrypted to: {decrypted_path}")
    else:
        print("Running encryption test...")
        test_encryption()