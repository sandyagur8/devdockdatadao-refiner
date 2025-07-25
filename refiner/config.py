from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Global settings configuration using environment variables"""
    
    INPUT_DIR: str = Field(
        default="/input",
        description="Directory containing input files to process"
    )
    
    OUTPUT_DIR: str = Field(
        default="/output",
        description="Directory where output files will be written"
    )
    
    REFINEMENT_ENCRYPTION_KEY: Optional[str] = Field(
        default="0x1234",
        description="Key to symmetrically encrypt the refinement. This is derived from the original file encryption key"
    )
    
    SCHEMA_NAME: str = Field(
        default="Coding Assistant Training Data Schema",
        description="Name of the schema"
    )
    
    SCHEMA_VERSION: str = Field(
        default="1.0.0",
        description="Version of the schema"
    )
    
    SCHEMA_DESCRIPTION: str = Field(
        default="Schema for collecting high-quality data from VS Code extension for fine-tuning coding language models",
        description="Description of the schema"
    )
    
    SCHEMA_DIALECT: str = Field(
        default="sqlite",
        description="Dialect of the schema"
    )
    
    # Optional, required if using https://pinata.cloud (IPFS pinning service)
    PINATA_API_KEY: Optional[str] = Field(
        default=None,
        description="Pinata API key"
    )
    
    PINATA_API_SECRET: Optional[str] = Field(
        default=None,
        description="Pinata API secret"
    )

    IPFS_GATEWAY_URL: str = Field(
        default="https://gateway.pinata.cloud/ipfs",
        description="IPFS gateway URL for accessing uploaded files. Recommended to use own dedicated gateway to avoid congestion and rate limiting. Example: 'https://ipfs.my-dao.org/ipfs' (Note: won't work for third-party files)"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 