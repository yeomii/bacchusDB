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
	#url(r'^user/', include(bacchusdb.user.urls),
	url(r'^$', 'user_manage.views.home'),
	url(r'^login$', 'user_manage.views.login_page'),
	url(r'^join$', 'user_manage.views.join_page'),
	url(r'^logout$', 'user_manage.views.logout_process'),
	url(r'^find_password$', 'user_manage.views.find_password'),
	url(r'^my_info$', 'user_manage.views.info_page'),
)
