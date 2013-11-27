#-*- coding: utf-8 -*-
from bacchusdb import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from group.models import Group, Private_Group, Membership
from db.models import DataBase, Row, Column, Cell
import json
import re

def db_name_validation(name):
	if not bool(re.search('\S+', name)):
		return True
	else:
		name = re.sub(" ", "", name)
		name = name.encode('utf-8')
		return bool(re.search('[^\wㄱ-ㅎㅏ-ㅣ가-힣]+', name))


@csrf_exempt
@login_required
def db_make(request, group_title):
	if request.method=="POST":
		data = {}
		title = request.POST['db_name']
		dbtype = request.POST['db_type']
		info = request.POST['db_info']
		col = request.POST.getlist('col')
		url = request.path.split("/")

		if (db_name_validation(title)):
			data['error'] = "Restriction"

		elif url[1] == "group":
			try: 
				group = Group.objects.get(title=group_title)
				db = DataBase.objects.get(name=title, group=group)
				data['error'] = "Exist"

			except ObjectDoesNotExist:
				db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info, private=False, col_preset=col)
				db.save()
				data['success'] = "Success"

		elif url[1] == "p_group":
			try:
				group = Private_Group.objects.get(title=group_title, user=request.user)
				db = DataBase.objects.get(name=title, p_group=group)
				data['error'] = "Exist"
				
			except ObjectDoesNotExist:			
				db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info, private=True, col_preset=col)
				db.save()
				data['success'] = "Success"

		return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		return render_to_response('db/db_make.html', RequestContext(request, {'u': request.user, 'css': 'db_make'}))

@csrf_exempt
@login_required
def db_page(request, g_title, dbname):
	if request.method == "POST" and request.is_ajax() and 'cell' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		row = Row.objects.get(rowdb=db, rownum=int(request.POST['row']))
		cell = Cell.objects.get(cellrow=row, colnum=request.POST['col'])
		cell.modify_cell(request.POST['content'])
		return HttpResponse('')
	elif request.method == "POST" and request.is_ajax() and 'total' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		
		row = Row.objects.get(rowdb=db, rownum=int(request.POST['row']))
		cell = Cell.objects.get(cellrow=row, colnum=request.POST['col'])
		cell.modify_cell(request.POST['content'])
		preset = json.loads(db.preset)
		colnum = int(request.POST['col'])
		try:
			moneyi=preset.index('금액'.decode('utf-8')) - 1
			if (colnum != moneyi):
				return HttpResponse('')
			totali=preset.index('누계'.decode('utf-8')) - 1
			moneycol = Column.objects.get(coldb=db, colnum=moneyi)
			totalcol = Column.objects.get(coldb=db, colnum=totali)
			mcs = Cell.objects.filter(cellcol=moneycol).order_by('rownum')
			tcs = Cell.objects.filter(cellcol=totalcol).order_by('rownum')
			tcs[0].modify_cell(mcs[0].contents)
			for i in range(1,db.rownum):
				 if mcs[i].ctype == False and tcs[i-1].ctype == False:
					m = int(mcs[i].contents)
					t = int(tcs[i-1].contents)
					sumc = m+t
					tcs[i].modify_cell(str(sumc))		
		except ValueError:
			return HttpResponse('')
			
		rows = Row.objects.filter(rowdb=db).order_by('rownum')
		size = json.loads(db.col_size)
                preset = zip(preset, size)
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
	
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})

		return HttpResponse(t.render(c))
		
	elif request.method == "POST" and request.is_ajax() and 'col' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		preset = json.loads(db.preset)
		preset[int(request.POST['num'])+1] = request.POST['content']
		db.preset = json.dumps(preset)
		db.save()

		return HttpResponse('')

	elif request.method == "POST" and request.is_ajax() and 'add_row' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		db.rowExpand(int(request.POST['add_row']))
	
		rows = Row.objects.filter(rowdb=db).order_by('rownum')

		preset = json.loads(db.preset)	
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})
		return HttpResponse(t.render(c))

	elif request.method == "POST" and request.is_ajax() and 'del_row[]' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		for row in request.POST.getlist('del_row[]'):
			db.rowDelete(int(row))

		rows = Row.objects.filter(rowdb=db).order_by('rownum')

		preset = json.loads(db.preset)	
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})
		return HttpResponse(t.render(c))

	elif request.method == "POST" and request.is_ajax() and 'del_col[]' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		for col in request.POST.getlist('del_col[]'):
			db.colDelete(int(col.split("col")[1]))
		cols = Column.objects.filter(coldb=db).order_by('colnum')
		preset = json.loads(db.preset)
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = []
		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))

		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset' : preset, 'col_num' : range(0, db.columnnum+1), 'db': db, 'cells': cells})
		return HttpResponse(t.render(c))

	elif request.method == "POST" and request.is_ajax() and 'add_col' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		if (request.POST['direction'] == 'left'):
			col = request.POST['add_col']
			db.addColumn(int(col.split("col")[1]))
		else:
			col = request.POST['add_col']
			db.addColumn(int(col.split("col")[1])+1)

		rows = Row.objects.filter(rowdb=db).order_by('rownum')

		preset = json.loads(db.preset)
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
	
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})

		return HttpResponse(t.render(c))
	
	elif request.method == "POST" and request.is_ajax() and 'sort_col' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		col = request.POST['sort_col']
		if (request.POST['direction'] == 'A-Z'):
			db.colSort(int(col.split("col")[1]),False)
		else:
			db.colSort(int(col.split("col")[1]),True)
		rows = Row.objects.filter(rowdb=db).order_by('rownum')
		preset = json.loads(db.preset)
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = []
		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})

		return HttpResponse(t.render(c))	

	elif request.method == "POST" and request.is_ajax() and 'add_row_d' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		if (request.POST['direction'] == 'up'):
			row = request.POST['add_row_d']
			db.addRow(int(row))
		else:
			row = request.POST['add_row_d']
			db.addRow(int(row)+1)

		rows = Row.objects.filter(rowdb=db).order_by('rownum')

		preset = json.loads(db.preset)	
		size = json.loads(db.col_size)
		preset = zip(preset, size)
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
	
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})
		return HttpResponse(t.render(c))


	else:
		url = request.path.split("/")
		if url[1] == 'p_group':
			g = Private_Group.objects.get(title=g_title, user=request.user)
			db = DataBase.objects.get(p_group=g, name=dbname)
			stat = 0 
		else:
			g = Group.objects.get(title=g_title)
			db = DataBase.objects.get(group=g, name=dbname)
			stat = Membership.objects.get(user=request.user, group=g).status
		dbrow = db.rownum
		dbcolumn = db.columnnum
		user = request.user
		group = g
		rows = Row.objects.filter(rowdb=db).order_by('rownum')
		preset = json.loads(db.preset)
		col_size = json.loads(db.col_size)
		preset = zip(preset, col_size)
		cells = []
		for i in range(dbrow):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		return render_to_response('db/db_page.html', RequestContext(request, {'u':user, 'g':group, 'preset': preset, 'col_num': range(0, dbcolumn+1), 'css':'db_page', 'db':db, 'cells':cells, 'stat':stat}))
