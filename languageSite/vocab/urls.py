from django.urls import path

from . import views

urlpatterns = [
   
	path('client', views.client, name='client'),
	path('add-language', views.addLanguage, name='addLanguage'),
	path('load-languages', views.loadLanguages, name='loadLanguages'), 
	path('add-expression', views.addExpression, name='addExpression'), 
	path('add-expressions-full', views.addExpressionFull, name='addExpressionFull'),
	path('register-user', views.registerUser, name='registerUser'), 
	path('get-logon-status', views.getLogOnStatus, name='getLogonStatus'),
	path('log-user-on', views.logUserOn, name='logUserOn'), 
	path('log-user-off', views.logUserOff, name='logUserOff'),
	path('add-cat', views.handleReqAddCat, name='addCat'),
	path('load-cats', views.handleReqLoadCategories, name='loadCats'),
	path('upload-translations-batch', views.uploadTranslationsBatch, name='uploadTrxBatch'), 
	path('test-read-objects', views.testReadObjects, name='testReadObjects'),
	path('next-question', views.nextQuestion, name='nextQuestion')

	
]