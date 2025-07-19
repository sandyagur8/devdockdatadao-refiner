#!/usr/bin/env python3
"""
Simple test script to verify the data flow of the refinement service.
"""

import json
import os
import sys
from pathlib import Path

# Add the refiner directory to the path
sys.path.insert(0, str(Path(__file__).parent / "refiner"))

from simple_refine import SimpleRefiner
from config import settings

def test_simple_refiner():
    """Test the simple refiner with sample data."""
    print("Testing Simple Refiner...")
    
    # Create a simple refiner
    refiner = SimpleRefiner()
    
    # Sample input data matching the Coding Assistant Training Data Schema
    sample_data = {
        "instruction_dataset": [
            {
                "id": "example_001",
                "instruction_type": "bug_fixing",
                "instruction": "Fix the syntax error in this Python function",
                "input": "def calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3\nprint(result)",
                "output": "def calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3)\nprint(result)",
                "context": {
                    "language": "python",
                    "user_prompt": "There's a syntax error in my function, can you help me fix it?"
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "model_used": "claude-3-sonnet"
            }
        ],
        "dataset_metadata": {
            "version": "1.0.0",
            "created_at": "2024-01-15T10:30:00Z",
            "sample_count": 1,
            "license": "MIT",
            "source": "VS Code Extension Data Collection"
        }
    }
    
    # Test the transformer
    print("Testing transformer...")
    transformed_data = refiner.transformer.transform(sample_data)
    print(f"Input data: {json.dumps(sample_data, indent=2)}")
    print(f"Transformed data: {json.dumps(transformed_data, indent=2)}")
    
    # Verify data is the same (simple pass-through)
    assert transformed_data == sample_data, "Data should be identical for simple transformation"
    print("✓ Transformer test passed - data is identical")
    
    # Test schema
    print("\nTesting schema...")
    schema = refiner.transformer.get_schema()
    schema_dict = json.loads(schema)
    print(f"Schema title: {schema_dict.get('title', 'N/A')}")
    assert schema_dict.get('title') == "Coding Assistant Training Data Schema", "Schema should have correct title"
    print("✓ Schema test passed")
    
    print("\nAll tests passed! The simple refiner is working correctly.")

if __name__ == "__main__":
    test_simple_refiner() 