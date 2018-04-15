import datetime
from enum import Enum, auto

import requests
import requests.exceptions
import keyring as kr
from bs4 import BeautifulSoup


class LoanPeriodState(Enum):
    """借りた本の期限が、まだ先/もうすぐ/過ぎてる のうちどの状態かを表す"""
    AWAY = auto()
    SOON = auto()
    OVERDUE = auto()


def decide_loan_period_state(ret_date, _reminder_days=3):
    _ret_date_formatted = datetime.datetime.strptime(ret_date, "%Y.%m.%d").date()
    _now = datetime.date.today()
    _delta = (_ret_date_formatted - _now).days
    if _delta < 0:
        return LoanPeriodState.OVERDUE
    if 0 <= _delta <= _reminder_days:
        return LoanPeriodState.SOON
    return LoanPeriodState.AWAY


def download_my_page(_session):
    _elms_id = kr.get_password('elmsid', 'elmsid')
    _passwd = kr.get_password('elms', _elms_id)
    _payload = {'PSTKBN': '2',
                'LOGIN_USERID': _elms_id,
                'LOGIN_PASS': _passwd, }
    _url = 'https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php'
    r = _session.post(_url, data=_payload)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')


def get_formatted_data(_book_data):
    _title = ''.join(_book_data.find_all('td')[6].string.split('/')[:-1])
    _ret_date = _book_data.find_all('td')[4].string
    return _title, _ret_date


def send_notify(message, *args):
    payload = {"message": message.format(*args)}
    auth_url = "https://notify-api.line.me/api/notify"
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer ' + kr.get_password('line_token', 'books'),
               }
    requests.post(auth_url, headers=headers, data=payload)


def main():
    with requests.Session() as session:
        soup = download_my_page(session)
        try:
            for book_data in soup.find_all('table')[3].find_all('tr')[1:]:
                title, ret_date = get_formatted_data(book_data)
                state = decide_loan_period_state(ret_date)

                if state == LoanPeriodState.AWAY:
                    return
                elif state == LoanPeriodState.OVERDUE:
                    message = "＊＊書籍の返却期限が過ぎています！＊＊。\n{}\n返却期限: {}"
                elif state == LoanPeriodState.SOON:
                    message = "書籍の返却期限が迫っています。\n{}\n返却期限: {}"

                send_notify(message, title, ret_date)

        except IndexError:
            """何も借りていない時はここを通る"""
            pass

        except requests.exceptions.HTTPError as error:
            message = "データを取得できませんでした。\n{}"
            send_notify(message, error.__traceback__)

if __name__ == '__main__':
    main()
