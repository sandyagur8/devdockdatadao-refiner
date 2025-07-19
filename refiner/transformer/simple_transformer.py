import json
import logging
from typing import Dict, Any

class SimpleTransformer:
    """
    Simple transformer that just casts input data to output data.
    Used for verifying data flow with SQLite schema for Vana compatibility.
    """
    
    def __init__(self):
        self.schema = self._get_schema()
    
    def _get_schema(self) -> str:
        """Get the SQLite schema definition for coding assistant training data"""
        return """CREATE TABLE instruction_dataset (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction_id TEXT NOT NULL,
    instruction_type TEXT NOT NULL,
    instruction TEXT NOT NULL,
    input_code TEXT NOT NULL,
    output_code TEXT NOT NULL,
    language TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    model_used TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dataset_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    sample_count INTEGER NOT NULL,
    license TEXT NOT NULL,
    source TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for better query performance
CREATE INDEX idx_instruction_type ON instruction_dataset(instruction_type);
CREATE INDEX idx_language ON instruction_dataset(language);
CREATE INDEX idx_timestamp ON instruction_dataset(timestamp);
CREATE INDEX idx_model_used ON instruction_dataset(model_used);"""
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple transformation that just returns the input data as-is.
        This is used to verify the data flow.
        
        Args:
            data: Input data dictionary
            
        Returns:
            The same data dictionary (no transformation)
        """
        logging.info(f"Simple transformation: input data has {len(data)} keys")
        logging.info(f"Input data keys: {list(data.keys())}")
        
        # Just return the data as-is for verification
        return data
    
    def get_schema(self) -> str:
        """Get the SQLite schema string"""
        return self.schema 