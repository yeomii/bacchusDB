from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^group/(\w+)/db_make$', 'db.views.db_make'),
	url(r'^p_group/(\w+)/db_make$', 'db.views.db_make'),
	url(r'^group/(\w+)/(\w+)$', 'db.views.db_page'),
	url(r'^p_group/(\w+)/(\w+)$', 'db.views.db_page'),
)
