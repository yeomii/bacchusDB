#-*- coding: utf-8 -*-
from bacchusdb import settings
from group.models import Group, Membership, Admission
from db.models import Group_db
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import json

def group_name_check(name):
	try:
		if Group.objects.get(title=name) is not None:
			return True
		else:
			return False
	except ObjectDoesNotExist:
	  	return False

@login_required
@csrf_exempt
def group_make(request):
	data = {}
	if request.method == "POST" and request.is_ajax() and 'name_check' in request.POST:
		name = request.POST['group_name']
		if group_name_check(name):
			data['fail'] = ""
		else:
		 	data['success'] = ""

		return HttpResponse(json.dumps(data), content_type="application/json")
	elif request.method == "POST" and request.is_ajax():
		group_name = request.POST['group_name']
		group_info = request.POST['group_info']
		if group_name == "":
			return HttpResponse('Group_name cannot be empty') 
		g = Group(title=group_name, info=group_info, num_member=1)
		g.save()
		m = Membership(user=request.user, group=g, status=0)
		m.save()
		data['success'] = ""
		return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		return render_to_response('group/group_make.html', RequestContext(request, {'u': request.user, 'css':'group_make'}))

@login_required
def group_page(request, title):
#	title = resolve(request.path_info).url_name.split("_")[1]
	try:
		m = Membership.objects.get(user=request.user, group=Group.objects.get(title=title))	

	except ObjectDoesNotExist:
		return redirect('user_manage.views.home')

	g = Group.objects.get(title=title)
	admin = Membership.objects.filter(group=g, status=0)
	normal = Membership.objects.filter(group=g, status=1)
	db = Group_db.objects.filter(group=g)

	if (m.status == 1):
		var = RequestContext(request, {'u': request.user, 'm': m, 'g': g, 'db': db, 'admin': admin, 'normal': normal, 'css':'group'})
	else:
		admission = Admission.objects.filter(group=g, status=0)
		var = RequestContext(request, {'u': request.user, 'join_req': admission, 'm': m, 'g': g, 'db': db, 'admin': admin, 'normal': normal, 'css':'group'})
	return render_to_response('group/group_page.html', var)

@csrf_exempt
@login_required
def group_search(request):
	group_name = request.POST['group_name']

	g = Group.objects.filter(title__contains=group_name)
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
		m.save()

		admission.status=1	
		
	else:
		admission.status = 2

	admission.save()

	return HttpResponse(json.dumps(""), content_type="application/json")
