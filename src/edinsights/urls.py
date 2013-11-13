from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'edinsights.core.views.index'),
    url('^', include('edinsights.core.urls')),
    url(r'^httpevent$', 'djeventstream.httphandler.views.http_view'),
    # url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'core.views.handle_view'),
    # url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)$', 'core.views.handle_view'),
    # url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)/([A-Za-z_0-9]+)$', 'core.views.handle_view'),
    # url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'core.views.handle_query'),
    # url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)$', 'core.views.handle_query'),
    # url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)/([A-Za-z_0-9+]+)$', 'core.views.handle_query'),
    # url(r'^schema$', 'core.views.list_all_endpoints'),
    # url(r'^probe$', 'core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)$', 'core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'core.views.handle_probe'),
    url('^tasks/', include('djcelery.urls')),
)

if settings.DEBUG and settings.DJFS['type'] == 'osfs':
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns+= patterns('',
                           url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.STATIC_ROOT,
                               'show_indexes' : True,
                               }),
                           url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.DJFS['directory_root'],
                               'show_indexes' : True,
                               }),
                           )
# else:
#     urlpatterns+= patterns('frontend.views',
#                            url(r'^data/(?P<path>.*)$', 'protected_data')
#     )

