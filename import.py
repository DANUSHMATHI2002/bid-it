import requests
import json
from bs4 import BeautifulSoup
import schedule
import time
import subprocess

def scrape_and_save_data(url, output_file):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table containing the data
        table = soup.find("div", class_="Table")

        # Initialize an empty list to store the scraped data
        data = []

        # Find all rows in the table
        rows = table.find_all("div", class_="Row")

        for row in rows:
            cells = row.find_all("div", class_="Cell")

            # Extract data from each cell
            name = cells[0].text.strip()
            unit = cells[1].text.strip()
            market_price = cells[2].text.strip()
            retail_price = cells[3].text.strip()
            shopping_mall = cells[4].text.strip()

            # Create a dictionary for the current row
            item_info = {
                "Name": name,
                "Unit": unit,
                "Market Price": market_price,
                "Retail Price": retail_price,
                "Shopping Mall": shopping_mall,
            }

            # Append the dictionary to the list
            data.append(item_info)

        # Check if the data has changed compared to the existing JSON file
        update_needed = False
        try:
            with open(output_file, "r", encoding="utf-8") as json_file:
                existing_data = json.load(json_file)

            for item_info in data:
                existing_item = next(
                    (item for item in existing_data if item["Name"] == item_info["Name"]),
                    None,
                )
                if existing_item:
                    if existing_item["Market Price"] != item_info["Market Price"]:
                        update_needed = True
                        existing_item["Market Price"] = item_info["Market Price"]

        except FileNotFoundError:
            update_needed = True

        if update_needed:
            # Save the updated data to the JSON file
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

            print(f"Data updated and saved to {output_file}")

            # Commit and push changes to Git
            commit_message = f"Update made in {output_file}"
            subprocess.run(["git", "commit", output_file, "-m", commit_message])
            subprocess.run(["git", "push"])

            # Print the updates made
            for item_info in data:
                existing_item = next(
                    (item for item in existing_data if item["Name"] == item_info["Name"]),
                    None,
                )
                if existing_item:
                    if existing_item["Market Price"] != item_info["Market Price"]:
                        print(
                            f"Updation done in {output_file} in {item_info['Name']} in Market Price"
                        )

        else:
            print("No changes had been made")

    else:
        print(f"Failed to retrieve the webpage for {url}")

# Define URLs and output file names as strings
vegetables_url = "https://market.todaypricerates.com/Tamil-Nadu-vegetables-price"
fruits_url = "https://market.todaypricerates.com/Tamil-Nadu-fruits-price"
vegetables_output_file = "vegetable_data.json"
fruits_output_file = "fruits_data.json"

# Schedule the scraping functions to run every minute
schedule.every(1).minutes.do(scrape_and_save_data, vegetables_url, vegetables_output_file)
schedule.every(1).minutes.do(scrape_and_save_data, fruits_url, fruits_output_file)

# Run the scheduling loop
while True:
    schedule.run_pending()
    time.sleep(1)
