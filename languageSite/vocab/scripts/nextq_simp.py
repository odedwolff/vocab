
#import vocab.views

from vocab.views import *

import json

iterations = 100
counter = {}


def run():
	for i in range(0,iterations):
		out=testRandFrequency()
		if "nextQ" in out:
			exp=out["nextQ"]["str"]
			print(exp)
			inc(exp)
	print(str(counter))

def inc(expression):
	if expression in counter:
		counter[expression]+=1
	else:
		counter[expression]=1

	