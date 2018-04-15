import requests
import keyring as kr
from bs4 import BeautifulSoup


def main():
    elmsid = kr.get_password('elmsid', 'elmsid')
    passwd = kr.get_password('elms', elmsid)
    payload = {'PSTKBN': '2',
               'LOGIN_USERID': elmsid,
               'LOGIN_PASS': passwd, }
    with requests.Session() as s:
        r = s.post('https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php', data=payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        print(soup.find_all('table')[3])

if __name__ == '__main__':
    main()
