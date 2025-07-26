#!/usr/bin/env python3
"""
Final comprehensive test for Vana-compatible refinement service.
This test validates that the service creates proper SQLite databases 
that are compatible with Vana's Query Engine.
"""

import os
import sqlite3
import json
import subprocess
import sys
from datetime import datetime

def run_refinement_service():
    """Run the refinement service and capture output."""
    print("🚀 Running Vana Refinement Service...")
    print("=" * 50)
    
    # Clean output directory
    if os.path.exists("output/db.libsql"):
        os.remove("output/db.libsql")
        print("🧹 Cleaned previous database")
    
    # Run the refinement service
    env = os.environ.copy()
    env.update({
        "INPUT_DIR": "input",
        "OUTPUT_DIR": "output"
    })
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "refiner"
        ], cwd=".", env=env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Refinement service completed successfully")
            return True
        else:
            print(f"❌ Refinement service failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Refinement service timed out")
        return False
    except Exception as e:
        print(f"❌ Error running refinement service: {e}")
        return False

def validate_output_files():
    """Validate that all expected output files are created."""
    print("\n📁 Validating Output Files...")
    print("=" * 50)
    
    expected_files = [
        "output/db.libsql",
        "output/schema.json", 
        "output/output.json"
    ]
    
    all_files_exist = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_exist = False
    
    return all_files_exist

def validate_database_schema():
    """Validate the SQLite database schema."""
    print("\n🗄️  Validating Database Schema...")
    print("=" * 50)
    
    db_path = "output/db.libsql"
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Expected tables
        expected_tables = [
            "instruction_dataset",
            "dataset_metadata", 
            "context_metadata",
            "project_dependencies",
            "linting_errors",
            "user_feedback"
        ]
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        actual_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = set(expected_tables) - set(actual_tables)
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        print("✅ All expected tables present")
        
        # Check instruction_dataset schema
        cursor.execute("PRAGMA table_info(instruction_dataset)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = [
            'id', 'instruction_id', 'instruction_type', 'instruction',
            'input_code', 'output_code', 'language', 'user_prompt',
            'timestamp', 'model_used', 'created_at'
        ]
        
        missing_columns = set(required_columns) - set(column_names)
        if missing_columns:
            print(f"❌ Missing columns in instruction_dataset: {missing_columns}")
            return False
        
        print("✅ instruction_dataset schema is correct")
        
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_list(linting_errors)")
        fk_constraints = cursor.fetchall()
        
        if not fk_constraints:
            print("❌ No foreign key constraints found")
            return False
        
        print("✅ Foreign key constraints present")
        return True
        
    except Exception as e:
        print(f"❌ Database schema validation failed: {e}")
        return False
    finally:
        conn.close()

def test_data_integrity():
    """Test that data was properly inserted."""
    print("\n📊 Testing Data Integrity...")
    print("=" * 50)
    
    db_path = "output/db.libsql"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Count records in each table
        tables_with_data = [
            ("instruction_dataset", 5),  # 5 training examples
            ("dataset_metadata", 1),     # 1 metadata record
            ("linting_errors", 2),       # 2 linting errors
            ("user_feedback", 1),        # 1 feedback record
            ("project_dependencies", 1)  # 1 dependency
        ]
        
        all_counts_correct = True
        for table, expected_count in tables_with_data:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            actual_count = cursor.fetchone()[0]
            
            if actual_count == expected_count:
                print(f"✅ {table}: {actual_count} records")
            else:
                print(f"❌ {table}: {actual_count} records (expected {expected_count})")
                all_counts_correct = False
        
        if not all_counts_correct:
            return False
        
        # Test data quality
        cursor.execute("SELECT COUNT(*) FROM instruction_dataset WHERE language IS NOT NULL")
        non_null_languages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM instruction_dataset")
        total_instructions = cursor.fetchone()[0]
        
        if non_null_languages != total_instructions:
            print(f"❌ Data quality issue: some languages are NULL")
            return False
        
        print("✅ Data quality checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False
    finally:
        conn.close()

def test_vana_compatibility():
    """Test complex queries that Vana Query Engine would run."""
    print("\n🎯 Testing Vana Query Engine Compatibility...")
    print("=" * 50)
    
    db_path = "output/db.libsql"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Complex queries that test Vana compatibility
    test_queries = [
        # Aggregation query
        ("Instruction type distribution",
         "SELECT instruction_type, COUNT(*) as count FROM instruction_dataset GROUP BY instruction_type"),
        
        # JOIN query with filtering
        ("Python instructions with errors",
         """SELECT i.instruction_id, i.instruction, l.message 
            FROM instruction_dataset i 
            JOIN linting_errors l ON i.id = l.instruction_id 
            WHERE i.language = 'python'"""),
        
        # Complex aggregation with multiple tables
        ("Code complexity analysis",
         """SELECT 
                i.language,
                COUNT(*) as instruction_count,
                AVG(LENGTH(i.input_code)) as avg_input_length,
                COUNT(l.id) as error_count
            FROM instruction_dataset i
            LEFT JOIN linting_errors l ON i.id = l.instruction_id
            GROUP BY i.language"""),
        
        # Time-based analysis
        ("Training data timeline",
         """SELECT 
                DATE(timestamp) as date,
                COUNT(*) as instructions_per_day
            FROM instruction_dataset 
            GROUP BY DATE(timestamp)
            ORDER BY date"""),
        
        # Quality metrics
        ("High-quality solutions",
         """SELECT 
                i.instruction_type,
                i.model_used,
                uf.rating,
                uf.comment
            FROM instruction_dataset i
            JOIN user_feedback uf ON i.id = uf.instruction_id
            WHERE uf.rating >= 4""")
    ]
    
    try:
        all_queries_passed = True
        for query_name, query_sql in test_queries:
            start_time = datetime.now()
            cursor.execute(query_sql)
            results = cursor.fetchall()
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds() * 1000
            
            if results:
                print(f"✅ {query_name}: {len(results)} results ({duration:.2f}ms)")
            else:
                print(f"⚠️  {query_name}: No results (might be expected)")
        
        print("✅ All Vana compatibility queries passed")
        return True
        
    except Exception as e:
        print(f"❌ Vana compatibility test failed: {e}")
        return False
    finally:
        conn.close()

def validate_schema_json():
    """Validate the schema.json file."""
    print("\n📋 Validating Schema JSON...")
    print("=" * 50)
    
    schema_path = "output/schema.json"
    if not os.path.exists(schema_path):
        print("❌ schema.json not found")
        return False
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        required_fields = ['name', 'version', 'description', 'dialect', 'schema']
        missing_fields = set(required_fields) - set(schema.keys())
        
        if missing_fields:
            print(f"❌ Missing schema fields: {missing_fields}")
            return False
        
        if schema['dialect'] != 'sqlite':
            print(f"❌ Wrong dialect: {schema['dialect']} (expected 'sqlite')")
            return False
        
        if 'CREATE TABLE' not in schema['schema']:
            print("❌ Schema doesn't contain CREATE TABLE statements")
            return False
        
        print(f"✅ Schema validation passed")
        print(f"   Name: {schema['name']}")
        print(f"   Version: {schema['version']}")
        print(f"   Dialect: {schema['dialect']}")
        print(f"   Tables: {schema['schema'].count('CREATE TABLE')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🧪 Vana Refinement Service - Final Validation")
    print("=" * 60)
    print("Testing complete pipeline from JSON input to SQLite database")
    print("=" * 60)
    
    # Test sequence
    tests = [
        ("Refinement Service", run_refinement_service),
        ("Output Files", validate_output_files),
        ("Database Schema", validate_database_schema),
        ("Data Integrity", test_data_integrity),
        ("Vana Compatibility", test_vana_compatibility),
        ("Schema JSON", validate_schema_json)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n🏁 Final Test Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Refinement service is fully Vana-compatible!")
        print("📊 Ready for production deployment!")
        
        # Show final database info
        if os.path.exists("output/db.libsql"):
            db_size = os.path.getsize("output/db.libsql")
            print(f"📁 Final database: output/db.libsql ({db_size:,} bytes)")
        
        return True
    else:
        print(f"\n💥 {total - passed} test(s) failed!")
        print("Please fix the issues before deploying to Vana.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 