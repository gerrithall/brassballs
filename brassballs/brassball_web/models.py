from django.db import models
from django.contrib.auth.models import User
class UserDetails(models.Model):
	pic_url = models.TextField()
	user = models.ForeignKey(User, unique=True)
	money = models.FloatField()
	email = models.TextField()
	credit = models.IntegerField()

class UserMatch(models.Model):
	date_logged = models.DateTimeField('date logged', auto_now_add=True)
	user = models.ForeignKey(User, unique=False)
	user2 = models.ForeignKey(User, unique=False)
	active = models.IntegerField() 
	matchback_id = models.IntegerField()
	money = models.FloatField()
	date_closed = models.DateTimeField('date closed')
	
class Vote(models.Model):
	usermatch = models.ForeignKey(UserMatch, unique=False)
	vote = models.TextField()
	vote_date = models.DateTimeField('date published', auto_now_add=True )


class PayPal(models.Model):
	money = models.FloatField()
	date_logged = models.DateTimeField('date logged', auto_now_add=True)
	user = models.ForeignKey(User, unique=False)	

class RateLog(models.Model):
	date_logged = models.DateTimeField('date logged', auto_now_add=True)
	total_money = models.FloatField()
	headcount = models.IntegerField()
	effective_rate = models.FloatField()
	

class EmailLog(models.Model):
	date_sent = models.DateTimeField('date sent', auto_now_add=True)
	recipient = models.TextField()
	message = models.TextField()
