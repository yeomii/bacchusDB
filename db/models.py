#-*- coding: utf-8 -*-
from django.db import models
from group.models import Group, Private_Group, Membership
import json
from datetime import datetime

# Create your models here.
class DataBaseManager(models.Manager):
	def create_database(self, dbname, dbgroup, dbtype, dbinfo, private, col_preset):
		if dbtype == "회계장부".decode('utf-8'):
			preset = ['', '지출/수입', '날짜', '금액', '누계', '', '', '', '', '', '']
		elif dbtype == "주소록".decode('utf-8'):
			preset = ['', '이름', '주소', '기록 날짜', '', '', '', '', '', '', '']
		elif dbtype == "도서장부".decode('utf-8'):
			preset = ['', '도서명', '저자', '대여자', '대출 날짜', '반납 날짜', '', '', '', '', '']
		elif dbtype == "연락처".decode('utf-8'):
			preset = ['', '이름', '집전화', '휴대전화', '기록 날짜', '', '', '', '', '', '']
		else:
			preset = ['']
			for c in col_preset:
				preset.append(c)	
			for i in range(11-len(preset)):
				preset.append('')
		size = [30]
		for i in range(10):
			size.append(100)


		if not private:
			db = self.create(name=dbname, group=dbgroup, rownum=10, columnnum=10, info=dbinfo, dbtype=dbtype, preset=json.dumps(preset), col_size=json.dumps(size))
		else:
			db = self.create(name=dbname, p_group=dbgroup, rownum=10, columnnum=10, info=dbinfo, dbtype=dbtype, preset=json.dumps(preset), col_size=json.dumps(size))
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
	col_size = models.TextField()
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
	def addRow(self, num):
		rows = Row.objects.filter(rowdb=self, rownum__gte=num)
		for row in rows:
			cells = Cell.objects.filter(cellrow=row)
			for cell in cells:
				cell.rownum += 1
				cell.save()
			row.rownum += 1
			row.save()

		r = Row.objects.create_row(rownum=num, db=self)
		for col in Column.objects.filter(coldb=self):
			Cell.objects.create_cell(col=col, row=r)
		self.rownum += 1
		self.save()
		return self
		
	def addColumn(self, num):
		cols = Column.objects.filter(coldb=self, colnum__gte=num)
		for col in cols:
			cells = Cell.objects.filter(cellcol=col)
			for cell in cells:
				cell.colnum += 1
				cell.save()
			col.colnum += 1
			col.save()

		c = Column.objects.create_col(colnum=num, db=self)
		for row in Row.objects.filter(rowdb=self):
			Cell.objects.create_cell(col=c, row=row)
		
		preset = json.loads(self.preset)
		preset.insert(num+1, '')
		size = json.loads(self.col_size)
		size.insert(num+1, 120)
		self.preset = json.dumps(preset)
		self.col_size = json.dumps(size)
		self.columnnum += 1
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

	def colDelete(self, num):
		col = Column.objects.get(coldb=self, colnum=num)
		cols = Column.objects.filter(coldb=self, colnum__gt=num)
		for cl in cols:
			cells = Cell.objects.filter(cellcol=cl)
			cl.colnum -= 1
			for c in cells:
				c.colnum -= 1
				c.save()
			cl.save()
		col.delete()
		self.columnnum -= 1
		col_size = json.loads(self.col_size)
		del col_size[num+1]
		self.col_size = json.dumps(col_size)
		preset = json.loads(self.preset)
		del preset[num+1]
		self.preset = json.dumps(preset)
		self.save()
		return self
	def colSort(self, num, direction):
		col = Column.objects.get(coldb=self, colnum=num)
		cells = Cell.objects.filter(cellcol=col).exclude(contents='').order_by('contents')
		nums = []
		for c in cells:
			nums.append(c.rownum)
		nums.sort(reverse=direction)
		numcell = filter(lambda x: x.ctype==True, cells)
		if numcell == [] :
			cells = sorted(cells,key= lambda x: x.intContents())
		for i in range(len(nums)):
			row = cells[i].cellrow
			row.changeNum(nums[i])
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
	def changeNum(self, num):
		cell = Cell.objects.filter(cellrow=self)
		for c in cell:
			c.rownum = num
			c.save()
		self.rownum = num
		self.save()
		return self
	
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
	def intContents(self):
		if self.contents == '':
			return float('0')
		else: 
			return float(self.contents)

