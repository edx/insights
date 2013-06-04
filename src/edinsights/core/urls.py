from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    # Examples:
    url(r'^view/([A-Za-z_+]+)$', 'edinsights.core.views.handle_view'),
    url(r'^query/([A-Za-z_+]+)$', 'edinsights.core.views.handle_query'),
    url(r'^schema$', 'edinsights.core.views.schema'),
    url(r'^event_properties$', 'edinsights.core.views.event_properties'),
    # url(r'^probe$', 'edinsights.core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)$', 'edinsights.core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'edinsights.core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'edinsights.core.views.handle_probe'),
    # url(r'^probe/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)/([A-Za-z_+]+)$', 'edinsights.core.views.handle_probe'),
)
