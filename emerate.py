import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from twilio.rest import Client
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service

import time
import random
import os

#initialize the webdriver
user_agent_list = \
    ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
     'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.6367.111 Mobile/15E148 Safari/604.1',
    ]

proxy_list = [
    '35.185.196.38:3128', # TODO add more proxies
]

chosen_proxy = random.choice(proxy_list)
print("chosen proxy: ", chosen_proxy)

chosen_agent = random.choice(user_agent_list)
print("chosen agent: ", chosen_agent)

options = webdriver.ChromeOptions()
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-javascript")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--blink-settings=imagesEnabled=false")
options.add_argument("--window-size=1920,1080")
options.add_argument(f'user-agent={chosen_agent}')
options.add_argument("--disable-webgl")
options.add_argument("--user-data-dir=/Users/sreyleak/Library/Application Support/Google/Chrome/Default")
options.add_argument(f"--proxy-server={chosen_proxy}")
options.add_argument("--disable-gpu")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-dev-shm-usage')

options.add_argument("--enable-javascript")
options.add_argument("--enable-cookies")
options.add_argument('--disable-web-security')

# options.add_experimental_option("useAutomationExtension", False)
# options.add_argument("headless")
# options.add_argument("--no-sandbox")
# options.add_argument("--incognito")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# driver.maximize_window()

driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

# TODO make cookies a custom option (if needed)
# driver.get('http://httpbin.org/ip')
#
# cookie1 = {'name': 'cookie_name1', 'value': 'cookie_value1'}
# cookie2 = {'name': 'cookie_name2', 'value': 'cookie_value2'}
# driver.add_cookie(cookie1)
# driver.add_cookie(cookie2)

driver.get("https://accounts.emirates.com/us/english/sso/login?clientId=5kZbI1Xknmwp569KaEpn7urgUh5dJMsu&state=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjYWxsYmFja1VybCI6Ii91cy9lbmdsaXNoLz9sb2dvdXQ9dHJ1ZSIsInB1YiI6InVzL2VuZ2xpc2giLCJ1bmlxSWQiOiJlZjQ5MDkxMiIsIm5vUHJvZmlsZSI6MX0.A6-zEV8VV2Px1WgVDUOH77WhnBkd2k-7-GMra6ru3TA")

em_username = os.environ.get('emerate_username')
em_password = os.environ.get('emerate_password')

# Function to simulate typing with a delay between each character
def type_with_delay(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.1))  # Random delay between typing each character
    return None


#function to check if the webpage is already logged in
def alreadyLoggedIn():
    try:
        #check if the log out button exists        
        logged_in_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/nav/div/div/div[5]/ul/li[3]/div/section/div/div/div[1]/div/div[2]/div[1]/div[6]/a[2]"))
        )
        print("User is logged in.")
        return True
    except:
        print("User is not logged in.")
        return False

def logIn() :
    #input the username to the text field
    username_textfield = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div/div[1]/section/form/div[1]/span/span/input"))
    )
    type_with_delay(username_textfield, em_username)
    #input password to the text field
    time.sleep(1)
    password_textfield = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div/div[1]/section/form/div[2]/span/span/input"))
    )
    password_textfield.clear()
    type_with_delay(password_textfield, em_password)
    time.sleep(random.uniform(0.1, 0.3))

    #click the log in button
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "login-button"))
        )

        # click the login button
        login_button.click()

    except:
        print("Timeout occurred while waiting for the login button to be clickable.")

    time.sleep(2)

    # 2FA
    #make selection for sms 2-factor authencation
    sms_selection_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div/div/div/div/form/div/div[2]/input"))
    )
    if not sms_selection_button.is_selected():
        sms_selection_button.click()

    #click to summit for authentication
    two_AF_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.ID, "send-OTP-button"))
    )
    currentTime = datetime.datetime.utcnow()
    two_AF_button.click()
    time.sleep(5)
    client = Client(os.environ.get('twilio_username'), os.environ.get('twilio_api_key'))

    messages = client.messages.list(limit = 2)

    verification_code = ""
    for sms in messages:
        if "one-time passcode" not in sms.body:
            continue
        verification_code = sms.body[:6]
        # TODO fix this
        # if sms.date_updated < currentTime:
        #     raise "old message encountered"
        time.sleep(1)
    verification_txt = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div/div/div/div/span/div/input[1]"))
    )
    verification_txt.click()
    time.sleep(1)
    verification_txt.send_keys(verification_code)

    time.sleep(10)


def run_emerate():
    if not alreadyLoggedIn():
        logIn()
    else:
        print("already logged in")




def origin_insertion ():
    clear_default_origin_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/button"))
    )
    clear_default_origin_btn.click()

    origin_txt_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/input"))
    )
    origin_txt_field.clear
    origin_txt_field.send_keys("houston")
    time.sleep(10)


def select_dropdown_menu_origin():
    origin_dropdown_selection= WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[1]/div/div[1]/div/div/div[2]/section/ol/li/div"))
    )
    origin_dropdown_selection.click()
    time.sleep(10)



def destination_insertion () :
    destination_txt_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[1]/div/div[2]/div/div/div[1]/div/input"))
    )
    destination_txt_field.send_keys("singapore")
    time.sleep(10)

def select_dropdown_menu_destination() :
    destination_dropdown_selection= WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[1]/div/div[2]/div/div/div[2]/section/ol/li/div"))
    )
    destination_dropdown_selection.click()
    time.sleep(10)

"""def select_departure_date() :
    select_departure_date= WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[3]/eol-datefield/div[1]/div[1]/input"))
    )
    select_departure_date.click() #click on the textfield so that the calendar popup

    date_picker= WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[1]/div[3]/eol-datefield/eol-calendar/div/div"))
    )

    desired_date = "04-2025-03"
    date_element = date_picker.find_element_by_xpath(f"//td[@data-date='{desired_date}']")
    date_element.click()
    
    time.sleep(10)
"""


"""def serching () :
    searching_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/main/div[2]/div/div/div[1]/div/div/div/div[2]/section/div[4]/div[2]/div[3]/form/button/span"))
    )
    searching_btn.click()

    time.sleep(60)
"""

"""
#function to select the departure date and return date

"""













