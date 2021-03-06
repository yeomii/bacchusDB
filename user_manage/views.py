#-*- coding: utf-8 -*-
from bacchusdb import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from group.models import Group, Private_Group, Membership, Admission
import hashlib
import json
import random
import re

def home(request):
	if not request.user.is_authenticated():
		return redirect('user_manage.views.login_page')
	else:
		groups = Membership.objects.filter(user=request.user).order_by('group__title')
		p_groups = Private_Group.objects.filter(user=request.user).order_by('title')
		admissions = Admission.objects.filter(user=request.user, status=0)
		var = RequestContext(request, {'u': request.user, 'groups': groups, 'p_groups': p_groups, 'admissions': admissions, 'css':'user'})
		return render_to_response('user/user_page.html', var)

@csrf_exempt
def login_page(request):
	if not request.user.is_authenticated():
		if request.method == 'POST' and request.is_ajax():
			username = request.POST['id']
			password = request.POST['pw']
			user = authenticate (username=username, password=password)
			
			data = {}
			if user is not None:
				if user.is_active:
					login(request, user)
					data['success'] = "Success"
			else:
				data['error'] = "Login Failure"

			return HttpResponse(json.dumps(data), content_type="application/json")
		else:
			return render(request, 'user/login.html', {'css':'login'})
	else:
		return redirect('user_manage.views.home')


def logout_process(request):
	if request.user.is_authenticated():
		logout(request)
		return redirect('user_manage.views.home')
	else:
		return redirect('user_manage.views.login_page') 


def pw_validation(password):		#비밀번호 제한 체크하는 함수 제한에 걸리면 True 반환
	if (len(password) < 6):
		return True
	else:
	 	return False


def	id_validation(username):		#아이디에 문제가 없으면 True를 반환
	return not bool(re.search('\W+', username))

@csrf_exempt
def join_page(request):
	if request.user.is_authenticated():
		return redirect('user_manage.views.home')
	else:
		if request.method == 'POST' and request.is_ajax() and ("id_check" in request.POST):
			data = {}

			username = request.POST['id']
		
			if id_validation(username):
				try: 
					user = User.objects.get(username=username)
								
				except ObjectDoesNotExist:
					data['success'] = "success"
			else:
				data['fail'] = "restriction"
				
			return HttpResponse(json.dumps(data), content_type="application/json")

		elif request.method == 'POST' and request.is_ajax():
			data = {}

			try:
				username = request.POST['id']
				password = request.POST['pw']
				password_confirm = request.POST['pwconfirm']
				name = request.POST['uname']
				email = request.POST['email']

				if not id_validation(username):
					raise ValidationError("Id")

				if (pw_validation(password)):
					raise ValidationError("Password")

				if (password != password_confirm):
					data['error'] = "password_failure"
				else:
					user = User.objects.create_user(username=username, password=password, first_name=name, email=email)
					user.save()
					data['success'] = 'success'

			except IntegrityError as e:
				data['error'] = e.messages[0]

			except ValidationError as e:
				data['error'] = e.messages[0]

			return HttpResponse(json.dumps(data), content_type="application/json")

		else:
			return render(request, 'user/join.html',{'css':'join'})


@csrf_exempt
def find_password(request):
	if request.method == "POST" and request.is_ajax():
		data = {}
		try: 
			username = request.POST['id']
			email = request.POST['email']
			name = request.POST['uname']
			user = User.objects.get(username=username, email=email, first_name=name)
			new_password = hashlib.sha512((username+email+str(random.randint(1, 100))).encode('utf-8')).hexdigest()
			user.set_password(new_password)
			user.save()
			send_mail('<주의>새 비밀번호를 안내해드립니다', '새 비밀번호입니다. 바로 로그인해서 변경해주세요 ' + new_password, 'bacchuswebdb@gmail.com', [email], fail_silently=False)
			data['success'] = "success"

		except ObjectDoesNotExist:
			data['fail'] = "fail"
		
		return HttpResponse(json.dumps(data), content_type="application/json")

	else:
	  	return render(request, 'user/find_password.html', {'css':'findpw'})


@login_required
@csrf_exempt
def info_page(request):
	if request.method == "POST" and request.is_ajax():
		data = {}

		try:
			email = request.user.email
			input_email = request.POST['email']
			password = request.POST['pw']
			new_password = request.POST['new_pw']
			pw_confirm = request.POST['pw_confirm']

			if not request.user.check_password(password):
				data['password'] = "password"

			if email != input_email:
				request.user.email = input_email

			if request.user.check_password(new_password):
				data['password'] = "same"

			if new_password == "" and pw_confirm == "":
				pass
			elif (pw_validation(new_password)):
				raise ValidationError('error')
			elif (new_password != pw_confirm):
				data['npassword'] = "not same"
			else:
				request.user.set_password(new_password)
			
			if not ("password" in data or "npassword" in data):
				data['success'] = "success"
				request.user.save()
						
		except ObjectDoesNotExist:
			data['error'] = "User Does Not Exist"	

		except ValidationError:
			data['npassword'] = "validation"

		return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		return render_to_response(
				'user/my_page.html',
				RequestContext(request, {
					'u': request.user,
					'css':'mypage'
				}))
				
