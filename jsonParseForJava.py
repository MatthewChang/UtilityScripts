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
parser.add_argument('-r', dest='recursive', action='store_const',
     const=True, default=False,
     help='Recurse into nested objects')
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
print A
#print len(A)
print "\n\n\n"

def parse(obj,object_name,assign,define,depth = 0):
    output= ""
    for name,val in obj.iteritems():
        jname = j(name)
        if(isinstance(val,list) and len(val) > 0):
            output += 'JSONArray {0} = {1}.getJSONArray("{2}");\n'.format(jname,object_name,name)
            output += "for(int i = 0; i < {0}.length(); i++) {{\n".format(jname);
            nested_name = "obj{0}".format(depth);
            output += 'JSONObject {0} = {1}.getJSONObject(i);\n'.format(nested_name,jname);
            output += parse(val[0],nested_name,True,True,depth+1)
            output += "}\n"
        elif(isinstance(val,dict) and args.recursive):
            output += 'JSONObject {0} = {1}.getObject("{2}");\n'.format(jname,object_name,name)
            output += parse(val,jname,True,True,depth+1)
        else:
          t2 = "Object"
          t = ""
          if(isinstance(val,int)):
                t = "Int"
                t2 = 'int'
          if(isinstance(val,basestring)):
                t = "String"
                t2 = "String"
          assignString = ' = {0}.get{1}("{2}");'.format(object_name,t,name) if assign else ";"
          lead = "{0} ".format(t2) if define else ""
          output+= "{0}{1}{2}\n".format(lead,j(name),assignString);
    return output
          
print parse(A,args.n,args.assign,args.define)
