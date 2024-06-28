import os
import re
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

FILE_PATH = 'scraps/'
headers = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
}
#URL = 'https://senderscore.org/assess/get-your-score/report/?lookup=202.162.237.227&authenticated=true'
if len(sys.argv) < 2:
    print("Please provide IP in command line arguement.Run:  <main.py 1.0.0.127>")
    exit(1)
IP = sys.argv[1]

load_dotenv()
URL = os.getenv("URL")
URL = URL.format(IP=IP) 

file_path = URL.split("://")[1]
file_path = file_path.replace("/", "-")
file_path = re.sub(r'[^a-zA-Z0-9]+', '', file_path)   
file_path = FILE_PATH + file_path
current_path = os.path.abspath(os.getcwd())
file_path = current_path+"/"+file_path

file_full_path = file_path+".html"
file_exists = os.path.isfile(file_full_path)

def to_snake_case(str: str)->str:
    str = str.lower().strip(" ")
    return "_".join(str.split(" "))

data = ""
if not file_exists:
    print("in file exists")
    try:
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        })
        page = requests.get(URL, headers=headers)
        # print(page.text)
        with open(file_path+".html", "w") as file:
            file.write(page.text)
    except Exception as e:
        print("Error while fetching page", e)
        exit(1)


with open(file_path+".html", "r") as file:
    data = file.read()
    if data == "":
        print("Empty data exiting...")
        exit(1)

def scan():
    # driver = webdriver.Firefox("/usr/bin/firefox")
    driver = webdriver.Chrome()
    driver.get("file://"+file_path+".html")

    search = {
        "by": By.CLASS_NAME,
        "value": "ss-rdns"
    }

    #Host
    scrape = driver.find_elements(**search)
    if scrape:
        rdns = scrape[0].text

    #Sender volume class
    search['value'] = "ss-vol-tier"
    scrape = driver.find_elements(**search)
    if scrape:
        sender_volume_class = scrape[0].text

    #Certified by validity
    search["value"] = "ss-certified"
    certified_by_validity = False
    scrape = driver.find_elements(**search)
    if scrape:
        certified_attr = scrape[0]
        certified_attr = certified_attr.find_element(by=By.CSS_SELECTOR, value="i").get_attribute("class")
        if certified_attr:
            if "fa-xmark" not in certified_attr:
                certified_by_validity = True

    #Safe return path
    search["value"] = "ss-rp-safe"
    safe_return_path = False
    scrape = driver.find_elements(**search)
    if scrape:
        return_path_element = scrape[0]
        return_path_attr = return_path_element.find_element(by=By.CSS_SELECTOR, value="i").get_attribute("class")
        if return_path_attr:
            if "fa-xmark" not in return_path_attr:
                safe_return_path = True

    #Sender Score
    search["value"] = ".ss-score .ss-score__num"
    search["by"] = By.CSS_SELECTOR
    scrape = driver.find_elements(**search)
    if scrape:
        sender_score = scrape[0].text

    #Sending domains
    sending_domains_td = []
    sending_domains = []
    search["value"] = "#sendingTable tbody tr"
    sending_domains_td = driver.find_elements(**search)
    if len(sending_domains_td) > 0: 
        for i in range(len(sending_domains_td)):
            sending_domains.append(sending_domains_td[i].find_element(by=By.CSS_SELECTOR, value="td a").text) 

    #Reputation Checks
    reputation_checks_td = []
    reputation_checks=[]
    search["value"] = "#repTable tbody tr"
    reputation_checks_td = driver.find_elements(**search)
    if len(reputation_checks_td) > 0: 
        for i in range(len(reputation_checks_td)):
            mesaure_d = {}
            elements = reputation_checks_td[i].find_elements(by=By.CSS_SELECTOR, value="td")
            mesaure_d["measure"] = to_snake_case(elements[0].text)
            mesaure_d["impact"] = elements[1].text 
            reputation_checks.append(mesaure_d)

    # Volume trend
    volume_trend = {}
    volume_data = driver.execute_script("return ssData.ss_volume_trend")
    volume_score_data = driver.execute_script("return ssData.ss_trend")
    for volume in volume_data:
        if volume:
            volume_trend[volume["timestamp"]] = {"volume": volume["value"]}
            for volume_score in volume_score_data:
                if volume_score:
                    if volume_score["timestamp"] in volume_trend:
                        volume_trend[volume_score["timestamp"]]["score"] = volume["value"]
                    else:
                        volume_trend[volume_score["timestamp"]] = {"score": volume["value"]}

    print("\nrdns : ",rdns)
    print("\nsender_volume_class : ",sender_volume_class)
    print("\ncertified_by_validity : ",certified_by_validity)
    print("\nsafe_return_path : ",safe_return_path)
    print("\nsender_score : ",sender_score)
    print("\nReputation checks:")
    print(reputation_checks)
    print("\nSending domains:")
    print(sending_domains)
    print("\nVolume : ")
    print(volume_trend)

scan()