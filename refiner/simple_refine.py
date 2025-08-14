import json
import logging
import os

from refiner.models.offchain_schema import OffChainSchema
from refiner.models.output import Output
from refiner.transformer.coding_assistant_transformer import CodingAssistantTransformer
from refiner.config import settings
try:
    from refiner.utils.encrypt import encrypt_file
    ENCRYPTION_AVAILABLE = True
except ImportError as e:
    # Handle Python 3.13 compatibility issue with pgpy/imghdr
    print(f"Warning: Encryption not available locally (Python 3.13 issue): {e}")
    print("Encryption will work in Docker container with Python 3.12")
    ENCRYPTION_AVAILABLE = False
    def encrypt_file(*args, **kwargs):
        raise ImportError("Encryption not available in Python 3.13 - use Docker container")
from refiner.utils.ipfs import upload_file_to_ipfs, upload_json_to_ipfs

class SimpleRefiner:
    def __init__(self):
        self.db_path = os.path.join(settings.OUTPUT_DIR, 'db.libsql')

    def transform(self) -> Output:
        """Transform input data into SQLite database for Vana compatibility."""
        logging.info("Starting data transformation to SQLite database")
        output = Output()

        # Process all JSON files in input directory
        for input_filename in os.listdir(settings.INPUT_DIR):
            input_file = os.path.join(settings.INPUT_DIR, input_filename)
            if os.path.splitext(input_file)[1].lower() == '.json':
                logging.info(f"Processing file: {input_filename}")
                
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    
                    # Create transformer and process data into SQLite database
                    transformer = CodingAssistantTransformer(self.db_path)
                    transformer.process(input_data)
                    logging.info(f"Transformed {input_filename} into SQLite database")
                    
                    # Create schema
                    schema = OffChainSchema(
                        name=settings.SCHEMA_NAME,
                        version=settings.SCHEMA_VERSION,
                        description=settings.SCHEMA_DESCRIPTION,
                        dialect=settings.SCHEMA_DIALECT,
                        schema=transformer.get_schema()
                    )
                    output.schema = schema
                    
                    # Save schema to output
                    schema_file = os.path.join(settings.OUTPUT_DIR, 'schema.json')
                    with open(schema_file, 'w') as f:
                        json.dump(schema.model_dump(), f, indent=2)
                    
                    # Log database info
                    if os.path.exists(self.db_path):
                        db_size = os.path.getsize(self.db_path)
                        logging.info(f"Created SQLite database: {self.db_path} ({db_size} bytes)")
                    
                    # Encrypt the database file for Vana compatibility
                    encrypted_db_path = None
                    if settings.REFINEMENT_ENCRYPTION_KEY and os.path.exists(self.db_path):
                        if ENCRYPTION_AVAILABLE:
                            try:
                                encrypted_db_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, self.db_path)
                                encrypted_size = os.path.getsize(encrypted_db_path)
                                logging.info(f"Database encrypted: {encrypted_db_path} ({encrypted_size} bytes)")
                            except Exception as e:
                                logging.error(f"Failed to encrypt database: {e}")
                                encrypted_db_path = None
                        else:
                            logging.warning("Encryption not available (Python 3.13 compatibility issue)")
                            logging.info("Database will be encrypted when running in Docker container (Python 3.12)")
                    else:
                        logging.warning("No encryption key provided or database file not found, skipping encryption")
                    
                    # Upload to IPFS if credentials are available
                    try:
                        if settings.PINATA_API_KEY and settings.PINATA_API_SECRET:
                            # Upload schema to IPFS
                            schema_ipfs_hash = upload_json_to_ipfs(schema.model_dump())
                            logging.info(f"Schema uploaded to IPFS with hash: {schema_ipfs_hash}")
                            
                            # Upload encrypted database to IPFS (or fallback to unencrypted)
                            upload_file = encrypted_db_path if encrypted_db_path else self.db_path
                            db_ipfs_hash = upload_file_to_ipfs(upload_file)
                            file_type = "encrypted database" if encrypted_db_path else "unencrypted database"
                            logging.info(f"{file_type.title()} uploaded to IPFS with hash: {db_ipfs_hash}")
                            
                            # Set the refinement URL
                            output.refinement_url = f"{settings.IPFS_GATEWAY_URL}/{db_ipfs_hash}"
                        else:
                            logging.warning("IPFS credentials not available, skipping IPFS upload")
                    except Exception as e:
                        logging.error(f"Failed to upload to IPFS: {e}")
                    
                    break  # Process only the first JSON file for simplicity

        logging.info("Data transformation to SQLite completed successfully")
        return output 