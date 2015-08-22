__author__ = 'krop'
import smtplib
import datetime
import time, sched
import sys, getopt
import argparse
from email.mime.text import MIMEText


def send_em(msg):
    me = 'andrekropes@gmail.com'
    you = 'andrekropes@yandex.ru'
    msg['Subject'] = 'Incoming party notification'
    msg['From'] = you
    msg['To'] = me

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.yandex.ru')
    s.set_debuglevel(1)
    s.starttls()
    s.login(you, '555Krop')
    s.sendmail(you, [me], msg.as_string())
    s.quit()


def get_birth(inputfile,outputfile=None):
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
    print(a)
    fp.close()
    if outputfile:
        out_file = open(outputfile, 'w')
        out_file.write(a)
        out_file.close()
        out_file = open(outputfile, 'r')
        print(out_file.read())
        out_file.close()
    else:
        msg = MIMEText(a)
        send_em(msg)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ifile", type=str,
                    help="input cvs file ")
    parser.add_argument("-o", "--ofile", type=str,
                    help="output cvs file ")
    args = parser.parse_args()
    inputfile=''
    outputfile=None
    if args.ifile:
        inputfile = args.ifile

    if args.ofile:
        outputfile = args.ofile
    d = datetime.datetime.now()
    t = d.replace(hour=1, minute=50, second=00)
    print(t)
    s = sched.scheduler(time.time, time.sleep)
    while True:
        s.enterabs(time.mktime(t.timetuple()), 1, get_birth, (inputfile,outputfile,))
        s.run()
        t = t.replace(day=t.day + 1)
        print(t)

if __name__ == "__main__":
    main()
