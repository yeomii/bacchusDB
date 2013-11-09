from django.db import models
from group.models import Group, Membership

# Create your models here.
class Group_db(models.Model):
	title = models.CharField(max_length=30)
	type = models.CharField(max_length=10)
	info = models.TextField()
	group = models.ForeignKey(Group)
	content = models.TextField()

	class Meta:
		unique_together = ('title', 'group')
