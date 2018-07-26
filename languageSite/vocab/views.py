from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language, User

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError

from django.db import IntegrityError

#from passlib.apps import custom_app_context as pwd_context

from passlib.hash import pbkdf2_sha256

import json




KEY_SESSION_LOGGED_USER = "loggedUser"
ERROR_CODE_NO_SUCH_USER = 5001
ERROR_CODE_PASSWORD_DONT_MATCH = 5002


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
	languageId = request.POST["languageID1"]
	expression = request.POST["expression1"]
	languageId2 = request.POST["languageID2"]
	expression2 = request.POST["expression2"]
	saved = saveTrxPair(languageId, expression, None, languageId2, expression2, None)
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
	

def validateExpression(expression, languageId, categoriesIds):
	return expression is not None and languageId is not None 
	
	

	
def saveTrxPair(languageId1, expression1, freq1, categories1, languageId2, expression2, freq2, categories2):
	"""
	saves to database new expressions translation pair 
	
	TODO
	*implment hadling of categories lists for both new expressions 
	"""
	
	if not validateExpression(expression1, languageId1, categories1) or not validateExpression(expression2, languageId2, categories2):
		return False
	
	#load languages
	loadedLanguage1 = Language.objects.get(id=languageId1)
	if loadedLanguage1 is None:
		return False
	
	loadedLanguage2 = Language.objects.get(id=languageId2)
	if loadedLanguage2 is None:
		return False
		
	
	qSet = Expression.objects.filter(expression=expression1, language=loadedLanguage1)
	if qSet:
		newExp1 = qSet[0]
	else:
		newExp1 = Expression()
		newExp1.expression  = expression1
		newExp1.language = loadedLanguage1
		newExp1.frequency = freq1
	
	qSet = Expression.objects.filter(expression=expression2, language=loadedLanguage2)
	if qSet:
		newExp2 = qSet[0]
	else:
		newExp2 = Expression()
		newExp2.expression  = expression2
		newExp2.language = loadedLanguage2
		newExp2.frequency = freq2
	
	#TODO- rid of double saving   
	newExp2.save()
	newExp1.save()
	newExp1.translations.add(newExp2)
	newExp2.save()
	newExp1.save()
	return True 
	

def hashPass(password):
	return pbkdf2_sha256.hash(password)
	
	