from django.db import models
from group.models import Group, Membership


# Create your models here.

class DataBaseManager(models.Manager):
	def create_database(self, dbname, dbgroup):
		db = self.create(name=dbname, group=dbgroup, rownum=10, columnnum=10)
		for i in range(db.rownum):
			Row.objects.create_row(cellnum=db.columnnum, rownum=i, db=db)
		return db

class DataBase(models.Model):
	name = models.CharField(max_length=50, unique=True)
	group = models.ForeignKey(Group)
	rownum = models.IntegerField()
	columnnum = models.IntegerField()
	objects = DataBaseManager()
	def __unicode__(self):
		return self.name

class RowManager(models.Manager):
	def create_row(self, cellnum, rownum, db):
		row = self.create(rownum=rownum, rowdb=db)
		for i in range(cellnum):
			Cell.objects.create_cell(row=row, num=i)
		return row

class Row(models.Model):
	rownum = models.IntegerField()
	rowdb = models.ForeignKey(DataBase)
	objects = RowManager()
	def __unicode__(self):
		return str(self.rownum)

class CellManager(models.Manager):
	def create_cell(self, row, num):
		cell = self.create(cellnum=num, cellrow=row)
		return cell
	def isNumber(s):
  		try:
    			float(s)
			return True
  		except ValueError:
    			return False
	def modify_cell(self, content):
		self.contents = content
		if isNumber(content):
			self.ctype = False
		else:
			self.ctype = True

class Cell(models.Model):
	contents = models.CharField(max_length=100, null=True, blank=True)
	ctype = models.BooleanField(default=True) # true indicates string content
	cellnum = models.IntegerField() # nth cell in row
	cellrow = models.ForeignKey(Row)
	objects = CellManager()
	def __unicode__(self):
		return str(self.cellnum)
