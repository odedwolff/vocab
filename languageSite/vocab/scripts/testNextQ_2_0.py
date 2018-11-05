from vocab.views import *


def run():
	rs =getNextQFromDb(2, 5, 31, "")
	log("recieved results at test scrtipt:" + str(rs))