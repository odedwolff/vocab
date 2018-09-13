from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language, User, Catagory

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError

from django.db import IntegrityError

#from passlib.apps import custom_app_context as pwd_context

from passlib.hash import pbkdf2_sha256

import json




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
	
	#saved = saveTrxPair(languageId, expression, frq1, cats1, languageId2, expression2, frq2, cats2)
	
	saved = saveTrxPair(exp1, exp2, CATS_TYPE_INTS)
	
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
	userId = request.session[KEY_SESSION_LOGGED_USER]
	#username = False
	#isLogged = "False"
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
	
	

	
#def saveTrxPair(languageId1, expression1, freq1, cats1, languageId2, expression2, freq2, cats2):


def extractCatIds (cats):
	log("entering extractCatIds, arg cats=" + str(cats))
	theResult = []
	if not cats or len(cats) is 0:
		return theResult
	for cat in cats:
		theResult.append(cat.id)
	return theResult

def extractCatStrings  (cats):
	log("entering extractCatStrings, arg cats=" + str(cats))
	theResult = []
	if not cats or len(cats) is 0:
		return theResult
	for cat in cats:
		theResult.append(cat.category)
	return theResult

def saveTrxPair(exp1, exp2, catsType):

	"""
	saves to database new expressions translation pair 
	
	TODO
	*implment hadling of categories lists for both new expressions 
	"""
	
	if not validateExpression(exp1[KEY_EXP_STR], exp1[KEY_LANG], exp1[KEY_FREQ]) or not validateExpression(exp2[KEY_EXP_STR], exp2[KEY_LANG], exp2[KEY_FREQ]):
		log("validation of new Expressions failed, aborting save")
		return False
	
	if not (catsType is CATS_TYPE_INTS or catsType is CATS_TYPE_INTS):
		log("invalid cats typs " + catsType)
		return False
	
	#load languages
	
	loadedLanguage1 = Language.objects.get(id=exp1[KEY_LANG])
	if loadedLanguage1 is None:
		log("could not load language with id " + exp1[KEY_LANG])
		return False
	
	loadedLanguage2 = Language.objects.get(id=exp2[KEY_LANG])
	if loadedLanguage2 is None:
		log("could not load language with id " + exp2[KEY_LANG])
		return False
	
	#check whether expression already exists, requires match of language, expresson and categories (that is,
	#having the exact same set of categories)
	match= False
	qSet = Expression.objects.filter(expression=exp1[KEY_EXP_STR], language=loadedLanguage1)
	#qSet = Expression.objects.filter(expression=exp1[KEY_EXP_STR], language__id=exp1[KEY_LANG])
	
	log("iterating loaded expressions")
	if qSet:
		#newExp1 = qSet[0]
		for loadedExp in qSet:
			log("loaded Expression: " + str(loadedExp))
			if(catsType is CATS_TYPE_INTS):
				#loadedCats = extractCatIds(loadedExp.categories)
				loadedCats = extractCatIds(loadedExp.categories.all())
			else:
				loadedCats = extractCatStrings(loadedExp.categories)
		
			if	compareCategories(exp1[KEY_CATS_IDS], loadedCats):
				newExp1= loadedExp
				match= True
				log("matched existing epxression1")
				break 

	#else:
	if not match:
		log("did not match existing epxression1, creating a new instance")
		newExp1 = Expression()
		newExp1.expression  = exp1[KEY_EXP_STR]
		newExp1.language = loadedLanguage1
		newExp1.frequency = exp1[KEY_FREQ]
		
	match= False
	qSet = Expression.objects.filter(expression=exp2[KEY_EXP_STR], language=loadedLanguage2)
	#qSet = Expression.objects.filter(expression=exp2[KEY_EXP_STR], language__id=exp2[KEY_LANG])
	
	if qSet:
		#newExp1 = qSet[0]
		for loadedExp in qSet:	
			if(catsType is CATS_TYPE_INTS):
				loadedCats = extractCatIds(loadedExp.categories)
			else:
				loadedCats = extractCatStrings(loadedExp.categories)
			if	compareCategories(exp2[KEY_CATS_IDS], loadedExp.categories):
				newExp2= loadedExp
				match= True
				log("matched existing epxression2")
				
	#else:
	if not match:
		log("did not match existing epxression2, creating a new instance")
		newExp2 = Expression()
		newExp2.expression  = exp2[KEY_EXP_STR]
		newExp2.language = loadedLanguage1
		newExp2.frequency = exp2[KEY_FREQ]
	
	
	#TODO- rid of double saving   
	newExp2.save()
	newExp1.save()
	newExp1.translations.add(newExp2)
	newExp2.save()
	newExp1.save()
	return True 
	

def handleReqAddCat(request):
	newCat = request.POST["cat"]
	insertCategory(newCat)
	return HttpResponse("new category saved")
	
def insertCategory(categroyName):
	cat = Catagory()
	cat.category = categroyName
	cat.save()
	
def compareCategories(list1, list2):
	"""
	compares content of 2 lists of integers or strings representing Sets, order is not important 
	"""
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
	
	