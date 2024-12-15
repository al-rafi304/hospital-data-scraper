import csv
import os
import requests
from tqdm import tqdm

input_csv = "NY_links.csv"
output_directory = "raw_files"
report_csv = "download_report.csv"

os.makedirs(output_directory, exist_ok=True)

report_data = []
with open(input_csv, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        file_name = row["name"]
        file_url = row.get("csv", "")

        if not file_url:
            report_data.append({"name": file_name, "status": "Failed (Missing URL)"})
            continue

        output_path = os.path.join(output_directory, f"{file_name}.csv")
        if os.path.exists(output_path):
            print(f"Already Downloaded {file_name}")
            continue

        try:
            # Start downloading the file
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            # Get the total file size from headers (if available)
            total_size = int(response.headers.get("content-length", 0))

            if total_size // (1024 ** 2) > 300:
                print(f"File size too big: {total_size // (1024 ** 2)}MB: {file_name}")
                continue
            # Use tqdm for the progress bar
            with open(output_path, mode="wb") as output_file, tqdm(
                desc=f"Downloading {file_name}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    output_file.write(chunk)
                    bar.update(len(chunk))

            report_data.append({"name": file_name, "status": "Success"})

        except requests.RequestException as e:
            report_data.append({"name": file_name, "status": f"Failed ({str(e)})"})

# Write the report CSV
with open(report_csv, mode="w", newline="", encoding="utf-8") as report_file:
    fieldnames = ["name", "status"]
    writer = csv.DictWriter(report_file, fieldnames=fieldnames)

    # Write headers and rows
    writer.writeheader()
    writer.writerows(report_data)

print(f"\nDownload completed! Report saved to {report_csv}")
