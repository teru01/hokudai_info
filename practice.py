import datetime

import requests
import keyring as kr
from bs4 import BeautifulSoup


def is_due_back_soon(ret_date):
    REMINDER_DAYS = 3
    ret_date_formatted = datetime.datetime.strptime(ret_date, "%Y.%m.%d")
    now = datetime.datetime.today()
    if (ret_date_formatted - now).days < REMINDER_DAYS:
        return True


def main():
    _elms_id = kr.get_password('elmsid', 'elmsid')
    _passwd = kr.get_password('elms', _elms_id)
    payload = {'PSTKBN': '2',
               'LOGIN_USERID': _elms_id,
               'LOGIN_PASS': _passwd, }

    with requests.Session() as s:
        r = s.post('https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php', data=payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            for book_data in soup.find_all('table')[3].find_all('tr')[1:]:
                title = ''.join(book_data.find_all('td')[6].string.split('/')[:-1])
                ret_date = book_data.find_all('td')[4].string
                if is_due_back_soon(ret_date):
                    print("返却期限が迫っています")
                    print("{} , 返却期限: {}".format(title, ret_date))
        except IndexError:
            pass

if __name__ == '__main__':
    main()
