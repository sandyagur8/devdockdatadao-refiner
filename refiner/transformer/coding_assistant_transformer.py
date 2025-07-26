from typing import Dict, Any, List
from datetime import datetime
from refiner.models.coding_assistant_refined import Base, InstructionDataset, DatasetMetadata, ContextMetadata, ProjectDependency, LintingError, UserFeedback
from refiner.transformer.base_transformer import DataTransformer
import logging

class CodingAssistantTransformer(DataTransformer):
    """
    Transformer for coding assistant training data that creates a proper SQLite database.
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
                license=metadata.get('license', 'Unknown'),
                source=metadata.get('source', 'Unknown')
            )
            models.append(dataset_metadata)
            logging.info(f"Created dataset metadata: version={dataset_metadata.version}")
        
        # Process instruction dataset
        if 'instruction_dataset' in data:
            for idx, instruction_data in enumerate(data['instruction_dataset']):
                # Create main instruction record
                instruction = InstructionDataset(
                    instruction_id=instruction_data.get('id', f'instruction_{idx}'),
                    instruction_type=instruction_data.get('instruction_type', 'unknown'),
                    instruction=instruction_data.get('instruction', ''),
                    input_code=instruction_data.get('input', ''),
                    output_code=instruction_data.get('output', ''),
                    language=instruction_data.get('context', {}).get('language', 'unknown'),
                    user_prompt=instruction_data.get('context', {}).get('user_prompt', ''),
                    timestamp=self._parse_datetime(instruction_data.get('timestamp')),
                    model_used=instruction_data.get('model_used', 'unknown')
                )
                models.append(instruction)
                
                # Process extended context if available
                context = instruction_data.get('context', {})
                if any(key in context for key in ['error_message', 'terminal_output', 'execution_time', 'file_context']):
                    context_metadata = ContextMetadata(
                        instruction_id=idx + 1,  # Will be updated after insert
                        error_message=context.get('error_message'),
                        terminal_output=context.get('terminal_output'),
                        execution_time=context.get('execution_time'),
                        execution_date=self._parse_datetime(context.get('execution_date')),
                        successful_execution=context.get('successful_execution'),
                        file_context=context.get('file_context'),
                        file_path=context.get('file_path'),
                        file_content=context.get('file_content'),
                        framework=context.get('framework')
                    )
                    models.append(context_metadata)
                
                # Process dependencies
                dependencies = context.get('dependencies', [])
                for dep in dependencies:
                    if isinstance(dep, dict):
                        dependency = ProjectDependency(
                            instruction_id=idx + 1,  # Will be updated after insert
                            name=dep.get('name', ''),
                            version=dep.get('version')
                        )
                        models.append(dependency)
                
                # Process linting errors
                linting_errors = context.get('linting_errors', [])
                for error in linting_errors:
                    if isinstance(error, dict):
                        linting_error = LintingError(
                            instruction_id=idx + 1,  # Will be updated after insert
                            line=error.get('line'),
                            column=error.get('column'),
                            message=error.get('message', ''),
                            severity=error.get('severity', 'error'),
                            rule=error.get('rule')
                        )
                        models.append(linting_error)
                
                # Process user feedback
                user_feedback = context.get('user_feedback', {})
                if user_feedback:
                    feedback = UserFeedback(
                        instruction_id=idx + 1,  # Will be updated after insert
                        rating=user_feedback.get('rating'),
                        comment=user_feedback.get('comment'),
                        was_helpful=user_feedback.get('was_helpful'),
                        helped_solve_problem=user_feedback.get('helped_solve_problem')
                    )
                    models.append(feedback)
                
                logging.info(f"Processed instruction {idx + 1}: {instruction.instruction_type}")
        
        logging.info(f"Created {len(models)} database records")
        return models
    
    def _parse_datetime(self, date_str: str = None) -> datetime:
        """Parse datetime string or return current time."""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Try to parse ISO format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(date_str)
        except:
            # Fallback to current time
            return datetime.utcnow() 