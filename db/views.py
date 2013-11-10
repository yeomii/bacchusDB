from bacchusdb import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from group.models import Group, Membership
from db.models import DataBase, Row, Cell
import json

@csrf_exempt
@login_required
def db_make(request, group_title):
	if request.method="POST":
		title = request.POST['db_name']
		dbtype = request.POST['db_type']
		info = request.POST['db_info']
		group = Group.objects.get(title=group_title)
		db = DataBase.objects.create_database(dbname=title, dbgroup=group, dbtype=dbtype, dbinfo = info)
		db.save()
		return HttpResponse("success")
	else:
		return render_to_response('db/db_make.html', RequestContext(request, {'u': request.user, 'css': 'db_make'}))

