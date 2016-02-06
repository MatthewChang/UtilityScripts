#! /usr/bin/python
import re
from sys import stdin

while True:
    line = stdin.readline()
    flag1 = re.match("Cannot render.*",line)
    flag2 = re.match('.*path=/api/users/\d*/messages format=json controller=api/users action=get_message status=200.*',line)
    if(not(flag1 or flag2)):
        print line[:-1]
