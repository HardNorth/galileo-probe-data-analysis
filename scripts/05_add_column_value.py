#!/usr/bin/env python3
"""
Script to add a specified value to each entry in a specified column of a CSV file.
Supports negative values and preserves the original data types when possible.
"""

import pandas as pd
import argparse
import sys
import os


def add_value_to_column(csv_file, column_name, value_to_add, output_file=None):
    """
    Add a specified value to each entry in a specified column of a CSV file.

    Args:
        csv_file (str): Path to the input CSV file
        column_name (str): Name of the column to modify
        value_to_add (float): Value to add to each entry in the column
        output_file (str): Path to the output CSV file. If None, overwrites input file.

    Returns:
        str: Path to the output file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Check if column exists
        if column_name not in df.columns:
            available_columns = ", ".join(df.columns)
            raise ValueError(f"Column '{column_name}' not found in CSV file. Available columns: {available_columns}")

        # Check if the column contains numeric data
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            print(f"Warning: Column '{column_name}' does not appear to contain numeric data.")
            print("Attempting to convert to numeric...")
            try:
                df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
                if df[column_name].isna().any():
                    print("Warning: Some values could not be converted to numeric and will become NaN")
            except Exception as e:
                raise ValueError(f"Cannot convert column '{column_name}' to numeric values: {str(e)}")

        # Store original data type
        original_dtype = df[column_name].dtype

        # Add the value to each entry in the specified column
        df[column_name] = df[column_name] + value_to_add

        # Preserve original data type if it was integer
        if pd.api.types.is_integer_dtype(original_dtype):
            # Check if the result can still be represented as integers
            if df[column_name].apply(lambda x: x == int(x)).all():
                df[column_name] = df[column_name].astype(original_dtype)
            else:
                print(
                    f"Warning: Results contain decimal values, keeping as float instead of original {original_dtype}"
                )

        # Determine output file path
        if output_file is None:
            output_file = csv_file

        # Write the modified DataFrame to CSV
        df.to_csv(output_file, index=False)

        print(f"Successfully added {value_to_add} to each value in column '{column_name}'")
        print(f"Output saved to: {output_file}")

        return output_file

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Add a specified value to each entry in a specified column of a CSV file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add -65 to each value in the 'TIME FROM ENTRY (SECONDS)' column
  python add_column_value.py data.csv "TIME FROM ENTRY (SECONDS)" -65

  # Add 10.5 to each value in the 'TEMPERATURE' column and save to a new file
  python add_column_value.py data.csv "TEMPERATURE" 10.5 -o modified_data.csv

  # Add -100 to each value in the 'ALTITUDE (KILOMETERS)' column
  python add_column_value.py data.csv "ALTITUDE (KILOMETERS)" -100
        """,
    )

    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("column_name", help="Name of the column to modify")
    parser.add_argument(
        "value", type=float, help="Value to add to each entry in the column (supports negative values)"
    )
    parser.add_argument("-o", "--output", help="Output CSV file path (default: overwrite input file)")

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: Input file '{args.csv_file}' does not exist.")
        sys.exit(1)

    # Process the file
    add_value_to_column(args.csv_file, args.column_name, args.value, args.output)


if __name__ == "__main__":
    main()
