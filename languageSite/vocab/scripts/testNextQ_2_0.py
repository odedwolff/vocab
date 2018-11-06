from vocab.views import *


def run():
	#rs =getNextQFromDb(2, 5, 31, "")
	#log("recieved results at test scrtipt:" + str(rs))
	
	test1()
	
iterations=1000
def test1():
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