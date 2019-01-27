import datetime
from enum import Enum, auto
import sys
import os
from base64 import b64decode

import requests
import requests.exceptions
from bs4 import BeautifulSoup
import boto3

class LoanPeriodState(Enum):
    """借りた本の期限が、まだ先/もうすぐ/過ぎてる のうちどの状態かを表す"""
    AWAY = auto()
    SOON = auto()
    OVERDUE = auto()

def get_decrypted_key(encrypted):
    return boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted))['Plaintext']


def decide_loan_period_state(ret_date, _reminder_days=3):
    ret_date_formatted = datetime.datetime.strptime(ret_date, "%Y.%m.%d").date()
    now = datetime.date.today()
    delta = (ret_date_formatted - now).days
    if delta < 0:
        return LoanPeriodState.OVERDUE
    if 0 <= delta <= _reminder_days:
        return LoanPeriodState.SOON
    return LoanPeriodState.AWAYe


def download_my_page(_session):
    elms_id = get_decrypted_key(os.environ['elms_id'])
    passwd = get_decrypted_key(os.environ['passwd'])
    payload = {'PSTKBN': '2',
                'LOGIN_USERID': elms_id,
                'LOGIN_PASS': passwd, }
    url = 'https://opac.lib.hokudai.ac.jp/opac-service/srv_odr_stat.php'
    response = _session.post(url, data=payload)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def get_formatted_data(_book_data):
    title = ''.join(_book_data.find_all('td')[6].string.split('/')[:-1])
    ret_date = _book_data.find_all('td')[4].string
    return title, ret_date


def send_notify(message, *args):
    payload = {"message": message.format(*args)}
    auth_url = "https://notify-api.line.me/api/notify"
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer ' + get_decrypted_key(os.environ['line_token']).decode(),
               }
    requests.post(auth_url, headers=headers, data=payload)


def handler(event, context):
    with requests.Session() as session:
        soup = download_my_page(session)
        try:
            for book_data in soup.find_all('table')[3].find_all('tr')[1:]:
                title, ret_date = get_formatted_data(book_data)

                if len(sys.argv) == 2:
                    state = decide_loan_period_state(ret_date, _reminder_days=int(sys.argv[1]))
                else:
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

