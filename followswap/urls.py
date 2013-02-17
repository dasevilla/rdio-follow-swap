from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'followswap.views.home', name='index'),
    url(r'^sign-out/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='sign-out'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include('social_auth.urls')),
    url(r'^give$', 'followswap.views.give', name='give'),
    url(r'^history$', 'followswap.views.history', name='history'),
)


urlpatterns += staticfiles_urlpatterns()
