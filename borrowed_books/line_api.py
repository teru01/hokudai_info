import requests
import keyring as kr
auth_url = "https://notify-api.line.me/api/notify"
headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'Authorization': 'Bearer ' + kr.get_password('line_token', 'books'),
           }
data = {'message': "hello"}
requests.post(auth_url, headers=headers, data=data)

