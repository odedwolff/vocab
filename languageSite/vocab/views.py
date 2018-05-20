from django.shortcuts import render

from django.http import JsonResponse

from .models import Expression, Language

from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.


from django.http import HttpResponse


def index(request):
	return HttpResponse("Hello, world. You're at the vocab index.")
	

def client (request):
	return render(request, 'vocab/client.html')
	
def ajaxTest(request):
	return render(request, 'vocab/ajaxTester.html')
	

def ajaxTestRequest1(request):
	dict = loadExpressionsTest()
	return JsonResponse(dict, safe=False)

	
#@csrf_exempt	
def addLanguage(request):
	lang = request.POST["lang"]
	print("lang=")
	print(lang)
	saveNewLanguage(lang)
	return HttpResponse("lnaguage saved")	


def addExpression(request):
	languageId = request.POST["languageID"]
	expression = request.POST["expression"]
	#TODO handle argument categories list
	saved = saveExpression(expression, languageId, None )
	if saved:
		return HttpResponse("expression saved")	
	else:
		#todo - add details to failure message 
		return HttpResponse("expression failed to save")	

		

#todo - add category lists for both expressions		
def addExpressionFull(request):
	
	languageId = request.POST["languageID1"]
	expression = request.POST["expression1"]
	languageId2 = request.POST["languageID2"]
	expression2 = request.POST["expression2"]
	
	saved = saveTrxPair(languageId, expression, None, languageId2, expression2, None)
	if saved:
		return HttpResponse("expressions pair saved")	
	else:
		#todo - add details to failure message 
		return HttpResponse("expression failed to save")	
	
		
	
def loadLanguages (request):	
	dict = loadLanguagesDB()
	return JsonResponse(dict, safe=False)
	#return HttpResponse(json.dumps(dict), content_type="application/json")
	
def loadLanguagesDB ():
	
	list = []
	tmpElm = {}
	loadedLang = Language.objects.all()
	for lang in loadedLang:
		tmpElm = {}
		tmpElm["lang"] = lang.language
		tmpElm["id"] = lang.id
		list.append(tmpElm)
	#jsonExps = json.dumps(list)
	result = {"loadedLangs": list}	
	print (list)
	return result 
	
def loadExpressionsTest():
	exps = []
	loadedExp = Expression.objects.all()
	for exp in loadedExp:
		exps.append(exp.expression)
	jsonExps = json.dumps(exps)
	result = {"loadedExpressions": jsonExps}
	return result 
	
def saveNewLanguage(languageName):
	lang = Language(language = languageName)
	lang.save()
	

#tries to save new expression, returns whether expression saved successfully 
def saveExpression (expression, languageId, categoriesIds):
	if not validateExpression(expression, languageId, categoriesIds):
		return False	
	newExp = Expression()
	newExp.expression  = expression
	#newExp.language = languageId
	
	ldLanguage = Language.objects.get(id=languageId)
	if ldLanguage is None:
		print ("failed to load language language with id " + languageId)
		return False
	
	newExp.language = ldLanguage
	
	if categoriesIds is not None:
		for cat in categoriesIds:
			newExp.categories.append(cat)
	try:
		newExp.save()
	except :
		print("Unexpected error:", sys.exc_info()[0])
		return False 
	return True 
	
def validateExpression(expression, languageId, categoriesIds):
	return expression is not None and languageId is not None 
	
	

#todo- handle category lists for both expressions 	
def saveTrxPair(languageId1, expression1, categories1, languageId2, expression2, categories2):
	if not validateExpression(expression1, languageId1, categories1) or not validateExpression(expression2, languageId2, categories2):
		return False
	
	#load languages
	loadedLanguage1 = Language.objects.get(id=languageId1)
	if loadedLanguage1 is None:
		print ("failed to load language language with id " + languageId1)
		return False
	
	loadedLanguage2 = Language.objects.get(id=languageId2)
	if loadedLanguage2 is None:
		print ("failed to load language language with id " + languageId2)
		return False
		
	newExp1 = Expression()
	newExp1.expression  = expression1
	newExp1.language = loadedLanguage1
	
	newExp2 = Expression()
	newExp2.expression  = expression2
	newExp2.language = loadedLanguage2
	
	
	#todo- should i add the many to many only on one side?? 
	#try:
	newExp2.save()
	newExp1.save()
	newExp1.translations.add(newExp2)
	newExp2.save()
	newExp1.save()
		
		
	#except :
	#	print("Unexpected error:", sys.exc_info()[0])
	#	return False 

	return True 
	
	
	
	
	