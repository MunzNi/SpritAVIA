import random
import time
import re
import os
import json

from bs4 import BeautifulSoup
from selenium import webdriver
import paho.mqtt.client as mqtt

mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = os.getenv("MQTT_PORT")
mqtt_topic = os.getenv("MQTT_TOPIC")
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
website_url = os.getenv("AVIA_URL")

#Chromedriver aufsetzen
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]
user_agent = random.choice(user_agents)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(f"--user-agent={user_agent}")
driver = webdriver.Chrome(options=chrome_options)


def scrape_website() -> dict:
    driver.get(website_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source)
    data = json.loads(soup.find("body").text)

    gas_prices_dict = {}

    # Iteriere durch die Liste der Gaspreise und extrahiere gasType und gasPrice
    for gas in data["gasPrices"]["gasPrices"]:
        gas_type = gas["gasType"]
        gas_price = gas["gasPrice"]
        gas_prices_dict[gas_type] = gas_price

    print(gas_prices_dict)
    
    return gas_prices_dict


def send_to_mqtt(gas_prices_dict: dict):

    # MQTT-Client initialisieren
    client = mqtt.Client()

    # Authentifizierung mit Benutzername und Passwort
    if mqtt_username and mqtt_password:
        client.username_pw_set(mqtt_username, mqtt_password)
    
    port = int(mqtt_port)
    client.connect(mqtt_broker, port)

    for gastype, price in gas_prices_dict.items():
        topic = f"{mqtt_topic}/{gastype}"
        client.publish(topic, price)

    # Verbindung trennen
    client.disconnect()


if __name__ == "__main__":
    gas_prices_dict = scrape_website()
    send_to_mqtt(gas_prices_dict)
