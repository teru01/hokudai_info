import datetime

import requests
import keyring as kr
from bs4 import BeautifulSoup


def is_due_back_soon(ret_date):
    REMINDER_DAYS = 3
    _ret_date_formatted = datetime.datetime.strptime(ret_date, "%Y.%m.%d")
    _now = datetime.datetime.today()
    if (_ret_date_formatted - _now).days < REMINDER_DAYS:
        return True


def download_my_page(_session):
    _elms_id = kr.get_password('elmsid', 'elmsid')
    _passwd = kr.get_password('elms', _elms_id)
    _payload = {'PSTKBN': '2',
                'LOGIN_USERID': _elms_id,
                'LOGIN_PASS': _passwd, }
    _url = 'https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php'
    r = _session.post(_url, data=_payload)
    return BeautifulSoup(r.text, 'html.parser')


def get_formatted_data(_book_data):
    _title = ''.join(_book_data.find_all('td')[6].string.split('/')[:-1])
    _ret_date = _book_data.find_all('td')[4].string
    return _title, _ret_date


def send_notify(title, ret_date):
    message = "以下の返却期限が迫っています\n{}\n返却期限: {}"
    payload = {"message": message.format(title, ret_date)}
    auth_url = "https://notify-api.line.me/api/notify"
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer ' + kr.get_password('line_token', 'books'),
               }
    requests.post(auth_url, headers=headers, data=payload)


def main():
    with requests.Session() as s:
        soup = download_my_page(s)
        try:
            for book_data in soup.find_all('table')[3].find_all('tr')[1:]:
                title, ret_date = get_formatted_data(book_data)
                if is_due_back_soon(ret_date):
                    send_notify(title, ret_date)
        except IndexError:
            pass

if __name__ == '__main__':
    main()
