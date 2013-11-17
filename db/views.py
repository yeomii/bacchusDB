from bacchusdb import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
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

		url = request.path.split("/")
		if url[1] == "group":
			group = Group.objects.get(title=group_title)
			db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info)

		elif url[1] == "p_group":
			group = Private_Group.objects.get(title=group_title, user=request.user)
			db = DataBase.objects.create_pdatabase(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info)

	
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
		preset[int(request.POST['num'])] = request.POST['content']
		db.preset = json.dumps(preset)
		db.save()

		return HttpResponse('')

	else:
		g = Group.objects.get(title=g_title)
		db = DataBase.objects.get(group=g, name=dbname)
		dbrow = db.rownum
		dbcolumn = db.columnnum
		user = request.user
		group = db.group
		rows = Row.objects.filter(rowdb=db).order_by('rownum')
		preset = json.loads(db.preset)
		cells = []
		for i in range(dbrow):
			cell = Cell.objects.filter(cellrow=rows[i])
			cells.append(cell.order_by('colnum'))
		return render_to_response('db/db_page.html', RequestContext(request, {'u':user, 'g':group, 'preset': preset, 'col_num': range(0, dbcolumn+1), 'css':'db_page', 'db':db, 'cells':cells}))
