import os
import tempfile
import logging
from typing import Union

import gnupg
from refiner.config import settings


class FileDecryptionError(Exception):
    """Exception raised when file decryption fails."""
    def __init__(self, error: str):
        self.error = error
        super().__init__(self.error)


def encrypt_file(encryption_key: str, file_path: str, output_path: str = None) -> str:
    """
    Encrypts a file using GPG encryption with symmetric encryption.
    
    Args:
        encryption_key (str): The passphrase to encrypt with
        file_path (str): Path to the file to encrypt
        output_path (str): Optional path to save encrypted file (defaults to file_path + .pgp)
    
    Returns:
        str: Path to encrypted file
    
    Raises:
        FileDecryptionError: If encryption fails
    """
    if output_path is None:
        output_path = f"{file_path}.pgp"
    
    # Initialize GPG
    gpg = gnupg.GPG()
    
    try:
        # Read the file to encrypt
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Encrypt using GPG symmetric encryption
        encrypted_data = gpg.encrypt(
            file_data,
            recipients=None,  # No recipients for symmetric encryption
            symmetric=True,   # Use symmetric encryption
            passphrase=encryption_key,
            armor=True,       # Create ASCII-armored output
            always_trust=True
        )
        
        if not encrypted_data.ok:
            raise FileDecryptionError(
                error=f"GPG encryption failed: Status '{encrypted_data.status}', Stderr: '{encrypted_data.stderr}'"
            )
        
        # Write encrypted data to output file
        with open(output_path, 'w') as f:
            f.write(str(encrypted_data))
        
        logging.info(f"File encrypted successfully: {output_path}")
        return output_path
        
    except Exception as e:
        if isinstance(e, FileDecryptionError):
            raise
        else:
            raise FileDecryptionError(error=f"An unexpected error occurred during encryption: {str(e)}")


def decrypt_file(encrypted_file_path: str, encryption_key: str, output_path: str = None) -> str:
    """
    Decrypts a file using GPG encryption. Based on Vana's implementation.

    Args:
        encrypted_file_path (str): Path to the encrypted file.
        encryption_key (str): Encryption key for decryption.
        output_path (str): Optional path for decrypted file.

    Returns:
        str: Path to the decrypted file.

    Raises:
        FileDecryptionError: If decryption fails.
    """
    gpg = gnupg.GPG()
    
    if output_path is None:
        if encrypted_file_path.endswith('.pgp'):
            output_path = encrypted_file_path[:-4]  # Remove .pgp extension
        else:
            output_path = f"{encrypted_file_path}.decrypted"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            logging.info(f"Ensured output directory exists: {output_dir}")
        except OSError as e:
            raise FileDecryptionError(error=f"Could not create output directory '{output_dir}': {e}")

    try:
        with open(encrypted_file_path, 'rb') as encrypted_file:
            decrypted_data = gpg.decrypt_file(
                encrypted_file,
                passphrase=encryption_key,
                output=output_path
            )

            logging.info(f"GPG decryption status: {decrypted_data.status}")
            logging.debug(f"GPG stderr: {decrypted_data.stderr}")

            if not decrypted_data.ok:
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except OSError:
                    pass
                raise FileDecryptionError(
                    error=f"GPG decryption failed: Status '{decrypted_data.status}', Stderr: '{decrypted_data.stderr}'"
                )

    except Exception as e:
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass
        if isinstance(e, FileDecryptionError):
            raise
        else:
            raise FileDecryptionError(error=f"An unexpected error occurred during decryption: {str(e)}")

    logging.info(f"Successfully decrypted file to: {output_path}")
    return output_path


def test_encryption():
    """Test the encryption/decryption functionality."""
    test_file = "test_file.txt"
    test_content = "This is a test file for GPG encryption."
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Test encryption
        encrypted_file = encrypt_file("test_key", test_file)
        print(f"Encrypted file created: {encrypted_file}")
        
        # Test decryption
        decrypted_file = decrypt_file(encrypted_file, "test_key")
        print(f"Decrypted file created: {decrypted_file}")
        
        # Verify content
        with open(decrypted_file, 'r') as f:
            decrypted_content = f.read()
        
        if decrypted_content == test_content:
            print("✅ GPG Encryption/Decryption test passed!")
        else:
            print("❌ GPG Encryption/Decryption test failed!")
            print(f"Expected: {test_content}")
            print(f"Got: {decrypted_content}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        
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
        decrypted_path = decrypt_file(encrypted_path, settings.REFINEMENT_ENCRYPTION_KEY)
        print(f"Database decrypted to: {decrypted_path}")
    else:
        print("Running GPG encryption test...")
        test_encryption()