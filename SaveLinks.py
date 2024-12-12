import requests
import csv

STATE_CODE = 'TX'
URL = f"https://pts.patientrightsadvocatefiles.org/facility/search?search=&searchstate={STATE_CODE}"
STORAGE = "https://storage.patientrightsadvocatefiles.org"
HEADERS = {'sessionid': '5087494111016062868872034'}

def fetchData():
    res = requests.get(URL, headers=HEADERS)
    if not res.ok:
        print("Error fetching data")
        return

    return res.json()

def extractLinks(data):
    links = []
    for item in data:
        info = { 'name': item['name'] }
        for file in item['files']:
            info[file['filesuffix']] = f"{STORAGE}/{file['project']}/{file['storage']}"
        
        links.append(info)
    return links

def getFileTypes(data):
    unique_types = {file["filesuffix"] for item in data for file in item["files"]}
    return sorted(list(unique_types))

def exportCSV(links:list, fields):
    filename = f"{STATE_CODE}_links.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=['name', *fields])
        writer.writeheader()
        writer.writerows(links)

if __name__ == '__main__':
    print(f"Fetching data for {STATE_CODE}...")
    data = fetchData()
    links = extractLinks(data)
    fileTypes = getFileTypes(data)
    print(f"Found file types: {fileTypes}")
    exportCSV(links, fields=fileTypes)
    print("Exported to CSV!")
