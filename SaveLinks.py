import requests
import csv

STATE_CODE = 'NY'
URL = f"https://pts.patientrightsadvocatefiles.org/facility/search?search=&searchstate={STATE_CODE}"
STORAGE = "https://storage.patientrightsadvocatefiles.org"
HEADERS = {'sessionid': '5087494111016062868872034'}
CSV_HEADERS = {'name':"", 'csv':"", 'hospital_link':"", 'hospital_address': ""}

def fetchData():
    res = requests.get(URL, headers=HEADERS)
    if not res.ok:
        print("Error fetching data")
        return

    return res.json()

def extractLinks(data):
    links = []
    for item in data:
        info = CSV_HEADERS.copy()
        info['name'] = item['name']
        info['hospital_link'] = f"https://hospitalpricingfiles.org/details/{item['id']}"
        info['hospital_address'] = f"{item['address']} {item['city']} {item['state']} {item['zip']}"

        for file in item['files']:
            if file['filesuffix'].lower() == 'csv':
                info['csv'] = f"{STORAGE}/{file['project']}/{file['storage']}"

        links.append(info)
    return links

# Returns all downloadable file types
def getFileTypes(data):
    unique_types = {file["filesuffix"] for item in data for file in item["files"]}
    return sorted(list(unique_types))

def exportCSV(links:list):
    filename = f"{STATE_CODE}_links.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(CSV_HEADERS.keys()))
        writer.writeheader()
        writer.writerows(links)

if __name__ == '__main__':
    print(f"Fetching data for {STATE_CODE}...")
    data = fetchData()
    links = extractLinks(data)
    # fileTypes = getFileTypes(data)
    # print(f"Found file types: {fileTypes}")
    exportCSV(links)
    print("Exported to CSV!")
