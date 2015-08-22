__author__ = 'krop'
import smtplib
import sys
import os
import datetime
import time, sched
import argparse
import getpass
from email.mime.text import MIMEText


def send_em(msg, serverSMTP, password):
    s = smtplib.SMTP(serverSMTP)
    s.set_debuglevel(1)
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()


def get_birth(inputfile, send_to=None, outputfile=None, password=None, serverSMTP=None, send_from=None):
    try:
        fp = open(inputfile, 'r')
    except:
        return print('Error to open %s' % inputfile)
    a = ''
    for i in fp:
        i = i.rstrip('\n')
        b = i.split(",")[1][0:6] + datetime.datetime.now().year.__str__()
        birth_time = datetime.datetime.strptime(b, "%d.%m.%Y")
        birth_time -= datetime.datetime.now()
        if birth_time <= datetime.timedelta(days=5) and birth_time >= datetime.timedelta(days=-1):
            z = '%s (%s) - %s days left\n' % (i.split(",")[0], i.split(",")[1], birth_time.days)
            a += z
    fp.close()
    msg = MIMEText(a)
    msg['Subject'] = 'Incoming party notification'
    msg['From'] = send_from
    if serverSMTP:
        msg['To'] = send_to
        send_em(msg, serverSMTP, password)
    else:
        print(msg)
    if outputfile:
        msg['To'] = send_to
        out_file = open(outputfile, 'w')
        out_file.write(str(msg))
        out_file.close()
    else:
        print(msg)


def main():
    print('Birthday notification app\n'
          'Ctrl+c to exit\n')
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ifile", type=str,
                        help="input cvs file ")
    parser.add_argument("-o", "--ofile", type=str,
                        help="output cvs file ")
    parser.add_argument("-e", "--email", type=str,
                        help="output email adress ")
    args = parser.parse_args()
    inputfile = None
    outputfile = None
    send_to = None
    send_from = input('Input From email adress\n')
    serverSMTP = None
    password=None
    if args.ifile:
        inputfile = args.ifile
    if args.email:
        send_to = args.email
        serverSMTP = input('Input server SMTP server:port or server\n')
        password = getpass.getpass('Enter email server password\n')
    if args.ofile:
        outputfile = args.ofile
        if args.email:
            send_to = args.email
        else:
            send_to = input('Input destination email adress\n')
    d = datetime.datetime.now()
    while True:
        s = input('Enter space-separated Hour 0-23, Minutes 0-59\n')
        try:
            H, M = map(int, s.split())
        except ValueError:
            pass
        else:
            if 0 <= H < 24 and 0 <= M < 60:
                break
            else:
                print('Try again')
    t = d.replace(hour=H, minute=M, second=00)
    print(t)
    s = sched.scheduler(time.time, time.sleep)
    while inputfile:
        s.enterabs(time.mktime(t.timetuple()), 1, get_birth,
                   (inputfile, send_to, outputfile, password, serverSMTP, send_from,))
        s.run()
        t = t.replace(day=t.day + 1)
        print('Next alarm at:')
        print(t)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nQuit!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
