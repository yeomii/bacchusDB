from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^group/(\D+)/db_make$', 'db.views.db_make'),
	url(r'^dbpage_(.*)$', 'db.views.db_page'),	
)
