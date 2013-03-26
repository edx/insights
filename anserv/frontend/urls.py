from django.conf.urls.defaults import *

urlpatterns=patterns('django.contrib.auth.views',
    url(r'^login/$','login'),
    url(r'^logout/$','logout'),
)

