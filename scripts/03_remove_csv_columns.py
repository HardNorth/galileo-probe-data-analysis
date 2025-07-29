#!/usr/bin/env python3
"""
Script to remove specified columns from a CSV file.
Columns can be specified either by name or by column number (0-based indexing).
"""

import pandas as pd
import os
import argparse
import sys


def remove_csv_columns(input_file, output_file, columns_to_remove):
    """
    Remove specified columns from a CSV file.

    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        columns_to_remove (list): List of column names or numbers to remove
    """
    # Read the CSV file
    print(f"Reading data from: {input_file}")
    df = pd.read_csv(input_file)

    print(f"Original data has {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")

    # Process columns to remove - handle both names and numbers
    processed_columns = []
    column_names = list(df.columns)

    for col in columns_to_remove:
        # Try to convert to integer first (column number)
        try:
            col_num = int(col)
            if 0 <= col_num < len(column_names):
                processed_columns.append(column_names[col_num])
                print(f"Will remove column {col_num}: '{column_names[col_num]}'")
            else:
                print(f"Error: Column number {col_num} is out of range (0-{len(column_names) - 1})")
                return False
        except ValueError:
            # Not a number, treat as column name
            if col in column_names:
                processed_columns.append(col)
                print(f"Will remove column: '{col}'")
            else:
                print(f"Error: Column '{col}' not found in CSV file")
                print(f"Available columns: {column_names}")
                return False

    # Remove duplicates while preserving order
    processed_columns = list(dict.fromkeys(processed_columns))

    if not processed_columns:
        print("No valid columns to remove!")
        return False

    # Remove the specified columns
    df_modified = df.drop(columns=processed_columns)

    print(f"After removal: {len(df_modified)} rows and {len(df_modified.columns)} columns")
    print(f"Remaining columns: {list(df_modified.columns)}")
    print(f"Removed {len(processed_columns)} column(s): {processed_columns}")

    # Write to output file
    df_modified.to_csv(output_file, index=False)
    print(f"Modified data saved to: {output_file}")
    return True


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Remove specified columns from a CSV file",
        epilog="""
Examples:
  %(prog)s data.csv -c "Column Name" "Another Column"    # Remove by name
  %(prog)s data.csv -c 0 2 5                           # Remove by number (0-based)
  %(prog)s data.csv -c "Name" 1 "Other"                # Mix names and numbers
  %(prog)s data.csv -c 0 -o output.csv                 # Specify output file
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument(
        "-c", "--columns", nargs="+", required=True, help="Column names or numbers (0-based) to remove"
    )
    parser.add_argument("-o", "--output", help="Output file path (default: input_file_columns_removed.csv)")

    args = parser.parse_args()

    input_file = args.input_file

    # Create output filename
    if args.output:
        output_file = args.output
    else:
        # Create output filename with "_columns_removed" suffix
        base_name = os.path.splitext(input_file)[0]  # Remove .csv extension
        output_file = f"{base_name}_columns_removed.csv"

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)

    # Check if output file would overwrite input file
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        print("Error: Output file cannot be the same as input file!")
        sys.exit(1)

    # Perform column removal
    success = remove_csv_columns(input_file, output_file, args.columns)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
