#!/usr/bin/env python3
"""
Script to convert temperature values from Celsius to Kelvin in CSV files
Accepts input file path and column name as command line arguments
"""

import argparse
import csv
import os
import sys


def convert_celsius_to_kelvin(csv_file_path, column_name):
    """
    Convert temperature values from Celsius to Kelvin in the CSV file

    Args:
        csv_file_path (str): Path to the CSV file
        column_name (str): Name of the temperature column to convert
    """
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File {csv_file_path} not found!")
        return False

    # Read the CSV data
    rows = []
    temp_column_index = None

    with open(csv_file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        # Read header and find the temperature column
        header = next(reader)
        print(f"Original header: {header}")

        # Find the temperature column by name
        for i, col_name in enumerate(header):
            if column_name.lower() in col_name.lower():
                temp_column_index = i
                # Update the column header to indicate Kelvin
                if "celsius" in col_name.lower():
                    header[i] = (
                        col_name.replace("Celsius", "Kelvin").replace("celsius", "Kelvin").replace("CELSIUS", "KELVIN")
                    )
                elif "degrees c" in col_name.lower():
                    header[i] = (
                        col_name.replace("degrees C", "Kelvin")
                        .replace("Degrees C", "Kelvin")
                        .replace("DEGREES C", "KELVIN")
                    )
                else:
                    header[i] = f"{col_name} (Kelvin)"
                print(f"Found temperature column: '{col_name}' at index {i}")
                print(f"Updated header: {header}")
                break

        if temp_column_index is None:
            print(f"Error: Could not find temperature column '{column_name}' in header")
            print(f"Available columns: {header}")
            return False

        rows.append(header)

        # Read data rows and convert temperature values
        converted_count = 0
        for row_num, row in enumerate(reader, start=2):
            try:
                if len(row) > temp_column_index and row[temp_column_index].strip():
                    # Convert temperature from Celsius to Kelvin
                    celsius_temp = float(row[temp_column_index])
                    kelvin_temp = celsius_temp + 273.15
                    row[temp_column_index] = f"{kelvin_temp:.2f}"
                    converted_count += 1

                rows.append(row)

            except (ValueError, IndexError) as e:
                print(f"Warning: Could not convert temperature in row {row_num}: {e}")
                rows.append(row)  # Keep original row if conversion fails

    # Write the updated data back to the file
    with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Successfully converted temperatures from Celsius to Kelvin in {csv_file_path}")
    print(f"Total rows processed: {len(rows) - 1}")  # Subtract 1 for header
    print(f"Temperature values converted: {converted_count}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert temperature values from Celsius to Kelvin in CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.csv "ATMOSPHERIC TEMPERATURE"
  %(prog)s output/ptz_parsed.csv "Temperature (degrees Celsius)"
  %(prog)s data.csv "temp"
        """,
    )

    parser.add_argument("csv_file", help="Path to the CSV file to process")

    parser.add_argument("column_name", help="Name (or part of name) of the temperature column to convert")

    args = parser.parse_args()

    # Validate file path
    if not os.path.exists(args.csv_file):
        print(f"Error: File '{args.csv_file}' does not exist!")
        sys.exit(1)

    print("Converting temperature values from Celsius to Kelvin...")
    print(f"File: {args.csv_file}")
    print(f"Column: {args.column_name}")
    print("-" * 50)

    success = convert_celsius_to_kelvin(args.csv_file, args.column_name)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
