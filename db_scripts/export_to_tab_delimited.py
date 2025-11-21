"""
Export Question Data to Tab-Delimited Format
Streams data directly from database to file WITHOUT loading into memory
"""

import mysql.connector
from mysql.connector import Error
import sys
import io
import csv
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

OUTPUT_FILE = r'c:\AMARDATA\GITHUB\NITIN_QUESTION_QUALITY\question_data_export.txt'
BATCH_SIZE = 100  # Process 100 records at a time

def export_to_tab_delimited():
    """Export xyz1 table to tab-delimited file"""
    connection = None
    cursor = None
    file_handle = None

    try:
        print("=" * 80)
        print("TAB-DELIMITED EXPORT UTILITY")
        print("=" * 80)

        # Connect to database
        print("\n[STEP 1] Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)

        if not connection.is_connected():
            print("[ERROR] Failed to connect to database")
            return False

        print("[OK] Connected successfully")

        # Get column names first
        print("\n[STEP 2] Fetching table structure...")
        cursor = connection.cursor()
        cursor.execute("DESCRIBE xyz1")
        columns_info = cursor.fetchall()
        column_names = [col[0] for col in columns_info]
        print(f"[OK] Found {len(column_names)} columns")

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM xyz1")
        total_records = cursor.fetchone()[0]
        print(f"[OK] Total records to export: {total_records}")

        # Open file for writing
        print(f"\n[STEP 3] Opening output file...")
        print(f"   File: {OUTPUT_FILE}")

        # Use UTF-8 encoding with BOM for Excel compatibility
        file_handle = open(OUTPUT_FILE, 'w', encoding='utf-8-sig', newline='')

        # Create CSV writer with tab delimiter
        writer = csv.writer(file_handle, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

        print("[OK] File opened successfully")

        # Write header row
        print("\n[STEP 4] Writing header row...")
        writer.writerow(column_names)
        print("[OK] Header written")

        # Stream data in batches
        print(f"\n[STEP 5] Streaming data to file (batch size: {BATCH_SIZE})...")

        # Use server-side cursor for efficient streaming
        cursor.close()
        cursor = connection.cursor()

        # Execute query
        cursor.execute("SELECT * FROM xyz1")

        records_written = 0
        batch_count = 0

        # Fetch and write in batches
        while True:
            batch = cursor.fetchmany(BATCH_SIZE)
            if not batch:
                break

            batch_count += 1

            # Write each row in the batch
            for row in batch:
                # Convert None to empty string, handle other data types
                clean_row = []
                for value in row:
                    if value is None:
                        clean_row.append('')
                    else:
                        # Convert to string and handle newlines/tabs
                        str_value = str(value)
                        # Replace actual tabs and newlines with spaces to avoid breaking format
                        str_value = str_value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
                        clean_row.append(str_value)

                writer.writerow(clean_row)
                records_written += 1

            # Show progress
            print(f"   Batch {batch_count}: {records_written}/{total_records} records written...")

        print(f"\n[OK] All data written to file!")

        # File stats
        file_handle.flush()
        file_size_kb = file_handle.tell() / 1024

        print("\n" + "=" * 80)
        print("EXPORT COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\n[SUMMARY]")
        print(f"   Records exported: {records_written}")
        print(f"   Columns: {len(column_names)}")
        print(f"   Output file: {OUTPUT_FILE}")
        print(f"   File size: {file_size_kb:.2f} KB")
        print(f"\n[NEXT STEPS]")
        print(f"   1. Open Excel")
        print(f"   2. Go to Data > From Text/CSV")
        print(f"   3. Select the file: {OUTPUT_FILE}")
        print(f"   4. Delimiter: Tab")
        print(f"   5. Or simply open the file and copy-paste into Excel")

        return True

    except Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up
        if file_handle:
            file_handle.close()
            print("\n[OK] File closed.")

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            print("[OK] Database connection closed.")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("QUESTION DATA - TAB-DELIMITED EXPORT")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Connect to your Aiven MySQL database")
    print("  2. Stream data from 'xyz1' table in batches")
    print("  3. Write to tab-delimited text file")
    print("  4. Ready for Excel import/paste")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")

    try:
        input()
        success = export_to_tab_delimited()

        if success:
            print("\n[SUCCESS] Export completed!")
            print("\nYou can now open the file in Excel or any text editor.")
        else:
            print("\n[FAILED] Export failed. Please check the output above.")

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Export cancelled by user.")
        sys.exit(0)
