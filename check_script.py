import smtplib
import subprocess
import datetime
import os
import argparse
from pathlib import Path

FROM_EMAIL = 'отправитель@gmail.com'
PASSWORD = 'пароль'
TO_EMAIL = 'почта@получателя'
NOTIFIED_MESSAGE = ' | Administrator has been notified'


def add_log(message):
    with open(LOG_PATH, 'a') as script_log:
        script_log.write(date_time + message + '\n')


if __name__ == '__main__':
    """python test.py --pwd env['post_password'] --ip 8.8.8.12"""
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--pwd', default=PASSWORD)
    parser.add_argument('--ip', default='8.8.8.8')
    parser.add_argument('--smtp_host', default='smtp.gmail.com')
    parser.add_argument('--smtp_port', default=587)
    args = parser.parse_args()
    ip = args.ip
    LOG_PATH = f'/mnt/d/some_IT_staff/KamaGames_Test/check_host_{ip}.log'
    text = f'Server {ip} is down, it is time to work!'
    date_time = datetime.datetime.now().isoformat()
    """
    Настроим почту, включим TLS и залогинимся
    """
    mailer = smtplib.SMTP(args.smtp_host, args.smtp_port)
    mailer.starttls()
    mailer.login(FROM_EMAIL, args.pwd)

    """
    проверим, есть ли лог и прочитаем последнюю строку. Нас интересует строка о неуспешной проверке
    @param path:
    @return:
    """
    if not os.path.isfile(LOG_PATH):
        script_log = Path(LOG_PATH)
        script_log.touch(exist_ok=True)
        script_log = open(LOG_PATH, 'a')
        script_log.write('date&time | message \n')
        script_log.close()
    with open(LOG_PATH, 'r') as script_log:
        last_check = script_log.readlines()[-1]

    try:
        response = subprocess.call(['ping -c 1 ' + ip], shell=True, stdout=subprocess.PIPE)
        result = ''
        if response == 0:
            result = f'{ip} is up!'
            add_log(f' | Check result = {response} host  {result}')
        else:
            result = f'{ip} is down!'
            """проверим, не был ли администратор уведомлен раньше"""
            if result in last_check:
                add_log(f' | Check result = {response} host  {result}')
            else:
                mailer.sendmail(FROM_EMAIL, TO_EMAIL, text)
                add_log(NOTIFIED_MESSAGE)
                add_log(f' | Check result = {response} host  {result}')

    except Exception as e:
        mailer.sendmail(FROM_EMAIL, TO_EMAIL, f'Can not check the service! Error: {e}')
    mailer.quit()
