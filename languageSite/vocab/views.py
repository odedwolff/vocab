from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language, User, Catagory, AggrScore

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError

from django.db import IntegrityError


from passlib.hash import pbkdf2_sha256

import json

import pprint 

from django.views.decorators.csrf import csrf_exempt

from django.db import connection

import random

	



KEY_SESSION_LOGGED_USER = "loggedUser"
ERROR_CODE_NO_SUCH_USER = 5001
ERROR_CODE_PASSWORD_DONT_MATCH = 5002
KEY_LANG = "language"
KEY_EXP_STR = "expressionStr"
KEY_FREQ = "frequency"
KEY_LANGUAGE = "language"
KEY_CATS_IDS = "catIds"
KEY_CATS_STRS = "catStrs"
CATS_TYPE_STRINGS = "compareStrings"
CATS_TYPE_INTS = "compareInts"
LANG_TYPE_STRING="compareString" 
LANG_TYPE_INTS="compareIntes"

pp = pprint.PrettyPrinter(indent=4)


def log(msg, imortance = 0):
	print(msg)
	##pp.pprint(msg)

def client (request):
	"""
	returns the main client page 
	"""	
	return render(request, 'vocab/client.html')
	
	

#@csrf_exempt	
def addLanguage(request):
	"""
	handels http request to add a new language  
	"""
	lang = request.POST["lang"]
	saveNewLanguage(lang)
	return HttpResponse("lnaguage saved")	



def addExpression(request):
	"""
	handels http request to add a new language 
	
	TODO
	*handle argument categories list
	*add details to failure message	
	"""
	languageId = request.POST["languageID"]
	expression = request.POST["expression"]
	
	saved = saveExpression(expression, languageId, None )
	if saved:
		return HttpResponse("expression saved")	
	else: 
		return HttpResponseServerError("expression failed to save")	
		
		
@csrf_exempt
def uploadTranslationsBatch(request):
	"""
	handles an array of translations pairs to be added, for instance when client 
	uploads a file containing translations 
	
	"""
	
	log("entering uploadTranslationsBatch ") 
	
	parsed = json.loads(request.body) 
	log("parsed = " + str(parsed))
	
	pairsArr = parsed["transInfo"]["wordpairs"]
	saved=False
	log("length of pairsArr=" + str(len(pairsArr)))
	for wordsPair in pairsArr:
		exp1 = {}
		exp1[KEY_LANG] = parsed["transInfo"]["srcLang"]
		exp1[KEY_EXP_STR] = wordsPair["srcWord"]["expression"]
		exp1[KEY_FREQ]=wordsPair["srcWord"]["frequency"] 
		if "categories" in wordsPair["srcWord"]:
			exp1[KEY_CATS_STRS] =  wordsPair["srcWord"]["categories"]
		exp2 = {}
		exp2[KEY_LANG] = parsed["transInfo"]["trgLang"]
		exp2[KEY_EXP_STR] = wordsPair["trgWord"]["expression"]
		exp2[KEY_FREQ]=wordsPair["trgWord"]["frequency"]
		if "categories" in wordsPair["trgWord"]:
			exp2[KEY_CATS_STRS] =  wordsPair["trgWord"]["categories"]
		#handle categories! 
		#exp1[KEY_CATS_IDS]= request.POST.getlist("cats1[]") 
		saved = saveTrxPair(exp1, exp2, CATS_TYPE_STRINGS, LANG_TYPE_STRING)
	if saved:
		return HttpResponse("expressions pair saved")	
	else:
		return HttpResponseServerError("expressions pair failed to save")	

	

def parseListOfInts(listOfInts):
	out = []
	for elm in listOfInts:
		out.append(int(elm))
	return out

	
def addExpressionFull(request):
	"""
	handles a request to add a translation pair between 2 given expressions 
	
	TODO
	*add category lists for both expressions	
	*renmae to better represent this adds a translation rather than an expression 
	*add details to failure message 
	"""	
	
	exp1 = {}
	exp1[KEY_LANG] = request.POST["languageID1"]
	exp1[KEY_EXP_STR] = request.POST["expression1"]
	exp1[KEY_FREQ]=request.POST["weight1"]
	#exp1[KEY_CATS_IDS]= request.POST.getlist("cats1[]")
	exp1[KEY_CATS_IDS]= parseListOfInts(request.POST.getlist("cats1[]"))
	exp2 = {}
	exp2[KEY_LANG] = request.POST["languageID2"]
	exp2[KEY_EXP_STR] = request.POST["expression2"]
	exp2[KEY_FREQ]=request.POST["weight2"]
	exp2[KEY_CATS_IDS]= parseListOfInts(request.POST.getlist("cats2[]"))
	
	saved = saveTrxPair(exp1, exp2, CATS_TYPE_INTS, LANG_TYPE_INTS)
	
	if saved:
		return HttpResponse("expressions pair saved")	
	else:
		return HttpResponseServerError("expressions pair failed to save")	

		
		
def registerUser(request):
	"""
	handels http request to add a new user 
	
	"""
	log("entering registerUser()")
	try:
		
		userName = request.POST["userName"]
		password = request.POST["password"]
		log("args:username,password=" + userName +"," +  password)
		log("password, len(pass)=" + password + ";" + str(len(password)))
		hash = hashPass(password)
		userId = saveUser(userName, hash)
		request.session[KEY_SESSION_LOGGED_USER] = userId
		result = {"success":True}
		log("returning sucess")
		return JsonResponse(result, safe=False)
		
	except IntegrityError:
		log("returning integrity error")
		return HttpResponseServerError("integrity error, possibly duplicate user name")
	except Exception as e:
		log("returning server error: " + str(e))
		return HttpResponseServerError("server error" + str(e))	

		
		
def logUserOn(request):
	"""
	handels http request to log in an existing uer  
	
	"""
	log("entering logUserin()")
	userName = request.POST["userName"]
	password = request.POST["password"]
	loadedUsers = User.objects.filter(name = userName)
	if len(loadedUsers) == 0 :
		log("no such user")
		result = {"success":False, "errorCode":ERROR_CODE_NO_SUCH_USER}
		return JsonResponse(result, safe=False)
	
	loadedUser = loadedUsers[0]
	savedHash = loadedUser.passHash
	
	match =  pbkdf2_sha256.verify(password, savedHash)
	if not match:
		log("password is not correct")
		result = {"success":False, "errorCode":ERROR_CODE_PASSWORD_DONT_MATCH}
		return JsonResponse(result, safe=False)
	
	log("log in credentidals correct")
	request.session[KEY_SESSION_LOGGED_USER] = loadedUser.id
	result = {"success":True}
	return JsonResponse(result, safe=False)
	
def logUserOff(request):
	#TODO - handle errors 
	request.session[KEY_SESSION_LOGGED_USER] = None
	result = {"success":True}
	return JsonResponse(result, safe=False)
	
		
def getLogOnStatus(request):
	"""
	seponds over http regarding login status of sending browser
	"""
	log("entering registerUser()")
	userId = None 
	if KEY_SESSION_LOGGED_USER in request.session:
		userId = request.session[KEY_SESSION_LOGGED_USER]
	username = ""
	isLogged = False
	if userId is not None:
		isLogged = True
		username = User.objects.get(pk= userId).name
	log("islogged=" + str(isLogged) + "; username= " + str(username))
	result = {"isLogged":isLogged,"username": username }
	return JsonResponse(result, safe=False)
		
		
def loadLanguages (request):
	"""
	loads a list of all languages 
	
	TODO
	*add error handling
	"""	
	dict = loadLanguagesDB()
	return JsonResponse(dict, safe=False)
	
	
def loadLanguagesDB ():
	"""
	loads all languages from database 
	"""
	list = []
	tmpElm = {}
	loadedLang = Language.objects.all()
	for lang in loadedLang:
		tmpElm = {}
		tmpElm["lang"] = lang.language
		tmpElm["id"] = lang.id
		list.append(tmpElm)
	result = {"loadedLangs": list}	
	return result 
	
def saveNewLanguage(languageName):
	"""
	saves new language in database 
	"""
	lang = Language(language = languageName)
	lang.save()
	
	
def saveUser(userName, hash):
	"""
	saves new user in database 
	"""
	user = User(name = userName, passHash = hash)
	user.save()
	return user.id
	

def saveExpression (expression, languageId, categoriesIds):
	"""
	tries to save new expression, returns whether expression saved successfully 
	"""
	if not validateExpression(expression, languageId, categoriesIds):
		return False	
	newExp = Expression()
	newExp.expression  = expression
	ldLanguage = Language.objects.get(id=languageId)
	if ldLanguage is None:
		return False
	newExp.language = ldLanguage
	if categoriesIds is not None:
		for cat in categoriesIds:
			newExp.categories.append(cat)
	try:
		newExp.save()
	except :
		return False 
	return True 
	

def validateExpression(expression, languageId, freq):
	return expression is not None and languageId is not None and freq is not None
	
	

def extractCatIds (cats):
	log("entering extractCatIds, arg cats=" + str(cats))
	theResult = []
	if not cats or len(cats) is 0:
		return theResult
	for cat in cats:
		theResult.append(str(cat.id))
	return theResult

def extractCatStrings  (cats):
	log("entering extractCatStrings, arg cats=" + str(cats))
	theResult = []
	if not cats or len(cats) is 0:
		return theResult
	for cat in cats:
		theResult.append(cat.category)
	return theResult

	
#29102018- changing data model. catetries list will be flatted out to a string- a singla field in the Expression class. 
#the Catatgory class will exist still, for enabling selecting of categories when inserting a new expression, but they will not be saved 
#as PK to the Categories table
	
def saveTrxPairOld(exp1, exp2, catsType, langType):

	"""
	saves to database new expressions translation pair 
	the expression contain information about categories and languages that can beferredd to 
	in IDs or String values (which are unique), the last 2 parametrs indicated which fields
	are used to identify categroies and languages 
	TODO
	*implment hadling of categories lists for both new expressions 
	"""
	
	
	#just some validations 
	
	log("entering saveTrxPair(exp1, exp2....)")
	log("exp1= " + str(exp1))
	log("exp2= " + str(exp2))
	
	if not validateExpression(exp1[KEY_EXP_STR], exp1[KEY_LANG], exp1[KEY_FREQ]) or not validateExpression(exp2[KEY_EXP_STR], exp2[KEY_LANG], exp2[KEY_FREQ]):
		log("validation of new Expressions failed, aborting save")
		return False
	if not (catsType is CATS_TYPE_STRINGS or catsType is CATS_TYPE_INTS):
		log("invalid cats typs " + catsType)
		return False
	if not (langType is LANG_TYPE_STRING or langType is LANG_TYPE_INTS):
		log("invalid language typs " + langType)
		return False
	
	#if language is referred to by ID it must load successfuly. however, if it is inidicated 
	#by name, it will be checked to exist, and if it doesnt a new language will be created with the given name 
	
	#languages are referred by id- load languages
	if langType is LANG_TYPE_INTS:
		lang1Set = Language.objects.filter(id=exp1[KEY_LANG])
		if len(lang1Set) is 0:
			log("could not load language with id " + exp1[KEY_LANG])
			return False
		else:
			lang1=lang1Set[0] 
		lang1Set = Language.objects.filter(id=exp2[KEY_LANG])
		if len(lang1Set) is 0:
			log("could not load language with id " + exp2[KEY_LANG])
			return False
		else:
			lang2=lang1Set[0] 
			
	#else- refer to language by name, not id. if such a language does not yet exist, create it and save it 
	else:
		lang1Set = Language.objects.filter(language=exp1[KEY_LANG])
		if len(lang1Set) is 0:
			lang1 = Language(language=exp1[KEY_LANG])
			lang1.save()
			log("added new language exp1[KEY_LANG]")
		else:
			lang1=lang1Set[0] 
		
		lang1Set = Language.objects.filter(language=exp2[KEY_LANG])
		if len(lang1Set) is 0:
			lang2 = Language(language=exp2[KEY_LANG])
			lang2.save()
			log("added new language exp1[KEY_LANG]")
		else:
			lang2=lang1Set[0] 
	
	
	#check whether any of the categories is new. if so, create it in database. 
	#this only applies when cats are given as strings 
	if catsType is CATS_TYPE_STRINGS and KEY_CATS_STRS in exp1:
		sentCats = exp1[KEY_CATS_STRS]
		for cat in sentCats:
			q = Catagory.objects.filter(category=cat)
			if len(q) is 0:
				Catagory(category=cat).save()
	if catsType is CATS_TYPE_STRINGS and KEY_CATS_STRS in exp2:
		sentCats = exp2[KEY_CATS_STRS]
		for cat in sentCats:
			q = Catagory.objects.filter(category=cat)
			if len(q) is 0:
				Catagory(category=cat).save()
		
	
	
	
	#check whether expression already exists, requires match of language, expresson and categories (that is,
	#having the exact same set of categories)
	match= False
	
	#check for match of expression and language 
	qSet = Expression.objects.filter(expression=exp1[KEY_EXP_STR], language=lang1)
	
	
	#for all matches, check for match of categories list
	if qSet:
		for loadedExp in qSet:
			loadedCatsFullObjs= loadedExp.categories.all()
			if(catsType is CATS_TYPE_INTS):
				loadedCats = extractCatIds(loadedCatsFullObjs)
				if KEY_CATS_IDS in exp1:
					sentCats = exp1[KEY_CATS_IDS]
				else:
					sentCats = []
			#else- cats type is strings 
			else:
				loadedCats = extractCatStrings(loadedCatsFullObjs)
				if KEY_CATS_STRS in exp1:
					sentCats = exp1[KEY_CATS_STRS]
				else:
					sentCats = []

			if	compareCategories(sentCats, loadedCats):
				newExp1= loadedExp
				match= True
				log("matched existing epxression1")
				break 

	#else:
	if not match:
		log("did not match existing epxression1, creating a new instance")
		newExp1 = Expression()
		newExp1.expression  = exp1[KEY_EXP_STR]
		newExp1.language = lang1
		newExp1.frequency = exp1[KEY_FREQ]
		newExp1.save()
		if(catsType is CATS_TYPE_INTS):
			if KEY_CATS_IDS in exp1:
				catsToSave = Catagory.objects.filter(id__in=exp1[KEY_CATS_IDS])
				newExp1.categories.add(*catsToSave.all())
		else:
			if KEY_CATS_STRS in exp1:
				catsToSave = Catagory.objects.filter(category__in=exp1[KEY_CATS_STRS])
				newExp1.categories.add(*catsToSave.all())
		
	
	#same thing for expression2 
	
	match= False
	qSet = Expression.objects.filter(expression=exp2[KEY_EXP_STR], language=lang2)
	
	if qSet:
		for loadedExp in qSet:	
			loadedCatsFullObjs= loadedExp.categories.all()
			if(catsType is CATS_TYPE_INTS):
				loadedCats = extractCatIds(loadedCatsFullObjs)
				if KEY_CATS_IDS in exp2:
					sentCats = exp2[KEY_CATS_IDS]
				else:
					sentCats = []
			#else- cats type is strings 
			else:
				loadedCats = extractCatStrings(loadedCatsFullObjs)
				if KEY_CATS_STRS in exp2:
					sentCats = exp2[KEY_CATS_STRS]
				else:
					sentCats = []

			if	compareCategories(sentCats, loadedCats):
				newExp2= loadedExp
				match= True
				log("matched existing epxression1")
				break 
				
	#else:
	if not match:
		log("did not match existing epxression2, creating a new instance")
		newExp2 = Expression()
		newExp2.expression  = exp2[KEY_EXP_STR]
		newExp2.language = lang2
		newExp2.frequency = exp2[KEY_FREQ]
		newExp2.save()
		if(catsType is CATS_TYPE_INTS):
			if KEY_CATS_IDS in exp2:
				catsToSave = Catagory.objects.filter(id__in=exp2[KEY_CATS_IDS])
				newExp2.categories.add(*catsToSave.all())
		else:
			if KEY_CATS_STRS in exp2:
				catsToSave = Catagory.objects.filter(category__in=exp2[KEY_CATS_STRS])
				newExp2.categories.add(*catsToSave.all())
			
	
	#TODO- rid of double saving   
	newExp2.save()
	newExp1.save()
	newExp1.translations.add(newExp2)
	newExp2.save()
	newExp1.save()
	return True 
	

def handleReqAddCat(request):
	newCat = request.POST["cat"]
	saved = insertCategory(newCat)
	if saved:
		return HttpResponse("new category saved")
	else:
		return HttpResponseServerError("new catgory failed to save, did you try to save a duplicate value?")
	
def insertCategory(categroyName):
	rs = Catagory.objects.filter(category=categroyName)
	#duplicate
	if rs:
		log("duplicate name for category, not saved")
		return False 
	cat = Catagory()
	cat.category = categroyName
	cat.save()
	return True 
	
def compareCategories(list1, list2):
	"""
	compares content of 2 lists of integers or strings representing Sets, order is not important 
	"""
	log("entering compareCategories(list1, list2)")
	log("list1=" + str(list1))
	log("list2=" + str(list2))

	if not list1 and not list2:
		return True
	if (list1 and not list2) or (list2 and not list1):
		return False
	
	list1.sort()
	list2.sort()
	if len(list1) != len(list2):
		return False
	for (elm1,elm2) in zip(list1, list2):
		if elm1 != elm2:
		#if elm1.id != elm2.id:
			return False
	return True
	
def loadCategoriesFromDB():
	"""
	loads all categories from database
	"""
	loadedCats = Catagory.objects.all()
	catList = []
	#convert to an array of strings, so it can be serielized by Json handler
	for cat in loadedCats:
		tmpElm = {}
		tmpElm["cat"] = cat.category
		tmpElm["id"] = cat.id
		catList.append(tmpElm)
	result = {"loadedCats": catList}
		
	return result
	
def handleReqLoadCategories(request):
	"""
	handles a request to load all categories by loading all categories and sending them back in reply 
	"""
	loadedList = loadCategoriesFromDB()
	return JsonResponse(loadedList, safe=False)
	

def hashPass(password):
	return pbkdf2_sha256.hash(password)
	
@csrf_exempt
def testReadObjects(request):
	log("requeat.body=")
	log(request.body)
	
	parsed = json.loads(request.body)
	log("parsed  =" + str(parsed)) 
	
	print (str(parsed["k1"]));
	print (str(parsed["k2"]));
	print (str(parsed["k3"]));
	return HttpResponse("test complete")
	

@csrf_exempt
def handleRequestNextQuestion(request):
	#TODO- extract variables from reqeust
	srcLanguageId=None
	trgLangId=None
	srcCategories=None
	uer=None
	##
	
	Q=Expression.objects.all()
	for cat in srcCategories:
		Q = Q.filter(categories__category=cat.category)
	
	

	
def saveTrxPair(exp1, exp2, catsType, langType):

	"""
	saves to database new expressions translation pair 
	the expression contain information about categories and languages that can beferredd to 
	in IDs or String values (which are unique), the last 2 parametrs indicated which fields
	are used to identify categroies and languages 
	TODO
	*implment hadling of categories lists for both new expressions 
	"""
	
	
	#just some validations 
	
	log("entering saveTrxPair(exp1, exp2....)")
	log("exp1= " + str(exp1))
	log("exp2= " + str(exp2))
	
	if not validateExpression(exp1[KEY_EXP_STR], exp1[KEY_LANG], exp1[KEY_FREQ]) or not validateExpression(exp2[KEY_EXP_STR], exp2[KEY_LANG], exp2[KEY_FREQ]):
		log("validation of new Expressions failed, aborting save")
		return False
	if not (catsType is CATS_TYPE_STRINGS or catsType is CATS_TYPE_INTS):
		log("invalid cats typs " + catsType)
		return False
	if not (langType is LANG_TYPE_STRING or langType is LANG_TYPE_INTS):
		log("invalid language typs " + langType)
		return False
	
	#if language is referred to by ID it must load successfuly. however, if it is inidicated 
	#by name, it will be checked to exist, and if it doesnt a new language will be created with the given name 
	
	#languages are referred by id- load languages
	if langType is LANG_TYPE_INTS:
		lang1Set = Language.objects.filter(id=exp1[KEY_LANG])
		if len(lang1Set) is 0:
			log("could not load language with id " + exp1[KEY_LANG])
			return False
		else:
			lang1=lang1Set[0] 
		lang1Set = Language.objects.filter(id=exp2[KEY_LANG])
		if len(lang1Set) is 0:
			log("could not load language with id " + exp2[KEY_LANG])
			return False
		else:
			lang2=lang1Set[0] 
			
	#else- refer to language by name, not id. if such a language does not yet exist, create it and save it 
	else:
		lang1Set = Language.objects.filter(language=exp1[KEY_LANG])
		if len(lang1Set) is 0:
			lang1 = Language(language=exp1[KEY_LANG])
			lang1.save()
			log("added new language exp1[KEY_LANG]")
		else:
			lang1=lang1Set[0] 
		
		lang1Set = Language.objects.filter(language=exp2[KEY_LANG])
		if len(lang1Set) is 0:
			lang2 = Language(language=exp2[KEY_LANG])
			lang2.save()
			log("added new language exp1[KEY_LANG]")
		else:
			lang2=lang1Set[0] 
	
	
	#check whether any of the categories is new. if so, create it in database. 
	#this only applies when cats are given as strings 
	if catsType is CATS_TYPE_STRINGS and KEY_CATS_STRS in exp1:
		sentCats = exp1[KEY_CATS_STRS]
		for cat in sentCats:
			q = Catagory.objects.filter(category=cat)
			if len(q) is 0:
				Catagory(category=cat).save()
	if catsType is CATS_TYPE_STRINGS and KEY_CATS_STRS in exp2:
		sentCats = exp2[KEY_CATS_STRS]
		for cat in sentCats:
			q = Catagory.objects.filter(category=cat)
			if len(q) is 0:
				Catagory(category=cat).save()
		
	
	
	
	#check whether expression already exists, requires match of language, expresson and categories (that is,
	#having the exact same set of categories)
	match= False
	
	cats1 = []
	cats2 = []
	cats1F1atted=""
	cats2F1atted=""
	
	if catsType is CATS_TYPE_STRINGS:
		if KEY_CATS_STRS in exp1:
			cats1= loadCatsId(exp1[KEY_CATS_STRS])
		if KEY_CATS_STRS in exp2:
			cats2= loadCatsId(exp2[KEY_CATS_STRS])
	else:
		cats1= exp1[KEY_CATS_IDS]
		cats2= exp2[KEY_CATS_IDS]
	
	log("cat1=" + str(cats1))
	log("cat2=" + str(cats2))


	
	if cats1:
		cats1.sort()
		cats1F1atted = json.dumps(cats1)
	else:
		cats1F1atted = ""
	if cats2:
		cats2.sort()
		cats2F1atted = json.dumps(cats2)
	else:
		cats2F1atted = ""
		
	log("cats1F1atted=" + cats1F1atted)	
	log("cats2F1atted=" + cats2F1atted)	
	
	
	
	#try to load matching expression from database  for exp1
	qSet = Expression.objects.filter(expression=exp1[KEY_EXP_STR], categories_ser=cats1F1atted, language=lang1)
	#a matching epxression exists
	if qSet:
		persistnaceExp1= qSet[0]	
	#else, create a new expression  
	else:
		log("did not match existing epxression1, creating a new instance")
		persistnaceExp1 = Expression()
		persistnaceExp1.expression  = exp1[KEY_EXP_STR]
		persistnaceExp1.language = lang1
		persistnaceExp1.frequency = exp1[KEY_FREQ]
		persistnaceExp1.save()
		persistnaceExp1.categories_ser = cats1F1atted
		
	#-----same thing for expression2 
	
	qSet = Expression.objects.filter(expression=exp2[KEY_EXP_STR], categories_ser=cats2F1atted, language=lang2)
	#a matching epxression exists
	if qSet:
		persistnaceExp2= qSet[0]	
	#else, create a new expression  
	else:
		log("did not match existing epxression1, creating a new instance")
		persistnaceExp2 = Expression()
		persistnaceExp2.expression  = exp2[KEY_EXP_STR]
		persistnaceExp2.language = lang2
		persistnaceExp2.frequency = exp2[KEY_FREQ]
		persistnaceExp2.save()
		persistnaceExp2.categories_ser = cats2F1atted
	
	#TODO- rid of double saving   
	persistnaceExp2.save()
	persistnaceExp1.save()
	persistnaceExp1.translations.add(persistnaceExp2)
	persistnaceExp2.save()
	persistnaceExp1.save()
	return True 



	
#loads from database a list of categories by their name reference 	
def loadCatsId (catsArr):
	log("entering loadCatsId, args:" + str(catsArr))
	#empts, nothing to load
	if not catsArr:
		return []
	
	inClause = "("
	for i,cat in enumerate(catsArr):
		inClause += "'" + cat + "'"
		if(i<len(catsArr) - 1):
			inClause+=","
	inClause += ")"
	query= "select id from vocab_catagory where category in " + inClause
	log("paramaterized query= " + query)
	crs = connection.cursor()
	crs.execute(query)
	rSet  = crs.fetchall()
	out = []
	for elm in rSet:
		out.append(elm[0])
	log("returning= " + str(out))
	return out
	

#serObj = json.dumps(obj)
#json.loads(serObj)



@csrf_exempt
def nextQuestion(request):
	log("entering nextQuestion()")
	log("request =" + str(request.POST))
	
	userId = None
	if KEY_SESSION_LOGGED_USER in request.session:
			userId = request.session[KEY_SESSION_LOGGED_USER]
	if userId is None:
		return HttpResponseServerError("the request requires a logged on user session")	 
	
	user=userId
	srcLang=request.POST["srcLang"]	
	trgLang=request.POST["trgLang"]
	cats=request.POST.getlist("cats[]")
	#if not empty 
	if cats:
		catsParsedInts = parseListOfInts(cats)
		catsParsedInts.sort()
		catsStr=json.dumps(catsParsedInts)
	else:
		catsStr ="" 
	
	log("extracted args from request, (serLang={srcLng},trgLang={trgLng},Cats={cats}, catsStr= {ctsStr})".format(srcLng=srcLang, trgLng=trgLang, 
		cats=str(cats), ctsStr= catsStr));
	
	
	outData = getNextQFromDb(srcLang, trgLang, userId, catsStr)
	return JsonResponse(outData, safe=False)
	#return HttpResponse("implementation under construction")	

	

#if the last char is a ']' - trim it 	
def trimSerCat(catsSer):
	if len(catsSer) > 0 and catsSer [-1] == ']':
		return catsSer[0:-1]
	return catsSer


def getNextQFromDb(srcLanguage, trgLanguage, userId, catsSer):
	
	
	catsSer=trimSerCat(catsSer)
	
	query = """
		SELECT srcExp.id as word_id, srcExp.expression as word, srcExp.frequency as frq, 
		scr.attempts as attempts, scr.successCount as correct 
	FROM 
		(vocab_expression as srcExp 
		inner join vocab_expression_translations as trx on trx.from_expression_id=srcExp.id
		inner join vocab_expression as trgExp on trx.to_expression_id=trgExp.id )
		left outer join vocab_aggrscore as scr 
		on (srcExp.id = scr.expression_id and scr.user_id = {userId} and scr.targetLanguage_id={trgLng})
	WHERE 
		srcExp.language_id={srcLngId} and srcExp.categories_ser like '{cats}' and trgExp.language_id={trgLng} 
	GROUP BY
		srcExp.id
	""".format(srcLngId=srcLanguage , cats=catsSer + '%', trgLng=trgLanguage,  userId=userId)
	
	
	#log("formatted querry={q}".format(q=query))
	
	
	crs = connection.cursor()
	crs.execute(query)
	rs= crs.fetchall()
	
	prcdResults = []
	i=0
	totalFactor=0
	while i<len(rs):
		newElm={}
		newElm['expId'] = rs[i][0]
		newElm['expStr'] = rs[i][1]
		newElm['expFreq'] = rs[i][2]
		newElm['expAttempts'] = rs[i][3]
		newElm['expCorrect'] = rs[i][4]
		factor=calcFactor(newElm, newElm['expFreq'])
		newElm['factor']=factor
		totalFactor+=factor
		prcdResults.append(newElm)
		i+=1
	#log("processed results=" + str(prcdResults))
	#log("processed results=" + toStrProcessedNextQ(prcdResults))
	 
	elm = chooseRandomWeighted(prcdResults, totalFactor)
	return elm


def chooseRandomWeighted(prcdResults, sumOfFactors):
	#this structure should allocate each candidate word a sub section of [0,1]
	#then a unified random variable will select the word to which its value belong
	spectrum=[]
	upperLimit = 0
	for wordInfo in prcdResults:
		upperLimit+= wordInfo['factor'] / sumOfFactors
		spectrum.append({'upperLimit':upperLimit, 'wordInfo':wordInfo})
	
	rnd= random.random()
	lowerLimit = 0 
	i=0
	
	#log("spectrum=" + str(spectrum))
	while i<len(spectrum):
		upperLimit = spectrum[i]['upperLimit']
		if rnd>lowerLimit and rnd <= upperLimit:
			return spectrum[i]['wordInfo']
		lowerLimit=upperLimit
		i+=1
	log("RUNTIME ERROR, spectrum search out of rang !!")

	

def toStrProcessedNextQ(elmList):
	out="[\n"
	for elm in elmList:
		out += str(elm) 
		out += "\n"
	out+="]"
	return out 
	
	

#default score to be used as if proper score records does not exist, also factored in with score record, 
#where the number of attempts is still low 	
#this value can be thought of as the ratio of correct answers to attempts that will give a similar factor 
#(so a 4/8 ratio should result similar factor to a default of  0.5 )
DEFAULT_HISTORY_FACTOR = 0.5
#the number of attempts after which the history record is fully considered (until then it is considered partially)
MAX_VALUE_FADE_IN = 8


#calculaates the total propbability factor of an expression to be chosen. the higher the value, the higher 
#the chances to get elected (ideally, a constant ration between this value and chances to get elected 
#should be aimed at) 
def calcFactor(elm, freq):
	historyFactor = computeHistoryFactor(elm)
	return historyFactor*freq
	

#calculates the total factor based on proper history record (or lack thereof)
def computeHistoryFactor(elm):
	if not elm['expAttempts']:
		return 1-DEFAULT_HISTORY_FACTOR
	fadeInFactor = computeFadeInFactor(elm['expAttempts'])
	return (1.0 - fadeInFactor) * (1 - DEFAULT_HISTORY_FACTOR) + (fadeInFactor) * (1 - 0.95*elm['expCorrect']/elm['expAttempts'])
	
#should fade away in [0,inf], 0->0, MAX_VALUE_FADE_IN > -> 1 , in between gently climb 
def computeFadeInFactor(attempts):
	if attempts >=MAX_VALUE_FADE_IN:
		return 1.0
	return attempts/MAX_VALUE_FADE_IN
	
	
	
def testRandFrequency():
	query= """
	
	select expr, freq, rnd, rnd*freq as rnd_freq  
	from (
		select exp.expression as expr, exp.frequency as freq, rand() as rnd
		from vocab_expression as exp
	) as drv 
	order by rnd_freq desc
	
	"""
	
	crs = connection.cursor()
	crs.execute(query)
	rs= crs.fetchall()
	#log("rs=" + str(rs))
	#if there is a match 
	
	if len(rs) > 0:
		expr= rs[0][0]
		freq= rs[0][1]
		nextQ = { "str":expr, "frq":freq}
	else:
		nextQ = None 
	
	#TODO- load translations! 
	outData = {"nextQ":nextQ}
	
	return outData
	
	
	

@csrf_exempt
def handleAnswer(request):
	log("entering handleAnswer(), requeset=" + str(request.POST))
	log("DEBUG- type of correct values= " + str(type(request.POST["correct"] )))
	
	
	userId=request.session[KEY_SESSION_LOGGED_USER]
	if not userId:
		return HttpResponseServerError("request cannot be proccessed without logged on user")
	srcExpId=request.POST["srcExpId"]
	targetLang=request.POST["targetLang"] 
	correct= request.POST["correct"] == '1'
	answerUpdateDb(userId, srcExpId, targetLang, correct)
	return HttpResponse("score updated")

	
def answerUpdateDb(userId, srcExpId, targetLang, correct):
	rs = AggrScore.objects.filter(user_id = userId, expression_id = srcExpId, targetLanguage_id = targetLang)
	score = None
	inc=0
	#no record for this (expression,targetLang,User) yet, this is the first one
	if correct:
			inc=1
	if not rs:
		score=AggrScore()
		score.user_id=userId
		score.expression_id=srcExpId
		score.targetLanguage_id=targetLang
		score.attempts=1
		score.successCount=inc
		score.attempts=1
	else:
		score=rs[0]
		score.successCount+=inc
		score.attempts+=1
	log("saving updated score obj:" + str(score))
	score.save()
	

@csrf_exempt
def handLoadTranslations(request):
	rs= loadTranslations(request.POST['expId'], request.POST['trgLang'])
	return JsonResponse(rs, safe=False)

def loadTranslations(expId, trgLng):
	q = """
		SELECT  
		trgExp.id, trgExp.expression
	FROM 
		vocab_expression_translations as trx
		join vocab_expression as srcExp on trx.from_expression_id=srcExp.id
		join vocab_expression as trgExp on trx.to_expression_id=trgExp.id
	WHERE 
		srcExp.id={srcExpI} and trgExp.language_id={lngId}
	""".format(srcExpI=expId, lngId=trgLng)
	
	crs = connection.cursor()
	crs.execute(q)
	rs= crs.fetchall()
	log("DEBUG-- rs=" + str(rs))
	return rs
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	