"""
Question Data Import Script V2
Imports question_samples.sql using mysql.connector with multi-statement support
"""

import mysql.connector
from mysql.connector import Error
import sys
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connection details from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 13288)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'defaultdb'),
    'ssl_disabled': False
}

SQL_FILE_PATH = r'c:\AMARDATA\GITHUB\NITIN_QUESTION_QUALITY\question_samples.sql'

def import_questions():
    """Import questions from SQL file into database"""
    connection = None
    cursor = None

    try:
        print("=" * 80)
        print("STARTING QUESTION DATA IMPORT (V2)")
        print("=" * 80)

        # Connect to database
        print("\n[STEP 1] Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)

        if not connection.is_connected():
            print("[ERROR] Failed to connect to database")
            return False

        print("[OK] Connected successfully")

        # Read SQL file
        print("\n[STEP 2] Reading SQL file...")
        print(f"   File: {SQL_FILE_PATH}")

        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        file_size_kb = len(sql_content) / 1024
        print(f"[OK] File read successfully ({file_size_kb:.2f} KB)")

        # Execute SQL file using multi-statement
        print("\n[STEP 3] Executing SQL file...")
        print("   This may take a few moments...")

        cursor = connection.cursor()

        # Split by semicolons but be smart about it
        # Execute in chunks to avoid timeout
        statements = []
        current_statement = []

        for line in sql_content.split('\n'):
            # Skip comments and empty lines
            line = line.strip()
            if line.startswith('--') or line.startswith('/*') or line.startswith('*/') or not line:
                continue
            if line.startswith('SET') or line.startswith('START') or line.startswith('/*!'):
                continue

            current_statement.append(line)

            # Check if statement ends
            if line.endswith(';'):
                full_statement = ' '.join(current_statement)
                if 'CREATE TABLE' in full_statement or 'INSERT INTO' in full_statement:
                    statements.append(full_statement)
                current_statement = []

        print(f"[OK] Found {len(statements)} statements to execute")

        # Execute statements one by one
        for idx, statement in enumerate(statements, 1):
            try:
                if 'CREATE TABLE' in statement:
                    print(f"   [{idx}/{len(statements)}] Creating table...")
                elif 'INSERT INTO' in statement:
                    print(f"   [{idx}/{len(statements)}] Inserting data...")

                cursor.execute(statement)
                connection.commit()

            except Error as e:
                error_msg = str(e)
                print(f"\n   [ERROR] Statement {idx} failed:")
                print(f"           {error_msg[:200]}")

                # If it's because table already exists, that's OK
                if "Table 'xyz1' already exists" in error_msg:
                    print("   [INFO] Table already exists, continuing with inserts...")
                    continue
                else:
                    # For other errors, show more context
                    print(f"   [DEBUG] Statement preview: {statement[:200]}...")
                    raise

        # Verify the import
        print("\n[STEP 4] Verifying import...")
        cursor.execute("SELECT COUNT(*) FROM xyz1")
        row_count = cursor.fetchone()[0]
        print(f"[OK] Table 'xyz1' now contains {row_count} records")

        if row_count > 0:
            # Show sample records
            print("\n[STEP 5] Sample records from imported data:")
            cursor.execute("SELECT questionid, LEFT(question, 80), status FROM xyz1 LIMIT 5")
            samples = cursor.fetchall()

            for i, (qid, question, status) in enumerate(samples, 1):
                print(f"\n   Record {i}:")
                print(f"      ID: {qid}")
                print(f"      Question: {question}...")
                print(f"      Status: {status}")

        print("\n" + "=" * 80)
        print("IMPORT COMPLETED!")
        print("=" * 80)
        print(f"\n[SUMMARY]")
        print(f"   Total records imported: {row_count}")
        print(f"   Table name: xyz1")
        print(f"   Database: defaultdb")
        print(f"   Host: {DB_CONFIG['host']}")

        return row_count > 0

    except FileNotFoundError:
        print(f"\n[ERROR] SQL file not found: {SQL_FILE_PATH}")
        return False

    except Error as e:
        print(f"\n[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n[OK] Database connection closed.")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("QUESTION DATA IMPORT UTILITY V2")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Drop table 'xyz1' if it exists (to start fresh)")
    print("  2. Create table 'xyz1' in your Aiven MySQL database")
    print("  3. Import all question data from question_samples.sql")
    print("  4. Verify the import was successful")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")

    try:
        input()

        # First, drop the table if it exists
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            print("\n[CLEANUP] Dropping existing table if it exists...")
            cursor.execute("DROP TABLE IF EXISTS xyz1")
            connection.commit()
            print("[OK] Ready for fresh import")
            cursor.close()
            connection.close()
        except:
            pass

        success = import_questions()

        if success:
            print("\n[SUCCESS] Import completed successfully!")
        else:
            print("\n[FAILED] Import failed. Please check the output above.")

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Import cancelled by user.")
        sys.exit(0)
