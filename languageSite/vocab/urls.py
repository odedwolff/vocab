from django.urls import path

from . import views

urlpatterns = [
   
	path('client', views.client, name='client'),
	path('add-language', views.addLanguage, name='addLanguage'),
	path('load-languages', views.loadLanguages, name='loadLanguages'), 
	path('add-expression', views.addExpression, name='addExpression'), 
	path('add-expressions-full', views.addExpressionFull, name='addExpressionFull'),
	path('register-user', views.registerUser, name='registerUser'), 
	
]