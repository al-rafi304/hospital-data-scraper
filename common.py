import csv
import os
import time
import random
import unicodedata
from undetected_playwright.sync_api import sync_playwright
import tqdm


import requests
import os

def download_file(url, output_directory, hospital_url):

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Scrape the hospital details to get the provider (hospital) name
    provider_name, _ = scrape_hospital_details(hospital_url)
    # sanitized_name = provider_name.replace(" ", "_").replace("/", "-")  # Sanitize for filenames
    
    # Generate filename
    filename = f"{provider_name}.csv"
    filepath = os.path.join(output_directory, filename)

    # Download the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=65536):
                file.write(chunk)
        print(f"File downloaded to: {filepath}")
    else:
        raise Exception(f"Failed to download file: {response.status_code} {response.reason}")

    return filepath

def download_csv(file_url, output_path):
    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    # Get the total file size from headers (if available)
    total_size = int(response.headers.get("content-length", 0))

    if total_size // (1024 ** 2) > 300:
        print(f"File size too big: {total_size // (1024 ** 2)}MB")
    # Use tqdm for the progress bar
    with open(output_path, mode="wb") as output_file, tqdm(
        desc=f"Downloading",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            output_file.write(chunk)
            bar.update(len(chunk))


def get_cpt_codes():
    cpt_codes = {
        "70450", "70486", "70491", "70551", "70553", "71045", "71046", "71047",
        "71048", "71101", "71250", "71260", "71275", "72040", "72050", "72070",
        "72072", "72100", "72110", "72131", "72141", "72146", "72148", "72156",
        "72157", "72158", "72170", "72192", "72193", "72195", "72197", "73000",
        "73030", "73070", "73080", "73090", "73100", "73110", "73120", "73130",
        "73140", "73221", "73560", "73562", "73564", "73565", "73590", "73600",
        "73610", "73620", "73630", "73650", "73660", "73700", "73718", "73721",
        "73722", "73723", "74022", "74150", "74160", "74170", "74176", "74177",
        "74178", "74181", "74183", "76000", "76512", "76514", "76536", "76642",
        "76700", "76705", "76770", "76775", "76801", "76805", "76811", "76813",
        "76815", "76817", "76818", "76819", "76830", "76831", "76856", "76857",
        "76870", "76872", "76882", "77047", "77065", "77066", "77067", "77080",
        "77385", "77386", "77387", "77412", "78014", "78306", "78452", "78815",
        "77063", "76641", "74018", "73502"
    }


    return cpt_codes

def scrape_hospital_details(hospital_url):
    """
    Scrapes hospital details (name, and address) from the given URL.
    
    Args:
        url (str): The URL of the hospital details page.
    
    Returns:
        dict: A dictionary containing hospital_name and hospital_address.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": random.randint(1024, 1920), "height": random.randint(768, 1080)},
            locale="en-US",
            timezone_id="America/New_York",
            # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.28 Safari/537.36"
        )
        page = context.new_page()

        # Go to the target website
        page.goto(hospital_url)
        time.sleep(random.uniform(1, 10))

        # Locate the element and extract text
        provider_name = page.locator('//*[@id="root"]/div/main/div/section[1]/div/div/div/div[1]').inner_text()
        street_address = page.locator('//*[@id="w-node-_4e8266c1-6898-cec1-579e-b783d40089d2-8d4be3ed"]').inner_text()
        city_address = page.locator('//*[@id="w-node-a3eac0d5-a762-3b16-4265-45a9441bbf19-8d4be3ed"]').inner_text()
        provider_address = f"{street_address}, {city_address}"

        provider_name = unicodedata.normalize('NFKC', provider_name)
        provider_address = unicodedata.normalize('NFKC', provider_address)
        
        browser.close()

        print(f"Provider name: {provider_name}, Provider address: {provider_address}")

        return provider_name, provider_address
