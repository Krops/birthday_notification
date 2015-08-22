#!/usr/bin/env python
__author__ = 'krop'
import smtplib
import sys
import os
import datetime
import time, sched
import argparse
import getpass
from email.mime.text import MIMEText


# function that send email
def send_em(msg, serverSMTP, password):
    # set SMTP server
    s = smtplib.SMTP(serverSMTP)
    # set debug output when sent email
    s.set_debuglevel(1)
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()


# function that read CVS file and convert it to email format
def get_birth(inputfile, send_to=None, outputfile=None, password=None, serverSMTP=None, send_from=None):
    # open CVS input file
    try:
        fp = open(inputfile, 'r')
    except:
        return print('Error to open %s' % inputfile)
    # read file lines and collect fields name and birth day into string 'a'
    a = ''
    for i in fp:
        i = i.rstrip('\n')
        # generate birth day from born date
        b = i.split(",")[1][0:6] + datetime.datetime.now().year.__str__()
        # get birth day delay
        birth_time = datetime.datetime.strptime(b, "%d.%m.%Y")
        birth_time -= datetime.datetime.now()
        # compare delay with 5 days
        if birth_time <= datetime.timedelta(days=5) and birth_time >= datetime.timedelta(days=-1):
            # collect birth day that will be in 5 days
            z = '%s (%s) - %s days left\n' % (i.split(",")[0], i.split(",")[1], birth_time.days)
            a += z
    fp.close()
    # convert string with bdays to email format and set from and to fields
    msg = MIMEText(a)
    msg['Subject'] = 'Incoming party notification'
    msg['From'] = send_from
    # if -e option send email
    if serverSMTP:
        msg['To'] = send_to
        send_em(msg, serverSMTP, password)
    else:
        print(msg)
    # if -o option create email file
    if outputfile:
        msg['To'] = send_to
        out_file = open(outputfile, 'w')
        out_file.write(str(msg))
        out_file.close()
    else:
        # or just print contents of the line
        print(msg)


def main():
    print('Birthday notification app\n'
          '"-h" for help\n'
          'Ctrl+c to exit\n')
    # create command line parser
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
    serverSMTP = None
    password = None
    # check -i option and get mailer field
    if args.ifile:
        inputfile = args.ifile
        send_from = input('Input From email adress\n')
    else:
        print('No input file!\n')
        sys.exit(0)
    # check -e option and get receiver, smtp server and password field
    if args.email:
        send_to = args.email
        serverSMTP = input('Input server SMTP server:port or server\n')
        password = getpass.getpass('Enter email server password\n')
    # check -o option
    if args.ofile:
        outputfile = args.ofile
        if args.email:
            send_to = args.email
        else:
            # get receiver field
            send_to = input('Input destination email adress\n')
    # get time
    d = datetime.datetime.now()
    # get alarm time
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
    print('Next alarm at:')
    print(t)
    # create daily scheduler
    s = sched.scheduler(time.time, time.sleep)
    while inputfile:
        s.enterabs(time.mktime(t.timetuple()), 1, get_birth,
                   (inputfile, send_to, outputfile, password, serverSMTP, send_from,))
        s.run()
        # after get_birth add one day to scheduler
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
