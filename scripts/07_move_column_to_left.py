#!/usr/bin/env python3
"""
Script to move a specified column to the leftmost position in a CSV file.
"""

import pandas as pd
import argparse
import sys
from pathlib import Path


def move_column_to_left(input_file, column_name, output_file=None):
    """
    Move a specified column to the leftmost position in a CSV file.

    Args:
        input_file (str): Path to the input CSV file
        column_name (str): Name of the column to move to the left
        output_file (str, optional): Path to the output CSV file.
                                   If None, overwrites the input file.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Check if the column exists
        if column_name not in df.columns:
            print(f"Error: Column '{column_name}' not found in the CSV file.")
            print(f"Available columns: {', '.join(df.columns.tolist())}")
            return False

        # Get all column names
        columns = df.columns.tolist()

        # Remove the specified column from its current position
        columns.remove(column_name)

        # Insert the column at the beginning
        new_columns = [column_name] + columns

        # Reorder the DataFrame
        df_reordered = df[new_columns]

        # Determine output file
        if output_file is None:
            output_file = input_file

        # Write the modified DataFrame to CSV
        df_reordered.to_csv(output_file, index=False)

        print(f"Successfully moved column '{column_name}' to the leftmost position.")
        print(f"Output saved to: {output_file}")

        return True

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return False
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{input_file}' is empty.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Move a specified column to the leftmost position in a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.csv "Column Name"
  %(prog)s input.csv "TIME (SECONDS)" -o output.csv
  %(prog)s output/nep_scatter.csv "TIME (SECONDS)"
        """,
    )

    parser.add_argument("input_file", help="Path to the input CSV file")

    parser.add_argument("column_name", help="Name of the column to move to the leftmost position")

    parser.add_argument(
        "-o", "--output", dest="output_file", help="Path to the output CSV file (default: overwrite input file)"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)

    # Move the column
    success = move_column_to_left(args.input_file, args.column_name, args.output_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
