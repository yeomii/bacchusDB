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
	url(r'^group_make$', 'group.views.group_make'),
	url(r'^group_name_check$', 'group.views.group_name_check'),
	url(r'^group_search$', 'group.views.group_search'),
	url(r'^group_search/(\D+)$', 'group.views.group_join_request'),
	url(r'^group/(\D+)/(\D+)/(\D)$', 'group.views.group_join_request_process'),
	url(r'^group/(\D+)$', 'group.views.group_page'),
	)
