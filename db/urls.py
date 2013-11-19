from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^group/([\w, \s]+)/db_delete$', 'group.views.group_page'),
	url(r'^group/([\w, \s]+)/db_make$', 'db.views.db_make'),
	url(r'^p_group/([\w, \s]]+)/db_make$', 'db.views.db_make'),
	url(r'^group/([\w, \s]+)/([\w, \s]+)$', 'db.views.db_page'),
	url(r'^p_group/([\w, \s]+)/([\w, \s]+)$', 'db.views.db_page'),
)
