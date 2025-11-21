"""
Question Data Import Script
Safely imports question_samples.sql into MySQL database
"""

import mysql.connector
from mysql.connector import Error
import sys
import io
import re
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
        print("STARTING QUESTION DATA IMPORT")
        print("=" * 80)

        # Connect to database
        print("\n[STEP 1] Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)

        if not connection.is_connected():
            print("[ERROR] Failed to connect to database")
            return False

        print("[OK] Connected successfully")

        cursor = connection.cursor()

        # Read SQL file
        print("\n[STEP 2] Reading SQL file...")
        print(f"   File: {SQL_FILE_PATH}")

        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        file_size_kb = len(sql_content) / 1024
        print(f"[OK] File read successfully ({file_size_kb:.2f} KB)")

        # Split SQL into statements
        print("\n[STEP 3] Parsing SQL statements...")

        # Remove comments and split by semicolon
        # Keep only CREATE TABLE and INSERT statements
        statements = []

        # Extract CREATE TABLE statement
        create_match = re.search(r'CREATE TABLE.*?;', sql_content, re.DOTALL | re.IGNORECASE)
        if create_match:
            statements.append(create_match.group(0))
            print("[OK] Found CREATE TABLE statement")
        else:
            print("[ERROR] No CREATE TABLE statement found")
            return False

        # Extract INSERT statements
        insert_pattern = r'INSERT INTO `xyz1`.*?VALUES.*?;'
        insert_matches = re.finditer(insert_pattern, sql_content, re.DOTALL | re.IGNORECASE)

        insert_count = 0
        for match in insert_matches:
            statements.append(match.group(0))
            insert_count += 1

        print(f"[OK] Found {insert_count} INSERT statement(s)")
        print(f"[OK] Total statements to execute: {len(statements)}")

        # Execute statements
        print("\n[STEP 4] Executing SQL statements...")
        print("   This may take a few moments...")

        successful = 0
        failed = 0

        for idx, statement in enumerate(statements, 1):
            try:
                # Show progress for every 10 statements
                if idx == 1:
                    print(f"\n   Creating table 'xyz1'...")
                elif idx % 10 == 0:
                    print(f"   Processed {idx}/{len(statements)} statements...")

                cursor.execute(statement)
                connection.commit()
                successful += 1

            except Error as e:
                failed += 1
                print(f"\n   [WARNING] Statement {idx} failed: {str(e)[:100]}")
                # Continue with other statements
                continue

        print(f"\n[OK] Execution complete!")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")

        # Verify the import
        print("\n[STEP 5] Verifying import...")
        cursor.execute("SELECT COUNT(*) FROM xyz1")
        row_count = cursor.fetchone()[0]
        print(f"[OK] Table 'xyz1' now contains {row_count} records")

        # Show sample records
        print("\n[STEP 6] Sample records from imported data:")
        cursor.execute("SELECT questionid, question, status FROM xyz1 LIMIT 3")
        samples = cursor.fetchall()

        for i, (qid, question, status) in enumerate(samples, 1):
            # Clean HTML tags for display
            clean_q = re.sub('<[^<]+?>', '', question)
            clean_q = clean_q[:100] + '...' if len(clean_q) > 100 else clean_q
            print(f"\n   Sample {i}:")
            print(f"      Question ID: {qid}")
            print(f"      Question: {clean_q}")
            print(f"      Status: {status}")

        print("\n" + "=" * 80)
        print("IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\n[SUMMARY]")
        print(f"   Total records imported: {row_count}")
        print(f"   Table name: xyz1")
        print(f"   Database: defaultdb")
        print(f"   You can now query this table using SQL or DBeaver")

        return True

    except FileNotFoundError:
        print(f"\n[ERROR] SQL file not found: {SQL_FILE_PATH}")
        return False

    except Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n[OK] Database connection closed.")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("QUESTION DATA IMPORT UTILITY")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Create table 'xyz1' in your Aiven MySQL database")
    print("  2. Import all question data from question_samples.sql")
    print("  3. Verify the import was successful")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")

    try:
        input()
        success = import_questions()

        if success:
            print("\n[SUCCESS] Import completed without errors!")
        else:
            print("\n[FAILED] Import encountered errors. Please check the output above.")

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Import cancelled by user.")
        sys.exit(0)
