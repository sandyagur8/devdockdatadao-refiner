import pgpy
from pgpy.constants import CompressionAlgorithm, HashAlgorithm
import os
from refiner.config import settings


def encrypt_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Symmetrically encrypts a file with an encryption key.

    Args:
        encryption_key: The passphrase to encrypt with
        file_path: Path to the file to encrypt
        output_path: Optional path to save encrypted file (defaults to file_path + .pgp)

    Returns:
        Path to encrypted file
    """
    if output_path is None:
        output_path = f"{file_path}.pgp"
    
    with open(file_path, 'rb') as f:
        buffer = f.read()
    
    message = pgpy.PGPMessage.new(buffer, compression=CompressionAlgorithm.ZLIB)
    encrypted_message = message.encrypt(
        passphrase=encryption_key, hash=HashAlgorithm.SHA512
    )
    
    with open(output_path, 'wb') as f:
        f.write(str(encrypted_message).encode())
    
    return output_path


def decrypt_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """Symmetrically decrypts a file with an encryption key.

    Args:
        encryption_key: The passphrase to decrypt with
        file_path: Path to the encrypted file
        output_path: Optional path to save decrypted file (defaults to file_path without .pgp)

    Returns:
        Path to decrypted file
    """
    if output_path is None:
        if file_path.endswith('.pgp'):
            output_path = f"{file_path[:-4]}.decrypted"  # Remove .pgp extension
        else:
            output_path = f"{file_path}.decrypted"
            
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    message = pgpy.PGPMessage.from_blob(encrypted_data)
    decrypted_message = message.decrypt(encryption_key)
    
    with open(output_path, 'wb') as f:
        f.write(decrypted_message.message)
    
    return output_path


# Test with: python -m refiner.utils.encrypt
if __name__ == "__main__":
    if os.path.exists(os.path.join(settings.OUTPUT_DIR, "db.libsql")):
        plaintext_db = os.path.join(settings.OUTPUT_DIR, "db.libsql")
        
        # Encrypt and decrypt
        encrypted_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, plaintext_db)
        print(f"File encrypted to: {encrypted_path}")
        
        decrypted_path = decrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, encrypted_path)
        print(f"File decrypted to: {decrypted_path}")
    else:
        # Test encryption
        test_file = "test_file.txt"
        test_content = "This is a test file for PGPy encryption."
        
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
                print("✅ PGPy Encryption/Decryption test passed!")
            else:
                print("❌ PGPy Encryption/Decryption test failed!")
                print(f"Expected: {test_content}")
                print(f"Got: {decrypted_content}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            
        finally:
            # Clean up
            for file in [test_file, f"{test_file}.pgp", f"{test_file}.pgp.decrypted"]:
                if os.path.exists(file):
                    os.remove(file)