from vocab.views import *


def run():
	#testLoadTranslations()
	#answerUpdateDb(31, 326, 5, True)
	testNextQStat()

iterations=1
def testNextQStat():
	stat = {}
	for i in range(0,iterations):
		rs =getNextQFromDb(2, 5, 31, "")
		#key=rs['expStr']
		key=rs['expId']
		if key in stat:
			stat[key]+=1
		else:
			stat[key]=1
	
	print("stat=" + str(stat))
	
def testUpdateAnswer():
	answerUpdateDb(31, 326, 5, True)
	
def testLoadTranslations():
	loadTranslations(326, 5)
