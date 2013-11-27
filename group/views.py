#-*- coding: utf-8 -*-
from bacchusdb import settings
from group.models import Group, Private_Group, Membership, Admission
from db.models import DataBase
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import json
import re

def group_name_check(name):
	try:
		if Group.objects.get(title=name) is not None:
			return True
		else:
			return False
	except ObjectDoesNotExist:
	  	return False


def group_name_validation(title):
	if not bool(re.search('\S+', title)):
		return True
	else:
		title = re.sub(" ", "", title)
		title = title.encode('utf-8')
		return bool(re.search('[^\wㄱ-ㅎㅏ-ㅣ가-힣]+', title))

@login_required
@csrf_exempt
def group_make(request):
	data = {}
	if request.method == "POST" and request.is_ajax() and 'name_check' in request.POST:
		name = request.POST['group_name']

		if group_name_validation(name):
			data['fail'] = "Restriction"
		elif group_name_check(name):
			data['fail'] = ""
		else:
		 	data['success'] = ""

		return HttpResponse(json.dumps(data), content_type="application/json")

	elif request.method == "POST" and request.is_ajax():
		group_name = request.POST['group_name']
		group_info = request.POST['group_info']
		
		if group_name_validation(group_name):
			data['fail'] = "Restriction"
		
		elif 'privategroup' in request.POST:
		 	pg = Private_Group(title=group_name, info=group_info, user=request.user)
		 	pg.save()
		 	data['success'] = ""	

		elif group_name_check(group_name):
			data['fail'] = ""

		else:
			g = Group(title=group_name, info=group_info, num_member=1)
			g.save()
			m = Membership(user=request.user, group=g, status=0)
			m.save()
			data['success'] = ""

		return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		return render_to_response('group/group_make.html', RequestContext(request, {'u': request.user, 'css':'group_make'}))

@csrf_exempt
@login_required
def group_page(request, title):
	if request.method == "POST" and request.is_ajax() and 'name' in request.POST:
		try:
			g = Group.objects.get(title=title)
			db = DataBase.objects.get(group=g, name=request.POST['name'])
			db.delete()

		except ObjectDoesNotExist:
			pg = Private_Group.objects.get(title=title, user=request.user)
			db = DataBase.objects.get(p_group=pg, name=request.POST['name'])
			db.delete()

		return HttpResponse()
	else:
		try:
			m = Membership.objects.get(user=request.user, group=Group.objects.get(title=title))	

		except ObjectDoesNotExist:
			return redirect('user_manage.views.home')

		g = Group.objects.get(title=title)
		admin = Membership.objects.filter(group=g, status=0)
		normal = Membership.objects.filter(group=g, status=1)
		db = DataBase.objects.filter(group=g).order_by('name')
		if (m.status == 1):
			var = RequestContext(request, {'u': request.user, 'm': m, 'g': g, 'db': db, 'admin': admin, 'normal': normal, 'css':'group'})
		else:
			admission = Admission.objects.filter(group=g, status=0)
			var = RequestContext(request, {'u': request.user, 'join_req': admission, 'm': m, 'g': g, 'db': db, 'admin': admin, 'normal': normal, 'private': 'false', 'css':'group'})
		return render_to_response('group/group_page.html', var)

@login_required
def private_group_page(request, title):
	pg = Private_Group.objects.get(user=request.user, title=title)
	db = DataBase.objects.filter(p_group=pg)

	var = RequestContext(request, {'u': request.user, 'g': pg, 'db': db, 'private': 'true', 'css': 'group'})

	return render_to_response('group/group_page.html', var)

@csrf_exempt
@login_required
def group_search(request):
	group_name = request.POST['group_name']

	g = Group.objects.filter(title=group_name)
	return render_to_response('group/group_search.html', RequestContext(request, {'u':request.user, 'groups': g, 'css':'searchr'}))

@csrf_exempt
@login_required
def group_join_request(request, g_title):
	data = {}
	g = Group.objects.get(title=g_title)
	u = request.user
	msg = request.POST['message']

	try:
		admission = Admission.objects.get(user=u, group=g) 
		
		if (admission.status == 0):
			data['error'] = "Already"
		elif (admission.status == 1):
			data['error'] = "Member"
		else:
			data['error'] = "Denied"

	except ObjectDoesNotExist:
		try:
			m = Membership.objects.get(user=u, group=g)
			data['error'] = "Member"

		except ObjectDoesNotExist:
			admission = Admission(user=u, group=g, status=0, message=msg)
			admission.save()
			data['success'] = "success"
	
	return HttpResponse(json.dumps(data), content_type="application/json")

@csrf_exempt
@login_required
def group_join_request_process(request, g_title, username, success):
	u = User.objects.get(username=username)
	g = Group.objects.get(title=g_title)

	admission = Admission.objects.get(user=u, group=g)

	if (success == "s"):
		m = Membership(user=u, group=g, status=1)
		
		g.num_member += 1

		g.save()
		m.save()

		admission.status=1	
		
	else:
		admission.status = 2

	admission.save()

	return HttpResponse(json.dumps(""), content_type="application/json")


@csrf_exempt
@login_required
def group_withdraw(request):
	title = request.POST['title']

	if (request.POST['private'] == "True"):
		g = Private_Group.objects.get(title=title, user=request.user)
		g.delete()
	else:
		g = Group.objects.get(title=title)
		m = Membership.objects.get(group=g, user=request.user)
		try:
			ad = Admission.objects.get(group=g, user=request.user)
			ad.delete()
		
		except ObjectDoesNotExist:
			pass

			
		g.num_member -= 1

		g.save()
		m.delete()

		if (g.num_member == 0):
			g.delete()

	return HttpResponse("")
@csrf_exempt
@login_required
def group_admin(request, title):
	if request.method == "POST" and request.is_ajax():
		g = Group.objects.get(title=title)
		user = User.objects.get(username = request.POST['user'])
		mem = Membership.objects.get(group=g, user=user) 
		mem.status = 0
		mem.save()
		return HttpResponse("")
		normal = Membership.objects.filter(group=g, status=1)
		var = RequestContext(request, {'u':request.user, 'g':g, 'normal':normal, 'css':'add_admin'})
		return render_to_response('group/add_admin.html', var)
	else:		
		g = Group.objects.get(title=title)
		normal = Membership.objects.filter(group=g, status=1)
		var = RequestContext(request, {'u':request.user, 'g':g, 'normal':normal, 'css':'add_admin'})
		return render_to_response('group/add_admin.html', var)
