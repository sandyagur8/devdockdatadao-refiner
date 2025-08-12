from typing import Dict, Any, List
from datetime import datetime
import json
import logging
from refiner.models.coding_assistant_refined import Base, InstructionDataset, DatasetMetadata, ContextMetadata
from refiner.transformer.base_transformer import DataTransformer

class CodingAssistantTransformer(DataTransformer):
    """
    Transformer for DevDock coding assistant training data that creates a proper SQLite database.
    """
    
    def __init__(self, db_path: str):
        """Initialize the transformer with the coding assistant models."""
        # Override the Base to use our coding assistant models
        self.original_base = None
        super().__init__(db_path)
    
    def _initialize_database(self) -> None:
        """
        Initialize or recreate the database and its tables using coding assistant models.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logging.info(f"Deleted existing database at {self.db_path}")
        
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logging.info(f"Created SQLite database at {self.db_path}")
    
    def transform(self, data: Dict[str, Any]) -> List[Base]:
        """
        Transform JSON data into SQLAlchemy model instances for coding assistant training data.
        
        Args:
            data: Dictionary containing the JSON data with instruction_dataset and dataset_metadata
            
        Returns:
            List of SQLAlchemy model instances to be saved to the database
        """
        models = []
        
        # Process dataset metadata
        if 'dataset_metadata' in data:
            metadata = data['dataset_metadata']
            dataset_metadata = DatasetMetadata(
                version=metadata.get('version', '1.0.0'),
                created_at=self._parse_datetime(metadata.get('created_at')),
                sample_count=metadata.get('sample_count', 0),
                license=metadata.get('license', 'MIT'),
                source=metadata.get('source', 'VS Code Extension Data Collection')
            )
            models.append(dataset_metadata)
            logging.info(f"Created dataset metadata: version={dataset_metadata.version}, samples={dataset_metadata.sample_count}")
        
        # Process instruction dataset
        if 'instruction_dataset' in data:
            for idx, instruction_data in enumerate(data['instruction_dataset']):
                # Create main instruction record
                instruction = InstructionDataset(
                    entry_id=instruction_data.get('id', f'entry_{idx}'),
                    instruction_type=instruction_data.get('instruction_type', 'unknown'),
                    instruction=instruction_data.get('instruction', ''),
                    input_data=json.dumps(instruction_data.get('input', '')) if instruction_data.get('input') else '',
                    output_data=json.dumps(instruction_data.get('output', '')) if instruction_data.get('output') else '',
                    timestamp=self._parse_datetime(instruction_data.get('timestamp')),
                    model_used=instruction_data.get('model_used', 'unknown')
                )
                models.append(instruction)
                
                # Process context metadata if available
                context = instruction_data.get('context', {})
                if context:
                    context_metadata = ContextMetadata(
                        instruction_id=idx + 1,  # Will be updated after insert
                        language=context.get('language'),
                        user_prompt=context.get('user_prompt'),
                        has_files=context.get('has_files'),
                        is_partial=context.get('is_partial'),
                        file_path=context.get('file_path'),
                        file_content=context.get('file_content'),
                        successful_execution=context.get('successful_execution'),
                        interaction_type=context.get('interaction_type'),
                        message_type=context.get('message_type'),
                        api_call=context.get('api_call'),
                        operation_type=context.get('operation_type'),
                        task_type=context.get('task_type'),
                        anonymized_user_id=context.get('metadata', {}).get('anonymized_user_id'),
                        skill_level=context.get('metadata', {}).get('skill_level'),
                        extension_version=context.get('metadata', {}).get('extension_version'),
                        vs_code_version=context.get('metadata', {}).get('vs_code_version'),
                        original_llm_response=context.get('original_llm_response')
                    )
                    
                    # Handle file metadata if present
                    file_metadata = context.get('file_metadata', {})
                    if file_metadata:
                        context_metadata.file_metadata_size = file_metadata.get('size')
                        context_metadata.file_metadata_creation_date = self._parse_datetime(file_metadata.get('creation_date'))
                        context_metadata.file_metadata_modification_date = self._parse_datetime(file_metadata.get('modification_date'))
                        context_metadata.file_metadata_line_count = file_metadata.get('line_count')
                    
                    # Store complex data as JSON strings
                    if 'project_structure' in context:
                        context_metadata.project_structure = json.dumps(context['project_structure'])
                    if 'dependencies' in context:
                        context_metadata.dependencies = json.dumps(context['dependencies'])
                    if 'runtime_environment' in context:
                        context_metadata.runtime_environment = json.dumps(context['runtime_environment'])
                    if 'llm_conversation_history' in context:
                        context_metadata.llm_conversation_history = json.dumps(context['llm_conversation_history'])
                    if 'user_interaction_history' in context:
                        context_metadata.user_interaction_history = json.dumps(context['user_interaction_history'])
                    if 'linting_errors' in context:
                        context_metadata.linting_errors = json.dumps(context['linting_errors'])
                    if 'metadata' in context and 'tags' in context['metadata']:
                        context_metadata.tags = json.dumps(context['metadata']['tags'])
                    
                    models.append(context_metadata)
                
                logging.info(f"Processed instruction {idx + 1}: {instruction.instruction_type} - {instruction.entry_id}")
        
        logging.info(f"Created {len(models)} database records")
        return models
    
    def _parse_datetime(self, date_str: str = None) -> datetime:
        """Parse datetime string or return current time."""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Try to parse ISO format with Z suffix
            if isinstance(date_str, str):
                if date_str.endswith('Z'):
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                elif 'T' in date_str:
                    return datetime.fromisoformat(date_str)
                else:
                    return datetime.fromisoformat(date_str)
            else:
                return datetime.utcnow()
        except Exception as e:
            logging.warning(f"Failed to parse datetime '{date_str}': {e}")
            # Fallback to current time
            return datetime.utcnow()