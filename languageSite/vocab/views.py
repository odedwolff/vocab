from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language, User, Catagory

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError

from django.db import IntegrityError


from passlib.hash import pbkdf2_sha256

import json

import pprint 

from django.views.decorators.csrf import csrf_exempt




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

def log(msg, imortance = 0):
	print(msg)


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
	exp1[KEY_CATS_IDS]= request.POST.getlist("cats1[]")
	exp2 = {}
	exp2[KEY_LANG] = request.POST["languageID2"]
	exp2[KEY_EXP_STR] = request.POST["expression2"]
	exp2[KEY_FREQ]=request.POST["weight2"]
	exp2[KEY_CATS_IDS]= request.POST.getlist("cats2[]")
	
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
	
	
	