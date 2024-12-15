import csv
import pandas as pd
import common
import os
import traceback
from process_csv import scrape_hospital_data

input_csv = "NY_links.csv"
report_csv = "process_report.csv"
output_directory = "Processed CSV"
raw_directory = "raw_files"

os.makedirs(output_directory, exist_ok=True)

# Initialize the report file with headers
with open(report_csv, mode="w", newline="", encoding="utf-8") as report_file:
    fieldnames = ["name", "status", "comments"]
    writer = csv.DictWriter(report_file, fieldnames=fieldnames)
    writer.writeheader()

with open(input_csv, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        
        hospital_name = row["name"]
        csv_link = row.get("csv", "")
        hospital_link = row.get("hospital_link", "")
        hospital_address = row.get("hospital_address", "")

        csv_file = os.path.join(raw_directory, f"{hospital_name}.csv")
        output_file = os.path.join(output_directory, f"{hospital_name}.csv")
        print(f"Processing: {hospital_name}")
        
        status = ''
        comment = ""

        if not csv_link:
            status = 'Failed'
            comment = "Missing CSV Link"
        else:
            if not os.path.exists(csv_file):
                print(f"File not found: {csv_file}")
                continue
                # common.download_csv(csv_link, csv_file)

            try:
                status, comment = scrape_hospital_data(csv_file, output_directory, common.get_cpt_codes(), hospital_name, hospital_address)
            except Exception as e:
                status = 'Failed'
                comment = traceback.format_exc()

        # Updating Report
        with open(report_csv, mode="a", newline="", encoding="utf-8") as report_file:
            writer = csv.DictWriter(report_file, fieldnames=["name", "status", "comments"])
            writer.writerow({"name": hospital_name, "status": status, "comments": comment})


print(f"Report generated at {report_csv}")