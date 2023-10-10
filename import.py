import requests
import json
from bs4 import BeautifulSoup
import schedule
import time
import subprocess

# Define a function to check and update data
def check_and_update_data(url, output_file):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table containing the data
        table = soup.find("div", class_="Table")

        # Initialize an empty dictionary to store the scraped data
        data_dict = {}

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

            # Create a dictionary for the current item
            item_info = {
                "Name": name,
                "Unit": unit,
                "Market Price": market_price,
                "Retail Price": retail_price,
                "Shopping Mall": shopping_mall,
            }

            # Add the item info to the data_dict
            data_dict[name] = item_info

        # Check if the data has changed compared to the existing data
        update_needed = False
        try:
            with open(output_file, "r", encoding="utf-8") as json_file:
                existing_data_dict = json.load(json_file)

            for name, item_info in data_dict.items():
                if name in existing_data_dict:
                    if item_info != existing_data_dict[name]:
                        update_needed = True
                        print(f"Updating {name} in {output_file}")
                        existing_data_dict[name] = item_info

            if update_needed:
                # Save the updated data to the JSON file
                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(existing_data_dict, json_file, ensure_ascii=False, indent=4)

                # Commit and push changes to Git
                commit_message = f"Update made in {name} in {output_file}"
                subprocess.run(["git", "add", output_file])
                subprocess.run(["git", "commit", output_file, "-m", commit_message])
                subprocess.run(["git", "push"])
            else:
                print(f"No changes had been made in {output_file}")

        except FileNotFoundError:
            # If the JSON file does not exist, create it with the scraped data
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

            print(f"Data scraped and saved to {output_file}")

    else:
        print(f"Failed to retrieve the webpage for {url}")

# Define URLs and output file names as strings
vegetables_url = "https://market.todaypricerates.com/Tamil-Nadu-vegetables-price"
fruits_url = "https://market.todaypricerates.com/Tamil-Nadu-fruits-price"
vegetables_output_file = "vegetable_data.json"
fruits_output_file = "fruits_data.json"

# Schedule the check_and_update_data function to run every minute
schedule.every(1).minutes.do(check_and_update_data, vegetables_url, vegetables_output_file)
schedule.every(1).minutes.do(check_and_update_data, fruits_url, fruits_output_file)

# Run the scheduling loop
while True:
    schedule.run_pending()
    time.sleep(1)
