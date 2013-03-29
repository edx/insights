from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'dashboard.views.new_dashboard'),
    url(r'^event$', 'an_evt.views.handle_event'),
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'an_evt.views.handle_view'),
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)$', 'an_evt.views.handle_view'),
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)/([A-Za-z_0-9]+)$', 'an_evt.views.handle_view'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'an_evt.views.handle_query'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)$', 'an_evt.views.handle_query'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)/([A-Za-z_0-9+]+)$', 'an_evt.views.handle_query'),
    url(r'^schema$', 'an_evt.views.list_all_endpoints'),
    url(r'^probe$', 'an_evt.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)$', 'an_evt.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'an_evt.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'an_evt.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'an_evt.views.handle_probe'),
    url(r'^dashboard$', 'dashboard.views.dashboard'),
    url(r'^new_dashboard$', 'dashboard.views.new_dashboard'),
    url(r'^sns', 'sns.views.sns'),
    # url(r'^anserv/', include('anserv.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^frontend/', include('frontend.urls')),
    url('^tasks/', include('djcelery.urls')),
)

if settings.DEBUG:
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns+= patterns('',
                           url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.STATIC_ROOT,
                               'show_indexes' : True,
                               }),
                           url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.PROTECTED_DATA_ROOT,
                               'show_indexes' : True,
                               }),
                           )
else:
    urlpatterns+= patterns('frontend.views',
                           url(r'^data/(?P<path>.*)$', 'protected_data')
    )

