from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^dbpage_(.*)$', 'db.views.db_page'),	
)
