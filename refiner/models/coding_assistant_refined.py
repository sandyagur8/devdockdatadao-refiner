from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model for SQLAlchemy
Base = declarative_base()

class InstructionDataset(Base):
    __tablename__ = 'instruction_dataset'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String, nullable=False, unique=True)  # e.g., "entry_1755013833461_yxgrdln"
    instruction_type = Column(String, nullable=False)
    instruction = Column(Text, nullable=False)
    input_data = Column(Text, nullable=False)  # JSON string input
    output_data = Column(Text)  # JSON string output (can be empty)
    timestamp = Column(DateTime, nullable=False)
    model_used = Column(String, nullable=False)
    
    # Relationships
    context_metadata = relationship("ContextMetadata", back_populates="instruction", cascade="all, delete-orphan")

class DatasetMetadata(Base):
    __tablename__ = 'dataset_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    sample_count = Column(Integer, nullable=False)
    license = Column(String, nullable=False)
    source = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ContextMetadata(Base):
    __tablename__ = 'context_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(Integer, ForeignKey('instruction_dataset.id'), nullable=False)
    
    # Basic context fields
    language = Column(String)
    user_prompt = Column(Text)
    has_files = Column(Boolean)
    is_partial = Column(Boolean)
    
    # File-related fields
    file_path = Column(String)
    file_content = Column(Text)
    file_metadata_size = Column(Integer)
    file_metadata_creation_date = Column(DateTime)
    file_metadata_modification_date = Column(DateTime)
    file_metadata_line_count = Column(Integer)
    
    # Execution context
    successful_execution = Column(Boolean)
    interaction_type = Column(String)  # e.g., "tool", "prompt"
    message_type = Column(String)
    api_call = Column(Boolean)
    operation_type = Column(String)  # e.g., "create", "update"
    task_type = Column(String)  # e.g., "initial_task"
    
    # User/environment info
    anonymized_user_id = Column(String)
    skill_level = Column(String)
    extension_version = Column(String)
    vs_code_version = Column(String)
    
    # Complex data stored as JSON strings
    project_structure = Column(Text)  # JSON string
    dependencies = Column(Text)  # JSON string
    runtime_environment = Column(Text)  # JSON string
    llm_conversation_history = Column(Text)  # JSON string
    user_interaction_history = Column(Text)  # JSON string
    linting_errors = Column(Text)  # JSON string
    tags = Column(Text)  # JSON string array
    
    # Additional fields
    original_llm_response = Column(Text)
    
    # Relationship
    instruction = relationship("InstructionDataset", back_populates="context_metadata")