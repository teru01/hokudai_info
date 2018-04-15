import requests
import keyring
from bs4 import BeautifulSoup


def main():
    payload = {'PSTKBN': '2', 'LOGIN_USERID': 's02166131n', 'LOGIN_PASS': keyring.get_password('elms', 's02166131n')}
    with requests.Session() as s:
        r = s.post('https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php', data=payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        print(soup.find_all('table')[3])

if __name__ == '__main__':
    main()
