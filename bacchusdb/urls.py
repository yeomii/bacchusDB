#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bacchusdb.views.home', name='home'),
    # url(r'^bacchusdb/', include('bacchusdb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	url(r'', include('db.urls')),	#현재 group/'group_title'/db_make가 user_manage.urls에서 catch되서 순서 변경해놓음
	url(r'', include('user_manage.urls')),
	url(r'', include('group.urls')),
	)
