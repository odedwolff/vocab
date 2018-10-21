from django.db import models

# Create your models here.

from django.db import models

class User(models.Model):
	#the user name, also the login name 
	name = models.CharField(max_length=200, unique=True)
	
	#hash value of user's password
	passHash =  models.CharField(max_length=200, null = True)
	
	
	def __str__(self):
		return self.name
		
	
	
	
class Language(models.Model):
	language = models.CharField(max_length=200)
	
	def __str__(self):
		return self.language
	
class Catagory(models.Model):
	category = models.CharField(max_length=200, unique=True)
	
	def __str__(self):
		return self.category
	
	
class Expression(models.Model):
	expression = models.CharField(max_length=1000, null=True)
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	frequency = models.FloatField()
	#expression = models.ForeignKey(Expression, on_delete=models.CASCADE)
	translations = models.ManyToManyField("self")
	categories = models.ManyToManyField(Catagory)
	
	def __str__(self):
		return self.expression






class AnswerAttempt(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	sourceExpression = models.ForeignKey(Expression, on_delete=models.CASCADE)
	targetLanguage = models.ForeignKey(Language, on_delete=models.CASCADE)
	date = models.DateTimeField(default=None, blank=True, null=True)
	correct = models.NullBooleanField()
	
	def __str__(self):
		return ("User,Expression,Language=" + str(self.user)+"," + str(self.sourceExpression)+","+str(self.targetLanguage))



class AggrScore(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	expression = models.ForeignKey(Expression, on_delete=models.CASCADE)
	targetLanguage = models.ForeignKey(Language, on_delete=models.CASCADE)
	attempts = models.IntegerField()
	successCount = models.IntegerField()
	

	
"""

		
#represents history of anwering attempts for scepcific (user, source word, target language). 
class StatPoint(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	srouce_Expression =  models.ForeignKey(Expression, on_delete=models.CASCADE)
	target_Language = models.ForeignKey(Language, on_delete=models.CASCADE)
	
	 
class AttemptsHistory (models.Model):
	statPoint = models.ForeignKey(StatPoint, on_delete=models.CASCADE)
	
class Attempt(models.Model):
	date = models.DateTimeField()
	correct = models.NullBooleanField()
	attemptsList = models.ForeignKey(AttemptsHistory, on_delete=models.CASCADE)
	
	
"""

	
