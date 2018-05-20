from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajaxtest', views.ajaxTest, name='ajaxTest'),
	path('ajax-test-request-1', views.ajaxTestRequest1, name='ajaxTestRequest1'),
	path('client', views.client, name='client'),
	path('add-language', views.addLanguage, name='addLanguage'),
	path('load-languages', views.loadLanguages, name='loadLanguages'), 
	path('add-expression', views.addExpression, name='addExpression'), 
	path('add-expressions-full', views.addExpressionFull, name='addExpressionFull')
	
]