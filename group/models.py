from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Group(models.Model):
	title = models.CharField(max_length=30, unique=True)
	info = models.TextField()
	user = models.ManyToManyField(User, through='Membership')
	num_member = models.IntegerField()

class Private_Group(models.Model):
	title = models.CharField(max_length=30)
	info = models.TextField()
	user = models.ForeignKey(User)

	class Meta:
		unique_together = ('user', 'title')

class Membership(models.Model):
	USER_TYPE = (
			(0, 'admin'),
			(1, 'normal')
	)

	user = models.ForeignKey(User)
	group = models.ForeignKey(Group)
	date_joined = models.DateField(auto_now_add=True)
	status = models.IntegerField(choices=USER_TYPE)

class Admission(models.Model):
	TYPE = (
		(0, 'waiting'),
		(1, 'accepted'),
		(2, 'denied')
	)

	user = models.ForeignKey(User)
	group = models.ForeignKey(Group)
	message = models.CharField(max_length=50)
	status = models.IntegerField(choices=TYPE)

	class Meta:
		unique_together = ('user', 'group')		
