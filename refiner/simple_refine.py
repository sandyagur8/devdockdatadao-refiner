import json
import logging
import os

from refiner.models.offchain_schema import OffChainSchema
from refiner.models.output import Output
from refiner.transformer.simple_transformer import SimpleTransformer
from refiner.config import settings
# from refiner.utils.encrypt import encrypt_file
from refiner.utils.ipfs import upload_file_to_ipfs, upload_json_to_ipfs

class SimpleRefiner:
    def __init__(self):
        self.transformer = SimpleTransformer()

    def transform(self) -> Output:
        """Simple transformation that just casts input data to output data."""
        logging.info("Starting simple data transformation for verification")
        output = Output()

        # Process all JSON files in input directory
        for input_filename in os.listdir(settings.INPUT_DIR):
            input_file = os.path.join(settings.INPUT_DIR, input_filename)
            if os.path.splitext(input_file)[1].lower() == '.json':
                logging.info(f"Processing file: {input_filename}")
                
                with open(input_file, 'r') as f:
                    input_data = json.load(f)
                    
                    # Simple transformation - just pass through the data
                    transformed_data = self.transformer.transform(input_data)
                    logging.info(f"Transformed data: {transformed_data}")
                    
                    # Create schema
                    schema = OffChainSchema(
                        name=settings.SCHEMA_NAME,
                        version=settings.SCHEMA_VERSION,
                        description=settings.SCHEMA_DESCRIPTION,
                        dialect=settings.SCHEMA_DIALECT,
                        schema=self.transformer.get_schema()
                    )
                    output.schema = schema
                    
                    # Save transformed data to output
                    output_file = os.path.join(settings.OUTPUT_DIR, 'transformed_data.json')
                    with open(output_file, 'w') as f:
                        json.dump(transformed_data, f, indent=2)
                    
                    # Save schema to output
                    schema_file = os.path.join(settings.OUTPUT_DIR, 'schema.json')
                    with open(schema_file, 'w') as f:
                        json.dump(schema.model_dump(), f, indent=2)
                    
                    # Upload schema to IPFS if credentials are available
                    try:
                        if settings.PINATA_API_KEY and settings.PINATA_API_SECRET:
                            schema_ipfs_hash = upload_json_to_ipfs(schema.model_dump())
                            logging.info(f"Schema uploaded to IPFS with hash: {schema_ipfs_hash}")
                            
                            # Upload transformed data to IPFS
                            data_ipfs_hash = upload_json_to_ipfs(transformed_data)
                            logging.info(f"Transformed data uploaded to IPFS with hash: {data_ipfs_hash}")
                            
                            # Set the refinement URL
                            output.refinement_url = f"{settings.IPFS_GATEWAY_URL}/{data_ipfs_hash}"
                        else:
                            logging.warning("IPFS credentials not available, skipping IPFS upload")
                    except Exception as e:
                        logging.error(f"Failed to upload to IPFS: {e}")
                    
                    break  # Process only the first JSON file for simplicity

        logging.info("Simple data transformation completed successfully")
        return output 