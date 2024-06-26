import requests
import os
import re

FILE_PATH = 'scraps/'
headers = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
}
URL = 'https://senderscore.org/assess/get-your-score/report/?lookup=202.162.237.227&authenticated=true'

file_path = URL.split("://")[1]
file_path = file_path.replace("/", "-")
file_path = re.sub(r'[^a-zA-Z0-9]+', '', file_path)   
file_path = FILE_PATH + file_path
file_exists = os.path.isfile(file_path)
current_path = os.path.abspath(os.getcwd())
file_path = current_path+"/"+file_path

if file_exists:
    print("file exists")
else:
    try:
        page = requests.get(URL, headers=headers)
        with open(file_path+".html", "w") as file:
            file.write(page.text)
    except Exception as e:
        print("Error while fetching page", e)


print(page.text)