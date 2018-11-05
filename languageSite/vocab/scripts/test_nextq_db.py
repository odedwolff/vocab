
#import vocab.views

from vocab.views import *

import json

"""
userId=34
srcLangId=34
trgLangId=34
cats = [2,13, 56]
"""

userId=31
srcLangId=2
trgLangId=5
cats = []

iterations=100
counter={}

if len(cats) > 0:
	cats.sort()
	catsSer = json.dumps(cats)
else:
	catsSer=""



def run():
	for i in range(0,iterations):
		out=getNextQFromDb(srcLangId, trgLangId, userId, catsSer)
		if out["nextQ"]:
			exp=out["nextQ"]["str"]
			print(exp)
			inc(exp)
	print(str(counter))

def inc(expression):
	if expression in counter:
		counter[expression]+=1
	else:
		counter[expression]=1

	