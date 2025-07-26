import json
import logging
import os

from refiner.models.offchain_schema import OffChainSchema
from refiner.models.output import Output
from refiner.transformer.coding_assistant_transformer import CodingAssistantTransformer
from refiner.config import settings
# from refiner.utils.encrypt import encrypt_file
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
                    
                    # Upload to IPFS if credentials are available
                    try:
                        if settings.PINATA_API_KEY and settings.PINATA_API_SECRET:
                            # Upload schema to IPFS
                            schema_ipfs_hash = upload_json_to_ipfs(schema.model_dump())
                            logging.info(f"Schema uploaded to IPFS with hash: {schema_ipfs_hash}")
                            
                            # Upload database to IPFS
                            db_ipfs_hash = upload_file_to_ipfs(self.db_path)
                            logging.info(f"Database uploaded to IPFS with hash: {db_ipfs_hash}")
                            
                            # Set the refinement URL
                            output.refinement_url = f"{settings.IPFS_GATEWAY_URL}/{db_ipfs_hash}"
                        else:
                            logging.warning("IPFS credentials not available, skipping IPFS upload")
                    except Exception as e:
                        logging.error(f"Failed to upload to IPFS: {e}")
                    
                    break  # Process only the first JSON file for simplicity

        logging.info("Data transformation to SQLite completed successfully")
        return output 