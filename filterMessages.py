#! /usr/bin/python
import re
from sys import stdin
import argparse

parser = argparse.ArgumentParser(description='Filter aptible logs')
parser.add_argument('-s', dest='sign_in', action='store_const',
                   const=True, default=False,
                   help='use flag to filter out sign in attempts')

args = parser.parse_args()
#pipe the output from rails into me to have the message poll lines filtered out

while True:
    line = stdin.readline()
    flag = re.match("Cannot render.*",line)
    
    good = re.match('.*method=[A-Z]+ path=.*',line)
    flag = flag or re.match('.*path=/api/users/\d*/messages',line)
    flag = flag or re.match('.*path=/api2/users/\d*/get_message',line)
    flag = flag or re.match('.*path=/api/physicians/\d*/current_call',line)
    if(args.sign_in):
        flag = flag or re.match('.*path=/api/users/sign_in',line)
    if(good and not flag):
        print line[:-1]
