#! /usr/bin/python

import json
import argparse
import sys



parser = argparse.ArgumentParser(description='Process JSON')
parser.add_argument('-d', dest='define', action='store_const',
     const=True, default=False,
     help='Add type definitions')
parser.add_argument('-a', dest='assign', action='store_const',
     const=True, default=False,
     help='Add type assignment from variable')
parser.add_argument('-n', type=str,
     help='name of variable',default="response");

args = parser.parse_args()
print args
print "Please input a valid JSON object: "

def j(name):
      name = name.title().replace('_','')
      return name[0].lower() + name[1:]

string_in = ""
while True:
      string_in += sys.stdin.readline()
      try:
            json.loads(string_in)
            break
      except:
            pass

A = json.loads(string_in)
#print A
#print len(A)
print "\n\n\n"
for name,val in A.iteritems():
      #print type(val)
      t2 = "Object"
      t = ""
      if(isinstance(val,int)):
            t = "Int"
            t2 = 'int'
      if(isinstance(val,basestring)):
            t = "String"
            t2 = "String"
      assignString = ' = {0}.get{1}("{2}");'.format(args.n,t,name) if args.assign else ";"
      lead = "{0} ".format(t2) if args.define else ""
      print "{0}{1}{2}".format(lead,j(name),assignString);
