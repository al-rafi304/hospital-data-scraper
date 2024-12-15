import csv
import pandas as pd
import os
import sys

csv.field_size_limit(sys.maxsize)

def scrape_hospital_data(raw_data_file, output_directory, cpt_codes, hospital_name, hospital_addr):
    
    all_columns = set()
    filepath = raw_data_file
    
    with open(filepath, newline='', encoding='utf-8', errors='ignore') as csvfile:
        
        lines = csvfile.readlines()[2:]
        reader = csv.DictReader(lines)
        header = reader.fieldnames
        header = [h.lower() for h in header]
        
        all_columns.update(header)
        # print("=== all columns > ", all_columns)
        # print("=== final  header = ", header)
        code_name = "code|1"
        charge_name = "standard_charge|gross"

        if (code_name in header or "code|1|type" in header) and (charge_name in header or "cpt" in header):
            output_rows = []
            price_column = charge_name if charge_name in header else "Discounted cash price"
            code_column = code_name if code_name in header else "code|1|type"

            print("== code column ==> ", code_column)
            print("price column --> ", price_column)

            # provider_name, provider_address = common.scrape_hospital_details(hospital_url)
            provider_name, provider_address = hospital_name, hospital_addr
            
            # Filter rows based on CPT codes
            for row in reader:
                if row[code_column] in cpt_codes:
                    # print("== code ", row[code_column])
                    # print("== price >> ", type(row[price_column]))
                    if row[price_column] is None or row[price_column] == "":
                        continue

                    output_rows.append({
                        "CPT": row[code_column],
                        "Price": row[price_column],
                        'Provider Name': provider_name,
                        "Provider Address": provider_address,
                    })
            # print("=== output rows: ", output_rows)
            # If we have matching rows, write them to a new CSV file in the "cash" directory
            if output_rows:
                script_name = os.path.basename(__file__).rsplit(".", 1)[0]

                output_filepath = os.path.join(output_directory, f"{hospital_name}.csv")

                with open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=["CPT", "Price", "Provider Name", "Provider Address"])
                    writer.writeheader()
                    writer.writerows(output_rows)
                
                print(f"Filtered data saved to {output_filepath}")
                return 'Success', ''
            else:
                return 'Failed', 'No output rows found'
        else:
            return 'Failed', 'No matching header found'