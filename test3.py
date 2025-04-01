from time import sleep
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os

options = webdriver.ChromeOptions()
ua = UserAgent()
user_agent = ua.random
print(user_agent)
#options.add_argument(f'--user-agent={user_agent}')
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)



origins = ['MAN', 'CDG', 'ZRH', 'JFK', 'LHR', 'BCN', 'BER', 'HKG', 'FCO']
mapped_list = []
for i in range(len(origins)):
    for j in range(len(origins)):
        if i != j:
            mapped_list.append((origins[i], origins[j]))

# destinations = ['YYZ', 'MAN', 'CDG', 'ZRH', 'JFK', 'LHR', 'BCN', 'BER', 'HKG', 'FCO']
        

start_date = np.datetime64('2025-04-01')
end_date = np.datetime64('2025-04-03')
days = end_date - start_date
num_days = days.item().days

# closing the popup window
#popup_window = '//div[@class = "dDyu-CLOSE dDYU-mod-variant-default dDYU-mod-size-default"]'
#driver.find_element("xpath", popup_window).click()

#flight_rows = driver.find_elements("xpath", '//div[@class="Fxw9-result-item-container"]')
# print(flight_rows)

today = datetime.today().strftime('%Y-%m-%d')

def get_airlines(soup):
    airline = []
    airlines = soup.find_all('span',class_='codeshares-airline-names',text=True)
    for i in airlines:
        airline.append(i.text)
    return airline

# retrieving     
def get_prices(soup):
    prices = []
    temp_price = soup.find("div", {"class": "nrc6-price-section"})
    if temp_price is not None:
        price = temp_price.find("div", {"class": "f8F1-price-text"})
        prices.append(price.text)
    return prices

column_names = ["Airline", "Origin", "Destination","Duration","Total stops", "Price","Flight date","Days left until flight"]
df = pd.DataFrame(columns = column_names)

# counter to store number of times we switched pages
counter = 0

prices = []
airlines = []
origins = []
destinations = []
flight_dates = []
stops = []
durations = []
days_left = []

# iterating through all flight paths
for journey in mapped_list:
    origin = journey[0]
    destination = journey[1]
    # initializing and resetting the list of important characteristics
    df = pd.DataFrame(columns = column_names)
    prices = []
    airlines = []
    origins = []
    destinations = []
    flight_dates = []
    stops = []
    durations = []
    days_left = []
# retrieving flight info for the given time range
    for i in range(num_days+1):
        counter += 1
        
        # close and open driver every 10 searches to avoid captcha
        if counter % 10 == 0:
            driver.quit()
            driver = webdriver.Chrome(options=options)#, chrome_options=chromeOptions)
        
        url = f'https://www.ca.kayak.com/flights/{origin}-{destination}/{start_date+i}?ucs=j3cp93&sort=bestflight_a'
        driver.get(url)
        sleep(10)
        flight_rows = driver.find_elements("xpath", '//div[@class="Fxw9-result-item-container"]')

        for WebElement in flight_rows:
            elementHTML = WebElement.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML, 'html.parser')
            
            # retrieving prices
            temp_price = elementSoup.find("div", {"class": "nrc6-price-section"})
            if temp_price is not None:
                price = temp_price.find("div", {"class": "f8F1-price-text"})
                prices.append(price.text)
                flight_dates.append(datetime.strftime(start_date + timedelta(days=i), "%Y-%m-%d"))
            
            # retrieving airlines
            temp_airline = elementSoup.find("div", {"class": "nrc6-content-section"})
            if temp_airline is not None:
                airline = temp_airline.find("div", {"class": "J0g6-operator-text"})
                airlines.append(airline.text)
                
            # retrieving stops
            temp_stop = elementSoup.find("div", {"class": "nrc6-content-section"})
            if temp_stop is not None:
                stop = temp_stop.find("span", {"class": "JWEO-stops-text"})
                stops.append(stop.text)
            
            # retrieving duration
            temp_duration = elementSoup.find("div", {"class": "nrc6-content-section"})
            if temp_duration is not None:
                duration = temp_duration.find("div", {"class": "xdW8 xdW8-mod-full-airport"})
                durations.append(duration.text)

            #flight_dates.append(datetime.strftime(start_date + timedelta(days=i), "%Y-%m-%d"))
            #print("In Webelement loop: \n", prices)
    
    #print("In num days loop \n:", prices)
    for j in range(len(prices)):
        df = pd.concat([df, pd.DataFrame([{
            'Airline': airlines[j],
            'Duration': durations[j],
            'Total stops': stops[j],
            'Price': prices[j],
            'Flight date': flight_dates[j],
            'Days left until flight': abs((datetime.strptime(flight_dates[j], "%Y-%m-%d")-
                                        (datetime.strptime(today, "%Y-%m-%d"))).days)
        }])], ignore_index=True)
    
    df['Origin'] = origin
    df['Destination'] = destination
    df['Booking date'] = today

    # save data as csv file for each route
    df.to_csv(f'{origin}_{destination}_{today}.csv',index=False)
    print(f"Succesfully saved {origin} => {destination} route as {origin}_{destination}{today}.csv")

# close the browser
driver.quit()

