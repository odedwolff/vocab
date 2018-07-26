from vocab.views import *

def run():
	print("running test script")
	#saveTrxPair(2, "1747", 0.4, None, 3, "1747gb", 0.6, None)
	
	#saveTrxPair(languageId1, expression1, freq1, categories1, languageId2, expression2, freq2, categories2)
	
	#insertCategory("cat1")
	
	catList1 = [1, 35, 4]
	catList2 = [4, 16, 2]
	catList11 = [4, 1, 35]
	
	print (compareCategories(catList1, catList2))
	print (compareCategories(catList1, catList11))