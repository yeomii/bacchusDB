from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^group/(\D+)/db_make$', 'db.views.db_make'),
	url(r'^p_group/(\D+)/db_make$', 'db.views.db_make'),
	url(r'^group/(\D+)/(\D+)$', 'db.views.db_page'),
	url(r'^p_group/(\D+)/(\D+)$', 'db.views.db_page'),
)
