from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    # Examples:
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_view'),
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)$', 'djanalytics.core.views.handle_view'),
    url(r'^view/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9]+)/([A-Za-z_0-9]+)$', 'djanalytics.core.views.handle_view'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_query'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)$', 'djanalytics.core.views.handle_query'),
    url(r'^query/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_0-9+]+)/([A-Za-z_0-9+]+)$', 'djanalytics.core.views.handle_query'),
    url(r'^schema$', 'djanalytics.core.views.list_all_endpoints'),
    url(r'^probe$', 'djanalytics.core.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_probe'),
    url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'djanalytics.core.views.handle_probe'),
)
