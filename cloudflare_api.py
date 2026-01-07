[database]
db_path = /mnt/z/OMRGBMK/OMGBMK.accdb[database]
db_path = /mnt/z/OMRGBMK/OMGBMK.accdb
cd /d Z:\OMRGBMK
python server.py

import requests

url = "https://api.cloudflare.com/client/v4/zones/4bdbf156dc9cf4fe3aecc7deabe80876/settings/transformations"
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",  # Use environment variable for the token!
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(response.json())