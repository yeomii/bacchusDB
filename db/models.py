from django.db import models
from group.models import Group, Private_Group, Membership
import json

# Create your models here.
class DataBaseManager(models.Manager):
	def create_database(self, dbname, dbgroup, dbtype, dbinfo):
		preset = []
		for i in range(11):
			preset.append('')
		db = self.create(name=dbname, group=dbgroup, rownum=10, columnnum=10, info=dbinfo, dbtype=dbtype, preset=json.dumps(preset))
		rows = []
		cols = []
		for i in range(db.rownum):
			rows.append (Row.objects.create_row(rownum=i, db=db))
		for i in range(db.columnnum):
			cols.append (Column.objects.create_col(colnum=i, db=db))
		for i in rows:
			for j in cols:
				Cell.objects.create_cell(col=j, row=i)
		return db

class DataBase(models.Model):
	name = models.CharField(max_length=50)
	private = models.BooleanField()
	group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
	p_group = models.ForeignKey(Private_Group, null=True, on_delete=models.CASCADE)
	dbtype = models.CharField(max_length=10)
	info = models.TextField()
	rownum = models.IntegerField()
	columnnum = models.IntegerField()
	preset = models.TextField()
	objects = DataBaseManager()

	class Meta:
		unique_together = ('name', 'group')
	def __unicode__(self):
		return self.name
	def rowExpand(self, num):
		rows = []
		cols = Column.objects.filter(coldb=self)
		for i in range(self.rownum, (self.rownum + num)):
			rows.append(Row.objects.create_row(rownum=i, db=self))
		for i in rows:
			for j in cols:
				Cell.objects.create_cell(col=j, row=i)
		self.rownum += num
		self.save()
		return self
	def colExpand(self, num):
		cols = []
		rows = Row.objects.filter(rowdb=self)
		for i in range(self.columnnum, (self.columnnum + num)):
                        cols.append(Column.objects.create_col(colnum=i, db=self))
		for i in rows:
                        for j in cols:
                                Cell.objects.create_cell(col=j, row=i)
                self.columnnum += num
                self.save()
                return self
	def rowDelete(self, num):
		row = Row.objects.get(rowdb=self, rownum=num)
		rows = Row.objects.filter(rowdb=self, rownum__gt=num)
		for r in rows:
			cells = Cell.objects.filter(cellrow=r)
			r.rownum -= 1
			for c in cells:
				c.rownum -= 1
				c.save()
			r.save()
	
		row.delete()
		self.rownum -= 1
		self.save()
		return self
class RowManager(models.Manager):
	def create_row(self, rownum, db):
		row = self.create(rownum=rownum, rowdb=db)
		return row

class Row(models.Model):
	rownum = models.IntegerField()
	rowdb = models.ForeignKey(DataBase, on_delete=models.CASCADE)
	objects = RowManager()
	def __unicode__(self):
		return str(self.rownum)
	def introw(self):
		cell = Cell.objects.filter(cellrow=self)
		t = True
                for c in cell:
                        t = t and (not cell.ctype)
                return t
	
class ColumnManager(models.Manager):
	def create_col(self, colnum, db):
		col = self.create(colnum=colnum, coldb=db)
		return col

class Column(models.Model):
	colnum = models.IntegerField()
	coldb = models.ForeignKey(DataBase, on_delete=models.CASCADE)
	objects = ColumnManager()
        def __unicode__(self):
                return str(self.colnum)
	def intcolumn(self):
		cell = Cell.objects.filter(cellcol=self)
		t = True
		for c in cell:
			t = t and (not cell.ctype)
		return t

class CellManager(models.Manager):
	def create_cell(self, row, col):
		cell = self.create(cellcol=col, cellrow=row, colnum=col.colnum, rownum=row.rownum)
		return cell

class Cell(models.Model):
	contents = models.CharField(max_length=100, blank=True)
	ctype = models.BooleanField(default=True) # true indicates string content
	editable = models.BooleanField(default=True)
	rownum = models.IntegerField()
	colnum = models.IntegerField()
	cellrow = models.ForeignKey(Row, on_delete=models.CASCADE)
	cellcol = models.ForeignKey(Column, on_delete=models.CASCADE)
	objects = CellManager()
	def __unicode__(self):
		return str(self.rownum) +'-'+str(self.colnum)
        def modify_cell(self, content):
		def isNumber(s):
               	 	try:
                 	       	float(s)
                 	       	return True
                	except ValueError:
                        	return False
                self.contents = content
                if isNumber(content):
                        self.ctype = False
                else:
                        self.ctype = True
		self.save()




