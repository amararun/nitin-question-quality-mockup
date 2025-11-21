"""
Database Explorer Script
Safely explores the MySQL database to see existing tables and their structure
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

def explore_database():
    """Explore the database and show all tables and their structures"""
    connection = None
    cursor = None
    try:
        print("=" * 80)
        print("CONNECTING TO AIVEN MYSQL DATABASE")
        print("=" * 80)

        # Establish connection
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"[OK] Successfully connected to MySQL Server version {db_info}")

            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"[OK] Connected to database: {db_name}\n")

            # Get all tables
            print("=" * 80)
            print("EXISTING TABLES IN DATABASE")
            print("=" * 80)
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            if not tables:
                print("[WARNING] No tables found in the database")
                print("[OK] Safe to create new table 'xyz1' from question_samples.sql\n")
                return True

            print(f"Found {len(tables)} table(s):\n")

            # For each table, show structure
            for (table_name,) in tables:
                print(f"\n[TABLE] {table_name}")
                print("-" * 80)

                # Get table structure
                cursor.execute(f"DESCRIBE {table_name};")
                columns = cursor.fetchall()
                print(f"   Columns ({len(columns)}):")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"      - {col[0]} ({col[1]})")
                if len(columns) > 5:
                    print(f"      ... and {len(columns) - 5} more columns")

                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   Total rows: {count}")

                # Check if this is the xyz1 table
                if table_name.lower() == 'xyz1':
                    print(f"\n   [WARNING] Table 'xyz1' already exists!")
                    print(f"   [WARNING] The question_samples.sql file wants to create this table.")
                    print(f"   [WARNING] We need to decide: DROP and recreate, or use different name?")

            print("\n" + "=" * 80)
            print("EXPLORATION COMPLETE")
            print("=" * 80)

            # Check specifically for xyz1
            table_names = [t[0].lower() for t in tables]
            if 'xyz1' in table_names:
                print("\n[ACTION REQUIRED]")
                print("   Table 'xyz1' exists. Options:")
                print("   1. Drop existing table and import fresh data")
                print("   2. Create table with different name (e.g., xyz1_new)")
                print("   3. Append data to existing table (if structure matches)")
                return False
            else:
                print("\n[SAFE TO PROCEED]")
                print("   Table 'xyz1' does not exist. Can safely import data.")
                return True

    except Error as e:
        print(f"\n[ERROR] Error connecting to MySQL: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("\n[OK] Database connection closed.")

if __name__ == "__main__":
    explore_database()
