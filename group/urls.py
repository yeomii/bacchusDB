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
	url(r'^group_withdraw$', 'group.views.group_withdraw'),
	url(r'^group_search$', 'group.views.group_search'),
	url(r'^group_search/([\w, \s]+)$', 'group.views.group_join_request'),
	url(r'^group/([\w, \s]+)/([\w, \s]+)/([s,f])$', 'group.views.group_join_request_process'),
	url(r'^p_group/([\w, \s]+)$', 'group.views.private_group_page'),
	url(r'^group/([\w, \s]+)$', 'group.views.group_page'),
	url(r'^group_admin/([\w, \s]+)$', 'group.views.group_admin'),
	)
