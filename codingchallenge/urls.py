from django.conf.urls import patterns, url

from codingchallenge import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^choose/$', views.choose, name='choose'),
    url(r'^(?P<category_id_1>[0-9]+)/(?P<category_id_2>[0-9]+)/(?P<category_id_3>[0-9]+)/(?P<page>[0-9]+)/$', views.results, name='results'),
)