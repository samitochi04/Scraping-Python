from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Set up Selenium WebDriver (make sure you have the correct driver for your browser)
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--headless')  # Run in headless mode if needed

# Initialize the driver
driver = webdriver.Chrome(options=options)

# Function to scrape restaurant data
def scrape_restaurants_in_montpellier():
    url = "https://www.google.com/maps"
    driver.get(url)

    # Wait for the search bar to load
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchboxinput"))
    )

    # Search for restaurants in Montpellier
    search_box.send_keys("restaurants in Montpellier")
    search_box.send_keys(Keys.RETURN)

    time.sleep(5)  # Allow time for results to load

    # Scroll through the list to load all restaurants
    for _ in range(10):  # Adjust range as needed
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    # Collect restaurant data
    restaurants = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Class name for each restaurant card

    restaurant_data = []

    for restaurant in restaurants:
        try:
            name = restaurant.find_element(By.CLASS_NAME, "qBF1Pd").text
        except:
            name = "N/A"
        try:
            location = restaurant.find_element(By.CLASS_NAME, "lI9IFe").text
        except:
            location = "N/A"
        try:
            phone = restaurant.find_element(By.CLASS_NAME, "Io6YTe").text
        except:
            phone = "N/A"
        try:
            website = restaurant.find_element(By.XPATH, "//a[contains(@href, 'http')]").get_attribute("href")
        except:
            website = "N/A"

        restaurant_data.append({
            "Name": name,
            "Location": location,
            "Phone": phone,
            "Website": website,
        })

    return restaurant_data

# Save data to a CSV file
def save_to_csv(data, filename="restaurants_in_montpellier.csv"):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Main execution
if __name__ == "__main__":
    try:
        restaurant_data = scrape_restaurants_in_montpellier()
        save_to_csv(restaurant_data)
        print(f"Scraped data saved to 'restaurants_in_montpellier.csv'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
