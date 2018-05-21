from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError

import json



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
		HttpResponseServerError("expression failed to save")	
		
		
	
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
	
	

	
def saveTrxPair(languageId1, expression1, categories1, languageId2, expression2, categories2):
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
		
	newExp1 = Expression()
	newExp1.expression  = expression1
	newExp1.language = loadedLanguage1
	
	newExp2 = Expression()
	newExp2.expression  = expression2
	newExp2.language = loadedLanguage2
	newExp2.save()
	newExp1.save()
	newExp1.translations.add(newExp2)
	newExp2.save()
	newExp1.save()
	return True 
	
	
	
	
	