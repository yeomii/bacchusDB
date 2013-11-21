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

@csrf_exempt
@login_required
def db_make(request, group_title):
	if request.method=="POST":
		title = request.POST['db_name']
		dbtype = request.POST['db_type']
		info = request.POST['db_info']
		col = request.POST.getlist('col')
		url = request.path.split("/")
		if url[1] == "group":
			group = Group.objects.get(title=group_title)
			db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info, private=False, col_preset=col)

		elif url[1] == "p_group":
			group = Private_Group.objects.get(title=group_title, user=request.user)
			db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info, private=True, col_preset=col)

	
		db.save()

		return HttpResponse("success")
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
	
		return HttpResponse()

	elif request.method == "POST" and request.is_ajax() and 'del_row[]' in request.POST:
		g = Group.objects.get(title=request.POST['group'])
		db = DataBase.objects.get(group=g, name=request.POST['db_name'])
		for row in request.POST.getlist('del_row[]'):
			db.rowDelete(int(row))

		rows = Row.objects.filter(rowdb=db).order_by('rownum')

		preset = json.loads(db.preset)	
		cells = [] 

		for i in range(db.rownum):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		
		t = loader.get_template('db/table.html')
		c = RequestContext(request, {'preset': preset, 'col_num': range(0, db.columnnum+1), 'db': db, 'cells': cells})
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
		else:
			g = Group.objects.get(title=g_title)
			db = DataBase.objects.get(group=g, name=dbname)

		dbrow = db.rownum
		dbcolumn = db.columnnum
		user = request.user
		group = g
		rows = Row.objects.filter(rowdb=db).order_by('rownum')
		preset = json.loads(db.preset)
		cells = []
		for i in range(dbrow):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		return render_to_response('db/db_page.html', RequestContext(request, {'u':user, 'g':group, 'preset': preset, 'col_num': range(0, dbcolumn+1), 'css':'db_page', 'db':db, 'cells':cells}))
