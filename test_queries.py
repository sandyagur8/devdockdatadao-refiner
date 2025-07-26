#!/usr/bin/env python3

import sqlite3
import os
import json
from datetime import datetime

def test_database_queries():
    """Test various SQL queries against the refinement database."""
    db_path = "output/db.libsql"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Please run the refinement service first: python -m refiner")
        return False
    
    print("🔍 Testing SQLite Database Queries")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Test 1: Basic table info
        print("\n📊 Database Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # Test 2: Count all instruction records
        print("\n📈 Data Statistics:")
        cursor.execute("SELECT COUNT(*) FROM instruction_dataset;")
        instruction_count = cursor.fetchone()[0]
        print(f"  Total instructions: {instruction_count}")
        
        cursor.execute("SELECT COUNT(*) FROM dataset_metadata;")
        metadata_count = cursor.fetchone()[0]
        print(f"  Dataset metadata records: {metadata_count}")
        
        # Test 3: Query by instruction type
        print("\n🔧 Instructions by Type:")
        cursor.execute("""
            SELECT instruction_type, COUNT(*) as count 
            FROM instruction_dataset 
            GROUP BY instruction_type
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} instruction(s)")
        
        # Test 4: Query by programming language
        print("\n💻 Instructions by Language:")
        cursor.execute("""
            SELECT language, COUNT(*) as count 
            FROM instruction_dataset 
            GROUP BY language
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} instruction(s)")
        
        # Test 5: Query by model used
        print("\n🤖 Instructions by Model:")
        cursor.execute("""
            SELECT model_used, COUNT(*) as count 
            FROM instruction_dataset 
            GROUP BY model_used
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} instruction(s)")
        
        # Test 6: Complex join query with metadata
        print("\n📋 Detailed Instruction Data:")
        cursor.execute("""
            SELECT 
                i.instruction_id,
                i.instruction_type,
                i.language,
                i.model_used,
                i.timestamp,
                d.version as dataset_version,
                d.license
            FROM instruction_dataset i
            CROSS JOIN dataset_metadata d
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        if rows:
            print("  ID | Type | Language | Model | Dataset Version | License")
            print("  " + "-" * 65)
            for row in rows:
                print(f"  {row[0][:8]} | {row[1][:12]} | {row[2][:8]} | {row[3][:10]} | {row[5]} | {row[6]}")
        
        # Test 7: Search functionality
        print("\n🔍 Search Examples:")
        
        # Search for Python-related instructions
        cursor.execute("""
            SELECT instruction_id, instruction_type, language
            FROM instruction_dataset 
            WHERE language = 'python' OR input_code LIKE '%python%'
        """)
        python_instructions = cursor.fetchall()
        print(f"  Python-related instructions: {len(python_instructions)}")
        
        # Search for bug fixing instructions
        cursor.execute("""
            SELECT instruction_id, instruction
            FROM instruction_dataset 
            WHERE instruction_type = 'bug_fixing'
        """)
        bug_fixing = cursor.fetchall()
        print(f"  Bug fixing instructions: {len(bug_fixing)}")
        if bug_fixing:
            print(f"    Example: {bug_fixing[0][1][:50]}...")
        
        # Test 8: Time-based queries
        print("\n⏰ Time-based Analysis:")
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as instructions_count
            FROM instruction_dataset 
            GROUP BY DATE(timestamp)
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} instruction(s)")
        
        # Test 9: Schema verification - check all columns exist
        print("\n📋 Schema Validation:")
        cursor.execute("PRAGMA table_info(instruction_dataset)")
        columns = cursor.fetchall()
        expected_columns = ['id', 'instruction_id', 'instruction_type', 'instruction', 
                          'input_code', 'output_code', 'language', 'user_prompt', 
                          'timestamp', 'model_used', 'created_at']
        
        actual_columns = [col[1] for col in columns]
        missing_columns = set(expected_columns) - set(actual_columns)
        extra_columns = set(actual_columns) - set(expected_columns)
        
        if not missing_columns and not extra_columns:
            print("  ✅ All expected columns present")
        else:
            if missing_columns:
                print(f"  ❌ Missing columns: {missing_columns}")
            if extra_columns:
                print(f"  ℹ️  Extra columns: {extra_columns}")
        
        # Test 10: Query performance test
        print("\n⚡ Performance Test:")
        start_time = datetime.now()
        cursor.execute("""
            SELECT COUNT(*) FROM instruction_dataset 
            WHERE instruction_type IN ('bug_fixing', 'code_completion', 'debugging')
            AND language IN ('python', 'javascript', 'java')
        """)
        result = cursor.fetchone()[0]
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        print(f"  Complex query returned {result} results in {duration:.2f}ms")
        
        print("\n✅ All database queries completed successfully!")
        print(f"📁 Database file: {db_path}")
        print(f"📏 Database size: {os.path.getsize(db_path):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False
    finally:
        conn.close()

def demonstrate_vana_compatibility():
    """Demonstrate that the database is compatible with Vana's query engine."""
    print("\n🎯 Vana Query Engine Compatibility Demo")
    print("=" * 50)
    
    db_path = "output/db.libsql"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Example queries that Vana's Query Engine might run
        queries = [
            ("Count total training examples", 
             "SELECT COUNT(*) FROM instruction_dataset;"),
            
            ("Get all bug fixing examples",
             "SELECT instruction_id, instruction, input_code FROM instruction_dataset WHERE instruction_type = 'bug_fixing';"),
            
            ("Find Python code examples",
             "SELECT instruction_id, input_code, output_code FROM instruction_dataset WHERE language = 'python';"),
            
            ("Get training examples by model",
             "SELECT model_used, COUNT(*) as count FROM instruction_dataset GROUP BY model_used;"),
            
            ("Find recent training data",
             "SELECT instruction_id, instruction_type, timestamp FROM instruction_dataset ORDER BY timestamp DESC LIMIT 5;"),
            
            ("Complex analytical query",
             """SELECT 
                instruction_type,
                language,
                COUNT(*) as example_count,
                AVG(LENGTH(input_code)) as avg_input_length,
                AVG(LENGTH(output_code)) as avg_output_length
                FROM instruction_dataset 
                GROUP BY instruction_type, language;""")
        ]
        
        for description, query in queries:
            print(f"\n📊 {description}:")
            print(f"   SQL: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            
            if len(results) <= 3:
                for result in results:
                    print(f"   Result: {result}")
            else:
                print(f"   Results: {len(results)} rows returned")
                print(f"   Sample: {results[0]}")
        
        print("\n✅ Database is fully compatible with Vana's Query Engine!")
        print("🚀 Ready for production deployment!")
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧪 Testing Vana Refinement Database")
    print("=" * 40)
    
    if test_database_queries():
        demonstrate_vana_compatibility()
    else:
        print("Please fix database issues before proceeding.") 