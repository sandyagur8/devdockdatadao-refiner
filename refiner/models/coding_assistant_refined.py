from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model for SQLAlchemy
Base = declarative_base()

class InstructionDataset(Base):
    __tablename__ = 'instruction_dataset'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(String, nullable=False)  # The original "id" field from JSON
    instruction_type = Column(String, nullable=False)
    instruction = Column(Text, nullable=False)
    input_code = Column(Text, nullable=False)
    output_code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    user_prompt = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class DatasetMetadata(Base):
    __tablename__ = 'dataset_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    sample_count = Column(Integer, nullable=False)
    license = Column(String, nullable=False)
    source = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# Extended context tables for rich data
class ContextMetadata(Base):
    __tablename__ = 'context_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(Integer, ForeignKey('instruction_dataset.id'), nullable=False)
    error_message = Column(Text, nullable=True)
    terminal_output = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
    execution_date = Column(DateTime, nullable=True)
    successful_execution = Column(Boolean, nullable=True)
    file_context = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    file_content = Column(Text, nullable=True)
    framework = Column(String, nullable=True)
    
    instruction = relationship("InstructionDataset", backref="context_metadata")

class ProjectDependency(Base):
    __tablename__ = 'project_dependencies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(Integer, ForeignKey('instruction_dataset.id'), nullable=False)
    name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    
    instruction = relationship("InstructionDataset", backref="dependencies")

class LintingError(Base):
    __tablename__ = 'linting_errors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(Integer, ForeignKey('instruction_dataset.id'), nullable=False)
    line = Column(Integer, nullable=True)
    column = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)  # error, warning, info
    rule = Column(String, nullable=True)
    
    instruction = relationship("InstructionDataset", backref="linting_errors")

class UserFeedback(Base):
    __tablename__ = 'user_feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction_id = Column(Integer, ForeignKey('instruction_dataset.id'), nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    was_helpful = Column(Boolean, nullable=True)
    helped_solve_problem = Column(Boolean, nullable=True)
    
    instruction = relationship("InstructionDataset", backref="user_feedback") 