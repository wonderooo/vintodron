from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import time
import requests
import shutil
from pyvirtualdisplay import Display

display = Display(visible=0, size=(1920, 1080))  
display.start()


options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36')

load_dotenv()
PATH = os.getenv('CHROME_DRIVER')
MONGO_CLIENT = os.getenv('MONGO_CLIENT')
#driver = webdriver.Chrome(service=Service(PATH)) #options = Options
#driver = webdriver.Remote('http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME, options=options)
driver = webdriver.Chrome(options=options)

db_client = MongoClient(MONGO_CLIENT)
db = db_client['vinted']
collection_channels = db['channel_subs']
collection_offers = db['offers']

count = 0
first_life = True

def cookie_button():
    global first_life
    try:
        if first_life != False:
            elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))
                )
            driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    except Exception as e:
        print(e)
        print('cookie button has not been laoded!')

def clear_cache():
    global driver
    driver.delete_all_cookies()


def scrap():
    try:
        global count
        global first_life

        clear_cache()
        #time.sleep(10000)

        if len(list(collection_channels.find())) > 0:
            current_channel = collection_channels.find({'_id': count})
            for elements in current_channel:
                current_url = elements['url']
        
            #if len(list(collection_channels.find())) == 1 and first_life == False:
            #    driver.get(current_url)
            #    print('shit')
            #else:
            #    driver.get(current_url)
            #    cookie_button()
            #    first_life = False
            clear_cache()
            driver.get(current_url)
            cookie_button()

            first_24_offers = driver.find_elements(By.CLASS_NAME, 'feed-grid__item')[0:8] + driver.find_elements(By.CLASS_NAME, 'feed-grid__item')[9:25] 
            for offer in first_24_offers:
                reference = offer.find_elements(By.TAG_NAME, 'a')
                reference = reference[1].get_attribute('href')

                occupied_references = list(collection_offers.find({}, {'reference': 1, '_id': 0}))
                occupied = False
                for occupancy in occupied_references:
                    if str(reference) in str(occupancy['reference']):
                        occupied = True
            
                if occupied == False:
                    price = offer.find_element(By.TAG_NAME, 'h3')
                    price = price.text
            
                    h4s = offer.find_elements(By.TAG_NAME, 'h4')
                    description = h4s[2].text
                    make = h4s[3].text
            
                    image = offer.find_elements(By.TAG_NAME, 'img')
                    image = image[1].get_attribute('src')
                    response = requests.get(image, stream = True)
                    save_code = reference.split('/')  
                    save_code = save_code[len(save_code) - 1]
                    image_path = '/data/common/{url}.png'.format(url=save_code)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            response.raw.decode_content = True
                            shutil.copyfileobj(response.raw, f)
                            f.close()

                    pointer = len(list(collection_offers.find()))
                    channel_name = collection_channels.find({'_id': count})
                    for n in channel_name:
                        channel_name = n['channel_name']
            
                    post = {
                        '_id': pointer,
                        'channel_name': channel_name,
                        'price': price,
                        'make': make,
                        'reference': reference,
                        'description': description,
                        'image_path': save_code,
                        'posted': 'False'
                    }
                    collection_offers.insert_one(post)
                    print('props: {price}, {description}, {make}, {reference}'.format(price=price, description=description, make=make, reference=reference))
            if count == len(list(collection_channels.find())) - 1:
                count = 0
            else:
                count += 1
        print(count)
    except Exception as e:
        print('global error: {0}'.format(e))
        #scrap()

#def on_press(key):
#    if key == Key.right:
#        scrap()

#with Listener(on_press = on_press) as listener:
#    listener.join()

while True:
    time.sleep(1)
    scrap()

driver.quit()
display.stop()