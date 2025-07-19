# Simple Refinement Service

This is a simplified version of the Vana Data Refinement Template that just casts input data to output data for verification purposes using the **Coding Assistant Training Data Schema**.

## Overview

The simple refinement service:
1. Reads JSON data from the `/input` directory
2. Passes the data through without any transformation (simple pass-through)
3. Creates a schema.json file with the Coding Assistant Training Data Schema
4. Saves the transformed data and schema to the `/output` directory
5. Optionally uploads to IPFS if credentials are provided

## Schema

The service uses the **Coding Assistant Training Data Schema** which is designed for collecting high-quality data from VS Code extensions for fine-tuning coding language models. The schema includes:

- **instruction_dataset**: Array of coding instruction examples with:
  - `instruction_type`: Category (bug_fixing, code_completion, etc.)
  - `instruction`: Task description
  - `input`: Input code/text
  - `output`: Expected/actual solution
  - `context`: Rich contextual information (language, user_prompt, etc.)
  - `timestamp`: When recorded
  - `model_used`: LLM that provided output

- **dataset_metadata**: Overall dataset information (version, created_at, sample_count, license, source)

## Files Created

- `output/schema.json` - The Coding Assistant Training Data Schema definition
- `output/transformed_data.json` - The input data (passed through unchanged)
- `output/output.json` - The refinement output with metadata

## Quick Start

### Local Development

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the refinement service:
```bash
INPUT_DIR=input OUTPUT_DIR=output python -m refiner
```

### Docker

1. Build the container:
```bash
docker build -t coding-assistant-refiner .
```

2. Run the container:
```bash
docker run --rm \
  --volume $(pwd)/input:/input \
  --volume $(pwd)/output:/output \
  coding-assistant-refiner
```

## Testing

Run the test script to verify the data flow:
```bash
python test_simple_refiner.py
```

## Data Flow Verification

The service processes the sample data in `input/sample_data.json` and outputs:
- **Input**: Coding instruction dataset with bug fixing example
- **Output**: Same data structure (no transformation)
- **Schema**: JSON Schema for Coding Assistant Training Data

This simple service is perfect for verifying that the data flow pipeline works correctly before implementing complex transformations.

## Sample Data Structure

The service expects input data in this format:
```json
{
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
```

## Environment Variables

- `INPUT_DIR` - Directory containing input files (default: `/input`)
- `OUTPUT_DIR` - Directory for output files (default: `/output`)
- `PINATA_API_KEY` - Optional IPFS API key
- `PINATA_API_SECRET` - Optional IPFS API secret

## Supported Instruction Types

The schema supports 24 different instruction types including:
- bug_fixing, code_completion, algorithm_implementation
- code_refactoring, unit_test_generation, documentation_generation
- performance_optimization, security_fix, debugging
- And many more for comprehensive coding assistance training 