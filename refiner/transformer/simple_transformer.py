import json
import logging
from typing import Dict, Any

class SimpleTransformer:
    """
    Simple transformer that just casts input data to output data.
    Used for verifying data flow with Coding Assistant Training Data Schema.
    """
    
    def __init__(self):
        self.schema = self._get_schema()
    
    def _get_schema(self) -> str:
        """Get the schema definition as JSON string"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Coding Assistant Training Data Schema",
            "description": "Schema for collecting high-quality data from VS Code extension for fine-tuning coding language models",
            "type": "object",
            "properties": {
                "instruction_dataset": {
                    "type": "array",
                    "description": "Collection of coding instruction examples for training",
                    "items": {
                        "type": "object",
                        "required": ["instruction_type", "instruction", "input", "output", "context"],
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the training example"
                            },
                            "instruction_type": {
                                "type": "string",
                                "description": "Category of the coding instruction",
                                "enum": [
                                    "bug_fixing",
                                    "code_completion",
                                    "algorithm_implementation",
                                    "code_refactoring",
                                    "unit_test_generation",
                                    "documentation_generation",
                                    "memory_leak_fix",
                                    "performance_optimization",
                                    "configuration_setup",
                                    "security_fix",
                                    "code_review",
                                    "api_implementation",
                                    "debugging",
                                    "data_processing",
                                    "pattern_implementation",
                                    "style_enforcement",
                                    "type_definition",
                                    "api_integration",
                                    "dependency_management",
                                    "code_explanation",
                                    "database_query_optimization",
                                    "frontend_component",
                                    "devops_automation",
                                    "architecture_design"
                                ]
                            },
                            "instruction": {
                                "type": "string",
                                "description": "The instruction or task description provided to the model"
                            },
                            "input": {
                                "type": "string",
                                "description": "The input code or text for the model to process"
                            },
                            "output": {
                                "type": "string",
                                "description": "The expected or actual output/solution for the given instruction and input"
                            },
                            "context": {
                                "type": "object",
                                "description": "Rich contextual information about the coding scenario",
                                "properties": {
                                    "language": {
                                        "type": "string",
                                        "description": "The programming language of the code"
                                    },
                                    "user_prompt": {
                                        "type": "string",
                                        "description": "The original query or question asked by the user in the VS Code extension"
                                    }
                                },
                                "required": ["language", "user_prompt"]
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "When this instruction example was recorded"
                            },
                            "model_used": {
                                "type": "string",
                                "description": "LLM that provided the output (e.g., claude-3-sonnet, gpt-4o)"
                            }
                        }
                    }
                },
                "dataset_metadata": {
                    "type": "object",
                    "description": "Metadata about the overall dataset",
                    "properties": {
                        "version": {
                            "type": "string",
                            "description": "Version of the dataset"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "When the dataset was created"
                        },
                        "sample_count": {
                            "type": "number",
                            "description": "Number of samples in the dataset"
                        },
                        "license": {
                            "type": "string",
                            "description": "License under which the dataset is released"
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of the dataset (e.g., 'VS Code Extension Data Collection')"
                        }
                    }
                }
            },
            "required": ["instruction_dataset"]
        }
        return json.dumps(schema, indent=2)
    
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
        """Get the schema string"""
        return self.schema 