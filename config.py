from requests.auth import HTTPBasicAuth

il_url = 'https://abe-in-il.cs300ohie.net:5000'
auth = HTTPBasicAuth('tutorial', 'pass')
headers = {'Content-Type': 'application/json'}