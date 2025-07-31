#!/usr/bin/env python3
"""
Galileo Probe Data Parser

This script parses Galileo Probe data files (.tab and .lbl) and converts
them to CSV format. The .lbl file contains metadata and column definitions,
while the .tab file contains the actual data.

Usage:
    python parse_wind_data.py <tab_file_path> <lbl_file_path> [output_csv_path]
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

        # Check if the original string contains scientific notation
        if "e" in value_str.lower() or "E" in value_str:
            # Convert scientific notation to decimal format
            # Use formatting to avoid scientific notation in output
            if abs(float_value) < 1e-4 or abs(float_value) >= 1e6:
                # For very small or very large numbers, use appropriate precision
                return float_value
            else:
                # For normal range numbers, format without scientific notation
                return float_value
        else:
            # Not scientific notation, return as float
            return float_value

    except ValueError:
        # Not a number, return as string
        return value_str


def parse_label_file(lbl_path):
    """
    Parse the PDS label file to extract table and column information.

    Args:
        lbl_path (str): Path to the .lbl file

    Returns:
        list: List of dictionaries containing table information, each with columns
    """
    tables = []

    with open(lbl_path, "r") as f:
        content = f.read()

    # First, extract table references to get starting positions
    table_refs = {}
    ref_pattern = r'\^([A-Z_]+)\s*=\s*\(\s*"[^"]+"\s*,\s*(\d+)\s*\)'
    ref_matches = re.findall(ref_pattern, content)
    for table_name, start_line in ref_matches:
        table_refs[table_name] = int(start_line)

    # Get full table sections with content
    full_table_pattern = r"OBJECT\s*=\s*([A-Z_]+)(.*?)END_OBJECT\s*=\s*\1"
    full_table_matches = re.findall(full_table_pattern, content, re.DOTALL)

    for table_name, table_content in full_table_matches:
        if table_name == "COLUMN":  # Skip individual column objects
            continue

        table_info = {"name": table_name, "start_line": table_refs.get(table_name, 1), "columns": []}

        # Extract table metadata
        rows_match = re.search(r"ROWS\s*=\s*(\d+)", table_content)
        if rows_match:
            table_info["rows"] = int(rows_match.group(1))

        columns_count_match = re.search(r"COLUMNS\s*=\s*(\d+)", table_content)
        if columns_count_match:
            table_info["columns_count"] = int(columns_count_match.group(1))

        # Extract description
        desc_match = re.search(r'DESCRIPTION\s*=\s*"([^"]+)"', table_content)
        if desc_match:
            table_info["description"] = desc_match.group(1)

        # Extract columns for this table
        column_pattern = r"OBJECT\s*=\s*COLUMN.*?END_OBJECT\s*=\s*COLUMN"
        column_sections = re.findall(column_pattern, table_content, re.DOTALL)

        for section in column_sections:
            column_info = {}

            # Extract column name
            name_match = re.search(r'NAME\s*=\s*"([^"]+)"', section)
            if name_match:
                column_info["name"] = name_match.group(1)

            # Extract column number
            number_match = re.search(r"COLUMN_NUMBER\s*=\s*(\d+)", section)
            if number_match:
                column_info["number"] = int(number_match.group(1))

            # Extract unit
            unit_match = re.search(r'UNIT\s*=\s*"([^"]+)"', section)
            if unit_match:
                column_info["unit"] = unit_match.group(1)

            # Extract description
            desc_match = re.search(r'DESCRIPTION\s*=\s*"([^"]+)"', section)
            if desc_match:
                column_info["description"] = desc_match.group(1)

            # Extract byte information for parsing
            start_byte_match = re.search(r"START_BYTE\s*=\s*(\d+)", section)
            bytes_match = re.search(r"BYTES\s*=\s*(\d+)", section)
            if start_byte_match and bytes_match:
                column_info["start_byte"] = int(start_byte_match.group(1))
                column_info["bytes"] = int(bytes_match.group(1))

            if column_info:
                table_info["columns"].append(column_info)

        # Sort columns by column number
        table_info["columns"].sort(key=lambda x: x.get("number", 0))

        if table_info["columns"]:  # Only add tables that have columns
            tables.append(table_info)

    # If no tables found, try to parse as single table (backward compatibility)
    if not tables:
        # Extract all columns without table structure
        columns = []
        column_pattern = r"OBJECT\s*=\s*COLUMN.*?END_OBJECT\s*=\s*COLUMN"
        column_sections = re.findall(column_pattern, content, re.DOTALL)

        for section in column_sections:
            column_info = {}

            # Extract column name
            name_match = re.search(r'NAME\s*=\s*"([^"]+)"', section)
            if name_match:
                column_info["name"] = name_match.group(1)

            # Extract column number
            number_match = re.search(r"COLUMN_NUMBER\s*=\s*(\d+)", section)
            if number_match:
                column_info["number"] = int(number_match.group(1))

            # Extract unit
            unit_match = re.search(r'UNIT\s*=\s*"([^"]+)"', section)
            if unit_match:
                column_info["unit"] = unit_match.group(1)

            # Extract description
            desc_match = re.search(r'DESCRIPTION\s*=\s*"([^"]+)"', section)
            if desc_match:
                column_info["description"] = desc_match.group(1)

            # Extract byte information for parsing
            start_byte_match = re.search(r"START_BYTE\s*=\s*(\d+)", section)
            bytes_match = re.search(r"BYTES\s*=\s*(\d+)", section)
            if start_byte_match and bytes_match:
                column_info["start_byte"] = int(start_byte_match.group(1))
                column_info["bytes"] = int(bytes_match.group(1))

            if column_info:
                columns.append(column_info)

        # Sort columns by column number
        columns.sort(key=lambda x: x.get("number", 0))

        # Return as single table for backward compatibility
        if columns:
            tables.append({"name": "TABLE", "start_line": 1, "columns": columns})

    return tables


def parse_tab_file(tab_path, table_info):
    """
    Parse the tab file containing the actual data for a specific table.

    Args:
        tab_path (str): Path to the .tab file
        table_info (dict): Table information including columns, start_line, and rows

    Returns:
        list: List of dictionaries containing the parsed data
    """
    data = []
    columns = table_info["columns"]
    start_line = table_info.get("start_line", 1)
    max_rows = table_info.get("rows", None)

    with open(tab_path, "r") as f:
        lines = f.readlines()

    # Convert to 0-based indexing for array access
    start_index = start_line - 1
    rows_processed = 0

    for i in range(start_index, len(lines)):
        line = lines[i].rstrip("\n\r")

        # Skip empty lines
        if not line.strip():
            continue

        # Stop if we've processed the expected number of rows
        if max_rows is not None and rows_processed >= max_rows:
            break

        row = {}

        # Parse each column based on byte positions
        for col in columns:
            if "start_byte" in col and "bytes" in col:
                # Convert to 0-based indexing
                start = col["start_byte"] - 1
                end = start + col["bytes"]

                if end <= len(line):
                    value_str = line[start:end].strip()
                    # Convert scientific notation to standard decimal notation
                    value = convert_scientific_to_decimal(value_str)
                    row[col["name"]] = value
                else:
                    row[col["name"]] = None

        if row:
            data.append(row)
            rows_processed += 1

    return data


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
        name = col.get("name", "Column_{}".format(col.get("number", "?")))
        unit = col.get("unit", "")

        if unit and unit != "N/A":
            # Clean up unit formatting
            unit = unit.replace("**", "^").replace("(", "").replace(")", "")
            header = "{} ({})".format(name, unit)
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

    print("CSV file created: {}".format(output_path))
    print("Records written: {}".format(len(data)))


def main():
    parser = argparse.ArgumentParser(
        description="Parse Galileo Probe data files and convert to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python %(prog)s data/dwe/wind.tab data/dwe/wind.lbl
    python %(prog)s data/dwe/wind.tab data/dwe/wind.lbl \\
        output/wind_data.csv
    python %(prog)s data/nep/ptz.tab data/nep/ptz.lbl \\
        output/ptz_data.csv
        """,
    )

    parser.add_argument("tab_file", help="Path to the .tab data file")
    parser.add_argument("lbl_file", help="Path to the .lbl label file")
    parser.add_argument("output_csv", nargs="?", help="Output CSV file path (default: parsed_data.csv)")

    args = parser.parse_args()

    # Validate input files
    tab_path = Path(args.tab_file)
    lbl_path = Path(args.lbl_file)

    if not tab_path.exists():
        print("Error: Tab file not found: {}".format(tab_path))
        sys.exit(1)

    if not lbl_path.exists():
        print("Error: Label file not found: {}".format(lbl_path))
        sys.exit(1)

    # Set output path
    if args.output_csv:
        output_path = Path(args.output_csv)
    else:
        # Generate default filename based on input file
        base_name = tab_path.stem + "_parsed.csv"
        output_path = Path(base_name)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print("Parsing label file: {}".format(lbl_path))
        tables = parse_label_file(lbl_path)

        if not tables:
            print("Error: No table information found in label file")
            sys.exit(1)

        print("Found {} table(s):".format(len(tables)))
        for table in tables:
            print(
                "  Table: {} ({} columns, {} rows)".format(
                    table["name"], len(table["columns"]), table.get("rows", "unknown")
                )
            )
            if table.get("description"):
                desc = table["description"]
                desc_text = desc[:100] + "..." if len(desc) > 100 else desc
                print("    Description: {}".format(desc_text))

        # Process each table
        for table in tables:
            print("\nProcessing table: {}".format(table["name"]))

            # Generate output filename with table suffix
            if len(tables) > 1:
                # Multiple tables - add suffix based on table name
                table_suffix = table["name"].replace("_TABLE", "").replace("TABLE", "")
                if table_suffix and table_suffix != table["name"]:
                    if args.output_csv:
                        # If user specified output file, modify it with suffix
                        output_stem = Path(args.output_csv).stem
                        output_dir = Path(args.output_csv).parent
                        table_output_path = output_dir / "{}_{}.csv".format(output_stem, table_suffix)
                    else:
                        # Generate default filename with table suffix
                        table_output_path = Path("{}_{}_{}.csv".format(tab_path.stem, "parsed", table_suffix))
                else:
                    # Use table name as suffix
                    if args.output_csv:
                        output_stem = Path(args.output_csv).stem
                        output_dir = Path(args.output_csv).parent
                        table_output_path = output_dir / "{}_{}.csv".format(output_stem, table["name"])
                    else:
                        table_output_path = Path("{}_{}_{}.csv".format(tab_path.stem, "parsed", table["name"]))
            else:
                # Single table - use original output path
                table_output_path = output_path

            # Create output directory if it doesn't exist
            table_output_path.parent.mkdir(parents=True, exist_ok=True)

            print("  Columns:")
            for col in table["columns"]:
                name = col.get("name", "Unknown")
                unit = col.get("unit", "N/A")
                desc = col.get("description", "No description")
                print("    {}: {} ({}) - {}".format(col.get("number", "?"), name, unit, desc))

            print(
                "  Parsing data from line {} ({} rows expected)".format(
                    table.get("start_line", 1), table.get("rows", "unknown")
                )
            )
            data = parse_tab_file(tab_path, table)

            print("  Writing CSV file: {}".format(table_output_path))
            write_csv(data, table["columns"], table_output_path)

        print("\nProcessing completed successfully!")

    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
