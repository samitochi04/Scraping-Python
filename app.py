import requests
import csv
import re
import time
from urllib.parse import urljoin

# Replace with your Google Places API key
API_KEY = "AIzaSyA3Qscf_M3HHSGykf3YRZbSeg7jXOfXXcs"

# Coordinates for Montpellier, France
LATITUDE = 43.610769
LONGITUDE = 3.876716

# Radius in meters (adjust as needed)
RADIUS = 45000

# Base URL for the Google Places API
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Parameters for the API request
params = {
    "location": f"{LATITUDE},{LONGITUDE}",
    "radius": RADIUS,
    "type": "shopping_mall",
    "key": API_KEY,
}

# Function to fetch restaurant data
def fetch_restaurants():
    restaurants = []
    next_page_token = None

    while True:
        if next_page_token:
            params["pagetoken"] = next_page_token

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data["status"] != "OK":
            print(f"Error: {data['status']}")
            break

        for place in data["results"]:
            place_id = place["place_id"]
            place_details = get_place_details(place_id)

            website = place_details.get("website", "")
            email = scrape_email_from_website(website) if website else "N/A"

            restaurant = {
                "name": place.get("name", "N/A"),
                "address": place_details.get("formatted_address", "N/A"),
                "phone": place_details.get("formatted_phone_number", "N/A"),
                "website": website,
                "email": email,
                "latitude": place.get("geometry", {}).get("location", {}).get("lat", "N/A"),
                "longitude": place.get("geometry", {}).get("location", {}).get("lng", "N/A"),
            }
            restaurants.append(restaurant)

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Wait to avoid token expiration
        time.sleep(2)

    return restaurants

# Function to get detailed information for a specific place
def get_place_details(place_id):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    details_params = {
        "place_id": place_id,
        "fields": "formatted_address,formatted_phone_number,website",
        "key": API_KEY,
    }
    response = requests.get(details_url, params=details_params)
    data = response.json()
    return data.get("result", {})

# Function to scrape email addresses from a website
def scrape_email_from_website(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Regex to find email addresses in the webpage content
            emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
            if emails:
                return emails[0]  # Return the first email found
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return "N/A"

# Function to save restaurant data to a CSV file
def save_to_csv(restaurants, filename="shopping_mall.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "address", "phone", "website", "email", "latitude", "longitude"])
        writer.writeheader()
        for restaurant in restaurants:
            writer.writerow(restaurant)
    print(f"Data saved to {filename}")

# Main function
def main():
    restaurants = fetch_restaurants()
    save_to_csv(restaurants)

if __name__ == "__main__":
    main()