#!/usr/bin/env python3
"""
Script to round specific columns in a CSV file to a specified number of decimal places.

Usage:
    python round_csv_columns.py input.csv output.csv decimal_places column1 [column2 ...]

Example:
    python round_csv_columns.py ptz_parsed.csv ptz_parsed_rounded.csv 2 "TIME FROM ENTRY (SECONDS)"
    python round_csv_columns.py data.csv data_rounded.csv 0 "Column1" "Column2"  # Round to whole numbers
"""

import numpy as np
import pandas as pd
import sys
import argparse
from pathlib import Path


def round_csv_columns(input_file, output_file, columns_to_round, decimal_places=0):
    """
    Round specified columns in a CSV file to a specified number of decimal places.

    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
        columns_to_round (list): List of column names to round
        decimal_places (int): Number of decimal places to round to (default: 0)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")

        # Check if specified columns exist
        missing_columns = [col for col in columns_to_round if col not in df.columns]
        if missing_columns:
            print("Warning: The following columns were not found in the CSV:")
            for col in missing_columns:
                print(f"  - '{col}'")
            print(f"Available columns: {list(df.columns)}")
            return False

        # Round the specified columns
        for column in columns_to_round:
            if column in df.columns:
                print(f"Rounding column '{column}' to {decimal_places} decimal places")
                # Convert to numeric first (in case there are string values)
                df[column] = pd.to_numeric(df[column], errors="coerce")
                # Replace NaN with -99999
                df[column] = df[column].replace(np.nan, -99999)
                # Round to specified decimal places
                df[column] = df[column].round(decimal_places)

                # Only convert to int if rounding to whole numbers (0 decimal places)
                if decimal_places == 0:
                    df[column] = df[column].astype(int)

        # Save the modified DataFrame
        df.to_csv(output_file, index=False)
        print(f"Successfully saved rounded data to: {output_file}")

        return True

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Round specific columns in a CSV file to a specified number of decimal places. "
        "Replaces NaN with -99999.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.csv output.csv 2 "TIME FROM ENTRY (SECONDS)"
  %(prog)s data.csv data_rounded.csv 0 "Column 1" "Column 2" "Column 3"
  %(prog)s measurements.csv measurements_rounded.csv 1 "Temperature" "Pressure"
        """,
    )

    parser.add_argument("input_file", help="Input CSV file path")
    parser.add_argument("output_file", help="Output CSV file path")
    parser.add_argument("decimal_places", type=int, help="Number of decimal places to round to")
    parser.add_argument("columns", nargs="+", help="Column names to round (space-separated)")

    # Also support interactive mode if no arguments provided
    if len(sys.argv) == 1:
        print("Interactive mode:")
        input_file = input("Enter input CSV file path: ").strip()
        output_file = input("Enter output CSV file path: ").strip()

        try:
            decimal_places = int(input("Enter number of decimal places (0 for whole numbers): ").strip())
        except ValueError:
            print("Invalid number for decimal places!")
            return 1

        columns_input = input("Enter column names to round (comma-separated): ").strip()
        columns = [col.strip() for col in columns_input.split(",")]

        if not input_file or not output_file or not columns or not columns[0]:
            print("All fields are required!")
            return 1

        success = round_csv_columns(input_file, output_file, columns, decimal_places)
        return 0 if success else 1

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist!")
        return 1

    # Validate decimal places is non-negative
    if args.decimal_places < 0:
        print(f"Error: Decimal places must be non-negative, got {args.decimal_places}")
        return 1

    success = round_csv_columns(args.input_file, args.output_file, args.columns, args.decimal_places)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
