import csv
import os

# Path to BigVul Dataset (assuming it's in the same directory as this script)
file_path = "Dataset/MSR_data_cleaned.csv"

# Create the "Dataset" folder if it doesn't exist
output_folder = "Dataset"
os.makedirs(output_folder, exist_ok=True)

# Output CSV file path within the "Dataset" folder
output_file = os.path.join(output_folder, "vulnerable_functions.csv")

# Increasing CSV field limit
csv.field_size_limit(100000000)

# Reading the file and writing to the new CSV
with open(file_path, "r", encoding="utf8", errors="ignore") as input_file, open(output_file, "w", newline="",
                                                                                encoding="utf8") as output_csv:
    # Reader for the input file
    reader = csv.DictReader(input_file)

    # Get all field names and add 'row_number'
    fieldnames = reader.fieldnames + ["row_number"]

    # Writer for the output CSV with all fields and row number
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row

    row_number = 1
    for row in reader:
        # Check conditions
        if row.get('vul') == '1' and row.get('lines_before') != row.get('lines_after'):
            # Add the row number to the row dictionary
            row["row_number"] = row_number

            # Write the entire row including the row number
            writer.writerow(row)

        row_number += 1

print("New CSV file created:", output_file)