from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^meta$', views.meta, name='meta'),
    url(r'^meta/authors$', views.metaAuthors, name='metaAuthors'),
    url(r'^keywords$', views.keywords, name='keywords')
]
