#!/usr/bin/env python3
"""
Galileo Probe NFR Data Parser

This script parses Galileo Probe Net Flux Radiometer (NFR) data files (.tab)
that contain embedded metadata and column definitions, and converts them to CSV format.

Usage:
    python 02_parse_nfr_data.py <tab_file_path> <output_csv_path>
"""

import argparse
import csv
import re
import sys
from pathlib import Path


def convert_scientific_to_decimal(value_str):
    """
    Convert scientific notation to standard decimal notation.

    Args:
        value_str (str): String that might contain scientific notation

    Returns:
        float or str: Converted value as float if numeric, original string otherwise
    """
    try:
        # Try to convert to float (handles scientific notation)
        float_value = float(value_str)
        return float_value
    except ValueError:
        # Not a number, return as string
        return value_str


def parse_nfr_file(file_path):
    """
    Parse the NFR file to extract column information and data.

    Args:
        file_path (str): Path to the .tab file

    Returns:
        tuple: (columns, data) where columns is list of column info and data is list of records
    """
    columns = []
    data = []

    with open(file_path, "r") as f:
        content = f.read()

    # Split content into lines
    lines = content.split("\n")

    # Find where the data starts
    data_start_line = None
    label_records = None

    # Parse header for metadata
    for line in lines:
        if line.strip().startswith("^TABLE"):
            # Extract table start line number
            match = re.search(r"\^TABLE\s*=\s*(\d+)", line)
            if match:
                data_start_line = int(match.group(1))
        elif line.strip().startswith("LABEL_RECORDS"):
            # Extract number of label records
            match = re.search(r"LABEL_RECORDS\s*=\s*(\d+)", line)
            if match:
                label_records = int(match.group(1))

    # Use data_start_line if available, otherwise use label_records
    if data_start_line:
        header_end = data_start_line - 1  # Convert to 0-based index
    elif label_records:
        header_end = label_records
    else:
        # Fallback: look for END marker
        for i, line in enumerate(lines):
            if line.strip() == "END":
                header_end = i + 1
                break
        else:
            raise ValueError("Could not determine where header ends")

    # Extract column information from header
    header_content = "\n".join(lines[:header_end])

    # Find all column definitions
    pattern = r"OBJECT\s*=\s*COLUMN.*?END_OBJECT\s*=\s*COLUMN"
    column_sections = re.findall(pattern, header_content, re.DOTALL)

    for section in column_sections:
        column_info = {}

        # Extract column name
        name_match = re.search(r"NAME\s*=\s*([^\s]+)", section)
        if name_match:
            column_info["name"] = name_match.group(1).strip('"')

        # Extract description
        desc_match = re.search(r'DESCRIPTION\s*=\s*"([^"]+)"', section)
        if desc_match:
            column_info["description"] = desc_match.group(1)

        # Extract data type
        type_match = re.search(r"DATA_TYPE\s*=\s*([^\s]+)", section)
        if type_match:
            column_info["data_type"] = type_match.group(1).strip('"')

        # Extract byte information for parsing
        start_byte_match = re.search(r"START_BYTE\s*=\s*(\d+)", section)
        bytes_match = re.search(r"BYTES\s*=\s*(\d+)", section)
        if start_byte_match and bytes_match:
            column_info["start_byte"] = int(start_byte_match.group(1))
            column_info["bytes"] = int(bytes_match.group(1))

        if column_info:
            columns.append(column_info)

    # Sort columns by start_byte to ensure correct order
    columns.sort(key=lambda x: x.get("start_byte", 0))

    # Parse data section
    data_lines = lines[header_end:]

    for line in data_lines:
        line = line.rstrip("\n\r")
        if not line.strip():
            continue

        row = {}

        # Parse each column based on byte positions
        for col in columns:
            if "start_byte" in col and "bytes" in col:
                # Convert to 0-based indexing
                start = col["start_byte"] - 1
                end = start + col["bytes"]

                if end <= len(line):
                    value_str = line[start:end].strip()
                    if value_str:
                        # Convert based on data type
                        if col.get("data_type") == "INTEGER":
                            try:
                                value = int(value_str)
                            except ValueError:
                                value = value_str
                        else:
                            # REAL or other types
                            value = convert_scientific_to_decimal(value_str)
                    else:
                        value = None
                    row[col["name"]] = value
                else:
                    row[col["name"]] = None

        if row:
            data.append(row)

    return columns, data


def create_csv_header(columns):
    """
    Create CSV header with column names and units.

    Args:
        columns (list): Column information

    Returns:
        list: CSV header row
    """
    headers = []
    for col in columns:
        name = col.get("name", "Unknown")
        description = col.get("description", "")

        # Extract unit from description if present
        unit_match = re.search(r"(W/m\^2|seconds|Hz|K|Pa|kg/m\^3|m/s)", description)
        if unit_match:
            unit = unit_match.group(1)
            header = f"{name} ({unit})"
        else:
            header = name

        headers.append(header)

    return headers


def write_csv(data, columns, output_path):
    """
    Write the parsed data to a CSV file.

    Args:
        data (list): Parsed data
        columns (list): Column information
        output_path (str): Path for the output CSV file
    """
    if not data:
        print("No data to write")
        return

    headers = create_csv_header(columns)
    column_names = [col["name"] for col in columns]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(headers)

        # Write data
        for row in data:
            csv_row = [row.get(col_name, "") for col_name in column_names]
            writer.writerow(csv_row)

    print(f"CSV file created: {output_path}")
    print(f"Records written: {len(data)}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse Galileo Probe NFR data files and convert to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python %(prog)s data/nfr/fluxes/tcnfdn.tab output/tcnfdn.csv
    python %(prog)s data/nfr/fluxes/tcnf.tab output/tcnf.csv
        """,
    )

    parser.add_argument("tab_file", help="Path to the .tab data file")
    parser.add_argument("output_csv", help="Output CSV file path")

    args = parser.parse_args()

    # Validate input file
    tab_path = Path(args.tab_file)

    if not tab_path.exists():
        print(f"Error: Tab file not found: {tab_path}")
        sys.exit(1)

    # Set output path
    output_path = Path(args.output_csv)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Parsing NFR data file: {tab_path}")
        columns, data = parse_nfr_file(tab_path)

        if not columns:
            print("Error: No column information found in file")
            sys.exit(1)

        print(f"Found {len(columns)} columns:")
        for i, col in enumerate(columns, 1):
            name = col.get("name", "Unknown")
            desc = col.get("description", "No description")
            data_type = col.get("data_type", "Unknown")
            print(f"  {i}: {name} ({data_type}) - {desc}")

        print(f"\nWriting CSV file: {output_path}")
        write_csv(data, columns, output_path)

        print("\nProcessing completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
